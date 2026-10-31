"""Two fresh processes; bounded local probe. Cleanup precedes optimization/engine guards."""
from pathlib import Path
import sys
import json
import hashlib
import os
import platform
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
(OUT / 'summary.json').unlink(missing_ok=True)
INVOCATION = str(uuid.uuid4())
receipt = {'invocation_id': INVOCATION, 'started_utc': datetime.now(timezone.utc).isoformat(),
           'optimization': sys.flags.optimize, 'status': 'STARTED', 'engine_spawn_attempts': 0}

def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n')

write('invocation.json', receipt)

def check(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reject_duplicates(pairs):
    d = {}
    for k, v in pairs:
        check(k not in d, 'duplicate JSON key')
        d[k] = v
    return d


def parse(line):
    return json.loads(line, object_pairs_hook=reject_duplicates,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def main():
    check(not sys.flags.optimize, 'Refusing optimized mode; stale success already removed')
    check(len(sys.argv) == 1, 'No runner arguments supported')
    check(sha(ROOT / 'contract.json') == 'f70e399b8aac89c6323ae29b78ebef281f0bf393f8fbe3fe727d700e216d1e50', 'frozen contract changed')
    engine = Path(os.environ.get('GODOT_BIN', '/usr/local/bin/godot')).resolve()
    check(engine.is_file(), 'engine does not exist')
    binary_sha = sha(engine)
    contract = parse((ROOT / 'contract.json').read_text())
    names = ('project.godot', 'main.gd', 'gradient.tres')
    sources = {n: sha(ROOT / n) for n in (*names, 'run.py', 'contract.json')}
    runs = []
    for case in contract['cases']:
        label = case['name']
        with tempfile.TemporaryDirectory(prefix='resource-broker-') as temp:
            tmp = Path(temp)
            project = tmp / 'project'; project.mkdir()
            for name in names:
                (project / name).write_bytes((ROOT / name).read_bytes())
            before_disk = {n: sha(project / n) for n in names}
            env = dict(os.environ, GODOT_SILENCE_ROOT_WARNING='1', HOME=str(tmp / 'home'),
                       XDG_CACHE_HOME=str(tmp / 'cache'), XDG_CONFIG_HOME=str(tmp / 'config'), XDG_DATA_HOME=str(tmp / 'data'))
            for key in ('HOME', 'XDG_CACHE_HOME', 'XDG_CONFIG_HOME', 'XDG_DATA_HOME'):
                Path(env[key]).mkdir()
            cmd = [str(engine), '--headless', '--path', str(project), '--script', 'res://main.gd', '--', label]
            command = {'command': cmd, 'invocation_id': INVOCATION, 'timeout_seconds': 20,
                       'isolation': 'fresh temporary project and HOME/XDG per case'}
            write(label + '.command.json', command)
            receipt['engine_spawn_attempts'] += 1; write('invocation.json', receipt)
            try:
                proc = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=20)
            except subprocess.TimeoutExpired as exc:
                (OUT / (label + '.stdout.txt')).write_bytes(exc.stdout or b'')
                (OUT / (label + '.stderr.txt')).write_bytes(exc.stderr or b'')
                command['timed_out'] = True; write(label + '.command.json', command)
                raise
            (OUT / (label + '.stdout.txt')).write_text(proc.stdout)
            (OUT / (label + '.stderr.txt')).write_text(proc.stderr)
            command['returncode'] = proc.returncode; write(label + '.command.json', command)
            after_disk = {n: sha(project / n) for n in names}
            write(label + '.disk.json', {'before': before_disk, 'after': after_disk})
            check(proc.returncode == 0 and not proc.stderr.strip(), label + ' engine rejected or stderr')
            calls = [parse(s.split('=', 1)[1]) for s in proc.stdout.splitlines() if s.startswith('CALL_JSON=')]
            records = [parse(s.split('=', 1)[1]) for s in proc.stdout.splitlines() if s.startswith('RESULT_JSON=')]
            check(len(records) == 1, label + ' result count')
            r = records[0]
            check(calls == r['trace'], 'raw calls differ from result trace')
            check(r['case'] == label and r['first_mode'] == case['first_mode'] and r['second_mode'] == case['second_mode'], 'case/modes')
            check(r['request_count'] == r['get_count'] == 2 and r['use_sub_threads'] is False, 'actual call counters')
            polls = [c for c in calls if c.get('stage') == 'first-poll']
            check(polls and polls[-1]['value'] == 3 and all(c['value'] == 1 for c in polls[:-1]), 'first poll sequence')
            check(r['frames'] == len(polls) and 1 <= r['frames'] <= 600, 'frame record')
            expected_calls = [
                {'op': 'request', 'number': 1, 'mode': case['first_mode'], 'return': 0},
                *polls,
                {'op': 'request', 'number': 2, 'mode': case['second_mode'], 'return': 0},
                {'op': 'status', 'stage': 'after-second-request', 'value': 3},
                {'op': 'get', 'number': 1, 'resource': r['result1']},
                {'op': 'status', 'stage': 'after-first-get', 'value': 3},
                {'op': 'get', 'number': 2, 'resource': r['result2']},
                {'op': 'status', 'stage': 'after-second-get', 'value': 0}]
            check(calls == expected_calls and r['final_status'] == 0, 'call order/status/returns')
            for descriptor in (r['initial'], r['active_after'], r['result1'], r['result2']):
                check(descriptor['type'] == 'Gradient' and type(descriptor['id']) is int and descriptor['id'] != 0, 'valid exact resource ID/type')
                check(descriptor['colors'] == contract['colors'] and descriptor['offsets'] == contract['offsets'], 'retained colors/offsets')
            check(r['initial'] == r['active_after'], 'active state/identity changed')
            check(r['result1'] == r['result2'], 'collections not same identity/content')
            check((r['result1']['id'] == r['initial']['id']) is case['result_same_as_active'], 'first policy alias mismatch')
            check(before_disk == after_disk == {n: sources[n] for n in names}, 'disk inputs changed')
            check(tuple(r['version'].get(k) for k in ('major', 'minor', 'patch')) == (4, 6, 3), 'version family')
            write(label + '.json', r)
            runs.append(r)
    check(sha(engine) == binary_sha, 'engine bytes changed during run')
    check(all(sha(ROOT / n) == h for n, h in sources.items()), 'source changed during run')
    check(runs[0]['version'] == runs[1]['version'], 'different engine identities')
    summary = {'status': 'PASS', 'invocation_id': INVOCATION, 'engine_processes': 2,
               'engine_path': str(engine), 'binary_sha256': binary_sha, 'version': runs[0]['version'],
               'source_sha256': sources, 'platform': platform.platform(), 'python': platform.python_version(),
               'cases': [r['case'] for r in runs], 'provenance': 'self-report; official source correspondence not authenticated'}
    receipt['status'] = 'PASS'; write('invocation.json', receipt)
    write('summary.json', summary)
    print('PASS: two fresh processes; request-policy/identity/status/color/disk oracles passed')


if __name__ == '__main__':
    try:
        main()
    except BaseException as exc:
        receipt['status'] = 'FAILED'; receipt['error'] = type(exc).__name__ + ': ' + str(exc)
        write('invocation.json', receipt)
        raise
