"""Bounded four-process runner. Do not run until native authorization."""
import sys, json, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parent
# Clear success before local imports or optimized rejection.
(ROOT/'summary.json').unlink(missing_ok=True)
OUT=ROOT/'evidence'/str(uuid.uuid4());OUT.mkdir(parents=True,exist_ok=False)
receipt={'status':'RUNNING','uuid':OUT.name,'processes':[],
         'original_source_directory':str(ROOT),'original_process_directory':str(OUT)}
def save(): (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
save()
def main():
    try:
        if sys.flags.optimize:raise ValueError('optimized runner rejected before native entry')
        if len(sys.argv)!=1:raise ValueError('runner takes no arguments')
        import subprocess, os, signal, shutil
        from datetime import datetime,timezone
        from isolation import prepare_environment,validate_environment
        from oracle import need,load,check
        from consumer import BINARY,BINARY_HASH,PROTOCOL,HELPER,SOURCES,INPUTS,MODES,sha,hashes,parse_stdout,verify
        def utc():return datetime.now(timezone.utc).isoformat()
        receipt['source_sha256']=hashes(ROOT,SOURCES)
        manifest=(ROOT/'SOURCE-SHA256.json').read_bytes();receipt['manifest_sha256']=sha(manifest)
        need(load(manifest)==receipt['source_sha256'],'pre-native frozen manifest')
        need(receipt['source_sha256']['PROTOCOL.md']==PROTOCOL and receipt['source_sha256']['isolation.py']==HELPER,'protocol/helper pins')
        receipt['binary_before']=sha(Path(BINARY).read_bytes());save()
        need(receipt['binary_before']==BINARY_HASH,'binary identity')
        eroot=OUT/'environment';eroot.mkdir()
        base={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'}
        env,selected=prepare_environment(base,eroot)
        receipt.update(base_environment=base,selected_environment=selected,inputs_before={},inputs_after={},parsed_sha256={},oracle={});save()
        for mode in MODES:
            work=OUT/'projects'/mode;work.mkdir(parents=True)
            for name in INPUTS:shutil.copyfile(ROOT/name,work/name)
            receipt['inputs_before'][mode]=hashes(work,INPUTS)
            need(receipt['inputs_before'][mode]=={n:receipt['source_sha256'][n] for n in INPUTS},'fresh input copies')
        save()
        for name in ('version',)+MODES:
            work=OUT if name=='version' else OUT/'projects'/name
            argv=[BINARY,'--version'] if name=='version' else [BINARY,'--headless','--path',str(work),'--script',str(work/'main.gd'),'--',name,OUT.name]
            validate_environment(env,eroot)
            p={'name':name,'argv':argv,'cwd':str(work),'timeout_seconds':10 if name=='version' else 20,'status':'ATTEMPTED','attempted_utc':utc()}
            receipt['processes'].append(p);save();stdout=stderr=b''
            try:
                child=subprocess.Popen(argv,cwd=work,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
                p['pid']=child.pid;save()
                stdout,stderr=child.communicate(timeout=p['timeout_seconds'])
                p.update(status='RETURNED',returncode=child.returncode,returned_utc=utc())
            except subprocess.TimeoutExpired as error:
                stdout=error.stdout or b'';stderr=error.stderr or b''
                p.update(status='TIMEOUT',error=repr(error),returned_utc=utc())
                try:os.killpg(child.pid,signal.SIGKILL);p['cleanup_signal']='SIGKILL own process group'
                except ProcessLookupError:p['cleanup_signal']='already absent'
                except OSError as e:p['cleanup_error']=repr(e)
                try:stdout,stderr=child.communicate(timeout=5);p['cleanup_returncode']=child.returncode
                except (subprocess.TimeoutExpired,OSError) as e:p['cleanup_wait_error']=repr(e)
                raise
            except OSError as error:
                p.update(status='LAUNCH_ERROR',error=repr(error),returned_utc=utc());raise
            finally:
                for stream,data in (('stdout',stdout),('stderr',stderr)):
                    if isinstance(data,str):data=data.encode()
                    (OUT/f'{name}.{stream}').write_bytes(data);p[stream+'_sha256']=sha(data)
                save()
            need(p['returncode']==0 and stderr==b'','native return/diagnostics '+name)
            if name=='version':need(stdout.strip()==b'4.6.3.stable.official.7d41c59c4','version string')
            else:
                actual=parse_stdout(stdout)
                need(actual['mode']==name and actual['process_id']==p['pid'] and actual['invocation_uuid']==OUT.name,'native binding')
                receipt['oracle'][name]=check(actual)
                data=(json.dumps(actual,indent=2)+'\n').encode();(OUT/f'{name}.json').write_bytes(data)
                receipt['parsed_sha256'][name]=sha(data)
                receipt['inputs_after'][name]=hashes(work,INPUTS);save()
        receipt['source_after']=hashes(ROOT,SOURCES);receipt['binary_after']=sha(Path(BINARY).read_bytes())
        need(receipt['source_after']==receipt['source_sha256'] and receipt['binary_before']==receipt['binary_after'],'post identity')
        need(receipt['inputs_after']==receipt['inputs_before'],'input delta')
        receipt.update(status='PASS',behavior_processes=3,version_processes=1);save()
        verify(ROOT,OUT)
        (ROOT/'summary.json').write_text(json.dumps({'status':'PASS','uuid':OUT.name,'receipt_sha256':sha((OUT/'receipt.json').read_bytes())},indent=2)+'\n')
        print(json.dumps({'status':'PASS','uuid':OUT.name,'behavior_processes':3,'version_processes':1}))
    except BaseException as error:
        receipt.update(status='FAIL',error=repr(error))
        # Best effort after-identities even for partial native failure; no fallback success.
        try:
            from consumer import hashes,SOURCES,INPUTS,sha,BINARY
            receipt['source_after']=hashes(ROOT,SOURCES);receipt['binary_after']=sha(Path(BINARY).read_bytes())
            for mode in receipt.get('inputs_before',{}):receipt.setdefault('inputs_after',{})[mode]=hashes(OUT/'projects'/mode,INPUTS)
        except BaseException as after_error:receipt['unavailable_after']=repr(after_error)
        save();raise
if __name__=='__main__':main()
