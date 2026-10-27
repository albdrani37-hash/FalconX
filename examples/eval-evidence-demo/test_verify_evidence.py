"""Synthetic acceptance and negative-path tests for the evidence checker."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from verify_evidence import digest, inspect


def clean():
    a = {"text": "tool returned verified result", "step": 1}
    b = {"text": "tool failed with exception", "step": 2}
    return {
        "artifacts": {"a": a, "b": b},
        "runs": [
            {"run_id": "r1", "included": True, "outcome": "success", "artifact_id": "a", "artifact_sha256": digest(a)},
            {"run_id": "r2", "included": True, "outcome": "failure", "artifact_id": "b", "artifact_sha256": digest(b)},
            {"run_id": "r3", "included": False, "exclusion_reason": "not in selected population"},
        ],
        "claims": {"total_included": 2, "successes": 1, "failures": 1, "success_rate": 0.5},
    }


class EvidenceTests(unittest.TestCase):
    def test_clean_pass(self):
        result = inspect(clean())
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["calculated"]["total_included"], 2)
        self.assertEqual(len(result["run_evidence"]), 3)

    def test_report_deterministic(self):
        d = clean()
        self.assertEqual(json.dumps(inspect(d), sort_keys=True), json.dumps(inspect(d), sort_keys=True))

    def test_claim_mismatch_fail(self):
        d = clean(); d["claims"]["successes"] = 2
        self.assertEqual(inspect(d)["status"], "FAIL")

    def test_duplicate_run_id_fail(self):
        d = clean(); d["runs"].append(copy.deepcopy(d["runs"][0]))
        self.assertIn("DUPLICATE_RUN_ID", [i["code"] for i in inspect(d)["issues"]])

    def test_mutated_artifact_fail(self):
        d = clean(); d["artifacts"]["a"]["text"] = "modified after declaration"
        self.assertIn("ARTIFACT_DIGEST_MISMATCH", [i["code"] for i in inspect(d)["issues"]])

    def test_missing_artifact_hold(self):
        d = clean(); del d["artifacts"]["a"]
        self.assertEqual(inspect(d)["status"], "HOLD")

    def test_missing_digest_hold(self):
        d = clean(); del d["runs"][0]["artifact_sha256"]
        self.assertEqual(inspect(d)["status"], "HOLD")

    def test_exclusions_not_in_denominator(self):
        d = clean(); d["runs"].append({"run_id": "r4", "included": False})
        self.assertEqual(inspect(d)["calculated"]["total_included"], 2)

    def test_missing_claim_hold(self):
        d = clean(); del d["claims"]["failures"]
        self.assertEqual(inspect(d)["status"], "HOLD")

    def test_invalid_outcome_fail(self):
        d = clean(); d["runs"][0]["outcome"] = "maybe"
        self.assertEqual(inspect(d)["status"], "FAIL")

    def test_top_level_schema_rejected(self):
        with self.assertRaises(ValueError): inspect({"runs": []})

    def test_cli_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "data.json"
            d = clean(); del d["artifacts"]["a"]
            p.write_text(json.dumps(d), encoding="utf-8")
            proc = subprocess.run([sys.executable, str(Path(__file__).with_name("verify_evidence.py")), str(p)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(json.loads(proc.stdout)["status"], "HOLD")


if __name__ == "__main__":
    unittest.main()