#!/usr/bin/env python3
"""Frozen finite experiment runner. Execution requires separate approval."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess

SOURCE_ID = '2025-07-30 19:33:53 4d8adfb30e03f9cf27f800a2c1ba3c48fb4ca1b08b0f5ed59a4d5ecbf45e20a3'
SOURCE_SHA3 = '9145255e83da6529e70121ee4d7a4c88fe83ca4511da0c9ed13d10842df36782'
EXPECTED = {'fixture/PROTOCOL.md', 'fixture/driver.c', 'fixture/runner.py', 'source/sqlite3.c', 'source/sqlite3.h'}
FLAGS = ['-O0', '-std=c99', '-DSQLITE_THREADSAFE=0', '-DSQLITE_OMIT_LOAD_EXTENSION']

def sha(data):
    return hashlib.sha256(data).hexdigest()

def no_symlinks(path):
    # Inspect lexical path before any resolve(), including all existing ancestors.
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError('Symlink path rejected')

def private_mkdir(path, exist_ok=False):
    no_symlinks(path)
    path.mkdir(mode=0o700, exist_ok=exist_ok)
    if not path.is_dir() or (path.stat().st_mode & 0o777) != 0o700:
        raise ValueError('Private directory mode mismatch')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run-name', required=True)
    a = p.parse_args()
    if os.name != 'posix':
        raise SystemExit('POSIX process groups required')
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,39}', a.run_name):
        raise SystemExit('Invalid run name')
    script = Path(os.path.abspath(__file__))
    no_symlinks(script)
    root = script.parent.parent
    manifest_path = root/'fixture/manifest.json'
    no_symlinks(manifest_path)
    raw_manifest = manifest_path.read_bytes()
    manifest = json.loads(raw_manifest)
    entries = manifest['inputs']
    if set(entries) != EXPECTED or manifest['source_id'] != SOURCE_ID or manifest['sqlite3_c_sha3_256'] != SOURCE_SHA3:
        raise SystemExit('Manifest schema/identity mismatch')
    payload = {}
    for rel in sorted(EXPECTED):
        path = root/rel
        no_symlinks(path)
        if path.is_symlink() or not path.is_file():
            raise SystemExit('Input is not a regular original')
        data = path.read_bytes()
        if sha(data) != entries[rel]:
            raise SystemExit('Input digest mismatch')
        payload[rel] = data
    if hashlib.sha3_256(payload['source/sqlite3.c']).hexdigest() != SOURCE_SHA3:
        raise SystemExit('Official source SHA3 mismatch')
    for rel in ('source/sqlite3.c', 'source/sqlite3.h'):
        data = payload[rel].decode('utf-8')
        if '#define SQLITE_SOURCE_ID      "'+SOURCE_ID+'"' not in data or '#define SQLITE_VERSION        "3.50.4"' not in data:
            raise SystemExit('Source declaration mismatch')
    runs = root/'executions'
    private_mkdir(runs, exist_ok=True)
    run = runs/a.run_name
    private_mkdir(run, exist_ok=False)  # Never reuse or remove a previous run.
    private = run/'private-logs'; private_mkdir(private)
    work = run/'work'; private_mkdir(work)
    result = {'status':'failed', 'stage':'preparation', 'manifest_sha256':sha(raw_manifest),
              'input_sha256':entries, 'copied_inputs_verified':False,
              'compile_returncode':None, 'run_returncode':None,
              'output_sha256':None, 'compile_stdout_empty':None,
              'compile_stderr_empty':None, 'run_stderr_empty':None,
              'scope':'same-host finite single-thread build; two fixed branches; no concurrency or crash test'}
    def save():
        (run/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    save()
    try:
        for rel,data in payload.items():
            dest=work/rel; private_mkdir(dest.parent, exist_ok=True); dest.write_bytes(data)
        if any(sha((work/rel).read_bytes()) != entries[rel] for rel in entries):
            raise ValueError('copy verification')
        result['copied_inputs_verified']=True
        for name in ('complete','cancel'):
            private_mkdir(work/name)
        env={'PATH':'/usr/bin:/bin', 'LANG':'C', 'LC_ALL':'C', 'TZ':'UTC'}
        private_mkdir(run/'isolated')
        for key in ('HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME','XDG_STATE_HOME','XDG_RUNTIME_DIR','XDG_CONFIG_DIRS','XDG_DATA_DIRS','TMPDIR','TMP','TEMP'):
            d=run/'isolated'/key.lower(); private_mkdir(d)
            env[key]=str(d)
        def invoke(command,timeout,prefix,stdout):
            with stdout.open('wb') as out, (private/(prefix+'-stderr.txt')).open('wb') as err:
                process = subprocess.Popen(command,cwd=work,env=env,stdin=subprocess.DEVNULL,
                                           stdout=out,stderr=err,start_new_session=True)
                try:
                    return process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    # Kill compiler descendants in the same POSIX process group too.
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    finally:
                        process.wait()
                    raise
        result['stage']='compile'; save()
        code=invoke(['cc',*FLAGS,'-Isource','fixture/driver.c','source/sqlite3.c','-o','driver'],120,'compile',private/'compile-stdout.txt')
        result['compile_returncode']=code
        result['compile_stdout_empty']=(private/'compile-stdout.txt').stat().st_size==0
        result['compile_stderr_empty']=(private/'compile-stderr.txt').stat().st_size==0
        if code!=0: return
        result['stage']='native'; save()
        code=invoke(['./driver'],5,'run',run/'output.jsonl')
        result['run_returncode']=code
        result['run_stderr_empty']=(private/'run-stderr.txt').stat().st_size==0
        output=(run/'output.jsonl').read_bytes()
        result['output_sha256']=sha(output)
        # No compiler output or exception text is copied into this safe summary.
        rows=[json.loads(line) for line in output.decode('utf-8').splitlines()]
        if code!=0 or not rows or rows[-1]!={'event':'all_checks_passed'}: return
        for branch,qty,length,done in [('complete',7,65536,True),('cancel',3,0,False)]:
            items=[r for r in rows if r.get('branch')==branch]
            steps=[r for r in items if r['event']=='step']
            if not steps or len(steps)>128: return
            if branch=='cancel' and (len(steps)!=1 or steps[0]['rc']!=0 or steps[0]['remaining']<=0): return
            if branch=='complete' and (steps[-1]['rc']!=101 or steps[-1]['remaining']!=0): return
            if [r for r in items if r['event']=='finish'] != [{'branch':branch,'event':'finish','rc':0,'saw_done':done}]: return
            if [r for r in items if r['event']=='readback'] != [{'branch':branch,'event':'readback','row':[1,qty,length],'schema_exact':True,'row_count':1,'zero_blob_exact':True}]: return
        result['status']='passed'; result['stage']='complete'
    except subprocess.TimeoutExpired:
        result['failure_kind']='timeout'
    except Exception:
        result['failure_kind']='preparation_or_validation_error'
    finally:
        save()
    return 0 if result['status']=='passed' else 1

if __name__=='__main__':
    outcome=main()
    # Early returns from failed stages cannot accidentally report process success.
    raise SystemExit(0 if outcome==0 else 1)
