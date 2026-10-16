# CTVI Agent Audit 0.2.0

An offline Python prototype that checks the structure of explicitly supplied agent execution records. Publisher: Abdullah Alharbi, Independent Researcher and AI Technology Developer, Saudi Arabia. Alharbi AI Research & Solutions is a provisional working brand, not a verified registered company. No OpenAI affiliation, endorsement or certification is claimed.

## Install or run locally

See `docs/INSTALL_AND_DEMO.md` for offline wheel installation, console usage and reproducible builds. Use `ctvi-agent-audit --version`, `--demo clean`, `--demo defective`, `--print-schema` or `--list-checks` after installation.

Python 3.10+ on Linux/POSIX with `O_NOFOLLOW` and directory file-descriptor support is required for guarded local file reads. Development verification used Python 3.12.14. No pip packages, credentials, network, model API or paid service are required.

```sh
python -m ctvi_audit examples/clean.json
python -m ctvi_audit examples/defective.json --format markdown
python -m ctvi_audit examples/clean.jsonl --input-format jsonl
python -m ctvi_audit examples/clean.json --artifact-root /absolute/path/to/ctvi_agent_audit/examples/artifacts
python -m unittest discover -s tests -v
```

Run commands from the source root. Output is stdout only; explicitly redirect it to retain a report. The tool never writes to input files. Exit codes: 0 successful report; 1 error/warning findings with `--fail-on-findings`; 2 rejected input or local runtime failure. Unknown findings produce `INCOMPLETE_EVIDENCE` when no warning/error is observed. They cause exit 1 only with `--fail-on-unknown`. Absence of warnings is not a scientific pass.

## Supported records

Use the documented normalized schema in `schema.json`; details and JSONL framing are in `docs/INPUT_FORMAT.md`. Provider-native traces are not accepted automatically. Review any conversion for omitted fields and retain the original trace separately. Synthetic example files contain no real research measurements or customer records.

Checks cover event and sequence duplication, sequence and timestamp reversal, missing or ambiguous tool references, missing results, claim provenance references, source ordering, trace boundaries, and optional artifact SHA-256 comparison. Indexes in reports are zero-based positions in the supplied arrays.

Reported success, errors and outcomes remain reported assertions. A digest match only means supplied bytes match a supplied digest. No semantic correctness, evidence authenticity, legal admissibility, model safety, causal effect or CTVI construct validity is established. The original CTVI research has separate scientific limitations and is not validated by this software.

## Privacy and security

The program contains no network client, telemetry, shell execution, dynamic code loading, database or hosted backend. It treats text and URLs as inert data. It omits raw text, trace IDs, event IDs, tool names, artifact paths and source URLs from JSON and Markdown reports. Counts, outcomes and fingerprints can still be sensitive; this is data minimization, not anonymization.

Use normalized, redacted input. Text fields are unnecessary for structural checks and should normally be omitted. Do not supply credentials, authentication secrets, government identifiers, payment-card data or protected health information to the plugin. The tool is not an automated redaction or sensitive-data-detection service.

It reads only the explicit trace file and, when `--artifact-root` is supplied, referenced files under that explicit directory. Artifact verification rejects absolute/URL paths, parent traversal, symlink components, nonregular files and hardlinks. It fails closed when safe filesystem primitives are absent. Supply a dedicated directory with only intended artifacts. Filenames, hashes and source declarations are not trusted as proof of origin. The host's filesystem permissions, snapshots, mounts, process isolation and retention still apply.

Defaults: trace 5 MiB; 10,000 events; 100 artifact records; 100 evidence references per event; artifact 8 MiB; cumulative successful artifact reads 32 MiB; string 65,536 characters; nesting 24; detailed findings 2,000 with complete aggregate counts. An oversized/rejected artifact is reported; no URL is fetched. A concurrent change detected during a read is rejected. These limits reduce resource exposure but are not a substitute for OS-level resource controls in an untrusted multi-tenant service.

The CLI does not retain files, but Python may create import bytecode caches unless started with `python -B`. Reports retained by the user or ChatGPT Work follow their host retention policies. Uploading private traces to ChatGPT is a separate disclosure from running this offline code locally. Delete retained reports through the system where they were saved; the tool cannot delete host backups or platform history.

## Status and distribution

Status: PROTOTYPE, tested on synthetic fixtures only. Not production ready; no customer validation or scientific calibration. Independent engineering checks do not constitute security certification. The plugin folder contains a candidate package; no directory approval is claimed. No third-party runtime or build dependencies. Support contact: albdrani36@gmail.com. See `docs/KNOWN_ISSUES.md` for tested-platform and interpretation limits. MIT licensed for this newly authored utility and its bundled components. See LICENSE and LICENSE_SCOPE.txt. This does not relicense CTVI manuscripts, third-party data or unrelated FalconX code.

See the [input format](docs/INPUT_FORMAT.md), [installation and synthetic demo](docs/INSTALL_AND_DEMO.md), [known limitations](docs/KNOWN_ISSUES.md), [privacy notice](docs/PRIVACY_POLICY.md), [usage guidance](docs/USAGE_TERMS.md), [security review](docs/SECURITY_REVIEW.md) and [support information](SUPPORT.md).
