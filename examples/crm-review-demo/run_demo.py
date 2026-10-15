"""Runs the packaged synthetic example, with simulated approval of two records."""
import json, tempfile
from pathlib import Path
from crm_demo import connect, seed, propose, apply, write_json, snapshot, report
root=Path(__file__).parent
out=root/'results'; out.mkdir(exist_ok=True)
rows=json.loads((root/'synthetic_contacts.json').read_text())
with tempfile.TemporaryDirectory() as tmp:
    db=connect(str(Path(tmp)/'demo.sqlite')); seed(db,rows); plan=propose(db)
    approval={'plan_id':plan['plan_id'],'reviewer':'demo-reviewer','approved_ids':['C001','C002']}
    result=apply(db,plan['plan_id'],approval); replay=apply(db,plan['plan_id'],approval)
    write_json(out/'plan.json',plan); write_json(out/'simulated_approval.json',approval)
    write_json(out/'after.json',snapshot(db)); write_json(out/'run_result.json',{'initial_apply':result,'replay':replay})
    audit=[dict(zip(['seq','plan_id','contact_id','before','after','reviewer','applied_at'],r)) for r in db.execute('SELECT * FROM audit ORDER BY seq')]
    write_json(out/'audit.json',audit); report(db,plan,result,replay,out/'demo.html'); db.close()
print(json.dumps({'contacts':len(rows),'proposed_records':len(plan['proposals']),'duplicate_groups':len(plan['duplicate_candidates']),'quality_flags':len(plan['issues']),'initial_apply':result,'replay':replay}))
