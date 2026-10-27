"""Small synthetic evaluation-evidence checker; no network, no dependencies.

This is an engineering demonstration, not an assurance/certification tool.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def inspect(document: Any) -> dict[str, Any]:
    """Check in-scope run evidence, population counts, and claims.

    PASS is *only* consistency with the supplied, untrusted snapshot.
    HOLD means evidence needed for a check was not supplied.
    FAIL means a check contradicted a declared invariant.
    """
    issues: list[dict[str, str]] = []
    rows: list[dict[str, str]] = []

    def flag(severity: str, code: str, identifier: str = "", detail: str = "") -> None:
        issues.append({"severity": severity, "code": code, "run_id": identifier, "detail": detail})

    if not isinstance(document, dict):
        raise ValueError("Top-level input must be a JSON object")
    runs, artifacts, claims = (document.get(k) for k in ("runs", "artifacts", "claims"))
    if not isinstance(runs, list) or not isinstance(artifacts, dict) or not isinstance(claims, dict):
        raise ValueError("Required fields: runs (array), artifacts (object), claims (object)")

    seen: set[str] = set()
    included = successes = failures = 0
    for index, run in enumerate(runs):
        if not isinstance(run, dict):
            flag("FAIL", "INVALID_RUN", str(index), "Expected object")
            continue
        rid = run.get("run_id")
        if not isinstance(rid, str) or not rid.strip():
            flag("FAIL", "INVALID_RUN_ID", str(index), "Missing nonempty run_id")
            continue
        if rid in seen:
            flag("FAIL", "DUPLICATE_RUN_ID", rid, "Run identity repeated")
            continue
        seen.add(rid)
        if type(run.get("included")) is not bool:
            flag("FAIL", "INCLUSION_UNDEFINED", rid, "included must be boolean")
            continue
        if not run["included"]:
            rows.append({"run_id": rid, "status": "EXCLUDED", "evidence": "NOT_CHECKED"})
            continue

        included += 1
        outcome = run.get("outcome")
        if outcome == "success":
            successes += 1
        elif outcome == "failure":
            failures += 1
        else:
            flag("FAIL", "OUTCOME_UNDEFINED", rid, "Expected success or failure")

        ref = run.get("artifact_id")
        declared = run.get("artifact_sha256")
        evidence_state = "VERIFIED"
        if not isinstance(ref, str) or not ref or ref not in artifacts:
            flag("HOLD", "MISSING_ARTIFACT", rid, "Referenced artifact absent")
            evidence_state = "UNKNOWN"
        elif not isinstance(declared, str) or not declared:
            flag("HOLD", "MISSING_DIGEST", rid, "Expected SHA-256 digest absent")
            evidence_state = "UNKNOWN"
        elif declared != digest(artifacts[ref]):
            flag("FAIL", "ARTIFACT_DIGEST_MISMATCH", rid, "Digest differs from supplied artifact")
            evidence_state = "CONTRADICTED"
        rows.append({"run_id": rid, "status": str(outcome), "evidence": evidence_state})

    calculated: dict[str, int | float | None] = {
        "total_included": included,
        "successes": successes,
        "failures": failures,
        "success_rate": successes / included if included else None,
    }
    if successes + failures != included:
        flag("FAIL", "OUTCOME_COUNT_INCOMPLETE", detail="Outcomes do not partition included runs")

    for field, actual in calculated.items():
        expected = claims.get(field)
        if field not in claims:
            flag("HOLD", "CLAIM_NOT_SUPPLIED", detail=field)
        elif field == "success_rate":
            if actual is None:
                if expected is not None:
                    flag("FAIL", "CLAIM_MISMATCH", detail=field)
            elif (type(expected) not in (float, int) or not math.isfinite(expected)
                  or not math.isclose(float(expected), actual, rel_tol=0, abs_tol=1e-9)):
                flag("FAIL", "CLAIM_MISMATCH", detail=field)
        elif type(expected) is not int or expected != actual:
            flag("FAIL", "CLAIM_MISMATCH", detail=field)

    issues.sort(key=lambda x: (x["severity"], x["code"], x["run_id"], x["detail"]))
    rows.sort(key=lambda x: x["run_id"])
    status = "FAIL" if any(i["severity"] == "FAIL" for i in issues) else (
        "HOLD" if issues else "PASS")
    return {"schema_version": "demo-1", "status": status,
            "source_sha256": digest(document), "calculated": calculated,
            "issues": issues, "run_evidence": rows,
            "scope_note": "Input snapshot consistency only; no authenticity, safety, or scientific validity claim."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", type=Path)
    parser.add_argument("--output", type=Path, help="Write deterministic JSON report")
    args = parser.parse_args()
    try:
        report = inspect(json.loads(args.input_json.read_text(encoding="utf-8")))
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Invalid input: {exc}\n")
    data = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(data, encoding="utf-8")
    else:
        print(data, end="")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())