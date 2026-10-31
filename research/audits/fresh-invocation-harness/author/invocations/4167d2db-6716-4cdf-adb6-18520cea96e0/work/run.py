"""Run installed Godot; fail on exit, timeout, engine errors or oracle mismatch."""
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time

if sys.flags.optimize:
    raise RuntimeError('Run without -O: verification requires enabled assertions')

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
# Never leave an older success summary beside a partially failed new run.
(OUT / 'summary.json').unlink(missing_ok=True)
RUNTIME = Path(tempfile.mkdtemp(prefix='gamelibrary-godot-'))
env = os.environ.copy()
for key, suffix in [('HOME', 'home'), ('XDG_CACHE_HOME', 'cache'),
                    ('XDG_DATA_HOME', 'data'), ('XDG_CONFIG_HOME', 'config')]:
    p = RUNTIME / suffix
    p.mkdir()
    env[key] = str(p)
env['GODOT_SILENCE_ROOT_WARNING'] = '1'
binary = shutil.which('godot')
assert binary

def run(command):
    start = time.monotonic()
    p = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=20)
    return p, time.monotonic() - start

version, _ = run([binary, '--version'])
(OUT / 'version.txt').write_text(version.stdout + version.stderr)
assert version.returncode == 0 and not version.stderr
help_result, _ = run([binary, '--help'])
help_text = re.sub(r'\x1b\[[0-9;]*m', '', help_result.stdout)
(OUT / 'cli-help.txt').write_text('\n'.join(line for line in help_text.splitlines()
    if any(flag in line for flag in ('--headless ', '--fixed-fps ', '--max-fps ', '--single-threaded-scene '))) + '\n')
assert help_result.returncode == 0 and not help_result.stderr
for required_flag in ('--headless', '--fixed-fps', '--max-fps', '--single-threaded-scene'):
    assert required_flag in help_text, ('unsupported CLI flag', required_flag)
summary = {'version': version.stdout.strip(), 'platform': platform.platform(),
           'python': platform.python_version(), 'runtime_dir': str(RUNTIME),
           'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
              for name in ('main.gd', 'main.tscn', 'project.godot', 'run.py')}, 'runs': []}
expected = []
x = 0
axis = 0
events = []
for tick in range(120):
    if tick in {0: 1, 30: -1, 90: 0}:
        axis = {0: 1, 30: -1, 90: 0}[tick]
    x += axis
    if tick in (6, 8):
        events.append(tick)
    expected.append([tick, x, axis, events.copy()])
for mode in ('fixed-fps', 'max-fps'):
    for fps in (30, 60, 144):
        name = f'{mode}-{fps}'
        command = [binary, '--headless', '--path', str(ROOT), '--single-threaded-scene',
                   '--' + mode, str(fps)]
        p, elapsed = run(command)
        text = p.stdout + p.stderr
        (OUT / (name + '.log')).write_text(text)
        assert p.returncode == 0, (name, p.returncode, text)
        assert 'ERROR' not in text and 'SCRIPT ERROR' not in text and not p.stderr, text
        lines = [line[len('RESULT_JSON='):] for line in p.stdout.splitlines()
                 if line.startswith('RESULT_JSON=')]
        assert len(lines) == 1, (name, text)
        r = json.loads(lines[0])
        (OUT / (name + '.json')).write_text(json.dumps(r, indent=2) + '\n')
        assert r['physics_ticks_per_second'] == 60
        assert r['max_physics_steps_per_frame'] == 8
        assert r['physics_jitter_fix'] == 0 and r['time_scale'] == 1
        if mode == 'fixed-fps':
            assert all(abs(f['delta'] - 1 / fps) < 1e-9 for f in r['frames'])
        assert r['tick_states'] == expected, name
        assert (r['ticks'], r['x'], r['axis'], r['events'], r['read_only_ok']) == (120, -30, 0, [6, 8], True)
        assert len(r['physics_deltas']) == 120
        assert all(abs(d - 1 / 60) < 1e-9 for d in r['physics_deltas'])
        assert sum(f['steps'] for f in r['frames']) == 120
        last_tick = 0
        for frame in r['frames']:
            assert frame['tick'] - last_tick == frame['steps'], (name, 'callback accounting')
            assert 0 <= frame['alpha'] <= 1
            t = frame['tick']
            current = expected[t-1][1] if t else 0
            previous = expected[t-2][1] if t > 1 else 0
            predicted_view = previous + (current - previous) * frame['alpha']
            assert abs(frame['presentation_x'] - predicted_view) < 1e-9, (name, 'numeric presentation')
            last_tick = t
        steps = [f['steps'] for f in r['frames']]
        if fps == 30:
            assert any(n >= 2 for n in steps), (name, 'missing multiple-step witness')
        if fps == 144:
            assert any(n == 0 for n in steps), (name, 'missing zero-step witness')
        summary['runs'].append({'name': name, 'command': command, 'exit_code': p.returncode,
            'wall_seconds': elapsed, 'process_callbacks': len(steps),
            'physics_callbacks': len(r['physics_deltas']),
            'steps_per_process_histogram': {str(n): steps.count(n) for n in sorted(set(steps))},
            'process_delta_sum': sum(f['delta'] for f in r['frames']),
            'tick_states_sha256': hashlib.sha256(json.dumps(r['tick_states'], separators=(',', ':')).encode()).hexdigest()})
summary['checks'] = '6 actual Godot processes matched the independent 120-tick integer oracle'
(OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
