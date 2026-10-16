# Install and demonstrate version 0.2.0

Use Python 3.10+ on a POSIX system with `O_NOFOLLOW` and directory file-descriptor support. Linux/Python 3.12.14 is the tested environment; macOS and other Python versions have not been independently tested. Windows guarded file reads are unsupported and must fail closed. A pure-Python wheel does not imply cross-platform file-access support.

## Install the supplied wheel without network access

```sh
python3 -m venv /absolute/path/to/ctvi-venv
/absolute/path/to/ctvi-venv/bin/python -m pip install --no-index --no-deps --no-cache-dir /absolute/path/to/ctvi_agent_audit-0.2.0-py3-none-any.whl
/absolute/path/to/ctvi-venv/bin/ctvi-agent-audit --version
/absolute/path/to/ctvi-venv/bin/ctvi-agent-audit --demo clean
/absolute/path/to/ctvi-venv/bin/ctvi-agent-audit --demo defective --fail-on-findings
```

The clean demo should report zero implemented findings and exit 0. The defective demo should report nine findings and exit 1 with the requested flag: four errors, two warnings, three unknowns. It does not read artifact bytes. Both fixtures are synthetic; they demonstrate software behavior, not external scientific validation. The two file-based examples under `examples/` are separate fixtures: providing their authorized `examples/artifacts` root yields a hash match for clean and mismatch for defective. With that opt-in, the defective file has five errors, two warnings and two unknowns.

## Audit a supplied normalized record

```sh
ctvi-agent-audit /absolute/path/to/redacted-trace.json --format markdown
ctvi-agent-audit /absolute/path/to/redacted-trace.jsonl --input-format jsonl
ctvi-agent-audit /absolute/path/to/redacted-trace.json --artifact-root /absolute/path/to/authorized-artifacts
ctvi-agent-audit /absolute/path/to/redacted-trace.json --fail-on-findings --fail-on-unknown
ctvi-agent-audit --print-schema
ctvi-agent-audit --list-checks
```

Reports go to stdout. Save only by explicitly redirecting output to the intended destination. Redact inputs first; this is not an automated redaction tool. Data in strings is never executed or fetched. A source URL is a declaration, not a network request. Use a dedicated artifact directory and actual paths without symlink components, `.` or `..` segments.

## Build offline from reviewed source

```sh
python -B build_backend.py
python -B -m unittest discover -s tests -v
python -m pip install --no-index --no-deps --no-build-isolation --no-cache-dir /absolute/path/to/source-directory
```

`build_backend.py` implements the required build hooks using the Python standard library. It creates `dist/` artifacts with fixed archive metadata and wheel RECORD hashes. No setuptools or external build dependency is fetched. The generated console entry point is installed by pip. Editable installs are not supported. No public package index upload has been performed.

The utility is distributed under MIT as specified in LICENSE and LICENSE_SCOPE.txt. Installation testing does not accept separate platform or partnership terms.
