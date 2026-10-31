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
           'optimization': sys.flags.optimize, 'status': 'STARTED', 'engine_processes_started': 0}

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
    check(sha(ROOT / 'contract.json') == '267f450ad57c6a802346d0b9c7ac9d79e240871a64a2e6566f62e3810f6bd941', 'frozen contract changed')
    engine = Path(os.environ.get('GODOT_BIN', '/usr/local/bin/godot')).resolve()
    check(engine.is_file(), 'engine does not exist')
    binary_sha = sha(engine)
    contract = parse((ROOT / 'contract.json').read_text())
    names = ('project.godot', 'main.gd', 'gradient.tres', 'candidate.tres')
    sources = {n: sha(ROOT / n) for n in (*names, 'run.py', 'contract.json')}
    runs = []
    for case in contract['cases']:
        label = case['name']
        with tempfile.TemporaryDirectory(prefix='resource-candidate-') as temp:
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
            receipt['engine_processes_started'] += 1; write('invocation.json', receipt)
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
            requests = [parse(s.split('=', 1)[1]) for s in proc.stdout.splitlines() if s.startswith('REQUEST_JSON=')]
            records = [parse(s.split('=', 1)[1]) for s in proc.stdout.splitlines() if s.startswith('RESULT_JSON=')]
            check(len(requests) == len(records) == 1, label + ' record count')
            r = records[0]; q = requests[0]
            check(q == {'case': label, 'mode': case['mode'], 'return': 0, 'initial': r['initial']}, 'request mismatch')
            check(r['case'] == label and r['mode'] == case['mode'], 'case/mode')
            check(r['request_count'] == r['get_count'] == 1 and r['use_sub_threads'] is False, 'request policy')
            check(r['statuses'] and r['statuses'][-1] == 3 and all(s == 1 for s in r['statuses'][:-1]), 'status sequence')
            check(r['frames'] == len(r['statuses']) and r['frames'] <= 600, 'frame record')
            b, a, initial = r['before'], r['after'], r['initial']
            red, blue = [1, 0, 0, 1], [0, 0, 1, 1]
            check(initial['color'] == b['active_color'] == b['candidate_color'] == red, 'initial color')
            check(initial['point_count'] == 2, 'initial graph')
            for key in ('active_root_id', 'candidate_root_id', 'active_gradient_id', 'candidate_gradient_id'):
                check(type(b[key]) is int and b[key] > 0 and b[key] == a[key], 'identity changed: ' + key)
            check(initial['root_id'] == r['initial_active_id'] == b['active_root_id'], 'active root replaced')
            check(initial['gradient_id'] == b['active_gradient_id'], 'active dependency replaced')
            check((b['active_root_id'] == b['candidate_root_id']) is case['root_same'], 'root alias expectation')
            check((b['active_gradient_id'] == b['candidate_gradient_id']) is case['dependency_same'], 'dependency alias expectation')
            check(a['active_color'] == a['held_gradient_color'] == case['active_after'] and a['candidate_color'] == blue, 'mutation outcome')
            check(before_disk == after_disk == {n: sources[n] for n in names}, 'disk inputs changed')
            check(r['version']['string'] == '4.6.3-stable (official)' or r['version'].get('major') == 4, 'version family')
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
    print('PASS: two fresh processes; alias/color/disk oracles passed')


if __name__ == '__main__':
    try:
        main()
    except BaseException as exc:
        receipt['status'] = 'FAILED'; receipt['error'] = type(exc).__name__ + ': ' + str(exc)
        write('invocation.json', receipt)
        raise
