"""Review draft: owns one fresh run directory and at most one SQLite child."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('local_isolation', HERE / 'isolation.py')
isolation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(isolation)
FILES = ('PROTOCOL.md', 'runner.py', 'launcher.py', 'isolation.py')


def hashes():
    return {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in FILES}


def check_events(events):
    def need(ok):
        if not ok:
            raise ValueError('trace_contract')
    for i, e in enumerate(events, 1):
        need(set(e) == {'seq', 'event', 'data'} and type(e['seq']) is int and e['seq'] == i)
    names = [e['event'] for e in events]
    prefix = ['begin', 'settings', 'baseline', 'committed', 'main_copy',
              'plain_read', 'closed', 'backup_attempt']
    suffix = ['backup_return', 'closed', 'backup_read', 'closed',
              'source_final', 'closed', 'success']
    need(names[:8] == prefix and names[-7:] == suffix)
    progress = events[8:-7]
    need(1 <= len(progress) <= 16 and all(e['event'] == 'backup_progress' for e in progress))
    for i, e in enumerate(progress):
        d = e['data']
        need(all(type(d[k]) is int for k in ('status', 'remaining', 'total')))
        need(d['status'] == (101 if i == len(progress)-1 else 0))
        need(0 <= d['remaining'] <= d['total'])
    need(progress[-1]['data']['remaining'] == 0)
    d = {e['event']: e['data'] for e in events if e['event'] != 'closed'}
    need(d['settings'] == {'journal_mode': [['wal']], 'wal_autocheckpoint': [[0]],
                          'isolation_level': None, 'autocommit': -1, 'busy_timeout': 0})
    baseline = d['baseline']
    cp = baseline['checkpoint']
    need(len(cp) == 1 and len(cp[0]) == 3 and all(type(v) is int for v in cp[0]))
    need(cp[0][0] == 0 and cp[0][1] == cp[0][2] and cp[0][1] >= 0)
    need(baseline['rows'] == [] and type(baseline['wal_bytes']) is int and baseline['wal_bytes'] == 0)
    h = baseline['main_sha256']
    need(type(h) is str and len(h) == 64 and all(c in '0123456789abcdef' for c in h))
    need(d['committed']['main_sha256'] == h == d['main_copy']['sha256'] == d['source_final']['main_sha256'])
    need(d['committed']['in_transaction'] is False and type(d['committed']['wal_bytes']) is int and d['committed']['wal_bytes'] > 0)
    need(d['main_copy']['path'] == 'plain/save.db' and d['plain_read']['rows'] == [])
    for name in ('committed', 'backup_read', 'source_final'):
        value = d[name]['rows']
        need(value == [[1, 7]] and all(type(v) is int for v in value[0]))
    need(d['backup_attempt'] == {'pages': 1, 'name': 'main', 'sleep': 0.0})
    need(type(d['backup_return']['progress_calls']) is int and d['backup_return']['progress_calls'] == len(progress))
    need([e['data'] for e in events if e['event'] == 'closed'] ==
         [{'role': r} for r in ('plain', 'backup_writer', 'backup_reader', 'remaining')])
    need(d['success'] == {'plain_rows': [], 'backup_rows': [[1, 7]], 'source_rows': [[1, 7]]})


def main():
    # Caller provides an absolute, nonexistent directory; never reuse old results.
    root = Path(sys.argv[1])
    if not root.is_absolute() or '..' in root.parts or root == Path(root.anchor):
        raise ValueError('invalid root')
    for p in (root, *root.parents):
        if p.is_symlink():
            raise ValueError('symlink component')
    root.mkdir(exist_ok=False)
    receipt = {'status': 'FAIL', 'child_count': 0, 'timeout_seconds': 15}
    try:
        env, _ = isolation.prepare_environment(dict(os.environ), root)
        receipt['environment'] = {k: k for k in isolation.KEYS}
        receipt['source_before'] = hashes()
        isolation.validate_environment(env, root)
        # Regular files retain partial output even if the child is terminated.
        with (root / 'stdout.jsonl').open('xb') as out, (root / 'stderr.bin').open('xb') as err:
            child = subprocess.Popen([sys.executable, '-I', '-B', str(HERE / 'runner.py')],
                                     cwd=root, env=env, stdout=out, stderr=err)
            receipt['child_count'] = 1
            receipt['termination_confirmed'] = False
            try:
                receipt['returncode'] = child.wait(timeout=15)
                receipt['termination_confirmed'] = True
            except BaseException:
                if child.poll() is None:
                    child.kill()
                receipt['returncode'] = child.wait(timeout=5)
                receipt['termination_confirmed'] = True
                raise
        receipt['source_after'] = hashes()
        if receipt['source_before'] != receipt['source_after']:
            raise RuntimeError('source_changed')
        raw = (root / 'stdout.jsonl').read_bytes()
        stderr = (root / 'stderr.bin').read_bytes()
        receipt['stdout_sha256'] = hashlib.sha256(raw).hexdigest()
        receipt['stderr_sha256'] = hashlib.sha256(stderr).hexdigest()
        events = [json.loads(line) for line in raw.splitlines()]
        if receipt['returncode'] != 0 or stderr or not events or events[-1]['event'] != 'success':
            raise RuntimeError('child_not_accepted')
        check_events(events)
        receipt['status'] = 'PASS'
    except BaseException as exc:
        receipt['failure_category'] = type(exc).__name__
        (root / 'private-launcher-error.txt').write_text(traceback.format_exc(), encoding='utf-8')
    finally:
        try:
            receipt['source_after'] = hashes()
            if receipt.get('source_before') != receipt['source_after']:
                receipt['status'] = 'FAIL'
                receipt['final_source_mismatch'] = True
        except Exception:
            receipt['source_after_unavailable'] = True
            receipt['status'] = 'FAIL'
        for name in ('stdout.jsonl', 'stderr.bin'):
            if (root / name).is_file():
                receipt[name + '_sha256'] = hashlib.sha256((root / name).read_bytes()).hexdigest()
        (root / 'receipt.pending').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        (root / 'receipt.pending').replace(root / 'receipt.json')
    print(json.dumps({'status': receipt['status'], 'receipt': 'receipt.json'}))
    return 0 if receipt['status'] == 'PASS' else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        # Startup before ownership: do not write into a rejected/reused directory.
        print(json.dumps({'status': 'FAIL', 'category': type(exc).__name__}))
        sys.exit(1)
