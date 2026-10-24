"""Regression coverage for replay integrity and optimistic evidence checks.

The tests use only synthetic SQLite contacts and deliberately alter local rows.
No production service, credentials, or third-party API is involved.
"""
import json
import unittest

from crm_demo import apply, canonical, connect, propose, seed, snapshot


def sample_contacts():
    return [
        {"id": f"C{i}", "name": f" Sample {i} ", "email": f"user{i}@EXAMPLE.COM ",
         "company": " Test Co ", "notes": "quote requested", "category": ""}
        for i in range(3)
    ]


class ReplayIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.db = connect(":memory:")
        seed(self.db, sample_contacts())
        self.plan = propose(self.db)
        self.approval = {
            "plan_id": self.plan["plan_id"],
            "reviewer": "simulated-reviewer",
            "approved_ids": ["C0"],
        }
        self.assertEqual(
            apply(self.db, self.plan["plan_id"], self.approval),
            {"applied": 1, "already_applied": 0},
        )

    def tearDown(self):
        self.db.close()

    def replay(self, approval=None):
        return apply(self.db, self.plan["plan_id"], approval or self.approval)

    def test_unchanged_replay_is_idempotent(self):
        self.assertEqual(self.replay(), {"applied": 0, "already_applied": 1})
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM audit").fetchone()[0], 1)

    def test_modified_applied_record_is_not_acknowledged_as_success(self):
        data = snapshot(self.db)[0]
        data["company"] = "Unauthorized manual edit"
        self.db.execute("UPDATE contacts SET data=? WHERE id='C0'", (canonical(data),))
        with self.assertRaisesRegex(ValueError, "Replay integrity"):
            self.replay()
        self.assertEqual(
            self.db.execute("SELECT COUNT(*) FROM audit").fetchone()[0], 1
        )

    def test_deleted_applied_record_is_not_acknowledged_as_success(self):
        self.db.execute("DELETE FROM contacts WHERE id='C0'")
        with self.assertRaisesRegex(ValueError, "Replay integrity"):
            self.replay()

    def test_tampered_audit_before_is_rejected(self):
        self.db.execute("UPDATE audit SET before_data='{}' WHERE contact_id='C0'")
        with self.assertRaisesRegex(ValueError, "Replay integrity"):
            self.replay()

    def test_tampered_audit_after_is_rejected(self):
        self.db.execute("UPDATE audit SET after_data='{}' WHERE contact_id='C0'")
        with self.assertRaisesRegex(ValueError, "Replay integrity"):
            self.replay()

    def test_failed_mixed_replay_does_not_write_other_approved_rows(self):
        data = snapshot(self.db)[0]
        data["company"] = "Unauthorized manual edit"
        self.db.execute("UPDATE contacts SET data=? WHERE id='C0'", (canonical(data),))
        mixed = {**self.approval, "approved_ids": ["C0", "C1"]}
        before = snapshot(self.db)
        with self.assertRaisesRegex(ValueError, "Replay integrity"):
            self.replay(mixed)
        self.assertEqual(snapshot(self.db), before)
        self.assertEqual(
            self.db.execute("SELECT COUNT(*) FROM audit").fetchone()[0], 1
        )


if __name__ == "__main__":
    unittest.main()
