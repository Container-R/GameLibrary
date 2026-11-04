"""Two gated fresh copies. DO NOT invoke main before independent approval.

--execute-approved is an explicit operator gate, not proof approval exists.
The default diagnostic policy is empty-only; reviewed-exact requires fresh approval.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess

ROOT=Path(__file__).resolve().parent
SOURCE_ROOT=ROOT/'upstream'
COMMIT='6dc1667f580357e8a2154c28b7867bea7e8ad3a7'
WARNING_SHA='d887b09f1c4f304b009fbfbcf61834c5d71dd80a44d8cc1cdb7f9978952f0bd5'
UNITS=('DetourAlloc','DetourAssert','DetourCommon','DetourNavMesh','DetourNavMeshBuilder','DetourNavMeshQuery','DetourNode')
HEADERS=UNITS+('DetourMath','DetourStatus')
SOURCES={'Detour/Source/'+x+'.cpp' for x in UNITS}|{'Detour/Include/'+x+'.h' for x in HEADERS}
CODE={'fixture.cpp','consumer.py','test_consumer.py','runner.py','test_runner.py','PROTOCOL.md','SCHEMA.md','expected.json','SOURCE-MANIFEST.json','reviewed-build-stderr.txt'}
BUILD=['c++','-std=c++11','-O0','-Wall','-Wextra','-Iupstream/Detour/Include','fixture.cpp']+['upstream/Detour/Source/'+x+'.cpp' for x in UNITS]+['-o','fixture']
DIRS={'HOME':'home','TMPDIR':'tmp','XDG_CONFIG_HOME':'config','XDG_CACHE_HOME':'cache','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'runtime'}

def require(ok,message):
    if not ok: raise ValueError(message)

def strict(raw):
    def pairs(items):
        result={}
        for k,v in items:
            require(k not in result,'duplicate key');result[k]=v
        return result
    def bad(_): raise ValueError('nonfinite token')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=bad)

def sha(raw): return hashlib.sha256(raw).hexdigest()

def identities(root, source_root):
    manifest_raw=(root/'CODE-MANIFEST.json').read_bytes()
    manifest=strict(manifest_raw)
    require(type(manifest) is dict and set(manifest)==CODE,'exact code set')
    observed={'CODE-MANIFEST.json':sha(manifest_raw)}
    for name in sorted(CODE):
        digest=sha((root/name).read_bytes())
        require(type(manifest[name]) is str and digest==manifest[name],'code identity '+name)
        observed[name]=digest
    source=strict((root/'SOURCE-MANIFEST.json').read_bytes())
    require(source['repository']=='recastnavigation/recastnavigation' and source['commit']==COMMIT,'source version')
    rows=source['files'];require(type(rows) is list and len(rows)==16,'source count')
    require({r['path'] for r in rows}==SOURCES,'source set')
    for row in rows:
        raw=(source_root/row['path']).read_bytes()
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        digest=sha(raw)
        require(blob==row['git_blob'] and digest==row['sha256'],'source identity '+row['path'])
        observed['upstream/'+row['path']]=digest
    require(sha((root/'reviewed-build-stderr.txt').read_bytes())==WARNING_SHA,'warning candidate identity')
    return observed

def isolated_env(work):
    # Each invocation revalidates real directories, even if created previously.
    require(not work.is_symlink() and work.is_dir(),'work directory')
    base=work.resolve(strict=True)
    env={'PATH':'/usr/bin:/bin','LC_ALL':'C','LANG':'C'}
    seen=set()
    for key,name in DIRS.items():
        p=work/name
        if not p.exists() and not p.is_symlink(): p.mkdir(mode=0o700)
        require(not p.is_symlink(),'environment symlink '+key)
        mode=p.lstat().st_mode
        require(stat.S_ISDIR(mode),'environment directory '+key)
        resolved=p.resolve(strict=True)
        require(resolved.parent==base and resolved not in seen,'environment containment/distinctness')
        seen.add(resolved)
        require(os.access(p,os.W_OK|os.X_OK),'environment writable '+key)
        if key=='XDG_RUNTIME_DIR':
            require(stat.S_IMODE(mode)==0o700 and p.stat().st_uid==os.getuid(),'runtime private ownership/mode')
        env[key]=str(resolved)
    return env

def validate_build(out,err,rc,policy,candidate):
    require(rc==0 and type(rc) is int,'build exit')
    require(out==b'','build stdout')
    require(policy in ('empty-only','reviewed-exact'),'diagnostic policy')
    require(sha(candidate)==WARNING_SHA,'candidate identity')
    require(err==b'' or (policy=='reviewed-exact' and err==candidate),'unreviewed build diagnostic')
    return 'empty' if not err else 'reviewed_exact'

def cleanup_group(child):
    errors=[]
    # This runs even after the leader exits: descendants are not presumed gone.
    for sig in (signal.SIGTERM,signal.SIGKILL):
        try: os.killpg(child.pid,sig)
        except ProcessLookupError: pass
        except OSError as exc: errors.append(type(exc).__name__)
        if sig==signal.SIGTERM:
            try: child.wait(timeout=1)
            except subprocess.TimeoutExpired: pass
            except Exception as exc: errors.append(type(exc).__name__)
    try: child.wait(timeout=1)
    except Exception as exc: errors.append(type(exc).__name__)
    return errors

def invoke(work,argv,seconds,label,receipt):
    record={'stage':label,'argv':argv,'timeout_seconds':seconds,'attempted':False,'reported_calls':None,'reported_calls_validated':False}
    receipt['processes'].append(record)
    child=None;out=b'';err=b'';primary=None
    try:
        env=isolated_env(work);record['environment_validated']=True
        child=subprocess.Popen(argv,cwd=work,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
        record['attempted']=True
        try:
            out,err=child.communicate(timeout=seconds)
        except subprocess.TimeoutExpired as exc:
            out=exc.output or b'';err=exc.stderr or b'';record['timeout']=True;raise
        record['returncode']=child.returncode
        require(child.returncode==0,label+' nonzero')
    except BaseException as exc:
        primary=exc;record['error']=type(exc).__name__
    finally:
        if child is not None:
            errors=cleanup_group(child);record['cleanup_errors']=errors
            if errors and primary is None: primary=RuntimeError('process group cleanup')
            # After termination gather complete available bytes; retain timeout bytes if this fails.
            try:
                complete_out,complete_err=child.communicate(timeout=1)
                out=complete_out;err=complete_err
                record['returncode']=child.returncode
            except Exception as exc:
                record['capture_error']=type(exc).__name__
                if primary is None: primary=exc
        if label=='native':
            try:
                parsed=strict(out)
                counts=parsed.get('calls') if type(parsed) is dict else None
                if type(counts) is dict and set(counts)=={'builder','nav_init','query_init','raycast','findPath'} and all(type(v) is int and v>=0 for v in counts.values()):
                    record['reported_calls']=counts
            except Exception: pass
            # Null means unknown, including a started process that crashed before JSON.
        for suffix,raw in (('stdout',out),('stderr',err)):
            try:
                (work/(label+'.'+suffix)).write_bytes(raw);record[suffix+'_sha256']=sha(raw)
            except Exception as exc:
                record.setdefault('capture_write_errors',[]).append(type(exc).__name__)
                if primary is None: primary=exc
    if primary is not None: raise primary
    return out,err

def run_copy(work,policy):
    work.mkdir(exist_ok=False)
    receipt={'status':'fail','stage':'identity_before','diagnostic_policy':policy,'processes':[]}
    primary=None;before=None
    try:
        before=identities(ROOT,SOURCE_ROOT);receipt['identity_before']=before
        for name in CODE|{'CODE-MANIFEST.json'}: shutil.copy2(ROOT/name,work/name)
        for rel in sorted(SOURCES):
            dest=work/'upstream'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SOURCE_ROOT/rel,dest)
        require(identities(work,work/'upstream')==before,'copy identity')
        receipt['stage']='build'
        out,err=invoke(work,BUILD,60,'build',receipt)
        receipt['build_diagnostics']=validate_build(out,err,receipt['processes'][-1]['returncode'],policy,(work/'reviewed-build-stderr.txt').read_bytes())
        receipt['stage']='native'
        out,err=invoke(work,['./fixture'],10,'native',receipt)
        require(err==b'','native diagnostics')
        receipt['stage']='consumer'
        spec=importlib.util.spec_from_file_location('captured_consumer',work/'consumer.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        result=module.validate(module.strict_json(out))
        receipt['processes'][-1]['reported_calls_validated']=True
        (work/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
        receipt['observation_sha256']=sha(out)
    except BaseException as exc:
        primary=exc;receipt['error']=type(exc).__name__;receipt['error_detail']=str(exc)
    finally:
        for key,root,sources in (('original_after',ROOT,SOURCE_ROOT),('copy_after',work,work/'upstream')):
            try:
                after=identities(root,sources);receipt[key]=after
                require(before is not None and after==before,'identity postcheck')
            except Exception as exc:
                receipt[key]={'error':type(exc).__name__,'detail':str(exc)}
                if primary is None: primary=exc
        if primary is None: receipt['status']='pass';receipt['stage']='complete'
        try: (work/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        except Exception as exc:
            receipt['status']='fail';receipt['receipt_error']=type(exc).__name__
            if primary is None: primary=exc
    return receipt,primary

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute-approved',action='store_true')
    parser.add_argument('--diagnostic-policy',choices=('empty-only','reviewed-exact'),default='empty-only')
    args=parser.parse_args()
    require(args.execute_approved,'explicit implementation and execution approval required')
    batch=ROOT/'execution'
    batch.mkdir(exist_ok=False)  # Never adopt stale receipts or silently retry.
    summary={'status':'fail','planned_executions':2,'executions':[]}
    try:
        for name in ('main','repeat'):
            receipt,error=run_copy(batch/name,args.diagnostic_policy)
            summary['executions'].append({'name':name,'status':receipt['status'],'stage':receipt['stage']})
            if error is not None: break
        if len(summary['executions'])==2 and all(x['status']=='pass' for x in summary['executions']): summary['status']='pass'
    except BaseException as exc:
        summary['error']=type(exc).__name__;summary['error_detail']=str(exc)
    finally:
        (batch/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary))
    return 0 if summary['status']=='pass' else 1

if __name__=='__main__': raise SystemExit(main())
