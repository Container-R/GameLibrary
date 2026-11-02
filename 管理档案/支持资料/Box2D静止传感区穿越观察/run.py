"""Separate, explicitly authorized build / execute entry points. No automatic retries."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
SOURCE_MANIFEST_SHA='7b4b4756e22e0ad9bc72110034c5e8b1be3c1fb74090a3a3874f1694795e9396'
REVIEWED_STDERR_SHA='c55f639fa5da94fed9737ff07f07048c47386213d14fe39dbefaf75e281ff4b5'
CODE_FILES=('fixture.c','expected.json','validate.py','run.py','test_validate.py','make_expected.py','PROTOCOL-DRAFT.md','BUILD-ARGV.json','SOURCE-MANIFEST.json','reviewed-build-stderr.txt')

def need(ok,message):
    if not ok:raise ValueError(message)

def sha(data):return hashlib.sha256(data).hexdigest()

def pairs(items):
    result={}
    for k,v in items:
        need(k not in result,'duplicate key');result[k]=v
    return result

def read_json(path):
    def reject(x):raise ValueError('nonfinite JSON')
    return json.loads(path.read_bytes(),object_pairs_hook=pairs,parse_constant=reject)

def save(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def regular(root,relative):
    p=Path(relative);need(not p.is_absolute() and '..' not in p.parts,'relative path required')
    target=root
    for part in p.parts:
        target=target/part;need(not target.is_symlink(),'symlink rejected')
    need(target.is_file(),'missing regular file');return target

def code_snapshot(root,manifest_sha):
    raw=regular(root,'CODE-MANIFEST.json').read_bytes();need(sha(raw)==manifest_sha,'code manifest identity')
    doc=read_json(root/'CODE-MANIFEST.json');need(type(doc) is dict and set(doc)=={'files'},'code manifest schema')
    need(type(doc['files']) is dict and set(doc['files'])==set(CODE_FILES),'code input set')
    found={}
    for name in CODE_FILES:
        digest=sha(regular(root,name).read_bytes());need(digest==doc['files'][name],name+' identity');found[name]=digest
    need(found['SOURCE-MANIFEST.json']==SOURCE_MANIFEST_SHA,'fixed upstream manifest')
    need(found['reviewed-build-stderr.txt']==REVIEWED_STDERR_SHA,'reviewed diagnostic identity')
    return found

def source_snapshot(root,manifest_path):
    need(sha(manifest_path.read_bytes())==SOURCE_MANIFEST_SHA,'fixed source list identity')
    doc=read_json(manifest_path);files=doc['files'];need(len(files)==84,'source cardinality')
    paths=[r['path'] for r in files];need(len(set(paths))==84,'duplicate source path')
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() or p.is_symlink()}
    need(actual==set(paths),'source set mismatch')
    result={}
    for row in files:
        data=regular(root,row['path']).read_bytes()
        need(len(data)==row['size'],'source byte count')
        need(sha(data)==row['sha256'],'source SHA256')
        need(hashlib.sha1(b'blob '+str(len(data)).encode('ascii')+b'\x00'+data).hexdigest()==row['git_blob_sha'],'source Git blob')
        result[row['path']]=sha(data)
    return result

def copy_code(source,destination):
    for name in (*CODE_FILES,'CODE-MANIFEST.json'):
        shutil.copyfile(regular(source,name),destination/name)

def copy_sources(source,destination):
    doc=read_json(ROOT/'SOURCE-MANIFEST.json')
    for row in doc['files']:
        target=destination/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(regular(source,row['path']),target)

def environment(work):
    env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'}
    for key,name in [('HOME','home'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('TMPDIR','tmp')]:
        p=work/'environment'/name;p.mkdir(parents=True);env[key]=str(p.resolve())
    return env

def stop_group(child):
    errors=[]
    for sig in [signal.SIGTERM,signal.SIGKILL]:
        try:os.killpg(child.pid,sig)
        except ProcessLookupError:pass
        except OSError as e:errors.append(type(e).__name__)
        if sig==signal.SIGTERM:
            try:child.wait(timeout=1)
            except subprocess.TimeoutExpired:pass
            except OSError as e:errors.append(type(e).__name__)
    try:child.wait(timeout=2)
    except (OSError,subprocess.TimeoutExpired) as e:errors.append(type(e).__name__)
    return errors

def build_diagnostics(stderr,reviewed_path):
    trusted=Path(reviewed_path).read_bytes()
    need(sha(trusted)==REVIEWED_STDERR_SHA,'reviewed diagnostic identity')
    need(type(stderr) is bytes,'diagnostic bytes required')
    if stderr==b'':return 'empty'
    need(stderr==trusted,'unreviewed build diagnostics')
    return 'reviewed_exact_warning'

def command(argv,work,timeout,env,prefix,empty_stdout=False):
    info={'argv':argv,'timeout_seconds':timeout,'status':'not_started','returncode':None,'secondary_errors':[]}
    child=None;out=b'';err=b'';primary=None;cleaned=False
    try:
        child=subprocess.Popen(argv,cwd=work,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
        info['status']='started';out,err=child.communicate(timeout=timeout);info['returncode']=child.returncode;info['status']='returned'
        need(type(info['returncode']) is int and info['returncode']==0,'child nonzero')
        if empty_stdout:
            need(out==b'','unreviewed build stdout')
            info['diagnostic_policy']=build_diagnostics(err,work/'reviewed-build-stderr.txt')
        else:
            need(err==b'','unreviewed child diagnostics')
            info['diagnostic_policy']='empty'
    except BaseException as e:
        primary=e;info['status']='timeout' if isinstance(e,subprocess.TimeoutExpired) else ('launch_error' if child is None else ('rejected_result' if info['status']=='returned' else 'communication_error'))
        info['error_type']=type(e).__name__
        if isinstance(e,subprocess.TimeoutExpired):out=e.output or b'';err=e.stderr or b''
        if child is not None:
            info['secondary_errors'].extend(stop_group(child));cleaned=True;info['returncode']=child.returncode
            try:
                more_out,more_err=child.communicate(timeout=1)
                if more_out is not None:out=more_out
                if more_err is not None:err=more_err
            except BaseException as extra:info['secondary_errors'].append(type(extra).__name__)
    finally:
        for name,data in [(prefix+'.stdout',out),(prefix+'.stderr',err)]:
            try:(work/name).write_bytes(data)
            except BaseException as e:
                info['secondary_errors'].append(type(e).__name__)
                if primary is None:primary=e
        if primary is not None and child is not None and not cleaned:
            info['secondary_errors'].extend(stop_group(child));cleaned=True
        info['stdout_sha256']=sha(out);info['stderr_sha256']=sha(err)
        try:save(work/(prefix+'.json'),info)
        except BaseException as e:
            if primary is None:primary=e
            if child is not None and not cleaned:info['secondary_errors'].extend(stop_group(child))
    if primary is not None:raise primary
    return out,info

def fresh(root,mode,name):
    need(name and all(c.isalnum() or c in '-_' for c in name),'attempt name')
    work=root/'attempts'/name;work.parent.mkdir(exist_ok=True)
    # Never overwrite a previous result. No import/optimization check before this exclusive guard.
    work.mkdir(exist_ok=False)
    for name in ['receipt.json','validation.json']:
        need(not (work/name).exists(),'stale result')
    need(sys.flags.optimize==0,'runner must not use -O')
    return work

def consumer(root):
    spec=importlib.util.spec_from_file_location('box2d_finite_consumer',root/'validate.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def operate(mode,name,manifest_sha,sources=None,build_name=None,root=None):
    root=Path(root) if root is not None else ROOT
    work=fresh(root,mode,name)
    receipt={'status':'fail','mode':mode,'attempt':name,'code_manifest_sha256':manifest_sha,'stage':'created','secondary_errors':[]}
    primary=None
    try:
        receipt['code_before']=code_snapshot(root,manifest_sha)
        copy_code(root,work);code_snapshot(work,manifest_sha)
        if mode=='build':
            need(sources is not None,'source root required');source=Path(sources)
            receipt['source_before']=source_snapshot(source,root/'SOURCE-MANIFEST.json');copy_sources(source,work/'upstream')
            source_snapshot(work/'upstream',work/'SOURCE-MANIFEST.json')
            argv=read_json(work/'BUILD-ARGV.json');need(type(argv) is list and all(type(x) is str for x in argv),'build argv')
            receipt['stage']='compile';out,info=command(argv,work,120,environment(work),'build',empty_stdout=True)
            receipt['process']=info
            receipt['artifact_sha256']=sha(regular(work,'sensor_fixture').read_bytes())
            receipt['source_original_after']=source_snapshot(source,root/'SOURCE-MANIFEST.json')
        elif mode=='execute':
            need(type(build_name) is str and build_name and all(c.isalnum() or c in '-_' for c in build_name),'build attempt name')
            build=root/'attempts'/build_name;record=read_json(regular(build,'receipt.json'))
            need(record.get('status')=='pass' and record.get('mode')=='build','accepted build required')
            need(record.get('code_manifest_sha256')==manifest_sha,'build code binding')
            code_snapshot(build,manifest_sha);receipt['source_before']=source_snapshot(build/'upstream',build/'SOURCE-MANIFEST.json')
            need(receipt['source_before']==record['source_after'],'build source binding')
            binary=regular(build,'sensor_fixture');need(sha(binary.read_bytes())==record['artifact_sha256'],'build artifact identity')
            receipt['build_receipt_sha256']=sha((build/'receipt.json').read_bytes());receipt['artifact_sha256']=record['artifact_sha256']
            copy_sources(build/'upstream',work/'upstream');shutil.copyfile(binary,work/'sensor_fixture');(work/'sensor_fixture').chmod(0o700)
            code_snapshot(work,manifest_sha);source_snapshot(work/'upstream',work/'SOURCE-MANIFEST.json')
            need(sha(regular(work,'sensor_fixture').read_bytes())==record['artifact_sha256'],'copied artifact identity')
            receipt['stage']='native';out,info=command(['./sensor_fixture'],work,20,environment(work),'native');receipt['process']=info
            code_snapshot(work,manifest_sha) # Bind executable Python before dynamic import.
            receipt['stage']='consume';checked=consumer(work).validate(out,work/'expected.json');save(work/'validation.json',checked)
            need(sha(binary.read_bytes())==record['artifact_sha256'],'original build artifact changed')
            need(sha((build/'receipt.json').read_bytes())==receipt['build_receipt_sha256'],'build receipt changed')
            code_snapshot(build,manifest_sha)
            receipt['source_original_after']=source_snapshot(build/'upstream',build/'SOURCE-MANIFEST.json')
            need(receipt['source_original_after']==receipt['source_before'],'original build source changed')
        else:raise ValueError('mode')
        receipt['stage']='identity_after'
        receipt['source_after']=source_snapshot(work/'upstream',work/'SOURCE-MANIFEST.json')
        need(receipt['source_after']==receipt['source_before'],'source before/after')
        receipt['code_after']=code_snapshot(work,manifest_sha);need(receipt['code_after']==receipt['code_before'],'code before/after')
        code_snapshot(root,manifest_sha)
        need(sha(regular(work,'sensor_fixture').read_bytes())==receipt['artifact_sha256'],'artifact after')
        receipt['status']='pass';receipt['stage']='complete'
    except BaseException as e:
        primary=e;receipt['error_type']=type(e).__name__;receipt['error']=str(e)
        # These are local receipts; raw exceptions must be redacted before any public derivative.
        for label,fn in [('code_after_failure',lambda:code_snapshot(work,manifest_sha)),('source_after_failure',lambda:source_snapshot(work/'upstream',work/'SOURCE-MANIFEST.json'))]:
            try:receipt[label]=fn()
            except BaseException as extra:receipt['secondary_errors'].append({'check':label,'error_type':type(extra).__name__})
    finally:
        try:save(work/'receipt.json',receipt)
        except BaseException as e:
            if primary is None:primary=e
    if primary is not None:raise primary
    return receipt

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['build','execute']);p.add_argument('--attempt',required=True);p.add_argument('--manifest-sha256',required=True)
    p.add_argument('--sources');p.add_argument('--build-attempt');a=p.parse_args()
    result=operate(a.mode,a.attempt,a.manifest_sha256,a.sources,a.build_attempt)
    print(json.dumps({'status':result['status'],'mode':a.mode,'attempt':a.attempt}))
if __name__=='__main__':main()
