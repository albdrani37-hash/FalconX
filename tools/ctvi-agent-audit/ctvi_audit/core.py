"""Bounded parsing and deterministic structural evidence checks (stdlib only)."""

import collections
import datetime as dt
import hashlib
import json
import os
import re
import stat

from . import __version__
from .catalog import describe

MAX_INPUT_BYTES = 5 * 1024 * 1024
MAX_EVENTS = 10000
MAX_ARTIFACTS = 100
MAX_ARTIFACT_BYTES = 8 * 1024 * 1024
MAX_TOTAL_ARTIFACT_BYTES = 32 * 1024 * 1024
MAX_DEPTH = 24
MAX_STRING = 65536
MAX_FINDINGS = 2000
EVENT_TYPES = {"start", "message", "tool_call", "tool_result", "observation", "claim", "end"}
OUTCOMES = {"success", "failure", "partial", "unknown"}
STATUSES = {"success", "error", "unknown"}
KINDS = {"event", "artifact", "external", "self_report"}
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
SHA = re.compile(r"^[a-f0-9]{64}$")
TIMESTAMP = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,6})?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])$")


class InputError(ValueError):
    """A fixed, non-sensitive error code; never stores user input in its text."""


def _fail(code):
    raise InputError(code)


def _object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            _fail("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def _no_constant(_):
    _fail("NON_FINITE_JSON_NUMBER")


def _loads(raw):
    try:
        return json.loads(raw, object_pairs_hook=_object_pairs, parse_constant=_no_constant)
    except (json.JSONDecodeError, UnicodeError, RecursionError, ValueError) as exc:
        if isinstance(exc, InputError):
            raise
        _fail("INVALID_JSON")


def _bounded_tree(value, depth=0):
    if depth > MAX_DEPTH:
        _fail("JSON_NESTING_LIMIT")
    if isinstance(value, str):
        if len(value) > MAX_STRING or any(0xD800 <= ord(c) <= 0xDFFF for c in value):
            _fail("INVALID_OR_OVERSIZED_STRING")
    elif isinstance(value, dict):
        for key, item in value.items():
            _bounded_tree(key, depth + 1)
            _bounded_tree(item, depth + 1)
    elif isinstance(value, list):
        for item in value:
            _bounded_tree(item, depth + 1)


def _keys(obj, required, optional):
    if not isinstance(obj, dict) or not required <= obj.keys() or obj.keys() - required - optional:
        _fail("INVALID_OBJECT_FIELDS")


def _identifier(value):
    if not isinstance(value, str) or not ID.fullmatch(value):
        _fail("INVALID_IDENTIFIER")


def _choice(value, choices):
    if not isinstance(value, str) or value not in choices:
        _fail("INVALID_ENUM_VALUE")


def _timestamp(value):
    if not isinstance(value, str) or not TIMESTAMP.fullmatch(value):
        _fail("INVALID_TIMESTAMP")
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        _fail("INVALID_TIMESTAMP")


def validate(trace):
    """Validate syntax/types; duplicate references are audit findings, not parse errors."""
    _bounded_tree(trace)
    _keys(trace, {"schema_version", "trace_id", "events"}, {"artifacts", "reported_outcome", "synthetic"})
    if trace["schema_version"] != "1.0":
        _fail("UNSUPPORTED_SCHEMA_VERSION")
    _identifier(trace["trace_id"])
    if "synthetic" in trace and not isinstance(trace["synthetic"], bool):
        _fail("INVALID_SYNTHETIC_FLAG")
    _choice(trace.get("reported_outcome", "unknown"), OUTCOMES)
    events = trace["events"]
    if not isinstance(events, list) or not 1 <= len(events) <= MAX_EVENTS:
        _fail("EVENT_COUNT_LIMIT")
    artifacts = trace.get("artifacts", [])
    if not isinstance(artifacts, list) or len(artifacts) > MAX_ARTIFACTS:
        _fail("ARTIFACT_COUNT_LIMIT")
    for a in artifacts:
        _keys(a, {"artifact_id"}, {"path", "sha256", "source_event_id"})
        _identifier(a["artifact_id"])
        if "source_event_id" in a:
            _identifier(a["source_event_id"])
        if "path" in a and (not isinstance(a["path"], str) or not 1 <= len(a["path"]) <= 1024):
            _fail("INVALID_ARTIFACT_PATH")
        if "sha256" in a and (not isinstance(a["sha256"], str) or not SHA.fullmatch(a["sha256"])):
            _fail("INVALID_SHA256")
    for e in events:
        _keys(e, {"event_id", "sequence", "type"}, {"timestamp", "text", "call_id", "tool_name", "status", "evidence"})
        _identifier(e["event_id"])
        if type(e["sequence"]) is not int or not 0 <= e["sequence"] <= 2**53 - 1:
            _fail("INVALID_SEQUENCE")
        _choice(e["type"], EVENT_TYPES)
        if "timestamp" in e:
            _timestamp(e["timestamp"])
        if "text" in e and not isinstance(e["text"], str):
            _fail("INVALID_TEXT")
        if e["type"] in {"tool_call", "tool_result"}:
            if "call_id" not in e:
                _fail("MISSING_CALL_ID")
            _identifier(e["call_id"])
        elif "call_id" in e:
            _fail("UNEXPECTED_CALL_ID")
        if e["type"] == "tool_call":
            if "tool_name" not in e:
                _fail("MISSING_TOOL_NAME")
            _identifier(e["tool_name"])
        elif "tool_name" in e:
            _fail("UNEXPECTED_TOOL_NAME")
        if e["type"] == "tool_result":
            if "status" not in e:
                _fail("MISSING_RESULT_STATUS")
            _choice(e["status"], STATUSES)
        elif "status" in e:
            _fail("UNEXPECTED_RESULT_STATUS")
        evidence = e.get("evidence", [])
        if not isinstance(evidence, list) or len(evidence) > 100:
            _fail("EVIDENCE_COUNT_LIMIT")
        for source in evidence:
            _keys(source, {"kind"}, {"ref"})
            _choice(source["kind"], KINDS)
            if source["kind"] in {"event", "artifact"}:
                if "ref" not in source:
                    _fail("MISSING_EVIDENCE_REFERENCE")
                _identifier(source["ref"])
            elif "ref" in source and (not isinstance(source["ref"], str) or not 1 <= len(source["ref"]) <= 2048):
                _fail("INVALID_EVIDENCE_REFERENCE")
    return trace


def parse_bytes(raw, input_format="json"):
    if not isinstance(raw, bytes) or len(raw) > MAX_INPUT_BYTES:
        _fail("INPUT_SIZE_LIMIT")
    try:
        text = raw.decode("utf-8")
    except UnicodeError:
        _fail("INVALID_UTF8")
    if input_format == "json":
        trace = _loads(text)
    elif input_format == "jsonl":
        # Blank lines are accepted. Exactly one first header is required.
        lines = [line for line in text.split("\n") if line.strip()]
        if not lines or len(lines) > MAX_EVENTS + MAX_ARTIFACTS + 1:
            _fail("JSONL_RECORD_COUNT_LIMIT")
        header = _loads(lines[0])
        _keys(header, {"record_type", "schema_version", "trace_id"}, {"reported_outcome", "synthetic"})
        if header["record_type"] != "trace":
            _fail("JSONL_HEADER_REQUIRED")
        trace = {k: v for k, v in header.items() if k != "record_type"}
        trace.update(events=[], artifacts=[])
        for line in lines[1:]:
            record = _loads(line)
            if not isinstance(record, dict) or not isinstance(record.get("record_type"), str) or record["record_type"] not in {"event", "artifact"}:
                _fail("INVALID_JSONL_RECORD")
            key = "events" if record["record_type"] == "event" else "artifacts"
            trace[key].append({k: v for k, v in record.items() if k != "record_type"})
    else:
        _fail("UNSUPPORTED_INPUT_FORMAT")
    return validate(trace)


def _safe_parts(path, absolute=False):
    if not isinstance(path, str) or "\x00" in path or "\\" in path or ":" in path:
        _fail("UNSAFE_LOCAL_PATH")
    if path.startswith("/") != absolute:
        _fail("UNSAFE_LOCAL_PATH")
    parts = path.split("/")
    if absolute:
        parts = parts[1:]
    if not parts or any(p in {"", ".", ".."} for p in parts):
        _fail("UNSAFE_LOCAL_PATH")
    return parts


def _open_directory(path):
    # Traverse with directory file descriptors and NOFOLLOW to prevent symlink races.
    if not hasattr(os, "O_NOFOLLOW") or os.open not in os.supports_dir_fd:
        _fail("SAFE_FILESYSTEM_OPERATIONS_UNAVAILABLE")
    parts = _safe_parts(path, absolute=True)
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in parts:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except OSError:
        os.close(fd)
        _fail("ARTIFACT_ROOT_UNAVAILABLE_OR_UNSAFE")


def _read_fd_bounded(fd, limit):
    st = os.fstat(fd)
    if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
        _fail("NON_REGULAR_OR_MULTILINK_FILE")
    if st.st_size > limit:
        _fail("FILE_SIZE_LIMIT")
    with os.fdopen(os.dup(fd), "rb") as stream:
        raw = stream.read(limit + 1)
    after = os.fstat(fd)
    if len(raw) > limit:
        _fail("FILE_SIZE_LIMIT")
    if (st.st_size, st.st_mtime_ns, st.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
        _fail("FILE_CHANGED_DURING_READ")
    return raw


def _read_beneath(root_fd, relative, limit):
    parts = _safe_parts(relative)
    directory = os.dup(root_fd)
    try:
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = child
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        try:
            return _read_fd_bounded(fd, limit)
        finally:
            os.close(fd)
    except OSError:
        _fail("FILE_UNAVAILABLE_OR_UNSAFE")
    finally:
        os.close(directory)


def read_trace_file(path):
    """Read an explicitly supplied path; no symlink components, FIFO or traversal."""
    if not isinstance(path, str) or not path:
        _fail("UNSAFE_LOCAL_PATH")
    if path.startswith("/"):
        parts = _safe_parts(path, absolute=True)
        parent = "/" + "/".join(parts[:-1])
        if parent == "/":
            _fail("UNSAFE_LOCAL_PATH")
        root_fd = _open_directory(parent)
        relative = parts[-1]
    else:
        _safe_parts(path)
        root_fd = _open_directory(os.getcwd())
        relative = path
    try:
        return _read_beneath(root_fd, relative, MAX_INPUT_BYTES)
    finally:
        os.close(root_fd)


def _json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


def audit(trace, artifact_root=None):
    """Inspect supplied declarations only. No network, execution, or scientific grading."""
    validate(trace)
    findings = []
    counts = collections.Counter()
    severity_counts = collections.Counter()

    def add(code, severity, event=None, artifact=None):
        counts[code] += 1
        severity_counts[severity] += 1
        if len(findings) < MAX_FINDINGS:
            f = {"code": code, "severity": severity}
            if event is not None:
                f["event_index"] = event
            if artifact is not None:
                f["artifact_index"] = artifact
            findings.append(f)

    events = trace["events"]
    artifacts = trace.get("artifacts", [])
    event_positions = collections.defaultdict(list)
    artifact_positions = collections.defaultdict(list)
    calls = collections.defaultdict(list)
    results = collections.defaultdict(list)
    sequences = set()
    previous_time = None
    previous_sequence = None
    for i, e in enumerate(events):
        event_positions[e["event_id"]].append(i)
        if len(event_positions[e["event_id"]]) > 1:
            add("DUPLICATE_EVENT_ID", "error", i)
        if e["sequence"] in sequences:
            add("DUPLICATE_SEQUENCE", "error", i)
        if previous_sequence is not None and e["sequence"] < previous_sequence:
            add("SEQUENCE_REVERSAL", "error", i)
        sequences.add(e["sequence"])
        previous_sequence = e["sequence"]
        if "timestamp" not in e:
            add("TIMESTAMP_MISSING", "unknown", i)
        else:
            timestamp = _timestamp(e["timestamp"])
            if previous_time is not None and timestamp < previous_time:
                add("TIMESTAMP_REVERSAL", "warning", i)
            previous_time = timestamp
        if e["type"] == "tool_call":
            calls[e["call_id"]].append(i)
        if e["type"] == "tool_result":
            results[e["call_id"]].append(i)
            if e["status"] == "error":
                add("TOOL_REPORTED_ERROR", "warning", i)
            elif e["status"] == "unknown":
                add("TOOL_RESULT_STATUS_UNKNOWN", "unknown", i)
    for i, a in enumerate(artifacts):
        artifact_positions[a["artifact_id"]].append(i)
        if len(artifact_positions[a["artifact_id"]]) > 1:
            add("DUPLICATE_ARTIFACT_ID", "error", artifact=i)
    for call, positions in calls.items():
        for position in positions[1:]:
            add("DUPLICATE_CALL_ID", "error", position)
        if call not in results:
            add("TOOL_RESULT_MISSING", "unknown", positions[0])
    for call, positions in results.items():
        for position in positions[1:]:
            add("DUPLICATE_TOOL_RESULT", "error", position)
        if call not in calls:
            for position in positions:
                add("ORPHAN_TOOL_RESULT", "error", position)
        elif len(calls[call]) != 1:
            for position in positions:
                add("AMBIGUOUS_CALL_REFERENCE", "error", position)
        else:
            for position in positions:
                if position <= calls[call][0]:
                    add("RESULT_BEFORE_CALL", "error", position)
    for i, e in enumerate(events):
        evidence = e.get("evidence", [])
        if e["type"] == "claim" and not evidence:
            add("CLAIM_WITHOUT_PROVENANCE", "unknown", i)
        for source in evidence:
            kind = source["kind"]
            if kind == "event":
                positions = event_positions.get(source["ref"], [])
                if not positions:
                    add("EVIDENCE_EVENT_MISSING", "error", i)
                elif len(positions) != 1:
                    add("EVIDENCE_EVENT_AMBIGUOUS", "error", i)
                elif positions[0] >= i:
                    add("EVIDENCE_NOT_PRIOR", "warning", i)
            elif kind == "artifact":
                positions = artifact_positions.get(source["ref"], [])
                if not positions:
                    add("EVIDENCE_ARTIFACT_MISSING", "error", i)
                elif len(positions) != 1:
                    add("EVIDENCE_ARTIFACT_AMBIGUOUS", "error", i)
                else:
                    origin = artifacts[positions[0]].get("source_event_id")
                    source_positions = event_positions.get(origin, [])
                    if len(source_positions) == 1 and source_positions[0] >= i:
                        add("ARTIFACT_SOURCE_NOT_PRIOR", "warning", i)
            elif kind == "external":
                add("EXTERNAL_EVIDENCE_UNVERIFIED", "unknown", i)
            else:
                add("SELF_REPORTED_EVIDENCE", "unknown", i)
    verified = 0
    attempted = 0
    total_bytes = 0
    root_fd = _open_directory(artifact_root) if artifact_root is not None else None
    try:
        for i, a in enumerate(artifacts):
            if "source_event_id" not in a:
                add("ARTIFACT_PROVENANCE_MISSING", "unknown", artifact=i)
            else:
                positions = event_positions.get(a["source_event_id"], [])
                if not positions:
                    add("ARTIFACT_SOURCE_EVENT_MISSING", "error", artifact=i)
                elif len(positions) != 1:
                    add("ARTIFACT_SOURCE_EVENT_AMBIGUOUS", "error", artifact=i)
            if "sha256" not in a:
                add("ARTIFACT_DIGEST_MISSING", "unknown", artifact=i)
            if "path" not in a:
                add("ARTIFACT_PATH_MISSING", "unknown", artifact=i)
            if root_fd is None:
                add("ARTIFACT_BYTES_NOT_CHECKED", "unknown", artifact=i)
            elif "path" in a and "sha256" in a:
                attempted += 1
                try:
                    raw = _read_beneath(root_fd, a["path"], min(MAX_ARTIFACT_BYTES, MAX_TOTAL_ARTIFACT_BYTES - total_bytes))
                    total_bytes += len(raw)
                    if hashlib.sha256(raw).hexdigest() == a["sha256"]:
                        verified += 1
                    else:
                        add("ARTIFACT_DIGEST_MISMATCH", "error", artifact=i)
                except InputError as exc:
                    add("ARTIFACT_" + str(exc), "error", artifact=i)
    finally:
        if root_fd is not None:
            os.close(root_fd)
    if not any(e["type"] == "start" for e in events):
        add("START_MARKER_MISSING", "unknown")
    if not any(e["type"] == "end" for e in events):
        add("END_MARKER_MISSING", "unknown")
    if events[0]["type"] != "start" and any(e["type"] == "start" for e in events):
        add("START_MARKER_NOT_FIRST", "warning")
    if events[-1]["type"] != "end" and any(e["type"] == "end" for e in events):
        add("END_MARKER_NOT_LAST", "warning")
    if sum(e["type"] == "start" for e in events) > 1:
        add("MULTIPLE_START_MARKERS", "warning")
    if sum(e["type"] == "end" for e in events) > 1:
        add("MULTIPLE_END_MARKERS", "warning")
    findings.sort(key=lambda f: (f.get("event_index", -1), f.get("artifact_index", -1), f["code"]))
    return {
        "report_schema_version": "1.1",
        "product": "CTVI Agent Audit",
        "product_version": __version__,
        "readiness": "PROTOTYPE",
        "assessment_scope": "STRUCTURAL_CHECKS_OF_USER_SUPPLIED_RECORDS_ONLY",
        "trace_fingerprint_sha256": hashlib.sha256(_json_bytes(trace)).hexdigest(),
        "input_schema_version": trace["schema_version"],
        "synthetic_as_declared": trace.get("synthetic", False),
        "reported_outcome": trace.get("reported_outcome", "unknown"),
        "outcome_verification": "NOT_PERFORMED",
        "scientific_validity": "NOT_ASSESSED",
        "structural_status": "ISSUES_OBSERVED" if severity_counts["error"] or severity_counts["warning"] else ("INCOMPLETE_EVIDENCE" if severity_counts["unknown"] else "NO_ISSUES_OBSERVED_WITHIN_CHECKS"),
        "evidence_status": "UNKNOWNS_PRESENT" if severity_counts["unknown"] else "NO_UNKNOWNS_IN_IMPLEMENTED_CHECKS",
        "counts": {"events": len(events), "artifacts": len(artifacts), "tool_calls": sum(map(len, calls.values())), "tool_results": sum(map(len, results.values())), "findings": sum(counts.values()), "findings_returned": len(findings), "findings_omitted": sum(counts.values()) - len(findings)},
        "severity_counts": {s: severity_counts[s] for s in ("error", "warning", "unknown")},
        "finding_code_counts": dict(sorted(counts.items())),
        "finding_explanations": {code: describe(code) for code in sorted(counts)},
        "artifact_verification": {"requested": artifact_root is not None, "attempted": attempted, "digest_matches": verified, "bytes_read": total_bytes},
        "findings": findings,
        "limitations": [
            "Only declared records are inspected; omitted or fabricated events cannot be detected reliably.",
            "Source links and artifact hashes do not establish truth, origin, safety, completeness, or scientific admissibility.",
            "Reported outcomes and tool statuses are assertions, not independently verified results.",
            "No CTVI construct validation, calibrated score, certification, causal inference, or peer-review conclusion is produced.",
            "Timestamps and order reflect supplied logs; concurrent and distributed systems may require contextual interpretation.",
            "Only normalized schema 1.0 is supported; external provider formats require an explicit reviewed adapter.",
            "An unchanged fingerprint supports report comparison; this tool does not replay an agent or establish stochastic reliability.",
            "Reports omit raw text, names, IDs, paths and URLs, but counts, fingerprints and outcomes may still be sensitive.",
        ],
    }


def json_report(report):
    return _json_bytes(report).decode("utf-8")


def markdown_report(report):
    lines = ["# CTVI Agent Audit", "", "Prototype technical report. Not scientific validation or certification.", "", f"Version: {report['product_version']}", f"Structural status: {report['structural_status']}", f"Reported outcome: {report['reported_outcome']} (not verified)", f"Trace fingerprint SHA-256: {report['trace_fingerprint_sha256']}", "", "## Counts", ""]
    lines.extend(f"- {key}: {value}" for key, value in report["counts"].items())
    lines.extend(["", "## Findings", ""])
    if not report["findings"]:
        lines.append("No findings within implemented checks. This is not proof of a complete, authentic, safe or correct trace.")
    for item in report["findings"]:
        position = ""
        if "event_index" in item:
            position += f"; event index {item['event_index']}"
        if "artifact_index" in item:
            position += f"; artifact index {item['artifact_index']}"
        lines.append(f"- {item['severity']}: {item['code']}{position}. {describe(item['code'])['meaning']}")
    if report["counts"]["findings_omitted"]:
        lines.append("Detailed findings are capped; complete aggregate counts appear in the JSON report.")
    lines.extend(["", "## Artifact verification", ""])
    lines.extend(f"- {key}: {value}" for key, value in report["artifact_verification"].items())
    lines.extend(["", "## Limitations", ""])
    lines.extend("- " + item for item in report["limitations"])
    return "\n".join(lines) + "\n"
