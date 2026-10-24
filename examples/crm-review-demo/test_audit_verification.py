"""Offline audit-verification regression tests on synthetic CRM records."""
import json
import unittest

from crm_demo import apply, canonical, connect, propose, seed, verify_audit


def rows():
    return [
        {"id": "C1", "name": " A ", "email": "a@EXAMPLE.COM ",
         "company": " Example ", "notes": "quote", "category": ""},
        {"id": "C2", "name": " B ", "email": "b@EXAMPLE.COM ",
         "company": " Example ", "notes": "support", "category": ""},
    ]


class AuditVerificationTests(unittest.TestCase):
    def setUp(self):
        self.db = connect(":memory:")
        seed(self.db, rows())
        self.plan = propose(self.db)
        apply(self.db, self.plan["plan_id"], {
            "plan_id": self.plan["plan_id"], "reviewer": "simulated",
            "approved_ids": ["C1", "C2"],
        })

    def tearDown(self):
        self.db.close()

    def test_valid_audit_reports_two_records(self):
        result = verify_audit(self.db)
        self.assertEqual(result, {
            "ok": True, "audited_records": 2, "audited_contacts": 2, "issues": []
        })

    def test_changed_current_row_detected(self):
        self.db.execute("UPDATE contacts SET data='{}' WHERE id='C1'")
        result = verify_audit(self.db)
        self.assertFalse(result["ok"])
        self.assertIn("CURRENT_ROW_MISMATCH", {x["code"] for x in result["issues"]})

    def test_deleted_current_row_detected(self):
        self.db.execute("DELETE FROM contacts WHERE id='C1'")
        result = verify_audit(self.db)
        self.assertFalse(result["ok"])
        self.assertIn("CURRENT_ROW_MISMATCH", {x["code"] for x in result["issues"]})

    def test_modified_audit_after_detected(self):
        self.db.execute("UPDATE audit SET after_data='{}' WHERE contact_id='C1'")
        result = verify_audit(self.db)
        self.assertFalse(result["ok"])
        self.assertIn("AUDIT_PLAN_MISMATCH", {x["code"] for x in result["issues"]})

    def test_missing_plan_detected(self):
        self.db.execute("DELETE FROM plans WHERE id=?", (self.plan["plan_id"],))
        result = verify_audit(self.db)
        self.assertFalse(result["ok"])
        self.assertIn("MISSING_PLAN", {x["code"] for x in result["issues"]})

    def test_malformed_audit_json_is_reported_not_crash(self):
        self.db.execute("UPDATE audit SET before_data='not-json' WHERE contact_id='C1'")
        result = verify_audit(self.db)
        self.assertFalse(result["ok"])
        self.assertIn("INVALID_AUDIT_JSON", {x["code"] for x in result["issues"]})

    def test_untracked_contact_without_audit_is_not_claimed_as_verified(self):
        self.db.execute("DELETE FROM audit")
        result = verify_audit(self.db)
        self.assertEqual(result, {
            "ok": True, "audited_records": 0, "audited_contacts": 0, "issues": []
        })


if __name__ == "__main__":
    unittest.main()
