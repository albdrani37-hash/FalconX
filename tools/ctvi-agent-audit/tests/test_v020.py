"""Regression and edge tests motivated by independent engineering review."""

import base64
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import build_backend
from ctvi_audit.core import InputError, audit, json_report, parse_bytes
from test_audit import codes, trace


class ReviewRegressions(unittest.TestCase):
    def test_artifact_self_and_future_source_order(self):
        with tempfile.TemporaryDirectory() as root:
            Path(root, "a").write_bytes(b"demo")
            for source in ("claim", "end"):
                t = trace()
                t["artifacts"] = [{"artifact_id": "a", "path": "a", "sha256": hashlib.sha256(b"demo").hexdigest(), "source_event_id": source}]
                t["events"][3]["evidence"] = [{"kind": "artifact", "ref": "a"}]
                r = audit(t, root)
                self.assertIn("ARTIFACT_SOURCE_NOT_PRIOR", codes(r))
                self.assertEqual(r["artifact_verification"]["digest_matches"], 1)
                self.assertEqual(r["structural_status"], "ISSUES_OBSERVED")

    def test_invalid_timezone_offsets_rejected(self):
        for offset in ("+00:60", "+01:99", "-01:99", "+24:00", "+99:00"):
            t = trace(); t["events"][0]["timestamp"] = "2026-10-16T10:00:00" + offset
            with self.subTest(offset=offset), self.assertRaisesRegex(InputError, "INVALID_TIMESTAMP"):
                parse_bytes(json.dumps(t).encode())

    def test_jsonl_unicode_separator_is_data(self):
        for separator in ("\u2028", "\u2029", "\u0085"):
            t = trace(); t["events"][2]["text"] = "before" + separator + "after"
            header = {k: v for k, v in t.items() if k != "events"}
            records = [dict(record_type="trace", **header)] + [dict(record_type="event", **e) for e in t["events"]]
            raw = "\r\n".join(json.dumps(r, ensure_ascii=False) for r in records).encode()
            parsed = parse_bytes(raw, "jsonl")
            self.assertEqual(parsed["events"][2]["text"], t["events"][2]["text"])

    def test_invalid_cli_arguments_do_not_echo(self):
        for args in (["--format", "SECRET_SENTINEL"], ["--SECRET_SENTINEL"], ["--demo", "SECRET_SENTINEL"]):
            r = subprocess.run([sys.executable, "-B", "-m", "ctvi_audit"] + args, capture_output=True, timeout=5)
            self.assertEqual(r.returncode, 2)
            self.assertEqual(r.stdout, b"")
            self.assertNotIn(b"SECRET_SENTINEL", r.stderr)
            self.assertEqual(r.stderr, b"CTVI_USAGE_ERROR: INVALID_ARGUMENTS (use --help)\n")


class BoundaryAndPrivacyTests(unittest.TestCase):
    def test_duplicate_keys_in_nested_record(self):
        raw = b'{"schema_version":"1.0","trace_id":"t","events":[{"event_id":"e","event_id":"f","sequence":0,"type":"start"}]}'
        with self.assertRaisesRegex(InputError, "DUPLICATE_JSON_KEY"): parse_bytes(raw)

    def test_too_many_evidence_references_rejected(self):
        t = trace(); t["events"][3]["evidence"] = [{"kind": "self_report"}] * 101
        with self.assertRaisesRegex(InputError, "EVIDENCE_COUNT_LIMIT"): audit(t)

    def test_too_many_artifacts_rejected(self):
        t = trace(); t["artifacts"] = [{"artifact_id": f"a{i}"} for i in range(101)]
        with self.assertRaisesRegex(InputError, "ARTIFACT_COUNT_LIMIT"): audit(t)

    def test_oversized_text_rejected(self):
        t = trace(); t["events"][0]["text"] = "x" * 65537
        with self.assertRaisesRegex(InputError, "INVALID_OR_OVERSIZED_STRING"): audit(t)

    def test_input_unicode_controls_do_not_render(self):
        t = trace(); t["events"][2]["text"] = "\x1b[31mPRIVATE\u202e"; t["events"][3]["evidence"] = [{"kind": "external", "ref": "https://private.invalid/PRIVATE"}]
        report = json_report(audit(t))
        self.assertNotIn("PRIVATE", report); self.assertNotIn("private.invalid", report)

    def test_no_network_or_subprocess_runtime_imports(self):
        import ast
        forbidden = {"socket", "http", "urllib", "requests", "subprocess", "pickle"}
        for path in (Path(__file__).parents[1] / "ctvi_audit").glob("*.py"):
            tree = ast.parse(path.read_text())
            names = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
            names |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
            self.assertFalse(names & forbidden, path.name)

    def test_aggregate_artifact_budget(self):
        with tempfile.TemporaryDirectory() as root:
            Path(root, "a").write_bytes(b"abc")
            t = trace(); t["artifacts"] = [{"artifact_id": f"a{i}", "path": "a", "sha256": hashlib.sha256(b"abc").hexdigest(), "source_event_id": "result"} for i in range(3)]
            with patch("ctvi_audit.core.MAX_TOTAL_ARTIFACT_BYTES", 6): r = audit(t, root)
            self.assertEqual(r["artifact_verification"]["bytes_read"], 6)
            self.assertEqual(r["artifact_verification"]["digest_matches"], 2)
            self.assertIn("ARTIFACT_FILE_SIZE_LIMIT", codes(r))

    def test_ambiguous_artifact_reference_is_not_verified_link(self):
        t = trace(); t["artifacts"] = [{"artifact_id": "a"}, {"artifact_id": "a"}]
        t["events"][3]["evidence"] = [{"kind": "artifact", "ref": "a"}]
        self.assertTrue({"DUPLICATE_ARTIFACT_ID", "EVIDENCE_ARTIFACT_AMBIGUOUS"} <= codes(audit(t)))

    def test_unknowns_have_incomplete_evidence_status(self):
        t = trace(); del t["events"][0]["timestamp"]
        r = audit(t)
        self.assertEqual(r["structural_status"], "INCOMPLETE_EVIDENCE")
        self.assertEqual(r["evidence_status"], "UNKNOWNS_PRESENT")

    def test_fail_on_unknown_is_explicit(self):
        with tempfile.TemporaryDirectory() as root:
            t = trace(); del t["events"][0]["timestamp"]
            p = Path(root, "t.json"); p.write_text(json.dumps(t))
            base = [sys.executable, "-B", "-m", "ctvi_audit", str(p)]
            self.assertEqual(subprocess.run(base + ["--fail-on-findings"], capture_output=True, timeout=5).returncode, 0)
            self.assertEqual(subprocess.run(base + ["--fail-on-unknown"], capture_output=True, timeout=5).returncode, 1)

    def test_explanations_contain_no_input_text(self):
        t = trace(); t["events"][3]["evidence"] = []
        r = audit(t)
        entry = r["finding_explanations"]["CLAIM_WITHOUT_PROVENANCE"]
        self.assertTrue(entry["meaning"] and entry["next_action"])
        self.assertNotIn("SECRET", json_report(r))


class PackagingTests(unittest.TestCase):
    def test_wheel_record_integrity_and_determinism(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            wa = Path(a, build_backend.build_wheel(a)); wb = Path(b, build_backend.build_wheel(b))
            self.assertEqual(wa.read_bytes(), wb.read_bytes())
            with zipfile.ZipFile(wa) as z:
                records = list(csv.reader(io.StringIO(z.read(build_backend.INFO + "/RECORD").decode())))
                self.assertEqual({row[0] for row in records}, set(z.namelist()))
                for name, digest, size in records:
                    if not digest: continue
                    data = z.read(name)
                    expected = "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()
                    self.assertEqual(digest, expected); self.assertEqual(int(size), len(data))
                self.assertFalse(any(".." in n.split("/") or n.startswith("/") or "__pycache__" in n for n in z.namelist()))
                self.assertIn("ctvi_audit/data/clean.json", z.namelist())

    def test_bundled_demo_and_schema(self):
        clean = subprocess.run([sys.executable, "-B", "-m", "ctvi_audit", "--demo", "clean"], capture_output=True, timeout=5)
        self.assertEqual(clean.returncode, 0); self.assertEqual(json.loads(clean.stdout)["counts"]["findings"], 0)
        defective = subprocess.run([sys.executable, "-B", "-m", "ctvi_audit", "--demo", "defective", "--fail-on-findings"], capture_output=True, timeout=5)
        self.assertEqual(defective.returncode, 1)
        self.assertTrue(json.loads(defective.stdout)["synthetic_as_declared"])
        schema = subprocess.run([sys.executable, "-B", "-m", "ctvi_audit", "--print-schema"], capture_output=True, timeout=5)
        self.assertEqual(schema.returncode, 0); self.assertEqual(json.loads(schema.stdout)["title"], "CTVI Agent Audit normalized trace 1.0")

    def test_info_modes_do_not_require_files(self):
        for arg in ("--version", "--help", "--list-checks"):
            result = subprocess.run([sys.executable, "-B", "-m", "ctvi_audit", arg], capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 0); self.assertTrue(result.stdout)


if __name__ == "__main__": unittest.main()
