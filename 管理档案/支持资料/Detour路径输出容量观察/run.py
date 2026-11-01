"""One reviewed build, one bounded native invocation. Do not run without approval."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
ATTEMPT = 'attempt-002'
REVIEWED_DIAGNOSTIC_SHA256 = 'd887b09f1c4f304b009fbfbcf61834c5d71dd80a44d8cc1cdb7f9978952f0bd5'
CODE_FILES = {'fixture.cpp','expected.json','validate.py','test_validate.py','run.py','PROTOCOL.md','SOURCE-MANIFEST.json','reviewed-build-stderr.txt'}
UNITS = ('DetourAlloc','DetourAssert','DetourCommon','DetourNavMesh','DetourNavMeshBuilder','DetourNavMeshQuery','DetourNode')
HEADERS = ('DetourAlloc','DetourAssert','DetourCommon','DetourMath','DetourNavMesh','DetourNavMeshBuilder','DetourNavMeshQuery','DetourNode','DetourStatus')
SOURCE_FILES = {'Detour/Source/'+n+'.cpp' for n in UNITS} | {'Detour/Include/'+n+'.h' for n in HEADERS}
BUILD = ['c++','-std=c++11','-O0','-Wall','-Wextra','-Iupstream/Detour/Include','fixture.cpp'] + ['upstream/Detour/Source/'+n+'.cpp' for n in UNITS] + ['-o','fixture']

def require(ok, why):
    if not ok: raise ValueError(why)

def strict(raw):
    def pairs(items):
        x={}
        for k,v in items:
            require(k not in x,'duplicate JSON key');x[k]=v
        return x
    def bad(_): raise ValueError('nonfinite JSON')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=bad)

def sha(raw): return hashlib.sha256(raw).hexdigest()

def identities(root):
    manifest=strict((root/'CODE-MANIFEST.json').read_bytes())
    require(type(manifest) is dict and set(manifest)==CODE_FILES,'code file set')
    observed={}
    for name in sorted(CODE_FILES):
        actual=sha((root/name).read_bytes());require(type(manifest[name]) is str and actual==manifest[name],'code identity');observed[name]=actual
    source=strict((root/'SOURCE-MANIFEST.json').read_bytes())
    require(source['repository']=='recastnavigation/recastnavigation' and source['commit']=='6dc1667f580357e8a2154c28b7867bea7e8ad3a7','upstream version')
    rows=source['files'];require(type(rows) is list and len(rows)==16,'source count')
    require({r['path'] for r in rows}==SOURCE_FILES,'source file set')
    for row in rows:
        name=row['path'];raw=(root/'upstream'/name).read_bytes()
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        require(sha(raw)==row['sha256'] and blob==row['git_blob'],'upstream byte identity');observed['upstream/'+name]=sha(raw)
    return observed

def validate_build(stdout, stderr, returncode):
    reviewed=(ROOT/'reviewed-build-stderr.txt').read_bytes()
    require(sha(reviewed)==REVIEWED_DIAGNOSTIC_SHA256,'reviewed diagnostic identity')
    require(type(returncode) is int and returncode==0,'build nonzero')
    require(stdout==b'', 'unexpected build stdout')
    require(stderr==b'' or stderr==reviewed,'unreviewed build diagnostics')
    return 'empty' if stderr==b'' else 'reviewed_warning'


def stop_group(child):
    # A leader exiting does not prove all owned descendants exited.
    errors=[]
    for sig in (signal.SIGTERM,signal.SIGKILL):
        try:os.killpg(child.pid,sig)
        except ProcessLookupError:pass
        except OSError as exc:errors.append(type(exc).__name__)
        if sig==signal.SIGTERM:
            try:child.wait(timeout=1)
            except subprocess.TimeoutExpired:pass
            except Exception as exc:errors.append(type(exc).__name__)
    try:child.wait(timeout=1)
    except Exception as exc:errors.append(type(exc).__name__)
    return errors

def command(work, argv, timeout, label, receipt):
    record={'stage':label,'argv':argv,'timeout_seconds':timeout,'attempted':False}
    receipt['processes'].append(record)
    child=None;out=b'';err=b'';primary=None
    try:
        env={'PATH':os.environ.get('PATH','/usr/bin:/bin'),'LC_ALL':'C','LANG':'C','HOME':str(work/'home'),'TMPDIR':str(work/'tmp')}
        child=subprocess.Popen(argv,cwd=work,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
        record['attempted']=True
        try:out,err=child.communicate(timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            out=exc.output or b'';err=exc.stderr or b'';raise
        record['returncode']=child.returncode
        require(child.returncode==0,label+' nonzero')
    except BaseException as exc:
        primary=exc;record['error']=type(exc).__name__
        if child is not None:record['cleanup_errors']=stop_group(child)
    finally:
        secondary=[]
        for suffix,raw in [('stdout',out),('stderr',err)]:
            try:
                (work/(label+'.'+suffix)).write_bytes(raw)
                record[suffix+'_sha256']=sha(raw)
            except Exception as exc:secondary.append(type(exc).__name__)
        if secondary:
            record['finalization_errors']=secondary
            if primary is None:primary=RuntimeError('stream finalization failed')
    if primary is not None:raise primary
    return out,err

def main():
    # Exclusive destination: historical PASS cannot be reused or overwritten.
    work=ROOT/'execution'/ATTEMPT
    work.mkdir(parents=True,exist_ok=False)
    receipt={'status':'fail','stage':'identity_before','processes':[]}
    primary=None
    try:
        require(not sys.flags.optimize,'runner requires normal Python')
        before=identities(ROOT);receipt['source_before']=before
        for name in CODE_FILES | {'CODE-MANIFEST.json'}:
            shutil.copy2(ROOT/name,work/name)
        shutil.copytree(ROOT/'upstream',work/'upstream')
        require(identities(work)==before,'copied identities')
        (work/'home').mkdir();(work/'tmp').mkdir()
        receipt['stage']='build'
        out,err=command(work,BUILD,60,'build',receipt)
        receipt['build_diagnostic_policy']=validate_build(out,err,receipt['processes'][-1]['returncode'])
        receipt['stage']='native'
        out,err=command(work,['./fixture'],10,'native',receipt)
        require(not err,'unexpected native diagnostics')
        receipt['stage']='consumer'
        spec=importlib.util.spec_from_file_location('consumer',work/'validate.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        result=module.validate(module.strict_json(out))
        (work/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
        receipt['observation_sha256']=sha(out)
    except BaseException as exc:
        primary=exc;receipt['error']=type(exc).__name__
    finally:
        for label,root in [('source_after',ROOT),('copied_after',work)]:
            try:
                receipt[label]=identities(root)
                require(receipt[label]==receipt.get('source_before'),'before/after identity mismatch')
            except Exception as exc:
                receipt[label]={'unavailable':type(exc).__name__}
                if primary is None:primary=exc
        if primary is None:
            receipt['status']='pass';receipt['stage']='complete'
        try:(work/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        except Exception as exc:
            receipt['status']='fail';receipt['finalization_error']=type(exc).__name__
            if primary is None:primary=exc
    print(json.dumps({'status':receipt['status'],'stage':receipt['stage'],'process_attempts':len(receipt['processes'])}))
    return 0 if primary is None else 1

if __name__=='__main__':raise SystemExit(main())
