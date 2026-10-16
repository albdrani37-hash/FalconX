# CTVI Agent Audit: licensed external trace example

This is a reproducible structural-check example from a **10-round fragment of one session**, adapted from publicly released coding-agent telemetry. It is not a customer trial, independent human evaluation, dataset-wide accuracy benchmark, scientific validation, security certification or endorsement by the dataset publisher.

CTVI Agent Audit utility **0.2.0** processed the 32 normalized events using Python 3.12.14. The result matched the explicit expectations below. Repeating the offline CLI invocation produced byte-identical output. No tools in the trace were executed, no model API was called and no artifact bytes were checked.

## Attribution and license

Credit: **TraceLab (SyFI Lab, University of Washington)** — <https://tracelab.cs.washington.edu> and <https://github.com/uw-syfi/TraceLab>.

The released dataset and the derived `tracelab_first10.normalized.json` fixture are available under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/). The publisher explicitly licenses released JSONL and DuckDB trace data separately from its Apache-licensed code. See [DATASET_LICENSE.md](DATASET_LICENSE.md), reproduced from the publisher's license notice, and its [pinned source](https://github.com/uw-syfi/TraceLab/blob/37402b4098dc65de56727b4c204fb71c8a59ddac/LICENSE-DATASET.md). We have made the transformations documented below. No endorsement is implied, and no attempt was made to re-identify contributors. The new normalizer code is covered by the parent CTVI utility's MIT license; this does not relicense the dataset.

## Pinned source and selection

- Dataset release: [v0.0.1](https://github.com/uw-syfi/TraceLab/releases/tag/v0.0.1), published 22 June 2026.
- Download: [syfi_coding_trace.jsonl.gz](https://github.com/uw-syfi/TraceLab/releases/download/v0.0.1/syfi_coding_trace.jsonl.gz), 53,601,226 bytes.
- Archive SHA-256: `9d265eae69a31cae203848bea936f018148eed7ca8bf56050c5abe96da0b4e6b`.
- Metadata/license repository commit: `37402b4098dc65de56727b4c204fb71c8a59ddac`; license Git blob: `6a7607f31a5e4c23a41acb2e242cef477be0d242`.
- Selection: the first 10 physical JSONL rows, fixed before inspecting checker output, with no filtering by outcome. These rows describe one Claude-provider session and contain 16 tool records.
- Exact selected source bytes SHA-256: `d84fb8ca953e73ce8483da5e74e88c3f4f343f0bc021c6032a637c3557b0cb5b`.

The full archive and original rows are not redistributed here. The publisher describes the source as sanitized real Claude Code/Codex telemetry. The archive checksum was verified. A matching checksum establishes consistency with the downloaded release, not independent authenticity of the underlying execution.

## Explicit normalization and information loss

| Source | Normalized representation | Limitation |
| --- | --- | --- |
| Each `tools[]` record | One `tool_call` | Only tool activity in the selected fragment is retained. |
| `tools[].result_at` present | One `tool_result` | A result record is not proof of successful execution. |
| Original tool identity and row/tool position | Local `rNNN.tNNN` identifier shared by call/result | Original identifiers are omitted; row/tool positions make the mapping reproducible. |
| `tool_name` | `tool_name` | A label only; the tool is never executed. |
| `emitted_at` / `result_at` | Call/result timestamp | Supplied times are not independently verified. |
| `is_error == true` | `status: error` | Preserves the publisher's recorded flag; the error itself is not replayed. |
| `is_error` not true | `status: unknown` | No-error flags do not establish independently verified success. |
| Recorded timestamps | Stable chronological sort and sequential indices | This creates a deterministic normalized order; it does not prove a causal total order. |

The adapter omits user, project, session, model, usage and latency metadata, source identifiers and the separate timing-event list. It adds no prompts, tool arguments, outputs, claims, artifacts or task-success evidence. The normalized fixture contains only local locators, tool names, statuses and timestamps. It does not fabricate start/end markers or a final outcome. `synthetic: false` records the publisher's description, not an independent authenticity conclusion. Missing boundaries are expected because the selection is a fragment. No statement is made that the original full session lacked boundaries.

## Expected and observed result

Expectations were written from the source-to-schema mapping before executing the checker.

| Finding | Expected | Observed | Interpretation |
| --- | ---: | ---: | --- |
| `START_MARKER_MISSING` | 1 | 1 | Fragment has no supplied start marker. |
| `END_MARKER_MISSING` | 1 | 1 | Fragment has no supplied end marker. |
| `TOOL_RESULT_STATUS_UNKNOWN` | 15 | 15 | Conservative unknown status was preserved. |
| `TOOL_REPORTED_ERROR` | 1 | 1 | One source result flag was carried through. |

Totals: 32 events, 16 calls, 16 results, 0 artifacts, 18 findings, 0 omitted findings. Severity counts: 0 errors, 1 warning, 17 unknowns. Report status: `ISSUES_OBSERVED`; outcome verification: `NOT_PERFORMED`; scientific validity: `NOT_ASSESSED`. Findings mostly describe the adapter's deliberately retained uncertainty. They are not a measure of the source agent's overall reliability.

## Reproduce

Use the CTVI Agent Audit utility 0.2.0 environment. The supplied normalizer uses only Python's standard library and checks the entire downloaded archive hash before reading its first ten rows. Download the source separately to a location of your choice; the normalizer performs no network requests.

```sh
python -B normalize_tracelab_sample.py /path/to/syfi_coding_trace.jsonl.gz
python -B -m ctvi_audit tracelab_first10.normalized.json --format json
```

Compare the output with `CTVI_EXTERNAL_SAMPLE_REPORT.json`. Run from the utility source environment, or install the exact 0.2.0 utility before invoking its module. Expected file SHA-256 values:

- Normalized fixture: `c772ee9b968702671941a042fa784326c74f98a46e62c1e2c470daf72f9188ea`.
- Report: `7392e852e782ca265d7912d1993469695d4d5789c66e8be267ea49b6bc8ebf89`.
- Utility `ctvi_audit/core.py`: `41a87b79f5daf533f1548a67e7cfb324197c5e262681c7d4de3104cdf2064d08`.

This example establishes that this pinned fragment can be explicitly normalized and checked with the recorded result. It does not assess unselected data, semantic correctness, hidden or fabricated events, source authenticity, representative performance, scientific constructs or commercial readiness.
