"""Read-only CLI. Output goes only to stdout; errors are fixed codes on stderr."""

import argparse
from importlib import resources
import sys

from . import __version__
from .catalog import catalog
from .core import InputError, audit, json_report, markdown_report, parse_bytes, read_trace_file


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # argparse normally echoes unknown arguments/values, which may be sensitive.
        self.exit(2, "CTVI_USAGE_ERROR: INVALID_ARGUMENTS (use --help)\n")


def main(argv=None):
    parser = SafeArgumentParser(description="Offline structural checks of supplied agent traces; not certification.")
    parser.add_argument("input", nargs="?", help="Explicit JSON or JSONL regular file; no symlink components")
    parser.add_argument("--version", action="version", version="CTVI Agent Audit " + __version__)
    parser.add_argument("--demo", choices=("clean", "defective"), help="Audit a bundled synthetic example; no customer data or artifact byte reads")
    parser.add_argument("--list-checks", action="store_true", help="Print implemented check descriptions and suggested actions")
    parser.add_argument("--print-schema", action="store_true", help="Print the supported normalized JSON schema")
    parser.add_argument("--input-format", choices=("json", "jsonl"), default="json")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--artifact-root", help="Explicit absolute allowed directory for opt-in artifact hashing")
    parser.add_argument("--fail-on-findings", action="store_true", help="Exit 1 for error/warning findings; unknowns alone do not fail")
    parser.add_argument("--fail-on-unknown", action="store_true", help="Also exit 1 when evidence is incomplete or unverified")
    args = parser.parse_args(argv)
    if sum((args.input is not None, args.demo is not None, args.list_checks, args.print_schema)) != 1:
        parser.error("choose exactly one input file, --demo or --list-checks")
    if (args.demo or args.list_checks or args.print_schema) and (args.artifact_root is not None or args.input_format != "json"):
        parser.error("artifact-root and input-format apply only to supplied files")
    try:
        if args.list_checks:
            sys.stdout.write(json_report(catalog()))
            return 0
        if args.print_schema:
            sys.stdout.write(resources.files("ctvi_audit").joinpath("data", "schema.json").read_text(encoding="utf-8"))
            return 0
        raw = resources.files("ctvi_audit").joinpath("data", args.demo + ".json").read_bytes() if args.demo else read_trace_file(args.input)
        report = audit(parse_bytes(raw, args.input_format), artifact_root=args.artifact_root)
        sys.stdout.write(markdown_report(report) if args.format == "markdown" else json_report(report))
    except InputError as exc:
        sys.stderr.write("CTVI_INPUT_ERROR: " + str(exc) + "\n")
        return 2
    except (OSError, MemoryError):
        sys.stderr.write("CTVI_RUNTIME_ERROR: LOCAL_RESOURCE_UNAVAILABLE\n")
        return 2
    return int((args.fail_on_findings and report["structural_status"] == "ISSUES_OBSERVED") or (args.fail_on_unknown and report["severity_counts"]["unknown"] > 0))


if __name__ == "__main__":
    raise SystemExit(main())
