"""Independent review required before execution."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys

INPUTS = ('PROTOCOL.md', 'driver.py', 'runner.py', 'expected.json')
ENV_DIRS = ('HOME', 'XDG_CACHE_HOME', 'XDG_CONFIG_HOME', 'XDG_DATA_HOME',
            'XDG_STATE_HOME', 'XDG_RUNTIME_DIR', 'XDG_CONFIG_DIRS',
            'XDG_DATA_DIRS', 'TMPDIR', 'TMP', 'TEMP')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def reject_links(path):
    for part in (path, *path.parents):
        if part.is_symlink():
            raise RuntimeError('symlink path rejected')

def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError('duplicate JSON key')
        obj[key] = value
    return obj

def parse_json(data):
    def reject_constant(value):
        raise ValueError('nonfinite JSON constant')
    return json.loads(data, object_pairs_hook=unique_object,
                      parse_constant=reject_constant)

def exact_equal(left, right):
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(exact_equal(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(exact_equal(a, b) for a, b in zip(left, right))
    return left == right

def atomic_write(path, data):
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('xb') as f:
        f.write(data)
    os.replace(temporary, path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-name', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,39}', args.run_name):
        raise RuntimeError('invalid run name')
    if sys.version_info < (3, 12):
        raise RuntimeError('requires existing Python 3.12 or newer; do not install a replacement')
    base = Path(__file__).absolute().parent
    reject_links(base)
    for name in (*INPUTS, 'manifest.json'):
        path = base / name
        reject_links(path)
        if not path.is_file():
            raise RuntimeError('missing regular input')
    manifest_bytes = (base / 'manifest.json').read_bytes()
    manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
    manifest = parse_json(manifest_bytes)
    hashes = manifest['inputs_sha256']
    if set(hashes) != set(INPUTS):
        raise RuntimeError('unexpected input manifest')
    for name in INPUTS:
        if digest(base / name) != hashes[name]:
            raise RuntimeError('input digest mismatch')
    expected = parse_json((base / 'expected.json').read_bytes())
    if set(expected) != {'checkpoints'}:
        raise RuntimeError('unexpected oracle schema')
    runs = base / 'local-runs'
    reject_links(runs)
    runs.mkdir(mode=0o700, exist_ok=True)
    if not runs.is_dir():
        raise RuntimeError('invalid runs directory')
    root = runs / args.run_name
    # exist_ok=False rejects any prior run, including dangling links.
    root.mkdir(mode=0o700)
    os.chmod(root, 0o700)
    work = root / 'work'
    logs = root / 'private-logs'
    work.mkdir(mode=0o700)
    logs.mkdir(mode=0o700)
    for name in INPUTS:
        data = (base / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != hashes[name]:
            raise RuntimeError('input changed before copy')
        with (work / name).open('xb') as f:
            f.write(data)
        if digest(work / name) != hashes[name]:
            raise RuntimeError('copied input digest mismatch')
    env = {'LANG': 'C', 'LC_ALL': 'C', 'TZ': 'UTC'}
    for key in ENV_DIRS:
        folder = root / ('env-' + key.lower())
        folder.mkdir(mode=0o700)
        os.chmod(folder, 0o700)
        # Verify writable destinations before the first child process.
        probe = folder / 'write-check'
        with probe.open('xb') as f:
            f.write(b'checked')
        if probe.read_bytes() != b'checked':
            raise RuntimeError('environment write check failed')
        probe.unlink()
        env[key] = str(folder)
    result = {'status': 'not_accepted', 'inputs_sha256': hashes,
              'manifest_sha256': manifest_hash,
              'copied_inputs_verified': True, 'environment_directory_count': 11,
              'timeout_seconds': 15, 'execution_scope': 'independent_memory_replace_upsert_cascade_SQL',
              'returncode': None, 'stderr_empty': None, 'failure_category': None,
              'cleanup_failures': [], 'post_execution_inputs_verified': False,
              'post_kill_wait_seconds': 2, 'child_exit_confirmed': False}
    # Raw stdout/stderr stay local even on failure; no traceback is copied to result.
    with (logs / 'stdout.txt').open('xb') as out, (logs / 'stderr.txt').open('xb') as err:
        proc = None
        reaped = False
        try:
            proc = subprocess.Popen([sys.executable, '-I', '-E', '-B', 'driver.py'],
                                    cwd=work, env=env, stdin=subprocess.DEVNULL,
                                    stdout=out, stderr=err, start_new_session=True)
        except OSError:
            result['failure_category'] = 'process_launch_error'
        if proc is not None:
            try:
                proc.wait(timeout=15)
                reaped = True
            except subprocess.TimeoutExpired:
                result['failure_category'] = 'timeout'
            except OSError:
                result['failure_category'] = 'process_wait_error'
            if not reaped:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                except OSError:
                    result['cleanup_failures'].append('process_group_kill_error')
                try:
                    proc.wait(timeout=2)
                    reaped = True
                except subprocess.TimeoutExpired:
                    result['cleanup_failures'].append('post_kill_wait_timeout')
                except OSError:
                    result['cleanup_failures'].append('post_kill_wait_error')
            result['returncode'] = proc.returncode
            result['child_exit_confirmed'] = reaped
    try:
        for name in INPUTS:
            reject_links(base / name)
            reject_links(work / name)
            if digest(base / name) != hashes[name] or digest(work / name) != hashes[name]:
                raise ValueError('input changed during execution')
        reject_links(base / 'manifest.json')
        if digest(base / 'manifest.json') != manifest_hash:
            raise ValueError('manifest changed during execution')
        result['post_execution_inputs_verified'] = True
    except (OSError, ValueError, RuntimeError):
        if result['failure_category'] is None:
            result['failure_category'] = 'post_execution_input_mismatch'
        else:
            result['cleanup_failures'].append('post_execution_input_mismatch')
    raw = (logs / 'stdout.txt').read_bytes()
    result['stderr_empty'] = (logs / 'stderr.txt').stat().st_size == 0
    if result['failure_category'] is None:
        if result['cleanup_failures'] or not result['child_exit_confirmed']:
            result['failure_category'] = 'process_cleanup_failure'
        elif result['returncode'] != 0:
            result['failure_category'] = 'driver_error'
        elif not result['stderr_empty']:
            result['failure_category'] = 'unexpected_stderr'
        else:
            try:
                observed = parse_json(raw)
                if type(observed) is not dict:
                    raise ValueError('schema')
                if set(observed) != {'python_version', 'sqlite_version', 'checkpoints'}:
                    raise ValueError('schema')
                if not isinstance(observed['python_version'], str) or not re.fullmatch(r'\d+\.\d+\.\d+', observed['python_version']):
                    raise ValueError('python version')
                if tuple(map(int, observed['python_version'].split('.'))) < (3, 12, 0):
                    raise ValueError('python version unsupported')
                if not isinstance(observed['sqlite_version'], str) or not re.fullmatch(r'\d+\.\d+\.\d+', observed['sqlite_version']):
                    raise ValueError('sqlite version')
                if tuple(map(int, observed['sqlite_version'].split('.'))) < (3, 24, 0):
                    raise ValueError('sqlite version unsupported')
                if not exact_equal(observed['checkpoints'], expected['checkpoints']):
                    raise ValueError('oracle')
            except (ValueError, TypeError, KeyError):
                result['failure_category'] = 'output_oracle_mismatch'
            else:
                result['status'] = 'PASS'
                result['python_version'] = observed['python_version']
                result['sqlite_version'] = observed['sqlite_version']
                result['output_sha256'] = hashlib.sha256(raw).hexdigest()
                atomic_write(root / 'output.json', raw)
    atomic_write(root / 'result.json', (json.dumps(result, sort_keys=True, indent=2) + '\n').encode('utf-8'))
    return 0 if result['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
