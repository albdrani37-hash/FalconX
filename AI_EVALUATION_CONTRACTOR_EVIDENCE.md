# AI Evaluation & Python QA — Technical Evidence Sheet

**Abdullah Alharbi** · Independent Researcher & Technology Developer · Saudi Arabia (UTC+3)
**Remote / written-first collaborations** · **Professional email:** [abdullahalharbi@purelymail.com](mailto:abdullahalharbi@purelymail.com)

This sheet is intended for recruiters and buyers assessing **AI-coding evaluation, Python test design, data-pipeline QA, and evidence-linked technical review**. It references inspectable engineering/research artifacts; it does not claim prior paid AI-training engagements.

## Capabilities with public evidence

| Evaluation need | Relevant inspectable artifact | Evidence / important boundary |
| --- | --- | --- |
| Executable Python regression tests | [Python/SQLite CRM sample: source and test suite](examples/crm-review-demo/README.md) | [Dated verification](examples/crm-review-demo/VERIFICATION.md) reports 12/12 passing tests on 15 Oct 2026. Synthetic-data, AI-assisted local demonstration, **not** a customer deployment. |
| Reliable state changes and negative tests | [Workflow test definitions](examples/crm-review-demo/test_crm_demo.py) | Coverage includes stale-input rejection, rollback after audit failure, duplicate-identifier rejection, replay/idempotency, approval-scope checks and deterministic proposals. Tests exercise this sample, not arbitrary production infrastructure. |
| AI-agent evaluation, provenance and measurement | [AgentDojo Trace Audit](https://github.com/albdrani37-hash/agentdojo-trace-audit) | Benchmark-specific reference pipeline and synthetic fault-catalog studies; explicit limits on generalization, external replication and construct validity. See [limitations](https://github.com/albdrani37-hash/agentdojo-trace-audit/blob/main/LIMITATIONS.md). |
| Structured, decision-ready QA reporting | [Sample QA delivery report](SAMPLE_DELIVERY_REPORT.md) | Evidence links, expected-vs-observed checks, uncertainty, failure mechanisms, remediation boundaries. A demonstration document, not a past client deliverable. |
| Fixed-scope paid exploratory assignment | [Two Python reliability pilots](PAID_PILOT.md) | USD 75 single-defect reproduction / USD 190 bounded regression-and-fix *indicative* prices; final scope, milestones and payment mechanism separately agreed. |

## Evaluation work I can discuss with a hiring team

- Construct bounded Python code-evaluation tasks with a clear task statement, expected behavior, acceptance conditions and reproducible test commands.
- Examine model-generated patches against functional and regression requirements; provide failure reproductions and precise technical feedback.
- Review dataset lineage, denominators, evidence gaps and misleading success-only aggregates **within the documented research tooling's scope**.
- Produce structured written explanations in Arabic or English, with uncertainty and unsupported assumptions clearly labeled.

## Example of discriminating test design from the public CRM sample

A requirement such as **“applying the same approved update twice must not create two writes”** is insufficiently tested by checking the final row value alone. The demonstration test checks the second run's applied count and the number of audit records. Separate tests deliberately fail an audit insert to verify transaction rollback, and mutate a source row before approval to test stale-state rejection. These are examples of distinguishing superficial task completion from valid state transitions; they do not prove production reliability.

## What I do not claim

No verified commercial customer outcome, AI-training employer, live production API or n8n deployment, accredited certification, external benchmark generalization, or third-party endorsement is asserted by this sheet. Technical fit for any particular task must be established through its own assessment. Sensitive records or credentials should not be shared during initial outreach.

## Contact and next step

For a contract opportunity, please send the task type, coding stack, sample/rubric or public specification, desired time commitment, pay basis, location eligibility, assessment process and payment method. I can respond with a scoped technical fit statement or complete the provider's approved evaluation process.

[Email](mailto:abdullahalharbi@purelymail.com?subject=AI%20evaluation%20%2F%20Python%20QA%20contractor) · [Selected portfolio](PORTFOLIO.md) · [Research repository](https://github.com/albdrani37-hash/agentdojo-trace-audit)
