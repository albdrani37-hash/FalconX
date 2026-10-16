# CTVI Agent Audit

Prototype technical report. Not scientific validation or certification.

Version: 0.2.0
Structural status: ISSUES_OBSERVED
Reported outcome: success (not verified)
Trace fingerprint SHA-256: 6df7bbb40acbe5c55de08307171121123864c16532629a87eaec187c5e620804

## Counts

- events: 5
- artifacts: 1
- tool_calls: 1
- tool_results: 1
- findings: 9
- findings_returned: 9
- findings_omitted: 0

## Findings

- error: ARTIFACT_DIGEST_MISMATCH; artifact index 0. Read artifact bytes differ from the declared SHA-256 digest.
- unknown: TOOL_RESULT_MISSING; event index 1. A call has no corresponding result in this trace.
- error: ORPHAN_TOOL_RESULT; event index 2. A result has no corresponding call in this trace.
- warning: TOOL_REPORTED_ERROR; event index 2. The supplied tool result declares an error.
- error: DUPLICATE_SEQUENCE; event index 3. Sequence values repeat in the supplied record order.
- error: EVIDENCE_EVENT_MISSING; event index 3. An evidence reference names an absent event.
- unknown: EXTERNAL_EVIDENCE_UNVERIFIED; event index 3. External evidence was declared but not fetched or verified.
- error: SEQUENCE_REVERSAL; event index 3. The declared sequence decreases in supplied order.
- warning: TIMESTAMP_REVERSAL; event index 3. A timestamp precedes the last supplied timestamp.

## Artifact verification

- requested: True
- attempted: 1
- digest_matches: 0
- bytes_read: 57

## Limitations

- Only declared records are inspected; omitted or fabricated events cannot be detected reliably.
- Source links and artifact hashes do not establish truth, origin, safety, completeness, or scientific admissibility.
- Reported outcomes and tool statuses are assertions, not independently verified results.
- No CTVI construct validation, calibrated score, certification, causal inference, or peer-review conclusion is produced.
- Timestamps and order reflect supplied logs; concurrent and distributed systems may require contextual interpretation.
- Only normalized schema 1.0 is supported; external provider formats require an explicit reviewed adapter.
- An unchanged fingerprint supports report comparison; this tool does not replay an agent or establish stochastic reliability.
- Reports omit raw text, names, IDs, paths and URLs, but counts, fingerprints and outcomes may still be sensitive.
