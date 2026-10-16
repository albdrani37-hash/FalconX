# Changelog

## 0.2.0 — 17 October 2026

- Add an offline-installable Python wheel, source distribution, console command and stdlib-only build backend. No package registry publication is implied.
- Add bundled synthetic demonstrations, printable normalized schema, version output and a fixed check catalog with explanations and next actions.
- Add report schema 1.1, explicit incomplete-evidence status and optional CI failure for unknowns. Input schema stays 1.0.
- Detect artifact provenance from the same or a later event, even when artifact bytes match their declared hash.
- Reject malformed timestamp offsets that Python would otherwise normalize.
- Preserve Unicode line-separator characters inside valid JSONL strings.
- Suppress potentially sensitive argument values in CLI error messages.
- Expand synthetic, edge, privacy and packaging tests. Independent engineering review reproduced four defects and confirmed their fixes.

## 0.1.0 — 16 October 2026

First offline normalized-trace prototype; deterministic JSON/Markdown reports, structural/provenance checks and opt-in guarded local artifact hashing. Thirty synthetic tests passed. No scientific or market validation.
