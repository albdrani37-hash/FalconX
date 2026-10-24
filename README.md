# FalconX

Python systems engineering and quantitative-automation project by **Abdullah Alharbi**, an independent researcher and developer based in Saudi Arabia.

**Reviewing my work for a project? Start with the [selected technical portfolio](PORTFOLIO.md).** It links to runnable source, a tested CRM workflow and AI-agent evaluation research.

**[AI engineering services and project inquiries](SERVICES.md)** · [Email Abdullah](mailto:abdullahalharbi@purelymail.com)

## Agent-trace audit tools

- [CTVI Agent Audit 0.2.0](tools/ctvi-agent-audit): offline normalized-trace checks and an installable wheel.
- [CTVI Agent Audit MCP 0.3.0](tools/ctvi-agent-audit-mcp): a separately versioned local Streamable HTTP server; public hosting and OpenAI submission remain pending.
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

