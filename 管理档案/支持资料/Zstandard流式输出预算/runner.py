#!/usr/bin/env python3
"""Preparation only until separately approved. No source download or installation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess

INPUTS = {
    'PROTOCOL.md', 'harness.c', 'runner.py',
    'fixtures/r32.hex', 'fixtures/r33.hex', 'fixtures/r32-truncated.hex',
    'vendor/zstddeclib.c', 'vendor/LICENSE', 'vendor/source-origin.json',
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def bounded(command, cwd, env, seconds, out, err):
    with out.open('xb') as stdout, err.open('xb') as stderr:
        proc = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            code = proc.wait(timeout=seconds)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
            return {'category': 'timeout', 'exit_code': None}
    return {'category': 'ok' if code == 0 else 'nonzero', 'exit_code': code}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-name', required=True,
                        help='New simple directory name under local-runs; existing names refused')
    args = parser.parse_args()
    if not args.run_name or len(args.run_name)>64 or any(
            c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in args.run_name):
        raise ValueError('invalid run name')
    base = Path(__file__).resolve().parent
    manifest_path = base/'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('status') != 'PREPARED_NOT_EXECUTED':
        raise ValueError('manifest not frozen for preparation')
    inputs = manifest.get('inputs', {})
    if set(inputs) != INPUTS:
        raise ValueError('input allowlist mismatch')
    for relative, expected in inputs.items():
        p=base/relative
        if p.is_symlink() or not p.is_file() or digest(p)!=expected:
            raise ValueError('input identity mismatch')
    runs=base/'local-runs'
    if runs.is_symlink():
        raise ValueError('run root must not be a symlink')
    runs.mkdir(exist_ok=True)
    root=runs/args.run_name
    root.mkdir()  # intentionally fails if the run name already exists
    work=root/'work'; work.mkdir()
    private=root/'private-logs'; private.mkdir()
    for relative in sorted(INPUTS):
        dst=work/relative; dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(base/relative,dst)
    for relative, expected in inputs.items():
        if digest(work/relative) != expected:
            raise ValueError('copied input identity mismatch')
    for name in ['home','tmp','xdg-config','xdg-cache','xdg-data','xdg-state','xdg-runtime']:
        (root/name).mkdir(mode=0o700)
    (root/'xdg-runtime').chmod(0o700)
    env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C',
         'HOME':str(root/'home'),'TMPDIR':str(root/'tmp'),
         'XDG_CONFIG_HOME':str(root/'xdg-config'),
         'XDG_CACHE_HOME':str(root/'xdg-cache'),'XDG_DATA_HOME':str(root/'xdg-data'),
         'XDG_STATE_HOME':str(root/'xdg-state'),
         'XDG_RUNTIME_DIR':str(root/'xdg-runtime')}
    compile_cmd=['cc','-std=c99','-O1','-Wall','-Wextra','harness.c','-o','observe']
    result={'status':'FAIL','protocol_sha256':inputs['PROTOCOL.md'],
            'manifest_sha256':digest(manifest_path),'inputs':inputs,
            'compile_options':compile_cmd,'case_count':3,
            'copied_inputs_verified':True}
    try:
        result['compile']=bounded(compile_cmd,work,env,120,
                                   private/'compile.stdout',private/'compile.stderr')
        result['compile']['stderr_empty']=(private/'compile.stderr').stat().st_size==0
        if result['compile']['category']=='ok':
            result['run']=bounded(['./observe'],work,env,5,
                                  private/'run.stdout',private/'run.stderr')
            result['run']['stderr_empty']=(private/'run.stderr').stat().st_size==0
            output=(private/'run.stdout').read_bytes()
            # The harness emits only literal case labels, positions and classifications.
            if (result['run']['category']=='ok' and result['run']['stderr_empty']
                    and len(output)<=65536 and output.endswith(b'PASS three bounded cases\n')):
                (root/'output.txt').write_bytes(output)
                result['output_sha256']=hashlib.sha256(output).hexdigest()
                result['status']='PASS'
    except (OSError, ValueError):
        result['failure_category']='execution_environment_error'
    (root/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(result['status'])
    return 0 if result['status']=='PASS' else 1

if __name__=='__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError):
        # Avoid leaking actual machine paths through a public-facing traceback.
        print('FAIL preparation_or_identity_error')
        raise SystemExit(1)
