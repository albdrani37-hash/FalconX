# Evidence Brief — Python QA, Deterministic Testing and AI-Coding Evaluation

**Abdullah Alharbi** — Independent Researcher & Python Developer — Saudi Arabia
**Remote, written-first, scoped engagements**
**Business email:** [abdullahalharbi@purelymail.com](mailto:abdullahalharbi@purelymail.com)

This page is a technical evidence index for buyers assessing Python debugging, test-design, AI-generated-code evaluation, data-pipeline QA and reproducibility work. It is **not** a record of paid customer engagements.

## Tested Python data workflow — directly inspectable

[CRM review demonstration](examples/crm-review-demo/README.md) · [Source](examples/crm-review-demo/crm_demo.py) · [Tests](examples/crm-review-demo/test_crm_demo.py) · [Verification](examples/crm-review-demo/VERIFICATION.md)

The offline Python/SQLite sample shows a guarded review-and-apply pipeline with synthetic data. Its packaged verification on 15 October 2026 reported:

- **12 automated tests passed** on Python 3.12.14.
- **20 synthetic contacts** included in the run; **3** duplicate candidate groups and **4** data-quality flags.
- **2 simulated-approved records** updated; reapplying the same approval caused **0 additional writes**.
- Test cases include stale-source detection, replay/idempotency, exact-plan checks, invalid IDs, ambiguity, and rollback on audit insertion failure.

To review independently, use the installation and test commands in the sample README. This is an AI-assisted local demonstration, **not a deployed customer CRM**. It has no production authentication, external LLM or live vendor APIs.

### Expanded replay-integrity verification — 24 October 2026

A later, separate [GitHub Actions run](https://github.com/albdrani37-hash/FalconX/actions/runs/40051950195) passed **18/18 tests** under each of Python 3.11, 3.12 and 3.13. Six additional cases check that already-applied records and audit entries still match the plan before a replay is accepted, including rejection of stale or tampered local state. [Full evidence and failed-then-fixed development history](CI_EVIDENCE.md) · [Additional tests](examples/crm-review-demo/test_replay_integrity.py). The 15 October 12-test results above remain an accurate historical snapshot.

## Agent-evaluation provenance and reproducibility — research software

[AgentDojo Trace Audit](https://github.com/albdrani37-hash/agentdojo-trace-audit) · [Quickstart](https://github.com/albdrani37-hash/agentdojo-trace-audit/blob/main/QUICKSTART.md) · [Limitations](https://github.com/albdrani37-hash/agentdojo-trace-audit/blob/main/LIMITATIONS.md)

This benchmark-specific reference implementation links raw-to-derived records, checks population accounting and denominators, and exposes evidence and lineage constraints. The project's repository reports a fixed corpus of **11,624 records and links** and fault-catalog verification results that apply only to its declared synthetic fixtures. Reproduction requires obtaining the specified upstream AgentDojo source separately.

These results do **not** demonstrate general-purpose agent safety, external replicability, or validation beyond the declared benchmark.

## Bounded services suitable for a paid trial

1. **Python/CSV/JSON quality check:** one schema and approved test sample, validation and reconciliation checks, concise findings and reproducible evidence.
2. **Bug-reproduction and regression-test design:** one clearly described defect or isolated Python module, expected/actual cases, executable tests when technically feasible, proposed corrective scope.
3. **AI-generated-code review:** inspect one supplied patch or bounded function against an agreed test specification, document edge cases, unsupported assumptions and reproducible failures.
4. **Agent execution-evidence review:** bounded trace-format mapping and structural-evidence checks. This is not independent certification.

For the initial **USD 190 indicative fixed-price data/workflow reliability trial**, see [the bounded offer](PAID_PILOT.md). Code-review and agent-evidence work need separate scope, sample and quotation. No price or timeline is binding without a written agreement.

## Minimum information needed to quote responsibly

Share a short problem statement, permitted **synthetic or de-identified** sample/schema, expected output, approximate number of records or cases, any existing tests, an acceptance criterion, a deadline, and the preferred payment/escrow arrangement.

**Do not send credentials, card photos, sensitive personal data or raw confidential production logs in an initial email.** If proprietary code or data is involved, agree an authorized secure channel and handling conditions first.

[Request a scoped quotation](mailto:abdullahalharbi@purelymail.com?subject=Python%20QA%20or%20AI%20code%20review%20-%20paid%20trial) · [General portfolio](PORTFOLIO.md)
