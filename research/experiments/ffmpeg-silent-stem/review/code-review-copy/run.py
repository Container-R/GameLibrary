"""Finite native runner. Separate authorization is required before invocation."""
import sys
import json
import uuid
from pathlib import Path
ROOT = Path(__file__).resolve().parent
# Fail-closed even when optimized or a local dependency cannot import.
(ROOT / 'summary.json').unlink(missing_ok=True)
OUT = ROOT / 'evidence' / str(uuid.uuid4())
OUT.mkdir(parents=True, exist_ok=False)
r = {'status':'RUNNING', 'uuid':OUT.name, 'original_directory':str(OUT), 'processes':[]}

def save():
    (OUT / 'receipt.json').write_text(json.dumps(r, indent=2, allow_nan=False) + '\n')
save()

def main():
    try:
        if sys.flags.optimize: raise ValueError('optimized runner rejected before native entry')
        if len(sys.argv) != 1: raise ValueError('runner accepts no arguments')
        import os
        import signal
        import subprocess
        from datetime import datetime, timezone
        from isolation import prepare_environment, validate_environment
        from signals import inputs, check
        from consumer import (BIN, LIB, PINS, PROTOCOL, HELPER, BASE, MODES, SOURCES,
                              need, sha, load, exact, hashes, archive, argv_for, verify, BANNER)
        def utc(): return datetime.now(timezone.utc).isoformat()
        def tools(): return {p:sha(Path(p).read_bytes()) for p in (BIN,LIB)}
        data = inputs()
        def ih(): return {k:sha((OUT / (k+'.f32le')).read_bytes()) for k in data}
        manifest_raw = (ROOT / 'SOURCE-SHA256.json').read_bytes()
        frozen = load(manifest_raw)
        r.update(manifest_sha256=sha(manifest_raw), source_before=hashes(ROOT), tools_before=tools(), inputs={}, outputs={})
        save()
        need(exact(frozen,r['source_before']), 'frozen source manifest')
        need(frozen['PROTOCOL.md']==PROTOCOL and frozen['isolation.py']==HELPER, 'protocol/helper pins')
        need(exact(r['tools_before'],PINS), 'selected tool pins')
        # Independent consumer table verifies generated inputs before native entry.
        from consumer import inputs as independent_inputs
        need(exact(data,independent_inputs()), 'literal input pins')
        for name,raw in data.items():
            with (OUT / (name+'.f32le')).open('xb') as f: f.write(raw)
            r['inputs'][name] = archive(OUT,name,raw)
        initial = ih(); save()
        for mode in ('version',) + MODES:
            envroot = OUT / 'environment' / mode
            envroot.mkdir(parents=True, exist_ok=False)
            env,_ = prepare_environment(BASE,envroot)
            validate_environment(env,envroot)
            need(ih()==initial,'inputs changed before process')
            output = OUT / (mode+'.f32le')
            need(not output.exists() and not output.is_symlink(),'fresh output')
            p = {'name':mode,'argv':argv_for(mode,OUT),'cwd':str(OUT),'environment':env,
                 'timeout_seconds':20,'status':'ATTEMPTED','attempted_utc':utc(),'inputs_before':ih()}
            r['processes'].append(p); save()
            stdout=stderr=b''
            try:
                child = subprocess.Popen(p['argv'],cwd=OUT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
                p['pid']=child.pid;save()
                stdout,stderr=child.communicate(timeout=20)
                p.update(status='RETURNED',returncode=child.returncode,returned_utc=utc())
            except subprocess.TimeoutExpired as error:
                stdout,stderr=error.stdout or b'',error.stderr or b''
                p.update(status='TIMEOUT',error=repr(error),timeout_observed_utc=utc())
                try: os.killpg(child.pid,signal.SIGKILL); p['cleanup_signal']='SIGKILL own process group'
                except ProcessLookupError: p['cleanup_signal']='already absent'
                except OSError as error: p['cleanup_signal_error']=repr(error)
                try:
                    stdout,stderr=child.communicate(timeout=5)
                    p.update(cleanup_returncode=child.returncode,cleanup_returned_utc=utc())
                except (subprocess.TimeoutExpired,OSError) as error: p['cleanup_wait_error']=repr(error)
                raise
            except OSError as error:
                p.update(status='LAUNCH_ERROR',error=repr(error),failure_observed_utc=utc()); raise
            finally:
                for stream,raw in (('stdout',stdout),('stderr',stderr)):
                    (OUT / (mode+'.'+stream)).write_bytes(raw)
                    p[stream+'_sha256']=sha(raw)
                p['inputs_after']=ih();save()
            need(p['returncode']==0 and stderr==b'','native return/diagnostics')
            need(p['inputs_after']==initial,'inputs changed during process')
            if mode=='version':
                first=stdout.splitlines()[0] if stdout else b''
                need(first==BANNER or first.startswith(BANNER+b' '),'version identity')
            else:
                need(stdout==b'','unexpected mix stdout')
                raw=output.read_bytes()
                # Retain complete reversible output even if waveform check fails.
                r['outputs'][mode]={'archive':archive(OUT,mode,raw)};save()
                r['outputs'][mode]['check']=check(mode,raw);save()
        r['source_after']=hashes(ROOT); r['tools_after']=tools();save()
        need(exact(r['source_before'],r['source_after']) and exact(r['tools_after'],PINS),'after pins')
        need((ROOT/'SOURCE-SHA256.json').read_bytes()==manifest_raw,'manifest changed')
        r['status']='PASS'; save()
        verify(ROOT,summary_required=False,invocation=OUT.name)
        summary={'status':'PASS','uuid':OUT.name,'receipt_sha256':sha((OUT/'receipt.json').read_bytes()),'processes':4,'mixing_conditions':3}
        (ROOT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
        print(json.dumps(summary,sort_keys=True))
    except BaseException as error:
        r['status']='FAIL'; r['error']=repr(error);save()
        (ROOT/'summary.json').unlink(missing_ok=True)
        print('FAIL '+OUT.name+': '+repr(error),file=sys.stderr)
        return 1
    return 0

if __name__=='__main__': sys.exit(main())
