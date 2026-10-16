# MCP deployment privacy notice template — NOT HOSTED

CTVI Agent Audit MCP 0.3.0 has no public hosted endpoint operated by this release. This template is a deployment preparation document, not a claim that a public service or its legal/privacy arrangements exist. Software publisher: Abdullah Alharbi. Contact: albdrani36@gmail.com.

The prototype accepts a trace explicitly supplied by a user through an MCP client. If hosted remotely, the server operator receives that trace over the network, computes structural checks in process memory and returns a report. This differs from the offline CLI. No third-party model API, evidence URL fetching, client filesystem access, recorded-tool execution or artifact file reading occurs through the MCP tools.

Supply only necessary redacted normalized fields. Do not supply credentials, authentication codes, government identifiers, payment-card information or protected health information. The software does not automatically identify or remove all sensitive content. Reports omit raw trace text, identifiers, tool names, paths and URLs, but counts, fingerprints and declared outcomes may still be sensitive.

The provided server entry point does not intentionally write request/response payloads to logs, files, telemetry or a trace database. Processing occurs in memory and no secure memory-zeroization claim is made. A hosting provider, reverse proxy, operating system, administrator or calling platform can have additional logs, transcripts, crash dumps, swap and backups. Their retention cannot be inferred from the application code. No real hosting retention configuration has been established by this prototype.

Before a public endpoint is offered, replace this template with the actual operator's notice naming the service URL, operator/contact, processing purposes, infrastructure and subprocessors, applicable lawful basis and rights, access controls, actual retention/deletion practices and support process. Verify those statements against deployed configuration. Private-data access requires appropriate authentication and authorization; this local prototype does not implement MCP OAuth.

Support email is voluntary and should contain a minimal synthetic reproduction. Correspondence may remain until manually deleted or a deletion request is handled, subject to provider backups and legal requirements. No automated support-retention/deletion service or completion guarantee is implemented. Ask through the contact address about information voluntarily provided to support.
