#!/usr/bin/env python3
"""Preparation artifact: invoke only after independent review and authorization."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
FLAGS = ['-std=c99', '-O0', '-Wall', '-Wextra', '-pedantic']
EXPECTED = ('dense.json parse=success load=success validate=success count=4 values=[10,7,30,9] read_float=false\n'
            'zero.json parse=success load=success validate=success count=4 values=[0,7,0,9] read_float=false\n'
            'PASS two_fixtures_only\n')

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    if sys.flags.optimize or len(sys.argv) != 2:
        raise RuntimeError('require_nonoptimized_python_and_one_new_run_directory')
    # mkdir(exist_ok=False) prevents old PASS, logs or binary from being reused.
    target = Path(sys.argv[1])
    if not target.parent.is_dir() or target.exists() or target.is_symlink():
        raise RuntimeError('run_directory_must_be_new_with_existing_parent')
    target.mkdir(mode=0o700)
    target = target.resolve()
    raw = target / 'private-raw'; raw.mkdir(mode=0o700)
    public = target / 'public-safe'; public.mkdir(mode=0o700)
    work = raw / 'work'; work.mkdir()
    env = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'LANG': 'C', 'TZ': 'UTC'}
    for key, sub in [('HOME','home'), ('TMPDIR','tmp'), ('TMP','tmp2'), ('TEMP','tmp3'),
                     ('XDG_CONFIG_HOME','config'), ('XDG_CACHE_HOME','cache'),
                     ('XDG_DATA_HOME','data'), ('XDG_STATE_HOME','state'), ('XDG_RUNTIME_DIR','runtime')]:
        p = raw / sub; p.mkdir(mode=0o700); env[key] = str(p)
    report = {'status': 'not_started', 'source_commit': '360db1a95480fe102ae9c69b27c5d101167ff5ba',
              'compile_options': FLAGS, 'cases': 2, 'stage_results': {}}
    try:
        manifest = json.loads((ROOT / 'manifest.json').read_text())
        required = {'cgltf.h','LICENSE','harness.c','dense.json','zero.json','fixture.hex','protocol.md','run.py'}
        if set(manifest['sha256']) != required:
            raise RuntimeError('manifest_file_set')
        for name, expected in manifest['sha256'].items():
            if digest(ROOT/name) != expected:
                raise RuntimeError('input_hash_mismatch')
        report['input_sha256'] = manifest['sha256']
        report['manifest_sha256'] = digest(ROOT/'manifest.json')
        for name in ['cgltf.h','LICENSE','harness.c','dense.json','zero.json']:
            shutil.copyfile(ROOT/name, work/name)
        # Explicit compiler, no shell, no inherited compiler flags or loader env.
        compiler = '/usr/bin/cc'
        if not os.path.isfile(compiler) or not os.access(compiler, os.X_OK):
            raise RuntimeError('compiler_unavailable_no_install')
        for phase, argv, timeout in [
            ('compile', [compiler, *FLAGS, 'harness.c', '-o', 'probe'], 30),
            ('run', ['./probe'], 5)]:
            with (raw/(phase+'.stdout')).open('wb') as out, (raw/(phase+'.stderr')).open('wb') as err:
                try:
                    proc = subprocess.Popen(argv, cwd=work, env=env, stdout=out, stderr=err,
                                            stdin=subprocess.DEVNULL, start_new_session=True)
                    proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    # Kill the compiler process group too, not only its driver.
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
                    report['stage_results'][phase] = {'status':'timeout', 'limit_seconds':timeout,
                                                      'exit_code_after_kill':proc.returncode}
                    raise RuntimeError('stage_timeout')
            report['stage_results'][phase] = {'status':'exited', 'exit_code':proc.returncode}
            if proc.returncode != 0:
                raise RuntimeError('stage_nonzero_exit')
        for name, expected in manifest['sha256'].items():
            if digest(ROOT/name) != expected:
                raise RuntimeError('input_changed_during_run')
        for name in ['cgltf.h','LICENSE','harness.c','dense.json','zero.json']:
            if digest(work/name) != manifest['sha256'][name]:
                raise RuntimeError('work_input_changed_during_run')
        output = (raw/'run.stdout').read_bytes()
        if output != EXPECTED.encode('ascii') or (raw/'run.stderr').read_bytes():
            raise RuntimeError('output_or_stderr_mismatch')
        # Only exact allowlisted technical output crosses into public-safe.
        (public/'output.txt').write_bytes(output)
        report['output_sha256'] = hashlib.sha256(output).hexdigest()
        report['status'] = 'PASS_two_fixtures_only'
    except Exception as exc:
        report['status'] = 'FAIL'
        # Raw exceptions can contain host paths; retain locally, never publish them.
        (raw/'runner-error.txt').write_text(repr(exc)+'\n')
        report['failure'] = 'see_local_raw_record_not_for_publication'
    (public/'result.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print(report['status'])
    return 0 if report['status'] == 'PASS_two_fixtures_only' else 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        # Pre-directory failures deliberately avoid leaking a supplied private path.
        print('FAIL_before_run_record', file=sys.stderr)
        sys.exit(2)
