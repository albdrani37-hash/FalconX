# GitHub Actions CI Evidence — Python CRM QA Demonstration

## Latest verified result: audit consistency and 25 regression tests — 24 October 2026

**GitHub Actions run:** [40052721026](https://github.com/albdrani37-hash/FalconX/actions/runs/40052721026) · **Result:** `success` · **Tested commit:** [6036c88357fba54da3b1c3a5705dd32a69fe7392](https://github.com/albdrani37-hash/FalconX/commit/6036c88357fba54da3b1c3a5705dd32a69fe7392).

| Runtime | Job ID | Regression suite | Packaged synthetic workflow and assertions |
| --- | --- | --- | --- |
| Python 3.11 | [120748705788](https://github.com/albdrani37-hash/FalconX/actions/runs/40052721026/job/120748705788) | 25/25 passed | passed |
| Python 3.12 | [120748705852](https://github.com/albdrani37-hash/FalconX/actions/runs/40052721026/job/120748705852) | 25/25 passed | passed |
| Python 3.13 | [120748705665](https://github.com/albdrani37-hash/FalconX/actions/runs/40052721026/job/120748705665) | 25/25 passed | passed |

These are **25 distinct tests repeated under three Python versions (75 successful test executions, not 75 unique cases)**. The job logs report `Ran 25 tests`, `OK` and successful synthetic workflow/JSON assertions on each runtime.

**Added audit verification:** `crm_demo.py --db <path> audit <report.json>` checks stored audit records against their respective plans, checks the latest audited after-state against the current SQLite contact and emits machine-readable results with a nonzero exit code on inconsistencies. Seven new tests exercise legitimate records, changed/deleted rows, altered evidence, missing plans, malformed JSON and unaudited-contact scope. [Tests](examples/crm-review-demo/test_audit_verification.py) · [Usage and limitations](examples/crm-review-demo/README.md).

**Test-first history:** initial run [40052680559](https://github.com/albdrani37-hash/FalconX/actions/runs/40052680559) failed before the new audit verifier was added. Later source and CLI runs [40052695734](https://github.com/albdrani37-hash/FalconX/actions/runs/40052695734) and [40052711595](https://github.com/albdrani37-hash/FalconX/actions/runs/40052711595) succeeded; the final complete run above also succeeded. Failure notification emails about earlier commits do not contradict the result of the tested final commit.

**Boundary:** These results concern an offline synthetic example; neither the stored SQLite audit nor the verification output is tamper-proof, and the run does not establish real customer integration, independent certification or guaranteed production reliability.

---

## Earlier verified result: replay-integrity fix — 24 October 2026

**Latest source-code change tested:** [`8350642a55efe6aae34f3eb7bac53e68ba0b39f5`](https://github.com/albdrani37-hash/FalconX/commit/8350642a55efe6aae34f3eb7bac53e68ba0b39f5)

**GitHub Actions run:** [`40051950195`](https://github.com/albdrani37-hash/FalconX/actions/runs/40051950195) — all three Python matrix jobs completed with **success**.

| Runtime | GitHub Actions job | Regression result | Synthetic end-to-end and JSON assertions |
| --- | --- | --- | --- |
| Python 3.11 | [120746337332](https://github.com/albdrani37-hash/FalconX/actions/runs/40051950195/job/120746337332) | **18/18 passed** | passed |
| Python 3.12 | [120746337287](https://github.com/albdrani37-hash/FalconX/actions/runs/40051950195/job/120746337287) | **18/18 passed** | passed |
| Python 3.13 | [120746337067](https://github.com/albdrani37-hash/FalconX/actions/runs/40051950195/job/120746337067) | **18/18 passed** | passed |

The same 18 distinct tests run on each of three Python runtimes; **54 passed test executions, not 54 different cases**. The six additional tests cover an unchanged replay, changed or missing applied records, changed audit before/after values, and a mixed previously-applied/new approval whose validation must fail atomically.

**Observed test-first history:** run [`40051851228`](https://github.com/albdrani37-hash/FalconX/actions/runs/40051851228) failed in five newly added tests because the pre-fix implementation accepted invalid replay evidence. The first patch in run [`40051915024`](https://github.com/albdrani37-hash/FalconX/actions/runs/40051915024) also failed because its implementation accidentally intersected a set with a dictionary. Both were superseded by the successful run `40051950195`. GitHub's failure emails refer to those historical attempts and do **not** establish that the later corrected revision failed.

**Guard behavior:** before acknowledging an already-applied approval, the implementation compares its plan-bound expected before/after records to saved audit evidence and checks that the current row still matches the expected after record. A mismatch raises a replay-integrity error before applying any pending changes in the same transaction. This is a local consistency check: it is **not** cryptographic authentication, an externally trusted audit ledger, or production security certification.

---

## Original 12-test baseline — preserved historical record



**Baseline verified:** 24 October 2026 · **Source:** GitHub Actions run [#1](https://github.com/albdrani37-hash/FalconX/actions/runs/40047365598) · **Conclusion:** `success`

**Workflow:** [`.github/workflows/crm-qa.yml`](.github/workflows/crm-qa.yml)
**Verified commit:** [`a4783781e828231bc0b4a8fdbb15c2292824d98d`](https://github.com/albdrani37-hash/FalconX/commit/a4783781e828231bc0b4a8fdbb15c2292824d98d)

## Results read back from GitHub Actions, not inferred from the workflow configuration

| Python runtime | Job ID | Run result | Regression tests | Packaged demonstration | JSON post-run assertions |
| --- | --- | --- | --- | --- | --- |
| 3.11 | [120732051481](https://github.com/albdrani37-hash/FalconX/actions/runs/40047365598/job/120732051481) | success | 12/12 passed | completed | passed |
| 3.12 | [120732051394](https://github.com/albdrani37-hash/FalconX/actions/runs/40047365598/job/120732051394) | success | 12/12 passed | completed | passed |
| 3.13 | [120732051246](https://github.com/albdrani37-hash/FalconX/actions/runs/40047365598/job/120732051246) | success | 12/12 passed | completed | passed |

Verified in each job log:
- `Ran 12 tests` followed by `OK`.
- Packaged synthetic dataset generated 20 contacts, 3 duplicate candidate groups and 4 quality flags.
- Initial simulated approval reported `{"applied": 2, "already_applied": 0}`.
- Replaying the same approval reported `{"applied": 0, "already_applied": 2}`.
- The final JSON assertions printed: `Verified: two simulated-approved writes; zero extra writes on replay`.

All three jobs completed successfully. This is **three executions of the same twelve-test suite under three Python runtimes**, not thirty-six unique test cases.

## How to reproduce locally

With Python 3.11, 3.12 or 3.13:

```sh
cd examples/crm-review-demo
python -m unittest discover -v
python run_demo.py
```

No customer data, external API, live CRM, authenticated human reviewer, production authorization or paid dependency is involved.

## Limits of interpretation

A green CI run proves that the **declared tests and assertions** passed for **the stated repository commit and CI environment**. It does not establish:
- coverage of all defects or reliability in production;
- live third-party CRM/API integration;
- independently authenticated approvals;
- security certification, adversarial safety, or external business outcomes;
- independent scientific validation of CTVI.

Documentation commits after the verified commit do not constitute another successful test run unless GitHub Actions actually executes them.

**Intended use:** share this evidence in proposals for bounded Python QA, regression checks, data-pipeline validation and AI-coding evaluation alongside the actual code and test sources.

[Tests](examples/crm-review-demo/test_crm_demo.py) · [CRM demo source](examples/crm-review-demo/crm_demo.py) · [Paid trial scope](PAID_PILOT.md) · [Professional inquiries](mailto:abdullahalharbi@purelymail.com)
