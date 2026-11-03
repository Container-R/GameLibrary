"""Do not invoke before independent protocol/code acceptance and execution approval."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
FILES = {'cgltf.h','LICENSE','harness.c','dense-normalized.json','zero-normalized.json','dense-raw.json','fixture.hex','expected.json','check.py','protocol.md','run.py'}
KEYS = ('HOME','XDG_CONFIG_HOME','XDG_CACHE_HOME','XDG_DATA_HOME','XDG_STATE_HOME','XDG_RUNTIME_DIR','XDG_CONFIG_DIRS','XDG_DATA_DIRS','TMPDIR','TMP','TEMP')
FLAGS = ['-std=c99','-O0','-Wall','-Wextra','-pedantic']
COMMIT = '360db1a95480fe102ae9c69b27c5d101167ff5ba'

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def pairs(items):
    d={}
    for k,v in items:
        if k in d: raise ValueError('duplicate_key')
        d[k]=v
    return d

def atomic(path,data):
    pending=path.with_name(path.name+'.pending')
    with pending.open('xb') as f: f.write(data)
    pending.replace(path)

def identities(root, hashes):
    for name,want in hashes.items():
        p=root/name
        if p.is_symlink() or not p.is_file() or digest(p)!=want: raise RuntimeError('input_identity')

def no_links(path):
    for p in (path,*path.parents):
        if p.is_symlink(): raise RuntimeError('symlink_path')

def validate_env(env,root):
    no_links(root)
    for key in KEYS:
        p=root/key
        if env.get(key)!=str(p) or p.is_symlink() or not p.is_dir() or stat.S_IMODE(p.stat().st_mode)!=0o700: raise RuntimeError('runtime_directory')
        # Actual exclusive write/read/remove, not only os.access.
        probe=p/'write-check'
        with probe.open('xb') as f: f.write(b'probe')
        if probe.read_bytes()!=b'probe': raise RuntimeError('runtime_write')
        probe.unlink()

def phase(raw,work,env,envroot,name,argv,limit,report):
    proc=None; first=None; cleanup=[]; rc=None; group_absent=False
    try:
        with (raw/(name+'.stdout')).open('xb') as out, (raw/(name+'.stderr')).open('xb') as err:
            validate_env(env,envroot)
            proc=subprocess.Popen(argv,cwd=work,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True)
            rc=proc.wait(timeout=limit)
    except BaseException as exc:
        first=exc
    finally:
        if proc is not None:
            # One total two-second cleanup deadline, including leader reaping.
            # Group disappearance is a limited observation, not a sandbox.
            deadline=time.monotonic()+2.0
            try: os.killpg(proc.pid,signal.SIGKILL)
            except ProcessLookupError: pass
            except BaseException as exc: cleanup.append(repr(exc))
            try: proc.wait(timeout=max(0.0,deadline-time.monotonic()))
            except BaseException as exc: cleanup.append(repr(exc))
            while True:
                try: os.killpg(proc.pid,0)
                except ProcessLookupError:
                    group_absent=True
                    break
                except BaseException as exc:
                    cleanup.append(repr(exc))
                    break
                remaining=deadline-time.monotonic()
                if remaining<=0:
                    cleanup.append('process_group_still_present_at_cleanup_deadline')
                    break
                time.sleep(min(0.02,remaining))
        report[name]={'exit_code':rc,'child_exit_confirmed':proc is not None and proc.returncode is not None,'group_absence_confirmed':group_absent,'cleanup_ok':not cleanup and group_absent}
        if cleanup: (raw/(name+'.cleanup.txt')).write_text('\n'.join(cleanup))
    if first is not None: raise first
    if cleanup or not group_absent: raise RuntimeError('cleanup_failure')
    if rc!=0: raise RuntimeError('nonzero_exit')
    if (raw/(name+'.stderr')).stat().st_size: raise RuntimeError('diagnostic_requires_review')
    if name=='compile' and (raw/(name+'.stdout')).stat().st_size: raise RuntimeError('unexpected_compile_stdout')

def main(target):
    target=Path(os.path.abspath(target)); no_links(target)
    if not target.parent.is_dir(): raise RuntimeError('missing_parent')
    target.mkdir(mode=0o700,exist_ok=False)
    raw=target/'private-raw'; raw.mkdir(mode=0o700)
    public=target/'public-safe'; public.mkdir(mode=0o700)
    work=raw/'work';work.mkdir(mode=0o700)
    envroot=raw/'runtime';envroot.mkdir(mode=0o700)
    env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','TZ':'UTC'}
    report={'status':'FAIL','source_commit':COMMIT,'compile_options':FLAGS,'stage_results':{},'scope':'three fixed generic accessor configurations only'}
    hashes=None; mh=None; failure=None
    try:
        for key in KEYS:
            p=envroot/key;p.mkdir(mode=0o700);env[key]=str(p)
        validate_env(env,envroot)
        mh=digest(ROOT/'manifest.json')
        m=json.loads((ROOT/'manifest.json').read_text(),object_pairs_hook=pairs)
        if set(m)!= {'source_commit','status','sha256'} or m['source_commit']!=COMMIT or m['status']!='PREPARED_NOT_EXECUTED' or set(m['sha256'])!=FILES: raise RuntimeError('manifest_schema')
        hashes=m['sha256'];identities(ROOT,hashes)
        for n in sorted(FILES): shutil.copyfile(ROOT/n,work/n)
        identities(work,hashes)
        report.update(input_sha256=hashes,manifest_sha256=mh)
        compiler='/usr/bin/cc'
        if not os.path.isfile(compiler) or not os.access(compiler,os.X_OK): raise RuntimeError('compiler_unavailable_no_install')
        phase(raw,work,env,envroot,'compile',[compiler,*FLAGS,'harness.c','-o','probe'],30,report['stage_results'])
        identities(ROOT,hashes);identities(work,hashes)
        if digest(ROOT/'manifest.json')!=mh: raise RuntimeError('manifest_changed')
        phase(raw,work,env,envroot,'native',['./probe'],5,report['stage_results'])
        identities(ROOT,hashes);identities(work,hashes)
        spec=importlib.util.spec_from_file_location('finite_consumer',work/'check.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        output=(raw/'native.stdout').read_bytes();module.check(output)
        identities(ROOT,hashes);identities(work,hashes)
        if digest(ROOT/'manifest.json')!=mh: raise RuntimeError('manifest_changed')
        validate_env(env,envroot)
        report.update(status='PASS_three_configurations',output_sha256=hashlib.sha256(output).hexdigest(),identity_after='MATCH',runtime_directories='11 validated, retained local only')
    except BaseException as exc:
        failure=exc
    finally:
        if hashes is not None:
            try:
                identities(ROOT,hashes);identities(work,hashes)
                if digest(ROOT/'manifest.json')!=mh: raise RuntimeError('manifest_changed')
            except BaseException as exc:
                if failure is None: failure=exc
                else: (raw/'after-check-error.txt').write_text(repr(exc))
    if failure is not None:
        report['status']='FAIL';report.pop('output_sha256',None)
        (raw/'runner-error.txt').write_text(repr(failure)+'\n')
    else:
        # Regenerate a schema-whitelisted public projection, not arbitrary stdout.
        safe=(json.dumps(module.check(output),sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
        atomic(public/'values.json',safe)
        report['public_values_sha256']=hashlib.sha256(safe).hexdigest()
    atomic(public/'result.json',(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n').encode())
    print(report['status'])
    return 0 if failure is None else 1

if __name__=='__main__':
    try:
        if sys.flags.optimize or not sys.dont_write_bytecode or len(sys.argv)!=2: raise RuntimeError('require_B_nonoptimized_one_fresh_directory')
        sys.exit(main(sys.argv[1]))
    except Exception:
        print('FAIL_before_final_receipt',file=sys.stderr);sys.exit(2)
