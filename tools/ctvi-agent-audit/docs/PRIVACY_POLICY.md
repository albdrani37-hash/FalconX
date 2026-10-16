# CTVI Agent Audit privacy notice

Updated 17 October 2026 for version 0.2.0. This notice describes the software as implemented. Publisher: Abdullah Alharbi, independent researcher and AI technology developer, Saudi Arabia. Contact: albdrani36@gmail.com. Alharbi AI Research & Solutions is a provisional working brand, not a verified registered company.

## Local processing

The standalone Python tool reads a trace file explicitly selected by the user. Records may include event identifiers, timestamps, declared outcomes, tool statuses, evidence references and optional text. It checks record structure and declared provenance relationships. If an artifact directory is explicitly supplied, it reads authorized local artifact files to compare SHA-256 values. It never retrieves evidence URLs, executes recorded tool calls or invokes a model API.

The tool contains no telemetry, analytics, network client, remote account, trace database or hosted processing service. It does not send input files or reports to the publisher. The publisher does not receive files merely because the standalone tool is run. Only necessary normalized fields should be supplied; optional text should ordinarily be omitted. Do not submit passwords, API keys, authentication codes, government identifiers, payment-card information or protected health information.

## Reports and retention

The program holds processed records in process memory for the run and prints a report to stdout. It creates no application-level trace archive or report file. This does not guarantee memory zeroization or removal from swap, host logs or backups. Inputs remain in their existing location; a redirected or saved report remains until deleted through the system where it was stored. Python and package installation may create bytecode caches and installation metadata. Run Python with `-B` when avoiding runtime bytecode-cache writes is required.

Reports omit raw input prose, trace IDs, event IDs, tool names, paths and source URLs. Counts, reported outcomes and content fingerprints can still be sensitive. Treat reports as potentially confidential. The tool does not automatically delete user files, platform history, backups or other applications' records.

## ChatGPT and other hosting environments

If the tool is invoked through a skill inside ChatGPT or another platform, files uploaded or made available to that platform and its outputs are also subject to that platform's own policies, controls and retention. The local tool cannot promise zero platform retention or control third-party recipients. Review those policies before uploading confidential information. The standalone CLI can be used without uploading traces to ChatGPT.

## Voluntary support correspondence

If you email the publisher, the address, message and voluntarily included information become support correspondence in the publisher's email account. Use it for questions or a minimal redacted reproduction; do not send private production traces or secrets. The intended purpose is to respond and diagnose the reported problem. The email provider processes the correspondence under its applicable service terms. Do not assume a fixed expiry: correspondence may remain until manually deleted or a deletion request is completed. No automated support-retention or deletion service has been implemented. Ask through the contact address for access, correction or deletion; legal obligations or provider backups may constrain deletion. No response-time or deletion-completion guarantee is made.

## Controls and changes

Choose whether to run the tool, which trace file to supply, whether to enable artifact hashing and whether to retain the report. Redact the input before processing. Use local filesystem controls to delete local outputs. Contact the publisher for concerns about information voluntarily sent to support. A future hosted service, telemetry feature or changed data flow would require an updated notice before being described as part of this product.

This notice describes implemented data handling and does not constitute compliance certification.
