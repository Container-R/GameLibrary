"""Actual Godot focus gate then isolated naive/guarded identity experiment."""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
if sys.flags.optimize:
    raise RuntimeError('Assertions required; do not run with -O')
ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
(OUT / 'summary.json').unlink(missing_ok=True)
env = os.environ.copy()
runtime = Path(tempfile.mkdtemp(prefix='gamelibrary-focus-'))
for key in ('HOME', 'XDG_CACHE_HOME', 'XDG_DATA_HOME', 'XDG_CONFIG_HOME'):
    p = runtime / key; p.mkdir(); env[key] = str(p)
env['GODOT_SILENCE_ROOT_WARNING'] = '1'
binary = shutil.which('godot')
assert binary

def execute(args, log_name=None):
    p = subprocess.run([binary, *args], env=env, capture_output=True, text=True, timeout=20)
    if log_name:
        (OUT / log_name).write_text(p.stdout + p.stderr)
    assert p.returncode == 0 and not p.stderr and 'ERROR' not in p.stdout, (p.returncode, p.stdout, p.stderr)
    return p

version = execute(['--version']).stdout.strip()
help_text = execute(['--help']).stdout
for flag in ('--headless', '--path', '--single-threaded-scene'):
    assert flag in help_text
(OUT / 'version.txt').write_text(version + '\n')
summary = {'version': version, 'platform': platform.platform(), 'python': platform.python_version(),
           'binary_sha256': hashlib.sha256(Path(binary).read_bytes()).hexdigest(),
           'source_sha256': {n: hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
                             for n in ('main.gd', 'main.tscn', 'project.godot', 'run.py')}, 'runs': []}
for mode in ('gate', 'naive', 'guarded'):
    args = ['--headless', '--path', str(ROOT), '--single-threaded-scene', '--', mode]
    p = execute(args, f'{mode}.log')
    lines = [s.removeprefix('RESULT_JSON=') for s in p.stdout.splitlines() if s.startswith('RESULT_JSON=')]
    assert len(lines) == 1
    r = json.loads(lines[0]); (OUT / f'{mode}.json').write_text(json.dumps(r, indent=2)+'\n')
    t = r['trace']
    assert r['mode'] == mode and r['display_server'] == 'headless'
    assert [e['sequence'] for e in t] == list(range(1, len(t)+1))
    def one(kind):
        rows = [e for e in t if e['kind'] == kind]
        assert len(rows) == 1, (mode, kind, rows)
        return rows[0]
    assert one('initial_focus')['owner_id'] == r['old_id']
    assert one('dialog_focus')['owner_id'] == r['close_id']
    assert any(e['kind'] == 'focus_entered' and e['target_id'] == r['old_id'] for e in t)
    assert any(e['kind'] == 'focus_entered' and e['target_id'] == r['close_id'] for e in t)
    if mode == 'gate':
        assert r['restore_count'] == 0 and one('process_observation')['owner_id'] == r['close_id']
    else:
        assert r['restore_count'] == 1 and r['old_id'] != r['new_id']
        assert one('old_detached')['inside_tree'] is False
        new = one('replacement_ready'); request = one('restore_started')
        assert new['new_path'] == one('initial_focus')['path']
        assert new['inside_tree'] and new['visible_in_tree'] and new['focus_mode'] == 2
        assert request['revision'] == request['request_revision'] == r['revision'] == 1
        assert request['candidate_id'] == r['new_id'] and request['expected_id'] == r['old_id']
        assert request['business'] == new['business'] == 'record-B'
        assert one('restore_enqueued')['sequence'] < new['sequence'] < request['sequence']
        assert request['sequence'] < one('restore_returned')['sequence'] < one('deferred_observation')['sequence'] < one('process_observation')['sequence']
        expected = r['new_id'] if mode == 'naive' else r['safe_id']
        for kind in ('restore_returned','deferred_observation','process_observation'):
            assert one(kind)['owner_id'] == expected
        assert any(e['kind'] == 'focus_entered' and e['target_id'] == expected and e['sequence'] > request['sequence'] for e in t)
        mismatches = [e for e in t if e['kind']=='identity_mismatch']
        assert len(mismatches) == (1 if mode == 'guarded' else 0)
        if mode == 'guarded':
            assert not any(e['kind']=='focus_entered' and e['target_id']==r['new_id'] for e in t)
    summary['runs'].append({'mode': mode, 'command': [binary, *args], 'exit_code': p.returncode, 'checks': 'passed'})
(OUT/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps(summary, indent=2))
