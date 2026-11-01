"""Run only after separate native authorization. No work happens on import."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import uuid


def startup(root, optimized):
    # This occurs before importing any local checker or starting any child.
    for name in ('summary.json', 'result.json'):
        path = Path(root)/name
        if path.exists():
            path.unlink()
    if optimized:
        raise RuntimeError('native runner requires normal Python; pure tests support -O')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


def tool_snapshot(env):
    out = {}
    for tool in ('cc','strace'):
        located = shutil.which(tool,path=env['PATH'])
        if not located:
            raise RuntimeError('missing required tool '+tool)
        p = Path(located).resolve()
        out[tool] = {'resolved':str(p),'sha256':digest(p)}
    return out


def stop_owned(child):
    """Bounded owned-group cleanup even if the group leader exits first."""
    problems = []
    for sig,wait in ((signal.SIGTERM,1),(signal.SIGKILL,2)):
        try:
            os.killpg(child.pid,sig)
        except ProcessLookupError:
            pass
        except Exception as exc:
            problems.append(type(exc).__name__+': '+str(exc))
        try:
            child.wait(timeout=wait)
        except subprocess.TimeoutExpired:
            if sig == signal.SIGKILL:
                problems.append('owned leader not reaped within cleanup bound')
        except Exception as exc:
            problems.append(type(exc).__name__+': '+str(exc))
        # Always reach the final group KILL, even if leader wait already succeeded.
    return problems


def command(record, evidence, work, env):
    child = None
    primary = None
    try:
        with (evidence/record['stdout']).open('wb') as out, (evidence/record['stderr']).open('wb') as err:
            child = subprocess.Popen(record['argv'],cwd=work,env=env,stdout=out,stderr=err,start_new_session=True)
            record['process_id'] = child.pid  # Local receipt only; not a publication artifact.
            try:
                record['returncode'] = child.wait(timeout=record['timeout_seconds'])
            except subprocess.TimeoutExpired:
                record['timed_out'] = True
                raise
            if record['returncode'] != 0:
                raise RuntimeError(record['name']+' returned nonzero')
    except BaseException as exc:
        primary = exc
        record['error'] = type(exc).__name__+': '+str(exc)
        if child is not None:
            record['cleanup_errors'] = stop_owned(child)
            record['returncode'] = child.returncode
    finally:
        # Stream finalization must never replace a timeout or primary child error.
        for stream in ('stdout','stderr'):
            try:
                record[stream+'_sha256'] = digest(evidence/record[stream])
            except Exception as exc:
                record.setdefault('finalization_errors',[]).append(type(exc).__name__+': '+str(exc))
                if primary is None:
                    primary = exc
    if primary is not None:
        raise primary


def execute(root):
    root = Path(root).resolve()
    startup(root,sys.flags.optimize)
    import consumer
    run = str(uuid.uuid4())
    evidence = root/'local-runs'/run
    work = evidence/'work'
    work.mkdir(parents=True,exist_ok=False)
    env = {'PATH':os.defpath,'LANG':'C','LC_ALL':'C','TZ':'UTC'}
    for key in ('HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR'):
        p = work/'environment'/key
        p.mkdir(parents=True)
        env[key] = str(p)
    receipt = {'schema':1,'run':run,'status':'INCOMPLETE','commands':[]}
    primary = None
    try:
        receipt['source_before'] = consumer.source_snapshot(root)
        for name in receipt['source_before']:
            target = work/name
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(root/name,target)
        consumer.need(consumer.same(consumer.source_snapshot(work),receipt['source_before']),'copy source mismatch')
        receipt['tools_before'] = tool_snapshot(env)
        plans = [('version',5,['cc','--version']),('build',60,consumer.BUILD),
                 ('fixture',20,['strace','-f','-e','trace=network','-o','network.trace','./queue_fixture',run])]
        for name,timeout,argv in plans:
            rec = {'name':name,'argv':argv,'timeout_seconds':timeout,'returncode':None,'timed_out':False,
                   'stdout':name+'.stdout','stderr':name+'.stderr'}
            receipt['commands'].append(rec)
            write_json(evidence/'receipt.json',receipt)
            command(rec,evidence,work,env)
            # A warning is retained, not silently certified. Main must review it.
            if name == 'version':
                consumer.need((evidence/'version.stdout').stat().st_size>0,'empty compiler version')
                consumer.need((evidence/'version.stderr').read_bytes()==b'','version diagnostic')
            if name == 'build':
                consumer.need((evidence/'build.stdout').read_bytes()==b'','unexpected build stdout')
                consumer.check_build_diagnostic((evidence/'build.stderr').read_bytes(),(root/'reviewed-build.stderr').read_bytes())
            if name == 'fixture':
                consumer.need((evidence/'fixture.stderr').read_bytes()==b'','fixture or tracer diagnostic')
                consumer.check_trace((work/'network.trace').read_bytes())
                records = consumer.check_raw((evidence/'fixture.stdout').read_bytes(),run)
                write_json(evidence/'parsed.json',records)
    except BaseException as exc:
        primary = exc
        receipt['error'] = type(exc).__name__+': '+str(exc)
    finally:
        # Failure evidence and first error survive best-effort post-run observations.
        for field,operation in (
            ('source_after',lambda:consumer.source_snapshot(root)),
            ('work_source_after',lambda:consumer.source_snapshot(work)),
            ('tools_after',lambda:tool_snapshot(env))):
            try:
                receipt[field] = operation()
            except Exception as exc:
                receipt[field] = {'unavailable':type(exc).__name__+': '+str(exc)}
                if primary is None:
                    primary = exc
        for name,field in (('queue_fixture','binary_sha256'),('network.trace','trace_sha256')):
            try:
                if not (work/name).is_file():
                    raise FileNotFoundError('artifact not created: '+name)
                shutil.copyfile(work/name,evidence/name)
                receipt[field] = digest(evidence/name)
            except Exception as exc:
                receipt[field] = None
                receipt.setdefault('artifact_errors',[]).append(type(exc).__name__+': '+str(exc))
                if primary is None:
                    primary = exc
        if (evidence/'parsed.json').is_file():
            receipt['parsed_sha256'] = digest(evidence/'parsed.json')
        try:
            consumer.need(consumer.same(receipt.get('source_before'),receipt.get('source_after')),'source after mismatch')
            consumer.need(consumer.same(receipt.get('source_before'),receipt.get('work_source_after')),'work source after mismatch')
            consumer.need(consumer.same(receipt.get('tools_before'),receipt.get('tools_after')),'tools after mismatch')
        except Exception as exc:
            if primary is None:
                primary = exc
        receipt['status'] = 'FAIL' if primary is not None else 'PASS'
        if primary is not None and 'error' not in receipt:
            receipt['error'] = type(primary).__name__+': '+str(primary)
        try:
            write_json(evidence/'receipt.json',receipt)
        except Exception as exc:
            if primary is None:
                primary = exc
    if primary is not None:
        raise primary
    try:
        result = consumer.verify(root,evidence)
        write_json(root/'summary.json',result)
    except BaseException as exc:
        receipt['status']='FAIL'; receipt['error']=type(exc).__name__+': '+str(exc)
        write_json(evidence/'receipt.json',receipt)
        (root/'summary.json').unlink(missing_ok=True)
        raise
    print(json.dumps(result,sort_keys=True))
    return evidence

if __name__ == '__main__':
    execute(Path(__file__).resolve().parent)
