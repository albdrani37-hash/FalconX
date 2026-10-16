"""Fixed explanations only; never interpolate untrusted trace values."""

CHECKS = {
    "DUPLICATE_EVENT_ID": ("More than one supplied event has the same identifier.", "Assign distinct event IDs at the source; preserve the original export."),
    "DUPLICATE_SEQUENCE": ("Sequence values repeat in the supplied record order.", "Check exporter ordering and retry/streaming conventions."),
    "SEQUENCE_REVERSAL": ("The declared sequence decreases in supplied order.", "Inspect export ordering; do not silently reorder or remove records."),
    "TIMESTAMP_REVERSAL": ("A timestamp precedes the last supplied timestamp.", "Check clocks, concurrency and export ordering before interpreting causality."),
    "TIMESTAMP_MISSING": ("The record has no timestamp.", "Supply a timestamp from the original source if available; otherwise retain unknown."),
    "DUPLICATE_CALL_ID": ("More than one call uses the same call identifier.", "Normalize retries or streaming calls explicitly and document the mapping."),
    "DUPLICATE_TOOL_RESULT": ("Multiple results refer to one call identifier.", "Confirm whether these are retries, streaming parts or duplicate exports."),
    "AMBIGUOUS_CALL_REFERENCE": ("A result refers to more than one possible call.", "Correct identifiers using original evidence, without inventing missing links."),
    "TOOL_RESULT_MISSING": ("A call has no corresponding result in this trace.", "Check truncation or incomplete execution; do not infer the result."),
    "ORPHAN_TOOL_RESULT": ("A result has no corresponding call in this trace.", "Find the original call record or label the trace incomplete."),
    "RESULT_BEFORE_CALL": ("A result appears before its corresponding call.", "Check exporter ordering and preserve both original records."),
    "TOOL_REPORTED_ERROR": ("The supplied tool result declares an error.", "Inspect the original sanitized error record; the error is not independently verified."),
    "TOOL_RESULT_STATUS_UNKNOWN": ("The tool result declares an unknown status.", "Retain unknown unless source evidence supports a more specific status."),
    "CLAIM_WITHOUT_PROVENANCE": ("A claim has no declared evidence reference.", "Link existing evidence or explicitly retain the claim as unsupported."),
    "EVIDENCE_EVENT_MISSING": ("An evidence reference names an absent event.", "Restore the missing record from an authorized source or retain the gap."),
    "EVIDENCE_EVENT_AMBIGUOUS": ("An evidence reference matches multiple events.", "Resolve duplicate identifiers from original records."),
    "EVIDENCE_NOT_PRIOR": ("An evidence event is not earlier in supplied order.", "Check chronology; this link cannot establish prior influence by itself."),
    "EVIDENCE_ARTIFACT_MISSING": ("An evidence reference names an absent artifact declaration.", "Provide the declaration from an authorized source or retain the gap."),
    "EVIDENCE_ARTIFACT_AMBIGUOUS": ("An evidence reference matches multiple artifact declarations.", "Resolve artifact identifier collisions using the original manifest."),
    "ARTIFACT_SOURCE_NOT_PRIOR": ("The artifact's declared source event is not earlier than the referencing event.", "Check source chronology and exporter ordering; do not infer earlier availability."),
    "EXTERNAL_EVIDENCE_UNVERIFIED": ("External evidence was declared but not fetched or verified.", "Review it through a separately authorized process; this tool never fetches URLs."),
    "SELF_REPORTED_EVIDENCE": ("The evidence is explicitly self-reported.", "Keep it distinct from independently observed evidence."),
    "DUPLICATE_ARTIFACT_ID": ("More than one artifact declaration uses the same identifier.", "Resolve declarations against the original artifact manifest."),
    "ARTIFACT_PROVENANCE_MISSING": ("No source event is declared for the artifact.", "Provide a supported source reference or retain unknown provenance."),
    "ARTIFACT_SOURCE_EVENT_MISSING": ("The artifact's declared source event is absent.", "Restore an original source record or retain the provenance gap."),
    "ARTIFACT_SOURCE_EVENT_AMBIGUOUS": ("The artifact's declared source event is ambiguous.", "Resolve duplicate event IDs from original records."),
    "ARTIFACT_DIGEST_MISSING": ("No SHA-256 digest was supplied for the artifact.", "Supply a digest from the intended manifest; hashing cannot prove authorship."),
    "ARTIFACT_PATH_MISSING": ("No local artifact path was supplied.", "Provide a relative path only when local-byte comparison is intended."),
    "ARTIFACT_BYTES_NOT_CHECKED": ("No authorized artifact root was supplied, so no artifact bytes were read.", "Opt in with a dedicated local artifact root if byte comparison is needed."),
    "ARTIFACT_DIGEST_MISMATCH": ("Read artifact bytes differ from the declared SHA-256 digest.", "Check version, transfer integrity and the manifest; preserve mismatching evidence."),
    "START_MARKER_MISSING": ("The supplied trace has no start marker.", "Check whether the export is partial; absence does not prove missing execution."),
    "END_MARKER_MISSING": ("The supplied trace has no end marker.", "Check whether execution or export ended; do not assume completion."),
    "START_MARKER_NOT_FIRST": ("A start marker appears after other records.", "Check trace boundaries and export order."),
    "END_MARKER_NOT_LAST": ("Records follow an end marker.", "Check trace boundaries and export order."),
    "MULTIPLE_START_MARKERS": ("Multiple start markers occur in one normalized trace.", "Separate runs or document nested/streaming boundaries explicitly."),
    "MULTIPLE_END_MARKERS": ("Multiple end markers occur in one normalized trace.", "Separate runs or document nested/streaming boundaries explicitly."),
}

for code, meaning in {
    "UNSAFE_LOCAL_PATH": "The path is outside the accepted relative-path syntax.",
    "FILE_UNAVAILABLE_OR_UNSAFE": "The path was unavailable or blocked by safe-file rules.",
    "NON_REGULAR_OR_MULTILINK_FILE": "The target is not a single-link regular file.",
    "FILE_SIZE_LIMIT": "The file or remaining byte budget exceeded the configured limit.",
    "FILE_CHANGED_DURING_READ": "The file changed while it was being read.",
}.items():
    CHECKS["ARTIFACT_" + code] = (meaning, "Use a stable, authorized regular file in the dedicated root; do not bypass safeguards.")


def describe(code):
    meaning, action = CHECKS.get(code, ("A declared artifact could not be verified safely.", "Inspect the fixed error code and retain the uncertainty."))
    return {"meaning": meaning, "next_action": action}


def catalog():
    return {code: describe(code) for code in sorted(CHECKS)}
