"""Real Godot input dispatch + pause fixture with independent expected labels."""
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
    raise RuntimeError('Assertions required; do not run with -O')
ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
(OUT / 'summary.json').unlink(missing_ok=True)
env = os.environ.copy()
runtime = Path(tempfile.mkdtemp(prefix='gamelibrary-godot-pause-'))
for key in ('HOME', 'XDG_CACHE_HOME', 'XDG_DATA_HOME', 'XDG_CONFIG_HOME'):
    path = runtime / key
    path.mkdir()
    env[key] = str(path)
env['GODOT_SILENCE_ROOT_WARNING'] = '1'
binary = shutil.which('godot')
assert binary
version = subprocess.run([binary, '--version'], env=env, capture_output=True, text=True, timeout=20)
assert version.returncode == 0 and not version.stderr
(OUT / 'version.txt').write_text(version.stdout)
help_run = subprocess.run([binary, '--help'], env=env, capture_output=True, text=True, timeout=20)
assert help_run.returncode == 0 and not help_run.stderr
help_text = re.sub(r'\x1b\[[0-9;]*m', '', help_run.stdout)
flags = ('--headless', '--single-threaded-scene', '--fixed-fps', '--path')
for flag in flags:
    assert flag in help_text, flag
(OUT / 'cli-help.txt').write_text('\n'.join(line for line in help_text.splitlines()
    if any(flag + ' ' in line for flag in flags)) + '\n')
summary = {'date_utc': '2026-10-31', 'version': version.stdout.strip(),
    'platform': platform.platform(), 'python': platform.python_version(),
    'binary_sha256': hashlib.file_digest(open(binary, 'rb'), 'sha256').hexdigest(),
    'source_sha256': {n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest()
        for n in ('main.gd', 'consumer.gd', 'main.tscn', 'project.godot', 'run.py')},
    'runs': []}
for fps in (30, 60, 144):
    command = [binary, '--headless', '--path', str(ROOT), '--single-threaded-scene', '--fixed-fps', str(fps)]
    start = time.monotonic()
    p = subprocess.run(command, env=env, capture_output=True, text=True, timeout=20)
    elapsed = time.monotonic() - start
    raw = p.stdout + p.stderr
    (OUT / f'{fps}.log').write_text(raw)
    assert p.returncode == 0 and not p.stderr and 'ERROR' not in raw, raw
    lines = [l.removeprefix('RESULT_JSON=') for l in p.stdout.splitlines() if l.startswith('RESULT_JSON=')]
    assert len(lines) == 1, raw
    r = json.loads(lines[0])
    (OUT / f'{fps}.json').write_text(json.dumps(r, indent=2) + '\n')
    assert (r['controller_mode'], r['gameplay_mode'], r['accumulated_input'], r['physics_hz'], r['jitter_fix'], r['epoch']) == (3, 1, False, 60, 0, 2)
    expected_all = [(label, pressed, paused) for label, paused in [('pre_pause', False), ('during_pause', True), ('fresh', False)] for pressed in (True, False)]
    assert [(x['label'], x['pressed'], x['paused']) for x in r['controller_inputs']] == expected_all
    assert [(x['label'], x['pressed'], x['paused']) for x in r['gameplay_inputs']] == [x for x in expected_all if not x[2]]
    assert r['naive_before_fresh'] == ['pre_pause', 'during_pause']
    assert r['guarded_before_fresh'] == []
    assert r['naive_events'] == ['pre_pause', 'during_pause', 'fresh']
    assert r['guarded_events'] == ['fresh']
    observations = [x for x in r['trace'] if x['kind'] == 'pause_observation']
    assert len(observations) == 1
    pause = observations[0]
    assert pause['before'] == pause['after'] and pause['queued_naive'] == 2 and pause['queued_guarded'] == 1
    heartbeats = [x for x in r['trace'] if x['kind'] == 'paused_heartbeat']
    assert len(heartbeats) >= 2 and len(heartbeats) == r['paused_heartbeats']
    assert all(x['gameplay_tick'] == pause['before'] for x in heartbeats)
    assert all(abs(x['delta'] - 1 / 60) < 1e-9 for x in heartbeats)
    assert all(abs(x['delta'] - 1 / fps) < 1e-9 for x in r['trace'] if x['kind'] == 'controller_process')
    assert all(not x['paused'] for x in r['trace'] if x['kind'] == 'gameplay_physics')
    assert all(not x['global_pressed'] for x in r['trace'] if x['kind'] == 'injected_pair')
    summary['runs'].append({'fps': fps, 'command': command, 'returncode': p.returncode,
        'wall_seconds': elapsed, 'process_callbacks': r['process_callbacks'],
        'physics_callbacks': r['physics_callbacks'], 'paused_heartbeats': r['paused_heartbeats'], 'checks': 'passed'})
(OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
