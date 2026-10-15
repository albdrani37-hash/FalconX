# Verification record

Executed 15 October 2026 using Python 3.12.14.

```sh
python3 -m unittest discover -v
python3 run_demo.py
```

Result: **12 tests passed**. [Test output](results/test_results.txt).

```json
{
  "contacts": 20,
  "proposed_records": 20,
  "duplicate_groups": 3,
  "quality_flags": 4,
  "initial_apply": {
    "applied": 2,
    "already_applied": 0
  },
  "replay": {
    "applied": 0,
    "already_applied": 2
  }
}
```

This verifies the packaged local demonstration on synthetic data. It is not independent certification, a production benchmark or a live CRM test. Approval is simulated. Audit timestamps are generated anew on each run.
