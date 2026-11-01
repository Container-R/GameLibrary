"""Finite runner; native entry requires separately approved code review."""
import sys, os, json, hashlib, subprocess, signal, uuid
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
(ROOT/'summary.json').unlink(missing_ok=True)
if sys.flags.optimize: raise SystemExit('optimized runner rejected before native entry')
from isolation import prepare_environment, validate_environment
from oracle import need, load, check
BINARY='/usr/local/bin/godot'
EXPECTED='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3'
SOURCES=('PROTOCOL.md','main.gd','project.godot','run.py','oracle.py','consumer.py','test_pure.py','isolation.py')
def sha(b):return hashlib.sha256(b).hexdigest()
def sources():return {n:sha((ROOT/n).read_bytes()) for n in SOURCES}
def utc():return datetime.now(timezone.utc).isoformat()
def main():
    out=ROOT/'evidence'/str(uuid.uuid4());out.mkdir(parents=True,exist_ok=False)
    receipt={'status':'RUNNING','uuid':out.name,'processes':[],
             'original_source_directory':str(ROOT),'original_process_directory':str(out)}
    def save():(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    save()
    try:
        receipt['source_sha256']=sources();receipt['binary_before']=sha(Path(BINARY).read_bytes());save()
        need(receipt['binary_before']==EXPECTED,'binary identity')
        need(receipt['source_sha256']['PROTOCOL.md']=='7e5197e2368bb8be30c446b3a8ac1cc2274b781e77e2db8238a1788963d53dad','protocol pin before native')
        need(receipt['source_sha256']['isolation.py']=='bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970','helper identity')
        eroot=out/'environment';eroot.mkdir()
        base={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'}
        env,selected=prepare_environment(base,eroot)
        receipt.update(base_environment=base,selected_environment=selected);save()
        commands={'version':[BINARY,'--version'],'behavior':[BINARY,'--headless','--path',str(ROOT),'--single-threaded-scene','--script',str(ROOT/'main.gd')]}
        for name,argv in commands.items():
            validate_environment(env,eroot)
            p={'name':name,'argv':argv,'timeout_seconds':10 if name=='version' else 20,'status':'ATTEMPTED','attempted_utc':utc()}
            receipt['processes'].append(p);save();stdout=stderr=b''
            try:
                child=subprocess.Popen(argv,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
                p['pid']=child.pid;save()
                stdout,stderr=child.communicate(timeout=p['timeout_seconds'])
                p.update(status='RETURNED',returncode=child.returncode,returned_utc=utc())
            except subprocess.TimeoutExpired as e:
                stdout=e.stdout or b'';stderr=e.stderr or b''
                p.update(status='TIMEOUT',error=repr(e),returned_utc=utc())
                try:os.killpg(child.pid,signal.SIGKILL);p['cleanup_signal']='SIGKILL own group'
                except ProcessLookupError:p['cleanup_signal']='already absent'
                except OSError as e2:p['cleanup_error']=repr(e2)
                try:stdout,stderr=child.communicate(timeout=5);p['cleanup_returncode']=child.returncode
                except (subprocess.TimeoutExpired,OSError) as e2:p['cleanup_wait_error']=repr(e2)
                raise
            except OSError as e:
                p.update(status='LAUNCH_ERROR',error=repr(e),returned_utc=utc());raise
            finally:
                for stream,b in (('stdout',stdout),('stderr',stderr)):
                    if isinstance(b,str):b=b.encode()
                    (out/f'{name}.{stream}').write_bytes(b);p[stream+'_sha256']=sha(b)
                save()
            need(child.returncode==0 and stderr==b'','process exit/stderr '+name)
            if name=='version':need(stdout.strip()==b'4.6.3.stable.official.7d41c59c4','version string')
            else:
                from consumer import parse_stdout
                result=parse_stdout(stdout)
                receipt['oracle']=check(result)
                parsed=json.dumps(result,indent=2)+'\n';(out/'behavior.json').write_text(parsed)
                receipt['parsed_sha256']=sha(parsed.encode())
        receipt['binary_after']=sha(Path(BINARY).read_bytes());receipt['source_after']=sources()
        need(receipt['binary_before']==receipt['binary_after'] and receipt['source_sha256']==receipt['source_after'],'identity changed')
        receipt.update(status='PASS',behavior_processes=1,version_processes=1);save()
        from consumer import verify
        verify(ROOT,out)
        (ROOT/'summary.json').write_text(json.dumps({'status':'PASS','uuid':out.name,'receipt_sha256':sha((out/'receipt.json').read_bytes())},indent=2)+'\n')
        print(json.dumps({'status':'PASS','uuid':out.name,'behavior_processes':1,'version_processes':1}))
    except BaseException as e:
        receipt.update(status='FAIL',error=repr(e))
        for key,reader in [('source_after',sources),('binary_after',lambda:sha(Path(BINARY).read_bytes()))]:
            try:receipt[key]=reader()
            except Exception as problem:receipt.setdefault('unavailable_after',{})[key]=repr(problem)
        save();raise
if __name__=='__main__':main()
