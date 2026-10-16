# CTVI Agent Audit MCP 0.3.0

A separate local prototype that exposes the unchanged 0.2.0 trace engine through two real MCP tools over Streamable HTTP. The version change adds an RPC server, schemas, transport safeguards and integration tests; it does not change or upgrade the research claims or the existing skills-only 0.2.0 release.

Use Python 3.11+ (tested 3.12). Install in a virtual environment with `python -m pip install .`, then run `ctvi-audit-mcp`. The default endpoint is `http://127.0.0.1:8765/mcp`. This is a localhost prototype, not a deployed or approved directory plugin.

- `audit_normalized_trace`: pass `trace_json` containing minimized normalized schema 1.0 JSON or JSONL, and optionally `input_format` (`json` or `jsonl`). It returns deterministic structural findings and limitations. Never pass a filename expecting a file read.
- `list_audit_checks`: no arguments; returns check meanings and input limits.

The MCP tools cannot access client or server artifact files, fetch URLs, run recorded tools, replay agents or verify outcomes. Optional text is treated as data and omitted from reports. Artifact bytes remain explicitly unchecked. No score, scientific validation, certification or OpenAI endorsement is produced.

Maximum trace 256 KiB UTF-8; HTTP body 320 KiB; 1000 events; 4000 total evidence links; 4 active application requests; 15-second cooperative/I/O timeout (not hard termination of a running worker thread). Reports are capped at 512 KiB. Body and structure limits are applied before audit processing. No application persistence, telemetry or runtime request logs. This does not guarantee memory zeroization or control client, proxy, host, platform or email retention. See docs/SECURITY_PRIVACY.md and docs/HOSTING.md.

Synthetic review cases are under review_cases/. Run `python -B -m unittest discover -s tests -v` after installation. Engineering test evidence is separate from scientific and market validation. MIT applies to newly authored adapter/utility components, not unrelated FalconX research or code; dependencies retain their own licenses.

The application enforces a global per-process token bucket of 60 MCP POST requests per minute, burst 10, returning fixed HTTP 429 when empty. It is not a per-user or distributed limit. Health/domain-proof GET routes are excluded from that bucket and still need upstream protection. `/healthz` returns fixed `ok`. The exact `/.well-known/openai-apps-challenge` path returns only a configured `CTVI_OPENAI_APPS_CHALLENGE` public token (1–256 restricted ASCII characters); it is 404 when unset. The token is not authentication and no domain verification is claimed until the platform confirms it. No directory/file reading is used. Captured SDK response bodies are bounded to 1,100,000 bytes and 64 messages before concatenation.

To replay the actual synthetic demonstration with the official SDK client while the server runs:

```sh
.venv/bin/python -B demo_client.py http://127.0.0.1:8765/mcp
```

The demonstration includes clean JSON, equivalent JSONL, a missing tool result with a broken provenance reference, and malformed JSON rejection. Its labels distinguish observed structural findings from unverified outcomes. The client disables environment proxies for its direct connection; choose network/proxy settings deliberately in another environment. See [hosting requirements](docs/HOSTING.md), [security and privacy notes](docs/SECURITY_PRIVACY.md), [not-hosted privacy template](docs/PRIVACY_NOTICE_NOT_HOSTED.md), and [official sources](docs/SOURCES.md).
