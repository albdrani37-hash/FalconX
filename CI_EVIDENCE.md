# GitHub Actions CI Evidence — Python CRM QA Demonstration

**Verified:** 24 October 2026 · **Source:** GitHub Actions run [#1](https://github.com/albdrani37-hash/FalconX/actions/runs/40047365598) · **Conclusion:** `success`

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
