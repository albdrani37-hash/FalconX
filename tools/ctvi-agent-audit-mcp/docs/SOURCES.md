# Official sources checked 17 October 2026

- https://py.sdk.modelcontextprotocol.io/ — identifies v2 as the stable Python SDK line and Python 3.11+ requirement. The installed distribution is mcp 2.3.0.
- https://py.sdk.modelcontextprotocol.io/run/ — Streamable HTTP endpoint, stateless/JSON mode and request-body limit support.
- https://py.sdk.modelcontextprotocol.io/advanced/middleware/ — documents the official low-level Server handlers used for explicit tool contracts; provisional middleware is avoided in the application.
- https://py.sdk.modelcontextprotocol.io/servers/structured-output/ — structured content and output schema contract.
- https://py.sdk.modelcontextprotocol.io/run/deploy/ — Host/Origin protection and distinction between modern and legacy transport behavior.
- https://py.sdk.modelcontextprotocol.io/client/ — official SDK client used for black-box integration.
- https://modelcontextprotocol.io/specification/2026-07-28/basic/transports — current transport binding and per-request protocol metadata model.
- https://developers.openai.com/plugins/build/mcp-server — focused tools, explicit input/output schemas, accurate safety annotations and local testing requirements.
- https://developers.openai.com/plugins/concepts/mcp-server — production HTTPS transport and authorization requirements for private data.

The application implements two bounded read-only audit tools; it does not claim company-knowledge search/fetch compatibility or OpenAI directory approval. Documentation is a point-in-time reference, not a guarantee of later submission eligibility.
