# Local operation and hosting requirements

This package has not been deployed, published or approved. External spending remains USD 0.

Local installation:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-deps --no-build-isolation .
.venv/bin/ctvi-audit-mcp --port 8765
```

Connect an official MCP client or MCP Inspector using Streamable HTTP to `http://127.0.0.1:8765/mcp`. The endpoint uses real SDK protocol handling, not a lookalike REST endpoint. Only POST is supported; no standalone SSE stream, resource retrieval, client roots, sampling or session persistence is needed for these two tools. The SDK negotiates protocol details. Integration evidence records the revision actually exercised.

Local Docker recipe (source supplied; Docker build/runtime status is in BUILD_EVIDENCE.json):

```sh
docker build -t ctvi-agent-audit-mcp:0.3.0 .
docker run --rm --read-only --cap-drop=ALL --security-opt=no-new-privileges --pids-limit=64 --memory=256m --cpus=1 -p 127.0.0.1:8765:8765 ctvi-agent-audit-mcp:0.3.0
```

No trace volume is needed. Container process is an unprivileged user. The image recipe uses a mutable base tag for local reproducibility convenience; select and verify an immutable base image digest and recheck dependency advisories before a public release. This recipe is not proof of a successfully built or tested container.

A remote OpenAI integration requires an operator-controlled stable HTTPS endpoint and domain verification when required by the submission flow. No endpoint, hostname, hosting account, payment or domain ownership is invented here. Static Sites hosting does not by itself run this Python ASGI process.

The current application is anonymous and intended for localhost testing with synthetic or explicitly permitted redacted data. Before exposing it remotely, the operator must resolve authentication/authorization for private input, HTTPS termination, exact Host/Origin allowlists, rate and connection limits, request size/deadline enforcement, resource isolation, service monitoring without payload logging, patching, backups/log retention and the public privacy notice. MCP-compatible OAuth is not implemented. Neither a hard-coded bearer token nor an unverified reverse proxy is represented as directory-compliant authorization.

The process-level request cap is not a distributed rate limiter. The deadline bounds async waits; it is not a hard kill of an executing Python worker thread. Input counts and body limits bound the synchronous workload. An upstream timeout, per-process memory/CPU limits and abuse controls are still needed for untrusted Internet traffic. Capacity has not been load-tested.

If an approved operator later deploys behind TLS, set `CTVI_ALLOWED_HOSTS` to exact served hosts (and explicit port forms when needed), and `CTVI_ALLOWED_ORIGINS` to explicit trusted origins. Defaults permit localhost only, and bare wildcard values are rejected. Do not disable rebinding protection. Trusted proxy configuration must be reviewed for the actual network; this prototype disables forwarded-header trust by default.

Publishing the package does not accept a hosting contract, privacy compliance certification or third-party portal agreement. Root execution handles any subsequent review and publication decision.

The application enforces a global per-process token bucket of 60 MCP POST requests per minute, burst 10, returning fixed HTTP 429 when empty. It is not a per-user or distributed limit. Health/domain-proof GET routes are excluded from that bucket and still need upstream protection. `/healthz` returns fixed `ok`. The exact `/.well-known/openai-apps-challenge` path returns only a configured `CTVI_OPENAI_APPS_CHALLENGE` public token (1–256 restricted ASCII characters); it is 404 when unset. The token is not authentication and no domain verification is claimed until the platform confirms it. No directory/file reading is used. Captured SDK response bodies are bounded to 1,100,000 bytes and 64 messages before concatenation.
