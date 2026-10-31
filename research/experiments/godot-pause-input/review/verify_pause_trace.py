"""Read-only evidence check, not an engine rerun; stdlib Python 3.10+."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

if sys.flags.optimize:
    raise RuntimeError('Assertions must be enabled; do not use -O')
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('evidence', nargs='?', type=Path, default=Path(__file__).resolve().parent,
                    help='Independent review directory containing results/')
parser.add_argument('--author', type=Path,
                    help='Fixture directory containing source and author results/; default evidence parent')
args = parser.parse_args()
review = args.evidence.resolve()
author = (args.author or review.parent).resolve()
a = json.loads((author / 'results/summary.json').read_text())
b = json.loads((review / 'results/summary.json').read_text())
assert a['source_sha256'] == b['source_sha256'], 'Author/reviewer source manifests differ'
assert a['binary_sha256'] == b['binary_sha256'], 'Author/reviewer engine binaries differ'
assert a['version'] == b['version'], 'Engine version labels differ'
for name, expected in b['source_sha256'].items():
    assert hashlib.sha256((author / name).read_bytes()).hexdigest() == expected, name
assert len(b['runs']) == 3
assert sorted(row['fps'] for row in b['runs']) == [30, 60, 144]
print('PASS: all five source fingerprints match author files and both manifests.')
print('PASS: author/reviewer engine binary hash and version match (same-build evidence).')
for row in b['runs']:
    assert row['checks'] == 'passed' and row['returncode'] == 0
    r = json.loads((review / 'results' / f"{row['fps']}.json").read_text())
    trace = r['trace']
    boundaries = [(i, e) for i, e in enumerate(trace) if e['kind'] == 'pause_boundary']
    assert len(boundaries) == 2
    (start, pause), (end, resume) = boundaries
    assert pause['paused'] is True and resume['paused'] is False
    heartbeats = [(i, e) for i, e in enumerate(trace) if e['kind'] == 'paused_heartbeat']
    assert len(heartbeats) >= 2 and len(heartbeats) == r['paused_heartbeats']
    assert len(heartbeats) == row['paused_heartbeats']
    assert all(start < i < end for i, _ in heartbeats)
    assert [e['count'] for _, e in heartbeats] == list(range(1, len(heartbeats) + 1))
    assert all(e['gameplay_tick'] == pause['gameplay_tick'] for _, e in heartbeats)
    assert pause['gameplay_tick'] == resume['gameplay_tick']
    assert not any(e['kind'] == 'gameplay_physics' for e in trace[start + 1:end])
    assert all(abs(e['delta'] - 1 / 60) < 1e-9 for _, e in heartbeats)
    print(f"PASS: {row['fps']} artificial fps; {len(heartbeats)} fixed heartbeats strictly "
          'between pause/resume, unchanged gameplay tick and no gameplay physics entry.')
print('No engine rerun performed; this verifies saved traces, not physical-device behavior.')
