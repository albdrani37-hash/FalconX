# FalconX

Python systems engineering and quantitative-automation project by **Abdullah Alharbi**, an independent researcher and developer based in Saudi Arabia.

**[International AI engineering services & paid subcontracting](COMMERCIAL_SERVICES.md)** · [Request a scoped commercial discussion](mailto:albdrani36@gmail.com?subject=Paid%20AI%20engineering%20scope)\n\n**For funded engineering teams:** [AI-agent evaluation evidence pilot — commercial scope and pricing parameters](https://github.com/albdrani37-hash/agentdojo-trace-audit/blob/main/PAID_AGENT_EVALUATION_PILOT.md) · [Request a scoped paid review](https://github.com/albdrani37-hash/agentdojo-trace-audit/blob/main/REQUEST_A_QUOTE.md) · [Independent AI engineering capability brief](INDEPENDENT_AI_ENGINEERING_CAPABILITIES.md) · [Selected portfolio](PORTFOLIO.md)

Two bounded service areas supported by inspectable research and synthetic demonstrations:

- **AI-agent evaluation evidence integrity:** reconcile execution-trace lineage, source populations, denominators, excluded or missing records, and reproducible claim checks on an agreed frozen sample. [Technical case study](https://github.com/albdrani37-hash/agentdojo-trace-audit/blob/main/BUYER_CASE_STUDY.md).
- **Python QA and workflow validation:** reproducible regression tests, input/output consistency checks, replay handling, defect evidence, and technical handover for a defined module or workflow. [Python QA evidence brief](PYTHON_QA_AI_EVALUATION.md).

**Buying step:** share a non-confidential work brief, purchasing contact, budget range, contractor eligibility and target acceptance criteria via [abdullahalharbi@purelymail.com](mailto:abdullahalharbi@purelymail.com?subject=Funded%20AI%20evaluation%20or%20Python%20QA%20scope). No contract, fee or delivery commitment exists until scope and safe payment terms are agreed in writing. [Small fixed-scope pilot options](PAID_PILOT.md) remain available separately.

Review the public code, tests and stated limitations before requesting a scoped quotation. The examples are local/research evidence, not paid customer deployments.

**[Verified GitHub Actions CI results: Python 3.11 / 3.12 / 3.13](CI_EVIDENCE.md)** — the documented 24 October 2026 run passed **25 distinct regression tests under each of three Python versions** (75 test executions, not 75 different tests). Earlier 18-test and 12-test results remain preserved as historical evidence.

**[AI engineering services and project inquiries](SERVICES.md)** · [Email Abdullah](mailto:abdullahalharbi@purelymail.com)

## Agent-trace audit tools

- [CTVI Agent Audit 0.2.0](tools/ctvi-agent-audit): offline normalized-trace checks and an installable wheel.
- [CTVI Agent Audit MCP 0.3.0](tools/ctvi-agent-audit-mcp): a separately versioned local Streamable HTTP server; this code alone does not establish hosted production readiness or customer deployment.
- [Licensed external trace example](tools/ctvi-agent-audit/external-validation/tracelab): a documented 10-round fragment, not a customer trial or scientific validation.
- [Scoped trace-audit service](tools/ctvi-agent-audit/COMMERCIAL_AUDIT.md): deliverables, acceptance criteria and nonbinding planning prices.

## What is public here

- [CRM review demonstration](examples/crm-review-demo): a separate, offline Python/SQLite work sample showing approval-scoped updates, replay handling and transactional audit records. It uses synthetic contacts and is not part of the trading engine.
- [FalconX overview](FALCONX_OVERVIEW.md): high-level context for the quantitative-automation work.
- `incoming_build/`: historical review templates. Blank checklists are not completed assessments or acceptance evidence.

The core trading implementation and operational configuration are not distributed in this public repository. This page does not establish current live operation, audited investment performance or institutional certification.

## Run the business-workflow sample

Python 3.10 or newer; standard library only. No credentials, paid services or internet access are required.

```sh
git clone https://github.com/albdrani37-hash/FalconX.git
cd FalconX/examples/crm-review-demo
python3 -m unittest discover -v
python3 run_demo.py
```

Open `results/demo.html` locally to see the generated walkthrough. See the sample's README for approval semantics and limitations.

## Project collaboration

Areas of work include Python automation, API/data integration, workflow validation and reproducible AI-agent evaluation. A first engagement starts with a defined outcome, approved sample data and written acceptance criteria; scope, price and schedule are agreed before delivery.

- [LinkedIn](https://www.linkedin.com/in/abdullahalharbi36)
- [AI-agent trace-audit research](https://github.com/albdrani37-hash/agentdojo-trace-audit)

The examples are presented with their actual implementation boundaries. Portfolio demonstrations are not represented as client deployments.

