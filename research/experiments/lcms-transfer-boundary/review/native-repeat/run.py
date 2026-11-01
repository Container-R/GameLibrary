"""One separately authorized CMM child. Never run merely to inspect archives."""
import pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parent
SUMMARY=ROOT/'summary.json'
if __name__=='__main__':
 SUMMARY.unlink(missing_ok=True)
 if not __debug__:raise SystemExit('optimized runner rejected before local imports/native entry')
import datetime,json,os,signal,subprocess,uuid
from isolation import prepare_environment
from check import SOURCES,BASE,LIB,LIB_SHA,PROTOCOL,HELPER,REF_SHA,need,same,sha,parse_stdout,consume

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def manifest():return {n:sha(ROOT/n) for n in SOURCES}
def write(path,data):path.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+'\n')
def main():
 out=ROOT/'evidence'/str(uuid.uuid4());out.mkdir(parents=True,exist_ok=False)
 python=str(pathlib.Path(sys.executable).resolve())
 r={'status':'ATTEMPTED','uuid':out.name,'original_source':str(ROOT),'original_invocation':str(out),'python_path':python,'base_environment':BASE}
 p=None;stdout=b'';stderr=b''
 def save():write(out/'receipt.json',r)
 try:
  save()
  r.update(python_before=sha(python),source_before=manifest(),library_before=sha(LIB));save()
  need(r['source_before']['PROTOCOL.md']==PROTOCOL and r['source_before']['isolation.py']==HELPER and r['source_before']['protocol-reference.json']==REF_SHA,'fixed source pins')
  need(r['library_before']==LIB_SHA,'library pin')
  envroot=out/'environment';envroot.mkdir();env,selected=prepare_environment(BASE,envroot);r['selected_environment']=selected
  argv=[python,str(ROOT/'child.py')];r['process']={'status':'ATTEMPTED','argv':argv,'cwd':str(ROOT),'attempted_utc':utc()};save()
  p=subprocess.Popen(argv,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
  r['process'].update(status='RUNNING',pid=p.pid);save()
  try:stdout,stderr=p.communicate(timeout=20)
  except subprocess.TimeoutExpired as e:
   stdout=e.output or b'';stderr=e.stderr or b'';r['process']['timeout']=True
   raise ValueError('child timeout')
  r['process'].update(status='RETURNED',exit_code=p.returncode,returned_utc=utc())
  (out/'stdout.txt').write_bytes(stdout);(out/'stderr.txt').write_bytes(stderr)
  need(p.returncode==0 and stderr==b'','child exit/stderr')
  data=parse_stdout(stdout);write(out/'result.json',data)
  r.update(source_after=manifest(),library_after=sha(LIB),python_after=sha(python))
  same(r['source_after'],r['source_before'],'source after');same(r['library_after'],LIB_SHA,'library after');same(r['python_after'],r['python_before'],'Python after')
  r['outputs']={n:sha(out/n) for n in ('stdout.txt','stderr.txt','result.json')};r['status']='PASS';save()
  consume(ROOT,out)
  write(SUMMARY,{'status':'PASS','uuid':out.name,'receipt_sha256':sha(out/'receipt.json')})
  print(json.dumps({'status':'PASS','uuid':out.name,'owned_children':1,'conversion_calls':3}));return 0
 except BaseException as e:
  r['status']='FAIL';r['failure']=type(e).__name__+': '+str(e)
  if p is not None:
   if p.poll() is None:
    r['process']['cleanup_attempted_utc']=utc()
    try:os.killpg(p.pid,signal.SIGKILL);r['process']['killpg']='sent'
    except OSError as problem:r['process']['killpg_error']=str(problem)
    try:p.wait(timeout=3)
    except subprocess.TimeoutExpired:r['process']['wait_timeout']=True
   try:stdout,stderr=p.communicate(timeout=1)
   except subprocess.TimeoutExpired as problem:
    stdout=problem.output or stdout;stderr=problem.stderr or stderr;r['process']['drain_incomplete']=True
   code=p.poll();r['process']['exit_code']=code
   if code is None:r['process']['status']='UNRESOLVED'
   else:r['process']['status']='RETURNED';r['process'].setdefault('returned_utc',utc())
  (out/'stdout.txt').write_bytes(stdout);(out/'stderr.txt').write_bytes(stderr)
  for field,reader in (('source_after',manifest),('library_after',lambda:sha(LIB)),('python_after',lambda:sha(python))):
   r.pop(field,None)
   try:r[field]=reader()
   except Exception as problem:r.setdefault('unavailable_after',{})[field]=type(problem).__name__+': '+str(problem)
  r['outputs']={n:sha(out/n) for n in ('stdout.txt','stderr.txt')};save()
  print(json.dumps({'status':'FAIL','uuid':out.name,'failure':r['failure']}));return 1
if __name__=='__main__':raise SystemExit(main())
