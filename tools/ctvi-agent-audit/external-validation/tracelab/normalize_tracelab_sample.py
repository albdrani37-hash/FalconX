"""Normalize a fixed, licensed TraceLab fragment without executing recorded tools.

Copyright (c) 2026 Abdullah Alharbi. Adapter code: MIT (parent project LICENSE).
Derived trace data: CC BY 4.0; see DATASET_LICENSE.md and README.md.
The archive must be downloaded separately. This program makes no network requests.
"""
import argparse
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path

ARCHIVE_SHA256 = '9d265eae69a31cae203848bea936f018148eed7ca8bf56050c5abe96da0b4e6b'
OUTPUT_SHA256 = 'c772ee9b968702671941a042fa784326c74f98a46e62c1e2c470daf72f9188ea'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def normalize(archive):
    digest = hashlib.sha256()
    with archive.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    require(digest.hexdigest() == ARCHIVE_SHA256, 'Pinned source checksum mismatch')
    rows = []
    with gzip.open(archive, 'rb') as stream:
        for _ in range(10):
            row = json.loads(next(stream))
            require(row['provider'] in {'claude', 'codex'}, 'Unexpected provider')
            require(isinstance(row['timing_events'], list) and isinstance(row['tools'], list), 'Unexpected source structure')
            require(all('input' not in t and 'output' not in t for t in row['tools']), 'Unexpected tool payload')
            require(all('text' not in e and 'content' not in e for e in row['timing_events']), 'Unexpected event payload')
            rows.append(row)
    events, seen_calls = [], set()
    for row_index, row in enumerate(rows):
        for tool_index, tool in enumerate(row['tools']):
            require(tool['tool_call_id'] not in seen_calls, 'Repeated tool identity needs explicit handling')
            seen_calls.add(tool['tool_call_id'])
            require(bool(tool.get('emitted_at')), 'Missing timestamp needs explicit handling')
            call_id = f'r{row_index + 1:03d}.t{tool_index + 1:03d}'
            events.append({'event_id': call_id + '.call', 'type': 'tool_call', 'call_id': call_id,
                           'tool_name': tool['tool_name'], 'timestamp': tool['emitted_at']})
            if tool.get('result_at'):
                events.append({'event_id': call_id + '.result', 'type': 'tool_result', 'call_id': call_id,
                               'timestamp': tool['result_at'],
                               'status': 'error' if tool.get('is_error') is True else 'unknown'})
    # Stable sort: timestamps from the source, original insertion order for ties.
    events.sort(key=lambda event: dt.datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00')))
    for sequence, event in enumerate(events):
        event['sequence'] = sequence
    trace = {'schema_version': '1.0', 'trace_id': 'tracelab-v0.0.1-first10-tools',
             'reported_outcome': 'unknown', 'synthetic': False, 'events': events}
    payload = (json.dumps(trace, ensure_ascii=True, indent=2, sort_keys=True) + '\n').encode('utf-8')
    require(hashlib.sha256(payload).hexdigest() == OUTPUT_SHA256, 'Unexpected normalized output')
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path, help='Pinned syfi_coding_trace.jsonl.gz release asset')
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('tracelab_first10.normalized.json'))
    args = parser.parse_args()
    payload = normalize(args.archive)
    args.output.write_bytes(payload)
    print(json.dumps({'source_records': 10, 'events': 32, 'sha256': OUTPUT_SHA256}))


if __name__ == '__main__':
    main()
