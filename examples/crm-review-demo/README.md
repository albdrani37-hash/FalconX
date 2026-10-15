# CRM Review Demonstration
Abdullah Alharbi · Independent researcher and Python developer · Saudi Arabia

A runnable, offline portfolio example created with AI assistance. It uses only synthetic contacts and the Python standard library. It is a local workflow demonstration, not a client deployment or an AI classifier.

## Quick start
Requires Python 3.10 or newer. No packages, API keys, accounts or internet access are needed.

```sh
python3 run_demo.py
python3 -m unittest discover -v
```
On Windows, use `python` if `python3` is unavailable. Open `results/demo.html` in a browser to view the results. Every run starts from a fresh temporary database and rewrites the demo results. Audit timestamps reflect the new run.

The included run uses 20 synthetic records: 20 have proposed field changes, 3 exact-email duplicate groups are identified, and 4 quality flags are raised. Two records receive simulated approval and are updated. Repeating that approval applies zero additional changes. All 12 automated tests passed when packaged.

## Explicit review workflow
```sh
python3 crm_demo.py --db my_demo.sqlite init synthetic_contacts.json
python3 crm_demo.py --db my_demo.sqlite plan review_plan.json
```
Inspect the generated plan. Create your own approval JSON with its exact `plan_id`, a reviewer label, and a list of approved contact IDs. The packaged simulated approval shows the format; it is not an endorsement by a human reviewer.

```sh
python3 crm_demo.py --db my_demo.sqlite apply approval.json
python3 crm_demo.py --db my_demo.sqlite export approved_contacts.json
```
Each approved contact accepts all proposed fields for that contact. Empty approvals change nothing. For field-level approval, create a revised workflow; do not edit the stored plan. A nonempty database cannot be reseeded by the init command.

## Decisions and evidence
- Whitespace is trimmed in name, company and email; only email-domain case is normalized. The local part is preserved.
- Email validation is a basic syntax screen, not deliverability validation.
- Identical normalized email addresses create review candidates, never automatic merges. Shared mailboxes are a known false-positive case; case variants of the email local part are not grouped.
- Blank category fields get a transparent suggestion when notes contain exactly one of the keywords `quote` or `support`. Multiple matches remain unclassified and flagged. This is a keyword demo, not semantic intent inference.
- SQLite stores the proposed source records. Their SHA-256 content-derived plan ID binds approvals to an exact stored plan. A changed approved row aborts the entire pending batch.
- Record writes and before/after audit entries use one transaction. Replays are idempotent for the same plan and record.
- Audit records include before/after data, plan ID, a reviewer label and UTC timestamp.

## Tests
The suite checks approval scoping, exact-plan matching, unknown IDs, stale-source batch rejection, rollback when audit insertion fails, replay idempotency, empty approvals, duplicate input IDs, duplicate candidate handling, ambiguous categories, deterministic proposals and preservation of email local-part case.

## Limits
No live CRM adapter, user authentication, identity-verified approval, encryption, semantic deduplication, external LLM, distributed concurrency system, performance benchmark, or production certification is included. The local reviewer label is not authentication. A local administrator can modify the database; the audit is not tamper-proof. This sample is designed for review and extension before any real data or CRM integration.

## Proposed paid extension
One agreed CRM sandbox, a defined field mapping and a small acceptance dataset. Implement the adapter and failure handling, add authenticated approval appropriate to the client's environment, validate the agreed scenarios, and deliver source plus setup instructions. Scope, access, hour cap and acceptance criteria must be agreed before work.
