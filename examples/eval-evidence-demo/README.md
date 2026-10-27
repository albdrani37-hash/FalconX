# Evaluation Evidence Review — runnable synthetic buyer example

**Independent, no-cost Python demonstration (standard library only).** This folder is separate from AgentDojo scientific results and is *not* a real client implementation, benchmark validation, tamper-proof audit or safety certification.

This tiny reproducible package checks that a frozen set of agent-evaluation claims is internally consistent with its included runs and supplied artifact payloads. It deliberately retains `HOLD` for missing evidence and `FAIL` for contradictory evidence; neither is silently converted into a pass.

## Reproduce the demonstration

From this directory with Python 3.11 or later:

```sh
python -m unittest -v test_verify_evidence.py
python verify_evidence.py sample_synthetic.json --output report.json
cat report.json
```

The sample is wholly synthetic. A clean case returns exit code `0` and `PASS`. Introduce missing evidence or a false claim and the checker returns nonzero exit code `1` with `HOLD` or `FAIL`. Malformed top-level inputs return `2`.

## Checked controls

- Explicit included/excluded run population and unique run IDs;
- Count reconciliation for total included, successes, failures and success rate;
- Evidence link to a caller-provided artifact and an untrusted, declared SHA-256 payload digest;
- Negative-path checks for duplicate identities, changed artifact bodies, absent records, absent digests, unsupported outcomes and false aggregate claims;
- Stable machine-readable JSON findings with disclosed limitations.

**Security boundary:** A matching digest proves only consistency *within the supplied snapshot*: anyone able to modify both payload and digest can fabricate a matching pair. No signatures, externally rooted provenance, client-authorized data processing, causal proof, model safety testing or scientific construct validation is present. False claims about a fully fabricated input can still pass if internally consistent.

## Potential commercial extension

For a real buyer, a *separate paid SOW* would define source record format, trustworthy origin/freeze, allowed data, acceptance test fixtures, record volume, permissions, evaluation metrics, limitations and safe payment milestones. Live systems, restricted datasets, legal sign-off and assurance certification are out of this demonstration's scope.

**Related:** [AgentDojo Trace Audit buyer case study](https://github.com/albdrani37-hash/agentdojo-trace-audit/blob/main/BUYER_CASE_STUDY.md) · [Request a bounded paid engineering review](https://github.com/albdrani37-hash/agentdojo-trace-audit/blob/main/REQUEST_A_QUOTE.md) · [Professional email](mailto:abdullahalharbi@purelymail.com).