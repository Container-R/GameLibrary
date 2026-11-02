"""Two fresh-copy native invocations. Execution requires separate authorization."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys

from checker import check, exact

BUILD = ['c++', '-std=c++17', '-O0', '-g0', '-Wall', '-Wextra', '-Wpedantic', '-Werror', '-I', 'source', 'fixture.cpp', '-o', 'out/fixture']
RUN = ['./out/fixture']

class Stop(Exception):
    pass

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def manifest_read(base):
    from checker import decode
    path = base / 'INPUT-MANIFEST.json'
    data = decode(path.read_text(encoding='utf-8'))
    if type(data) is not dict or list(data) != ['schema', 'files'] or type(data['schema']) is not int or data['schema'] != 1:
        raise Stop('manifest_schema')
    if type(data['files']) is not dict or set(data['files']) != {'PROTOCOL-v2.md', 'fixture.cpp', 'runner.py', 'checker.py', 'independent-oracle.json', 'PROTOCOL-REVIEW.md', 'source/entt.hpp', 'source/LICENSE', 'test_runner_cleanup.py'}:
        raise Stop('manifest_files')
    for name, value in data['files'].items():
        if type(value) is not str or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            raise Stop('manifest_hash')
        if (base / name).is_symlink():
            raise Stop('input_symlink')
    return data, digest(path)

def snapshot(base, names):
    return {name: digest(base / name) for name in names}

def cleanup_group(proc, event):
    """Always address the owned group, even if its leader already exited."""
    ok = True
    try:
        os.killpg(proc.pid, signal.SIGKILL)
        event['group_cleanup'] = 'SIGNAL_SENT'
    except ProcessLookupError:
        event['group_cleanup'] = 'NO_GROUP'
    except BaseException:
        event['group_cleanup'] = 'FAILED'
        ok = False
    # A group signal and reaping its leader are separate bounded operations.
    try:
        proc.wait(timeout=10)
        event['leader_cleanup'] = 'REAPED'
    except BaseException:
        event['leader_cleanup'] = 'FAILED'
        ok = False
    return ok

def process(argv, cwd, label, seconds, receipt):
    stdout = cwd / (label + '.stdout')
    stderr = cwd / (label + '.stderr')
    event = {'copy': cwd.name, 'phase': label, 'argv': argv, 'status': 'NOT_STARTED', 'returncode': None, 'timeout': False}
    receipt['processes'].append(event)
    env = {'PATH': os.defpath, 'LANG': 'C', 'LC_ALL': 'C', 'TMPDIR': str(cwd / 'tmp')}
    proc = None
    cleanup_done = False
    try:
        with stdout.open('xb') as out, stderr.open('xb') as err:
            proc = subprocess.Popen(argv, cwd=cwd, env=env, stdout=out, stderr=err, start_new_session=True)
            event['status'] = 'STARTED'
            try:
                event['returncode'] = proc.wait(timeout=seconds)
                event['status'] = 'RETURNED'
            except subprocess.TimeoutExpired:
                event['timeout'] = True
                event['status'] = 'TIMED_OUT'
                raise Stop(label + '_timeout')
            out.flush()
            err.flush()
        event['stdout_sha256'] = digest(stdout)
        event['stderr_sha256'] = digest(stderr)
        if event['returncode'] != 0:
            raise Stop(label + '_return')
        if stderr.stat().st_size != 0 or (label == 'build' and stdout.stat().st_size != 0):
            raise Stop(label + '_diagnostics')
        if stdout.stat().st_size > 65536:
            raise Stop(label + '_output_size')
        raw = stdout.read_bytes()
        # Close owned groups even on a successful leader exit, before callers
        # can fail their content or binding checks. No poll-based shortcut.
        cleanup_done = True
        if not cleanup_group(proc, event):
            raise Stop(label + '_cleanup')
        return raw
    except BaseException:
        if proc is not None and not cleanup_done:
            cleanup_group(proc, event)  # helper cannot replace the first error
        if proc is None:
            event['status'] = 'LAUNCH_FAILED'
        raise

def publish_receipt(root, receipt):
    """Only receipt.json is authoritative; pending files never are results.

    This is atomic publication on the same directory, not a durability claim.
    """
    pending = root / 'receipt.pending.json'
    final = root / 'receipt.json'
    if os.path.lexists(final):
        raise Stop('receipt_already_exists')
    with pending.open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    # Last publication action: a normally closed pending file becomes official.
    os.replace(pending, final)

def main():
    if len(sys.argv) != 2:
        raise SystemExit('usage: runner.py NEW_OUTPUT_DIRECTORY')
    base = Path(__file__).resolve().parent
    root = Path(sys.argv[1]).absolute()
    # Reject every pre-existing path, including dangling symlinks. No reuse.
    if os.path.lexists(root):
        raise SystemExit('output_already_exists')
    if not root.parent.is_dir() or root.parent.is_symlink():
        raise SystemExit('output_parent_invalid')
    root.mkdir()
    receipt = {'schema': 1, 'status': 'INCOMPLETE', 'error': None, 'processes': [], 'copies': []}
    original = None
    manifest_hash = None
    try:
        original, manifest_hash = manifest_read(base)
        receipt['manifest_sha256'] = manifest_hash
        receipt['input_before'] = snapshot(base, original['files'])
        if not exact(receipt['input_before'], original['files']):
            raise Stop('input_before_mismatch')
        observed = []
        for name in ('repeat-1', 'repeat-2'):
            work = root / name
            work.mkdir()
            (work / 'source').mkdir()
            (work / 'out').mkdir()
            (work / 'tmp').mkdir()
            copied = ['fixture.cpp', 'source/entt.hpp', 'source/LICENSE']
            for item in copied:
                shutil.copyfile(base / item, work / item)
            copy = {'name': name, 'before': snapshot(work, copied)}
            receipt['copies'].append(copy)
            if any(copy['before'][item] != original['files'][item] for item in copied):
                raise Stop('copy_before_mismatch')
            process(BUILD, work, 'build', 120, receipt)
            copy['artifact_sha256'] = digest(work / 'out/fixture')
            raw = process(RUN, work, 'native', 10, receipt)
            observed.append(check(raw, base / 'independent-oracle.json'))
            copy['after'] = snapshot(work, copied)
            copy['artifact_after_sha256'] = digest(work / 'out/fixture')
            if not exact(copy['before'], copy['after']) or copy['artifact_sha256'] != copy['artifact_after_sha256']:
                raise Stop('copy_after_mismatch')
            copy['content_check'] = 'PASS'
        if not exact(observed[0], observed[1]):
            raise Stop('repeat_difference')
        receipt['input_after'] = snapshot(base, original['files'])
        receipt['manifest_after_sha256'] = digest(base / 'INPUT-MANIFEST.json')
        if not exact(receipt['input_after'], original['files']) or receipt['manifest_after_sha256'] != manifest_hash:
            raise Stop('input_after_mismatch')
        receipt['status'] = 'PASS'
    except BaseException as exc:
        receipt['status'] = 'FAIL'
        receipt['error'] = str(exc) if type(exc) is Stop else type(exc).__name__
        # Preserve the first error; post-failure collection is best effort only.
        if original is not None:
            try:
                receipt['input_after_failure'] = snapshot(base, original['files'])
                receipt['manifest_after_failure_sha256'] = digest(base / 'INPUT-MANIFEST.json')
            except BaseException:
                receipt['post_failure_collection'] = 'UNAVAILABLE'
        for copy in receipt['copies']:
            try:
                work = root / copy['name']
                copy['after_failure'] = snapshot(work, copy['before'])
            except BaseException:
                copy['after_failure_collection'] = 'UNAVAILABLE'
    # No overall PASS exists until both repeats and all post-bindings passed.
    try:
        publish_receipt(root, receipt)
    except BaseException:
        receipt['status'] = 'FAIL'
        if receipt['error'] is None:
            receipt['error'] = 'receipt_write_failed'
        receipt['receipt_write'] = 'FAILED'
        # Best-effort safe fallback; no local paths or exception messages.
        sys.stderr.write(json.dumps(receipt, ensure_ascii=False) + '\n')
        return 1
    return 0 if receipt['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
