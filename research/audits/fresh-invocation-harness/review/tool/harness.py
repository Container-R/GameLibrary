"""Bounded Linux legacy freshness wrapper. No shell or archive result reuse."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import signal
import subprocess
import sys
import time
import uuid

HERE = Path(__file__).resolve().parent

class Rejected(ValueError): pass

def require(ok, why):
    if not ok: raise Rejected(why)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def strict_pairs(items):
    d = {}
    for k,v in items:
        require(k not in d, 'duplicate JSON key')
        d[k] = v
    return d

def number(s):
    v=float(s);require(math.isfinite(v),'nonfinite JSON float');return v

def read(p):
    return json.loads(p.read_text(), object_pairs_hook=strict_pairs, parse_float=number,
        parse_constant=lambda s: (_ for _ in ()).throw(Rejected('nonstandard JSON number')))

def write(p, value):
    temp=p.with_name(p.name+'.new')
    with temp.open('x') as f: json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    os.replace(temp,p)

def contained(root, rel, must_exist=True):
    require(type(rel) is str and rel and '\\' not in rel and ':' not in rel and not any(ord(c)<32 for c in rel), 'invalid relative path')
    require(not PurePosixPath(rel).is_absolute() and all(x not in ('','.','..') for x in rel.split('/')), 'unnormalized path')
    p=root
    for part in rel.split('/'):
        p=p/part
        require(not p.is_symlink(),'symlink path rejected')
    require(p.resolve().is_relative_to(root.resolve()),'path escape')
    if must_exist: require(p.is_file(),'missing regular file: '+rel)
    return p

def group_alive(pid):
    try: os.killpg(pid,0);return True
    except ProcessLookupError:return False

def terminate_group(proc):
    for sig,wait in ((signal.SIGTERM,0.2),(signal.SIGKILL,2.0)):
        try:os.killpg(proc.pid,sig)
        except ProcessLookupError:pass
        try:proc.wait(timeout=wait)
        except subprocess.TimeoutExpired:pass
        if not group_alive(proc.pid):return True
    return not group_alive(proc.pid)

def launch(command, cwd, env, directory, timeout):
    """Internal primitive also tested with original synthetic Python children."""
    result={'exit_code':None,'timed_out':False,'group_remaining':False,'spawned':False}
    with (directory/'stdout.txt').open('xb') as out,(directory/'stderr.txt').open('xb') as err:
        proc=subprocess.Popen(command,cwd=cwd,env=env,stdout=out,stderr=err,start_new_session=True)
        result['spawned']=True;result['pid']=proc.pid
        try:
            result['exit_code']=proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            result['timed_out']=True
            result['group_remaining']=not terminate_group(proc)
            result['exit_code']=proc.poll()
        except BaseException:
            terminate_group(proc)
            raise
        else:
            if group_alive(proc.pid):
                result['group_remaining']=not terminate_group(proc)
                result['unexpected_descendants']=True
    return result

def process_acceptable(process):
    require(type(process.get('exit_code')) is int and process['exit_code']==0,'child not successful')
    require(process.get('timed_out') is False and process.get('group_remaining') is False,'timeout or unclosed group')
    require(not process.get('unexpected_descendants',False),'unexpected descendants')
    require(process.get('spawned') is True,'child not spawned')

def registry():
    value=read(HERE/'registry.json')
    require(value.get('version')==1 and isinstance(value.get('fixtures'),dict),'registry schema')
    return value['fixtures']

def validate_summary(inv, fixture, entry):
    # Only this normal adapter has been approved and tested; other five reject-only.
    require(fixture=='godot-focus-boundary' and entry['normal_enabled'] is True,'normal adapter not validated')
    s=read(contained(inv,'work/results/summary.json'))
    require(s.get('source_sha256')==entry['sources'],'summary source pins')
    runs=s.get('runs');require(type(runs) is list and len(runs)==3,'focus run count')
    require([x.get('mode') for x in runs]==['gate','naive','guarded'],'focus modes')
    for row in runs:require(type(row.get('exit_code')) is int and row['exit_code']==0 and row.get('checks')=='passed','focus run failed')
    for mode in ('gate','naive','guarded'):
        log=contained(inv,'work/results/'+mode+'.log').read_text()
        records=[read_json_line(line[len('RESULT_JSON='):]) for line in log.splitlines() if line.startswith('RESULT_JSON=')]
        require(len(records)==1,'focus raw record count')
        parsed=read(contained(inv,'work/results/'+mode+'.json'))
        require(json.dumps(records[0],sort_keys=True)==json.dumps(parsed,sort_keys=True),'raw/parsed mismatch')
        require(parsed.get('mode')==mode,'raw mode')
    require(type(s.get('binary_sha256')) is str and len(s['binary_sha256'])==64,'summary binary metadata')
    return s

def read_json_line(value):
    return json.loads(value,object_pairs_hook=strict_pairs,parse_float=number,
        parse_constant=lambda s: (_ for _ in ()).throw(Rejected('nonstandard JSON number')))

def consumer(invocation, expected_id):
    inv=Path(invocation).resolve(strict=True)
    require(inv.name==expected_id and str(uuid.UUID(expected_id))==expected_id,'unexpected invocation ID')
    rec=read(contained(inv,'receipt.json'))
    require(rec.get('invocation_id')==expected_id and rec.get('status')=='ACCEPTED','not accepted invocation')
    require(rec.get('harness_sha256')==sha(HERE/'harness.py') and rec.get('registry_sha256')==sha(HERE/'registry.json'),'consumer source/registry identity differs')
    entries=registry();name=rec.get('fixture');require(name in entries,'unregistered fixture');entry=entries[name]
    require(rec.get('optimize_child') is False,'optimized child cannot be accepted')
    process_acceptable(rec['process'])
    require(rec.get('source_sha256')==entry['sources'],'source manifest differs')
    for rel,digest in entry['sources'].items():require(sha(contained(inv,'work/'+rel))==digest,'copied source changed')
    artifacts=rec.get('artifacts');require(type(artifacts) is dict,'artifact manifest missing')
    required={'stdout.txt','stderr.txt','work/results/summary.json'}
    for mode in ('gate','naive','guarded'):required|={'work/results/'+mode+'.json','work/results/'+mode+'.log'}
    require(required<=set(artifacts),'required artifacts missing')
    for rel,digest in artifacts.items():
        require(type(digest) is str and len(digest)==64 and all(c in '0123456789abcdef' for c in digest),'bad digest')
        require(sha(contained(inv,rel))==digest,'artifact changed: '+rel)
    summary=validate_summary(inv,name,entry)
    require(summary['binary_sha256']==rec.get('binary_sha256'),'engine hash metadata mismatch')
    return {'status':'ACCEPTED','invocation_id':expected_id,'fixture':name}

def invoke(repository, output, fixture, optimize=False, timeout=90):
    repo=Path(repository).resolve(strict=True);out=Path(output).resolve()
    require(sys.platform.startswith('linux'),'Linux only')
    require(not out.is_relative_to(repo),'output must be outside inspected repository')
    entries=registry();require(fixture in entries,'fixture not allowlisted');entry=entries[fixture]
    require(optimize or entry['normal_enabled'],'normal mode not enabled for this fixture')
    source=repo/entry['directory'];source=source.resolve(strict=True)
    require(source.is_relative_to(repo),'source directory escape')
    out.mkdir(parents=True,exist_ok=True)
    ident=str(uuid.uuid4());inv=out/ident;inv.mkdir()
    rec={'invocation_id':ident,'status':'STARTED','fixture':fixture,'optimize_child':optimize,
         'started_utc':datetime.now(timezone.utc).isoformat(),'harness_sha256':sha(HERE/'harness.py'),
         'registry_sha256':sha(HERE/'registry.json'),'source_sha256':entry['sources'],
         'python':sys.version,'python_executable':sys.executable,'repository':str(repo),'artifacts':{}}
    write(inv/'receipt.json',rec);started=time.monotonic()
    try:
        work=inv/'work';work.mkdir()
        for rel,digest in entry['sources'].items():
            p=contained(source,rel);require(sha(p)==digest,'registered source changed: '+rel)
            target=contained(work,rel,False);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
        require(not (work/'results').exists(),'archived results copied')
        engine=Path('/usr/local/bin/godot').resolve(strict=True);rec['engine_path']=str(engine);rec['binary_sha256']=sha(engine)
        env=dict(os.environ,GODOT_SILENCE_ROOT_WARNING='1')
        for key in ('HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR'):
            p=inv/key;p.mkdir();env[key]=str(p)
        env['PATH']=str(engine.parent)+os.pathsep+os.environ.get('PATH','')
        # Legacy which('godot') must still resolve exactly the measured installed alias.
        import shutil
        require(Path(shutil.which('godot',path=env['PATH'])).resolve()==engine,'different engine on PATH')
        command=[sys.executable,'-B',*(['-O'] if optimize else []),str(work/'run.py')]
        rec['command']=command;rec['timeout_seconds']=timeout;write(inv/'receipt.json',rec)
        rec['process']=launch(command,work,env,inv,timeout)
        process_acceptable(rec['process'])
        require(not optimize,'optimized legacy cannot be accepted')
        for rel,digest in entry['sources'].items():
            require(sha(contained(source,rel))==digest and sha(contained(work,rel))==digest,'source changed during invocation')
        require(sha(engine)==rec['binary_sha256'],'engine changed during invocation')
        summary=validate_summary(inv,fixture,entry)
        require(summary['binary_sha256']==rec['binary_sha256'],'runner engine differs')
        artifacts=['stdout.txt','stderr.txt']+[str(p.relative_to(inv)) for p in (work/'results').rglob('*') if p.is_file()]
        rec['artifacts']={rel:sha(contained(inv,rel)) for rel in sorted(artifacts)}
        rec['status']='ACCEPTED'
    except BaseException as exc:
        rec['status']='REJECTED';rec['error']=type(exc).__name__+': '+str(exc)
        rec['artifacts']={name:sha(inv/name) for name in ('stdout.txt','stderr.txt') if (inv/name).is_file() and not (inv/name).is_symlink()}
    finally:
        rec['ended_utc']=datetime.now(timezone.utc).isoformat();rec['elapsed_seconds']=time.monotonic()-started
        write(inv/'receipt.json',rec)
    return inv,rec

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    run=sub.add_parser('invoke');run.add_argument('repository');run.add_argument('output');run.add_argument('fixture');run.add_argument('--optimize-child',action='store_true')
    consume=sub.add_parser('consume');consume.add_argument('invocation');consume.add_argument('--expected-id',required=True)
    args=parser.parse_args()
    try:
        if args.action=='consume':result=consumer(args.invocation,args.expected_id);print(json.dumps(result));return 0
        inv,rec=invoke(args.repository,args.output,args.fixture,args.optimize_child)
        print(json.dumps({'invocation_id':rec['invocation_id'],'directory':str(inv),'status':rec['status']}))
        return 0 if rec['status']=='ACCEPTED' else 1
    except (ValueError,OSError,RuntimeError,TypeError,KeyError) as exc:
        print('harness rejected: '+str(exc),file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
