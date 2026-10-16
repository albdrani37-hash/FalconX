# Normalized input version 1.0

Use UTF-8 JSON with one trace object. Unknown fields, duplicate JSON keys, nonfinite constants and incorrect types are rejected. This intentionally prevents silently interpreting arbitrary provider exports. `schema.json` is a descriptive JSON Schema; the bundled Python validator is authoritative for extra parser/resource restrictions.

Trace fields: required `schema_version` equal to `1.0`, `trace_id`, and nonempty `events`. Optional `reported_outcome` is `success`, `failure`, `partial`, or `unknown`; it defaults to unknown. Optional `synthetic` is boolean and describes the user's declaration only. Optional `artifacts` is an array.

Every event requires `event_id`, integer `sequence` in 0 through 9007199254740991, and `type`. Types: `start`, `message`, `tool_call`, `tool_result`, `observation`, `claim`, `end`. Sequence numbers need not be consecutive. Events are analyzed in supplied order; they are never silently sorted. Each may have `timestamp`, `text`, and `evidence`. Missing timestamps are reported as unknown. Timestamps use RFC3339-style `YYYY-MM-DDTHH:MM:SS[.ffffff]Z` or an explicit numeric offset. Leap seconds are not supported.

Tool calls require `call_id` and `tool_name`; tool results require `call_id` and `status` (`success`, `error`, `unknown`). These fields are rejected on other event types. One result per call is expected in v1; streaming or retried results must be normalized explicitly, not collapsed without disclosure.

Evidence entries contain `kind` (`event`, `artifact`, `external`, `self_report`) and optional `ref`. Event and artifact references require an ID. External references may be supplied but are not fetched. Self-reports are always unverified. Presence of a link establishes only linkage in the supplied records.

Artifact entries require `artifact_id`; optional fields are `source_event_id`, `path`, and lowercase hexadecimal `sha256`. Local paths are POSIX relative paths under an explicitly supplied absolute artifact root. No `.` or `..`, empty path component, backslash, colon, URL, symlink or hardlink is accepted for hashing. Without the root the declared bytes are never read. Input files follow the same regular-file and no-symlink restrictions.

Identifiers are 1–128 ASCII alphanumeric, dot, underscore, colon or hyphen characters; first character is alphanumeric. Text may contain UTF-8 prose but is never rendered in reports. Prefer removing sensitive content before processing.

JSONL format: first nonblank line is a header object with `record_type: trace`, `schema_version`, `trace_id`, and optional outcome/synthetic flag. Subsequent nonblank lines have `record_type: event` or `record_type: artifact`, plus the corresponding record's fields. A second header is rejected. No streaming incomplete JSON is supported.

Findings use fixed machine-readable codes and zero-based `event_index`/`artifact_index`. `error` means an observed structural inconsistency or blocked byte verification; `warning` means an observed condition needing interpretation; `unknown` means missing or unverified evidence. None is a calibrated safety probability. Report schema 1.1 includes complete per-code and severity counts, even when detailed findings are capped. Fixed explanations and suggested next actions are provided per observed code. Unknown-only reports use INCOMPLETE_EVIDENCE; --fail-on-unknown is an explicit CI option.
