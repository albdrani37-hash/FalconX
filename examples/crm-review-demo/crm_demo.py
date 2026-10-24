"""Local CRM review demonstration. Python standard library only; no network calls."""
import argparse, hashlib, html, json, re, sqlite3
from datetime import datetime, timezone
from pathlib import Path

VERSION = '1.0'

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

def connect(path):
    db = sqlite3.connect(path, isolation_level=None)
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript('''
    CREATE TABLE IF NOT EXISTS contacts(id TEXT PRIMARY KEY, data TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS plans(id TEXT PRIMARY KEY, data TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS audit(seq INTEGER PRIMARY KEY, plan_id TEXT NOT NULL,
      contact_id TEXT NOT NULL, before_data TEXT NOT NULL, after_data TEXT NOT NULL,
      reviewer TEXT NOT NULL, applied_at TEXT NOT NULL, UNIQUE(plan_id, contact_id));
    ''')
    return db

def snapshot(db):
    return [json.loads(row[0]) for row in db.execute('SELECT data FROM contacts ORDER BY id')]

def seed(db, rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError('Input must be a non-empty list')
    ids = set()
    for r in rows:
        if not isinstance(r, dict) or set(r) != {'id', 'name', 'email', 'company', 'notes', 'category'}:
            raise ValueError('Invalid contact schema')
        if not all(isinstance(v, str) for v in r.values()) or not r['id'] or r['id'] in ids:
            raise ValueError('IDs must be non-empty and unique; values must be strings')
        ids.add(r['id'])
    db.execute('BEGIN IMMEDIATE')
    try:
        if db.execute('SELECT COUNT(*) FROM contacts').fetchone()[0]:
            raise ValueError('Database is not empty; use a new database')
        db.executemany('INSERT INTO contacts VALUES (?,?)', [(r['id'], canonical(r)) for r in rows])
        db.execute('COMMIT')
    except Exception:
        db.execute('ROLLBACK'); raise

def propose(db):
    rows = snapshot(db)
    proposals, issues, groups = [], [], {}
    for row in rows:
        changes = {}
        for field in ('name', 'company', 'email'):
            value = row[field].strip()
            if field == 'email':
                # Preserve local-part case; only normalize the domain.
                if '@' in value:
                    local, domain = value.rsplit('@', 1)
                    value = local + '@' + domain.lower()
                valid = bool(re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', value))
                if not valid:
                    issues.append({'id': row['id'], 'issue': 'Missing or invalid email; manual review'})
                else:
                    groups.setdefault(value, []).append(row['id'])
            if value != row[field]:
                changes[field] = value
        if not row['name'].strip():
            issues.append({'id': row['id'], 'issue': 'Missing name; manual review'})
        # Transparent demonstration rule, not an AI model or inferred customer intent.
        notes = row['notes'].casefold()
        tags = [tag for token, tag in [('quote', 'quote_request'), ('support', 'support_request')] if token in notes]
        if not row['category'] and len(tags) == 1:
            changes['category'] = tags[0]
        elif not row['category'] and len(tags) > 1:
            issues.append({'id': row['id'], 'issue': 'Conflicting category keywords; manual review'})
        if changes:
            proposals.append({'id': row['id'], 'before': row, 'changes': changes})
    plan = {'version': VERSION, 'source_hash': digest(rows), 'proposals': proposals,
            'issues': issues, 'duplicate_candidates': [v for v in groups.values() if len(v) > 1]}
    plan_id = digest(plan)
    db.execute('INSERT OR IGNORE INTO plans VALUES (?,?)', (plan_id, canonical(plan)))
    return {'plan_id': plan_id, **plan}

def apply(db, plan_id, approval):
    if set(approval) != {'plan_id', 'reviewer', 'approved_ids'} or approval['plan_id'] != plan_id:
        raise ValueError('Approval must match the exact plan')
    if not isinstance(approval['reviewer'], str) or not approval['reviewer'].strip():
        raise ValueError('A reviewer label is required')
    ids = approval['approved_ids']
    if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids) or len(ids) != len(set(ids)):
        raise ValueError('Approved IDs must be a list of unique strings')
    db.execute('BEGIN IMMEDIATE')
    try:
        stored = db.execute('SELECT data FROM plans WHERE id=?', (plan_id,)).fetchone()
        if stored is None:
            raise ValueError('Unknown plan')
        plan = json.loads(stored[0])
        if digest(plan) != plan_id:
            raise ValueError('Stored plan integrity check failed')
        choices = {p['id']: p for p in plan['proposals']}
        if not set(ids) <= choices.keys():
            raise ValueError('Approval contains IDs outside this plan')
        # A prior audit entry is not enough to certify a replay: the stored
        # before/after evidence and current contact must still match this plan.
        done = {
            row[0]: (row[1], row[2]) for row in db.execute(
                'SELECT contact_id,before_data,after_data FROM audit WHERE plan_id=?',
                (plan_id,))
        }
        completed = set(ids) & set(done)
        for cid in sorted(completed):
            p = choices[cid]
            expected_before = canonical(p['before'])
            expected_after = canonical({**p['before'], **p['changes']})
            audit_before, audit_after = done[cid]
            current = db.execute('SELECT data FROM contacts WHERE id=?', (cid,)).fetchone()
            if (audit_before != expected_before or audit_after != expected_after
                    or current is None or current[0] != expected_after):
                raise ValueError('Replay integrity check failed: ' + cid)
        pending = sorted(set(ids) - completed)
        # Check every pending row before writing; stale data aborts the complete batch.
        for cid in pending:
            current = db.execute('SELECT data FROM contacts WHERE id=?', (cid,)).fetchone()
            if current is None or json.loads(current[0]) != choices[cid]['before']:
                raise ValueError('Stale contact: ' + cid)
        for cid in pending:
            p = choices[cid]
            after = {**p['before'], **p['changes']}
            db.execute('UPDATE contacts SET data=? WHERE id=?', (canonical(after), cid))
            db.execute('INSERT INTO audit(plan_id,contact_id,before_data,after_data,reviewer,applied_at) VALUES (?,?,?,?,?,?)',
                (plan_id, cid, canonical(p['before']), canonical(after), approval['reviewer'].strip(), datetime.now(timezone.utc).isoformat()))
        db.execute('COMMIT')
        return {'applied': len(pending), 'already_applied': len(completed)}
    except Exception:
        db.execute('ROLLBACK'); raise


def verify_audit(db):
    """Check local plan/audit consistency; not a tamper-proof security attestation.

    Every audit entry must match its stored plan's exact before/after values.
    Only the most recent audited update for each contact is compared to the
    current contact; later approved plans may legitimately supersede earlier ones.
    Untracked contacts are outside this verification scope.
    """
    issues = []
    records = db.execute(
        'SELECT seq,plan_id,contact_id,before_data,after_data FROM audit ORDER BY seq'
    ).fetchall()
    plans = {}
    latest = {}
    for seq, plan_id, cid, before, after in records:
        latest[cid] = (seq, after)
        if plan_id not in plans:
            stored = db.execute('SELECT data FROM plans WHERE id=?', (plan_id,)).fetchone()
            if stored is None:
                plans[plan_id] = None
            else:
                try:
                    parsed = json.loads(stored[0])
                    plans[plan_id] = parsed if digest(parsed) == plan_id else False
                except (ValueError, TypeError):
                    plans[plan_id] = False
        plan = plans[plan_id]
        if plan is None:
            issues.append({'seq': seq, 'contact_id': cid, 'code': 'MISSING_PLAN'})
            continue
        if plan is False:
            issues.append({'seq': seq, 'contact_id': cid, 'code': 'INVALID_PLAN'})
            continue
        try:
            before_value = json.loads(before)
            after_value = json.loads(after)
        except (ValueError, TypeError):
            issues.append({'seq': seq, 'contact_id': cid, 'code': 'INVALID_AUDIT_JSON'})
            continue
        matches = [p for p in plan.get('proposals', []) if p.get('id') == cid]
        if len(matches) != 1:
            issues.append({'seq': seq, 'contact_id': cid, 'code': 'AUDIT_PLAN_MISMATCH'})
            continue
        p = matches[0]
        expected_after = {**p['before'], **p['changes']}
        if before_value != p['before'] or after_value != expected_after:
            issues.append({'seq': seq, 'contact_id': cid, 'code': 'AUDIT_PLAN_MISMATCH'})
    for cid, (seq, after) in latest.items():
        current = db.execute('SELECT data FROM contacts WHERE id=?', (cid,)).fetchone()
        try:
            expected = json.loads(after)
            actual = json.loads(current[0]) if current else None
        except (ValueError, TypeError):
            expected, actual = object(), None
        if current is None or actual != expected:
            issues.append({'seq': seq, 'contact_id': cid, 'code': 'CURRENT_ROW_MISMATCH'})
    return {
        'ok': not issues,
        'audited_records': len(records),
        'audited_contacts': len(latest),
        'issues': issues,
    }

def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def report(db, plan, result, replay, out):
    esc = lambda x: html.escape(str(x))
    rows = ''.join('<tr><td>'+esc(p['id'])+'</td><td>'+esc(p['before']['name'])+'</td><td>'+esc(', '.join(p['changes']))+'</td></tr>' for p in plan['proposals'])
    content = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CRM Review | Abdullah Alharbi</title><style>body{font:16px/1.65 system-ui;color:#183342;background:#eff4f5;margin:0}main{max-width:1000px;margin:auto;padding:48px 24px}.eyebrow{letter-spacing:.15em;font-size:12px;color:#267a70}h1{font-size:48px;line-height:1.1;max-width:760px}h2{font-size:24px}.cards{display:flex;flex-wrap:wrap;gap:15px}.card{background:white;border-top:4px solid #168c7c;border-radius:8px;padding:20px;flex:1;min-width:140px}.num{display:block;font-size:38px;font-weight:700}section{background:white;padding:26px;margin-top:24px;border-radius:10px}table{border-collapse:collapse;width:100%;font-size:14px}td,th{text-align:left;padding:9px;border-bottom:1px solid #e2eaed}code{overflow-wrap:anywhere}footer{font-size:13px;margin-top:24px;color:#506575}</style><main><p class="eyebrow">ABDULLAH ALHARBI · PYTHON AUTOMATION</p><h1>Review changes.<br>Approve precisely.<br>Keep the evidence.</h1><p>A working local CRM demonstration using synthetic records. Rule-based suggestions, explicit approval and transactional audit history. No live CRM or external AI service.</p><div class="cards">'''
    for label, n in [('Synthetic contacts', len(snapshot(db))), ('Records with suggestions', len(plan['proposals'])), ('Approved updates applied', result['applied']), ('Extra writes on replay', replay['applied'])]:
        content += '<div class="card"><span class="num">'+esc(n)+'</span>'+esc(label)+'</div>'
    content += '</div><section><h2>What the workflow does</h2><p>Normalizes surrounding whitespace and email-domain case; identifies exact-email duplicate candidates; suggests categories from documented keywords; holds invalid and ambiguous data for review. Duplicate records are never merged automatically.</p><p>The packaged run approves two synthetic records under the label demo-reviewer. This is a simulated approval, not an independent human review.</p></section><section><h2>Review queue</h2><table><thead><tr><th>Record</th><th>Name</th><th>Proposed fields</th></tr></thead><tbody>'+rows+'</tbody></table><p>Duplicate candidate groups: '+esc(len(plan['duplicate_candidates']))+'. Data-quality flags: '+esc(len(plan['issues']))+'.</p></section><section><h2>Evidence & limits</h2><p>Updates and audit entries commit together in SQLite. Exact approved IDs are tied to a content-derived plan identifier. Changed source rows abort a pending batch. Repeating an applied batch creates no additional writes.</p><p>This demonstrates local mechanics only. It has no authenticated reviewer identity, external CRM integration, authorization server, encrypted storage, semantic deduplication, live LLM classification or production performance claim. Local administrators can change SQLite; this is not a tamper-proof audit system.</p><p>Plan identifier: <code>'+esc(plan['plan_id'])+'</code></p></section><footer>Independent demonstration · Created with AI assistance · October 2026 · Synthetic data only</footer></main></html>'
    Path(out).write_text(content, encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', default='demo.sqlite')
    sub = parser.add_subparsers(dest='command', required=True)
    p=sub.add_parser('init'); p.add_argument('input')
    p=sub.add_parser('plan'); p.add_argument('output')
    p=sub.add_parser('apply'); p.add_argument('approval')
    p=sub.add_parser('export'); p.add_argument('output')
    p=sub.add_parser('audit'); p.add_argument('output')
    args=parser.parse_args(); db=connect(args.db)
    try:
        if args.command=='init': seed(db, json.loads(Path(args.input).read_text(encoding='utf-8')))
        elif args.command=='plan': write_json(args.output, propose(db))
        elif args.command=='apply':
            approval=json.loads(Path(args.approval).read_text(encoding='utf-8'))
            print(json.dumps(apply(db, approval['plan_id'], approval)))
        elif args.command=='export': write_json(args.output, snapshot(db))
        elif args.command=='audit':
            result = verify_audit(db)
            write_json(args.output, result)
            if not result['ok']:
                raise SystemExit(1)
    finally: db.close()

if __name__=='__main__': main()
