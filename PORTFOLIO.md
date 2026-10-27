# Abdullah Alharbi — Selected Technical Portfolio

**Python automation · API/data integration · Workflow validation · AI-agent evaluation**  
Independent researcher and developer, Saudi Arabia. Available for remote, scoped project work.

This selection gives reviewers concrete code and evidence to inspect. It distinguishes local demonstrations from research software and private operational work.

**For evaluation and delivery teams:** [Independent AI Engineering — evidence-backed capabilities and paid work packages](INDEPENDENT_AI_ENGINEERING_CAPABILITIES.md).

## Runnable synthetic evaluation-evidence demonstration (new, 27 October 2026)

[**Run the bounded Python evidence checker and its 12 tests**](examples/eval-evidence-demo/README.md) · [Source](examples/eval-evidence-demo/verify_evidence.py) · [Tests](examples/eval-evidence-demo/test_verify_evidence.py) · [CI](../../actions/workflows/eval-evidence-demo.yml).

This independent, standard-library-only demo reconciles explicitly included/excluded synthetic agent runs with reported counts, validates supplied artifact payload digests, retains missing evidence as `HOLD`, and reports contradictory records as `FAIL`. All 12 local tests passed on Python 3.13 in the recorded 27 October 2026 run. These claims concern a fabricated local sample; they do not establish input authenticity, enterprise deployment, or AI safety certification.

## 1. CRM review, approval and replay-safe updates

**Business problem:** review messy contact data and apply only explicitly selected changes, while recording what changed and avoiding duplicate writes on retry.

**Implementation:** Python standard library and SQLite. Twenty synthetic contacts are normalized, checked for basic data-quality issues and grouped into exact-email duplicate candidates. An approval file binds selected contact IDs to a content-derived plan identifier. Contact updates and before/after audit records commit in one transaction.

**Verified on 15 October 2026:** 12 automated tests passed. The packaged run produced 3 duplicate candidate groups and 4 quality flags. Two simulated-approved records were updated; replay produced 0 additional writes. Tests also cover stale-source rejection and rollback on audit insertion failure.

- [Source and setup](examples/crm-review-demo/README.md)
- [Core implementation](examples/crm-review-demo/crm_demo.py)
- [Automated tests](examples/crm-review-demo/test_crm_demo.py)
- [Verification record](examples/crm-review-demo/VERIFICATION.md)
- [Machine-readable run result](examples/crm-review-demo/results/run_result.json)

**Boundaries:** AI-assisted local portfolio demonstration, not a customer deployment. No live CRM, external LLM, authenticated reviewer, semantic deduplication or tamper-proof audit is included. Categories use documented keyword rules. Duplicate candidates are never merged automatically.

**Possible paid extension:** connect one agreed CRM/API sandbox, map approved fields, add environment-appropriate authenticated approval and test agreed failure scenarios. Access, data handling, effort cap and acceptance criteria are agreed first.

## 2. AI-agent execution evidence and reproducibility

**Problem:** determine whether an evaluation's records, denominators and reported findings are supported by traceable evidence.

The [AgentDojo Trace Audit](https://github.com/albdrani37-hash/agentdojo-trace-audit) repository contains benchmark-specific research software for source identity, raw-to-derived lineage, population accounting and declared provenance-fault checks. It includes source, schemas, tests, setup instructions and explicit limitations.

- [Research repository](https://github.com/albdrani37-hash/agentdojo-trace-audit)
- [Quick start and source prerequisite](https://github.com/albdrani37-hash/agentdojo-trace-audit/blob/main/QUICKSTART.md)
- [Limitations](https://github.com/albdrani37-hash/agentdojo-trace-audit/blob/main/LIMITATIONS.md)
- [Archived software v1.0.0](https://doi.org/10.5281/zenodo.22217485)

**Boundaries:** one frozen AgentDojo corpus and declared synthetic fault catalogs. This is research software, not general AI certification. External replication and cross-benchmark generalization have not been established. The CRM verification above does not imply that this separate research pipeline was rerun in the same review.

**Possible paid extension:** agree a bounded evaluation task and acceptance dataset, inspect execution traces, document failures and provide reproducible checks and evidence-linked findings.

## 3. Related private engineering work

My practical experience includes API-connected Python automation using Docker on a VPS, with state handling and operational logs. The trading implementation and private operating-system project are not included in this public selection. No access credentials, live trading configuration, customer data or unverified performance claims are shared here.

## 4. CTVI Agent Audit utility and MCP adapter

[Offline utility](tools/ctvi-agent-audit) and [MCP adapter](tools/ctvi-agent-audit-mcp) expose bounded structural checks and explicit evidence gaps. The adapter provides two read-only tools; it does not execute recorded tools, retrieve URLs or access artifact files. Local engineering tests are distinct from a hosted deployment or directory approval.

A [licensed TraceLab fragment](tools/ctvi-agent-audit/external-validation/tracelab) produced 32 normalized events and 18 expected findings, mostly preserved unknowns. Repeated offline output was identical. This is one partial session, not an accuracy benchmark, independent customer trial or scientific validation.

[Defined commercial audit scope](tools/ctvi-agent-audit/COMMERCIAL_AUDIT.md)

## Working together

[Services, scope and project inquiries](SERVICES.md) · [Email Abdullah](mailto:abdullahalharbi@purelymail.com)

Send the required outcome, systems involved, an approved or anonymized example, deadline and acceptance criteria. I will assess fit and propose a scoped paid task with a delivery schedule and an agreed fee or hour cap.

[LinkedIn](https://www.linkedin.com/in/abdullahalharbi36) · [GitHub](https://github.com/albdrani37-hash)

