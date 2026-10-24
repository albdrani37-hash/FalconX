# Python Workflow Reliability — Two Fixed-Scope Paid Pilots

**Independent developer:** Abdullah Alharbi · Saudi Arabia · remote, written-first collaboration
**Commercial contact:** [abdullahalharbi@purelymail.com](mailto:abdullahalharbi@purelymail.com?subject=Python%20reliability%20pilot)

## Why this service exists

When a Python data or CRM workflow runs twice, will it write the same updates twice? What happens if inputs change after approval, an audit step fails, or a malformed record reaches the processor?

This service focuses on **reproducible failure cases, controlled changes and verification evidence**. It does not claim to replace broad data-cleaning providers or certify a production system.

## Option A — One-Defect Reproduction | USD 75 indicative fixed price

**Buyer outcome:** a clear answer about one reported fault in an existing Python data-processing step.

**Boundaries:** one specified Python script/function or small isolated module, one sanitized input/output example, one reported problem, up to **three agreed checks**. Initial scoping and feasibility must confirm that the code can run in an agreed local or sandbox environment without new paid dependencies or production credentials.

**Deliverables:** expected-versus-observed notes, minimal reproducible steps, up to three executable checks where the interface supports them, and a concise findings/next-fix recommendation. If the failure is not reproducible on the supplied sample, the report says so explicitly rather than inventing a defect. **Code remediation is not included** in this tier.

**Indicative delivery:** 1–2 business days after written scope, sample and funding agreement, subject to availability.

## Option B — Regression Guard & One Bounded Fix | USD 190 indicative fixed price

**Buyer outcome:** a small data workflow backed by regression evidence, with one narrowly specified defect corrected where technically feasible.

**Boundaries:** one existing Python-driven CSV/JSON transformation or CRM-import preparation step, one documented schema, up to **200 approved synthetic/de-identified records**, up to **five agreed checks**, and at most **one agreed, isolated correction** in the provided code. A correction that requires a new connector, production authentication, extensive refactoring or external API implementation is quoted separately.

**Checks may include:** input/schema validation; duplicate/replay/idempotency handling; invalid-row and error paths; output reconciliation; stale-data protection or rollback behavior as supported by the code.

**Deliverables:** short technical findings and evidence links, runnable test cases or a test harness where feasible, the bounded code patch if applicable, before/after test outcomes, setup/run notes and one in-scope clarification or correction round. If no defect is reproducible, deliver documented tests and findings, not a fictional fix.

**Indicative delivery:** 2–4 business days after written scope, permitted sample and funding agreement, subject to availability.

## Evidence to inspect before buying

- [Worked Python/SQLite CRM example](examples/crm-review-demo/README.md)
- [Dated verification record](examples/crm-review-demo/VERIFICATION.md): **12 passing automated tests** on a **20-contact synthetic dataset**, recorded 15 October 2026.
- [Independent-reader sample delivery report](SAMPLE_DELIVERY_REPORT.md)
- [Selected portfolio](PORTFOLIO.md)
- [Research-grade agent trace audit software](https://github.com/albdrani37-hash/agentdojo-trace-audit) — benchmark-specific; not general certification.

**Honest limitations:** The CRM example is an AI-assisted *local portfolio demonstration*, not a production customer deployment. Its approval is simulated; the audit record is not tamper-proof. These sample checks do not establish real-world defect rates, production reliability or broad AI safety.

### Later regression evidence

On **24 October 2026**, **25 distinct tests** passed on each of Python 3.11, 3.12 and 3.13 in [the latest verified GitHub Actions run](https://github.com/albdrani37-hash/FalconX/actions/runs/40052721026) (75 successful test executions; not 75 distinct tests). Beyond the original replay/idempotency guards, the model now provides an **offline audit-verification CLI** that compares saved records against their plans and checks the current row against the last audited state, with seven additional regression cases and a machine-readable report. [Read exact verification evidence, earlier failures and limitations](CI_EVIDENCE.md). This local synthetic portfolio demonstration does not change either pilot's indicative price, confer production security assurance or establish client-delivery history.

## Before either pilot can start

Please provide the business symptom, one permitted redacted/synthetic sample or schema, expected output, existing tests if any, and an acceptance criterion. Initial inquiry **must not** include credentials, payment card photos, personal data or raw production logs.

The parties must agree on: exact input and output, permitted environment and data handling, one fixed scope, turnaround, currency/taxes, written acceptance criteria, ownership/usage of deliverables, and a verified invoicing or escrow/payment method **before work begins**. Prices and turnaround above are **nonbinding planning offers**; they are not unconditional quotes.

**Excluded:** live production access, credential handling, payment testing, n8n or vendor-specific workflow implementation, live API/CRM connectors, scraping, penetration testing, assurance/certification, performance promises, complex security reviews, or unlimited debugging.

**Contact:** [Request a written scope & paid pilot](mailto:abdullahalharbi@purelymail.com?subject=Python%20Workflow%20Reliability%20-%20scope%20inquiry)
