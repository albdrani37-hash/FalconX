import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from ctvi_audit.core import (InputError, MAX_FINDINGS, MAX_INPUT_BYTES, audit,
                             json_report, markdown_report, parse_bytes, read_trace_file)


def trace():
    return {
        "schema_version": "1.0", "trace_id": "synthetic-secret-customer",
        "synthetic": True, "reported_outcome": "success",
        "events": [
            {"event_id": "start", "sequence": 0, "type": "start", "timestamp": "2026-10-16T10:00:00Z"},
            {"event_id": "call", "sequence": 1, "type": "tool_call", "call_id": "c1", "tool_name": "synthetic-secret-tool", "timestamp": "2026-10-16T10:00:01Z"},
            {"event_id": "result", "sequence": 2, "type": "tool_result", "call_id": "c1", "status": "success", "timestamp": "2026-10-16T10:00:02Z", "text": "SECRET_do_not_render <script>alert(1)</script>"},
            {"event_id": "claim", "sequence": 3, "type": "claim", "timestamp": "2026-10-16T10:00:03Z", "evidence": [{"kind": "event", "ref": "result"}]},
            {"event_id": "end", "sequence": 4, "type": "end", "timestamp": "2026-10-16T10:00:04Z"},
        ],
    }


def codes(report):
    return set(report["finding_code_counts"])


class StructuralTests(unittest.TestCase):
    def test_clean_trace_is_not_validated(self):
        r = audit(trace())
        self.assertEqual(r["counts"]["findings"], 0)
        self.assertEqual(r["scientific_validity"], "NOT_ASSESSED")
        self.assertEqual(r["outcome_verification"], "NOT_PERFORMED")
        self.assertEqual(r["readiness"], "PROTOTYPE")

    def test_determinism_and_no_input_mutation(self):
        t = trace(); original = copy.deepcopy(t)
        self.assertEqual(json_report(audit(t)), json_report(audit(t)))
        self.assertEqual(markdown_report(audit(t)), markdown_report(audit(t)))
        self.assertEqual(t, original)

    def test_report_does_not_render_sensitive_values(self):
        t = trace()
        t["events"][3]["evidence"] = [{"kind": "external", "ref": "https://secret.example/key=SECRET"}]
        for report in [json_report(audit(t)), markdown_report(audit(t))]:
            for secret in ["SECRET", "secret.example", "synthetic-secret", "<script>"]:
                self.assertNotIn(secret, report)

    def test_duplicate_and_order_issues(self):
        t = trace()
        t["events"][3]["event_id"] = "result"
        t["events"][3]["sequence"] = 1
        t["events"][3]["timestamp"] = "2026-10-16T09:00:00Z"
        c = codes(audit(t))
        self.assertTrue({"DUPLICATE_EVENT_ID", "DUPLICATE_SEQUENCE", "SEQUENCE_REVERSAL", "TIMESTAMP_REVERSAL", "EVIDENCE_EVENT_AMBIGUOUS"} <= c)

    def test_missing_and_orphan_results(self):
        t = trace(); t["events"][2]["call_id"] = "missing"
        self.assertTrue({"TOOL_RESULT_MISSING", "ORPHAN_TOOL_RESULT"} <= codes(audit(t)))

    def test_result_precedes_call(self):
        t = trace(); t["events"][1], t["events"][2] = t["events"][2], t["events"][1]
        self.assertIn("RESULT_BEFORE_CALL", codes(audit(t)))

    def test_duplicate_call_and_result(self):
        t = trace(); t["events"].extend([copy.deepcopy(t["events"][1]), copy.deepcopy(t["events"][2])])
        self.assertTrue({"DUPLICATE_CALL_ID", "DUPLICATE_TOOL_RESULT", "AMBIGUOUS_CALL_REFERENCE"} <= codes(audit(t)))

    def test_provenance_gaps(self):
        t = trace(); t["events"][3]["evidence"] = [{"kind": "event", "ref": "missing"}, {"kind": "artifact", "ref": "absent"}, {"kind": "event", "ref": "end"}, {"kind": "external"}, {"kind": "self_report"}]
        self.assertTrue({"EVIDENCE_EVENT_MISSING", "EVIDENCE_ARTIFACT_MISSING", "EVIDENCE_NOT_PRIOR", "EXTERNAL_EVIDENCE_UNVERIFIED", "SELF_REPORTED_EVIDENCE"} <= codes(audit(t)))

    def test_missing_timestamps_claim_evidence_and_boundaries(self):
        t = trace(); t["events"] = [t["events"][3]]; del t["events"][0]["timestamp"]; del t["events"][0]["evidence"]
        self.assertTrue({"TIMESTAMP_MISSING", "CLAIM_WITHOUT_PROVENANCE", "START_MARKER_MISSING", "END_MARKER_MISSING"} <= codes(audit(t)))

    def test_timezone_comparison(self):
        t = trace(); t["events"][2]["timestamp"] = "2026-10-16T13:00:02+03:00"
        self.assertNotIn("TIMESTAMP_REVERSAL", codes(audit(t)))

    def test_error_status_does_not_change_reported_outcome(self):
        t = trace(); t["events"][2]["status"] = "error"
        r = audit(t)
        self.assertIn("TOOL_REPORTED_ERROR", codes(r))
        self.assertEqual(r["reported_outcome"], "success")
        self.assertEqual(r["outcome_verification"], "NOT_PERFORMED")

    def test_finding_cap_preserves_aggregate_counts(self):
        t = trace(); t["events"] = [{"event_id": f"e{i}", "sequence": i, "type": "claim"} for i in range(1500)]
        r = audit(t)
        self.assertEqual(len(r["findings"]), MAX_FINDINGS)
        self.assertEqual(r["counts"]["findings"], 3002)
        self.assertEqual(r["counts"]["findings_omitted"], 1002)


class ParsingTests(unittest.TestCase):
    def test_jsonl_equivalent(self):
        t = trace()
        lines = [dict(record_type="trace", **{k:v for k,v in t.items() if k != "events"})]
        lines += [dict(record_type="event", **e) for e in t["events"]]
        parsed = parse_bytes(("\n\n".join(map(json.dumps, lines)) + "\n").encode(), "jsonl")
        self.assertEqual(parsed["events"], t["events"])
        self.assertEqual(audit(parsed)["finding_code_counts"], {})

    def test_invalid_json_and_duplicate_key(self):
        for raw in [b'{', b'{"schema_version":"1.0","schema_version":"1.0"}', b'NaN', b'Infinity', b'\xff']:
            with self.subTest(raw=raw), self.assertRaises(InputError):
                parse_bytes(raw)

    def test_size_limit(self):
        with self.assertRaisesRegex(InputError, "INPUT_SIZE_LIMIT"):
            parse_bytes(b" " * (MAX_INPUT_BYTES + 1))

    def test_depth_limit(self):
        raw = b"[" * 100 + b"0" + b"]" * 100
        with self.assertRaises(InputError): parse_bytes(raw)

    def test_strict_types_and_fields(self):
        mutations = [lambda t: t.update(schema_version="9.0"), lambda t: t.update(events=[]), lambda t: t.update(extra="secret"), lambda t: t["events"][0].update(sequence=True), lambda t: t["events"][0].update(timestamp="2026-10-16T10:00:00"), lambda t: t["events"][0].update(timestamp="2026-02-30T10:00:00Z"), lambda t: t["events"][1].update(call_id="bad\n"), lambda t: t["events"][0].update(text="\ud800"), lambda t: t["events"][0].update(type=[])]
        for mutate in mutations:
            t = trace(); mutate(t)
            with self.subTest(t=t), self.assertRaises(InputError): parse_bytes(json.dumps(t).encode())

    def test_bad_jsonl_record_type_and_header(self):
        for raw in [b'{"record_type":"event"}', b'{"record_type":"trace","schema_version":"1.0","trace_id":"x"}\n{"record_type":[]}']:
            with self.assertRaises(InputError): parse_bytes(raw, "jsonl")


class FilesystemTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
        self.content = b"synthetic artifact\n"; (self.root / "artifact.txt").write_bytes(self.content)
        self.t = trace(); self.t["artifacts"] = [{"artifact_id": "a1", "path": "artifact.txt", "sha256": hashlib.sha256(self.content).hexdigest(), "source_event_id": "result"}]

    def tearDown(self): self.temp.cleanup()

    def test_optional_hash_matches_and_mismatch(self):
        r = audit(self.t, str(self.root)); self.assertEqual(r["artifact_verification"]["digest_matches"], 1)
        self.t["artifacts"][0]["sha256"] = "0" * 64
        self.assertIn("ARTIFACT_DIGEST_MISMATCH", codes(audit(self.t, str(self.root))))

    def test_no_read_without_explicit_root(self):
        self.t["artifacts"][0]["path"] = "https://invalid.example/private"
        r = audit(self.t)
        self.assertEqual(r["artifact_verification"]["attempted"], 0)
        self.assertIn("ARTIFACT_BYTES_NOT_CHECKED", codes(r))

    def test_escape_url_absolute_and_backslash_rejected(self):
        for path in ["../secret", "/etc/passwd", "sub/../../secret", "file:///etc/passwd", "https://example.com/x", "x\\y", "./artifact.txt", "x//y"]:
            self.t["artifacts"][0]["path"] = path
            with self.subTest(path=path): self.assertIn("ARTIFACT_UNSAFE_LOCAL_PATH", codes(audit(self.t, str(self.root))))

    def test_leaf_symlink_rejected(self):
        (self.root / "link").symlink_to(self.root / "artifact.txt")
        self.t["artifacts"][0]["path"] = "link"
        self.assertIn("ARTIFACT_FILE_UNAVAILABLE_OR_UNSAFE", codes(audit(self.t, str(self.root))))

    def test_directory_symlink_rejected(self):
        (self.root / "sub").mkdir(); (self.root / "sub" / "x").write_bytes(self.content)
        (self.root / "alias").symlink_to(self.root / "sub", target_is_directory=True)
        self.t["artifacts"][0]["path"] = "alias/x"
        self.assertIn("ARTIFACT_FILE_UNAVAILABLE_OR_UNSAFE", codes(audit(self.t, str(self.root))))

    def test_root_symlink_rejected(self):
        (self.root / "alias").symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(InputError): audit(self.t, str(self.root / "alias"))

    def test_hardlink_rejected(self):
        os.link(self.root / "artifact.txt", self.root / "hard")
        self.assertIn("ARTIFACT_NON_REGULAR_OR_MULTILINK_FILE", codes(audit(self.t, str(self.root))))

    def test_fifo_rejected_without_blocking(self):
        os.mkfifo(self.root / "pipe"); self.t["artifacts"][0]["path"] = "pipe"
        self.assertIn("ARTIFACT_NON_REGULAR_OR_MULTILINK_FILE", codes(audit(self.t, str(self.root))))

    def test_missing_file_and_digest_missing(self):
        self.t["artifacts"][0]["path"] = "absent"
        self.assertIn("ARTIFACT_FILE_UNAVAILABLE_OR_UNSAFE", codes(audit(self.t, str(self.root))))
        del self.t["artifacts"][0]["sha256"]
        self.assertIn("ARTIFACT_DIGEST_MISSING", codes(audit(self.t, str(self.root))))

    def test_oversized_artifact_rejected(self):
        with (self.root / "artifact.txt").open("wb") as f: f.truncate(8 * 1024 * 1024 + 1)
        self.assertIn("ARTIFACT_FILE_SIZE_LIMIT", codes(audit(self.t, str(self.root))))

    def test_input_symlink_rejected(self):
        (self.root / "input").symlink_to(self.root / "artifact.txt")
        with self.assertRaises(InputError): read_trace_file(str(self.root / "input"))

    def test_cli_exit_codes_and_determinism(self):
        p = self.root / "trace.json"; p.write_text(json.dumps(trace()))
        cmd = [sys.executable, "-m", "ctvi_audit", str(p), "--fail-on-findings"]
        a = subprocess.run(cmd, capture_output=True, timeout=5)
        b = subprocess.run(cmd, capture_output=True, timeout=5)
        self.assertEqual(a.returncode, 0); self.assertEqual(a.stdout, b.stdout)
        t = trace(); t["events"][2]["status"] = "error"; p.write_text(json.dumps(t))
        self.assertEqual(subprocess.run(cmd, capture_output=True, timeout=5).returncode, 1)
        p.write_text('{"password":"SECRET"')
        bad = subprocess.run(cmd, capture_output=True, timeout=5)
        self.assertEqual(bad.returncode, 2); self.assertEqual(bad.stdout, b""); self.assertNotIn(b"SECRET", bad.stderr)


if __name__ == "__main__": unittest.main()
