"""One authorized finite attempt only. Imports do not launch tools."""
import pathlib
import sys
ROOT=pathlib.Path(__file__).resolve().parent
SUMMARY=ROOT/'summary.json'
if __name__=='__main__':
    SUMMARY.unlink(missing_ok=True)
    if not __debug__:
        raise SystemExit('optimized runner rejected before native entry')
import datetime
import hashlib
import json
import os
import selectors
import signal
import subprocess
import time
import uuid
from isolation import prepare_environment
from oracle import SOURCES, BASE_ENV, BINARY, VERSION, PROTOCOL, HELPER, require, equal, ready, parse_stream, check_payloads
EXE='/usr/local/bin/godot'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def manifest(): return {name:sha(ROOT/name) for name in SOURCES}
def write(path,value): path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')

def mark_return(item, code, observed_utc):
    item['exit_code']=code
    if code is None:
        item['status']='UNRESOLVED'
        item['last_observed_utc']=observed_utc
    else:
        item['status']='RETURNED'
        item.setdefault('returned_utc',observed_utc)

def main():
    out=ROOT/'evidence'/str(uuid.uuid4()); out.mkdir(parents=True,exist_ok=False)
    stop=out/'STOP'; require(not stop.exists(),'STOP initially absent')
    receipt={'uuid':out.name,'original_source_root':str(ROOT),'original_invocation':str(out),'status':'ATTEMPTED','processes':[], 'orchestration':[], 'source_before':manifest(), 'binary_before':sha(pathlib.Path(EXE)), 'base_environment':BASE_ENV, 'stop_initially_absent':True}
    children={}; buffers={}; selector=selectors.DefaultSelector()
    def save(): write(out/'receipt.json',receipt)
    def log(kind,**fields): receipt['orchestration'].append(dict(kind=kind,**fields)); save()
    def launch(name,argv):
        envroot=out/'environment'/name; envroot.mkdir(parents=True,exist_ok=False)
        env,selected=prepare_environment(BASE_ENV,envroot)
        item={'name':name,'argv':argv,'cwd':str(ROOT),'selected_environment':selected,'attempted_utc':utc(),'status':'ATTEMPTED'}
        receipt['processes'].append(item); buffers[name]={'stdout':bytearray(),'stderr':bytearray()}; log('ATTEMPT',name=name)
        child=subprocess.Popen(argv,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
        item.update(pid=child.pid,status='RUNNING');children[name]=(child,item);save()
        return child,item
    def finish(name):
        child,item=children[name]
        mark_return(item,child.poll(),utc())
        for stream,data in buffers[name].items(): (out/(name+'.'+stream)).write_bytes(data)
        save()
    try:
        require(receipt['binary_before']==BINARY,'binary pin')
        require(receipt['source_before']['protocol.md']==PROTOCOL and receipt['source_before']['isolation.py']==HELPER,'protocol/helper pin')
        p,item=launch('version',[EXE,'--version'])
        try:
            stdout,stderr=p.communicate(timeout=20)
        except subprocess.TimeoutExpired:
            raise ValueError('version timeout')
        buffers['version']={'stdout':bytearray(stdout),'stderr':bytearray(stderr)};finish('version')
        require(p.returncode==0 and stderr==b'' and stdout.strip()==VERSION.encode(),'version output')
        log('VERSION_ACCEPTED')
        deadline=time.monotonic()+20
        def launch_role(role):
            p,_=launch(role,[EXE,'--headless','--path',str(ROOT),'--single-threaded-scene','--script',str(ROOT/'main.gd'),'--',role,str(stop)])
            for stream in ('stdout','stderr'):
                pipe=getattr(p,stream);os.set_blocking(pipe.fileno(),False);selector.register(pipe,selectors.EVENT_READ,(role,stream))
        launch_role('server'); client_started=False; released=False
        while selector.get_map():
            remaining=deadline-time.monotonic();require(remaining>0,'behavior shared timeout')
            for key,_mask in selector.select(remaining):
                role,stream=key.data
                chunk=os.read(key.fileobj.fileno(),65536)
                if not chunk:
                    selector.unregister(key.fileobj);key.fileobj.close();continue
                buffers[role][stream].extend(chunk)
                require(sum(len(x) for b in buffers.values() for x in b.values())<1024*1024,'bounded raw output')
                require(not buffers[role]['stderr'],'nonempty behavior stderr')
                raw=bytes(buffers[role]['stdout']);complete=raw[:raw.rfind(b'\n')+1]
                events,results=parse_stream(complete,b'',complete=False)
                if role=='server' and not client_started and any(e.get('kind')=='READY' for e in events):
                    require(len(events)>=2,'server startup events')
                    from oracle import startup
                    equal(events[:2],startup('server',2),'server startup before client')
                    log('SERVER_READY_ACCEPTED'); launch_role('client');client_started=True
                finals={}
                for name in ('server','client'):
                    if name not in buffers:continue
                    raw=bytes(buffers[name]['stdout']);prefix=raw[:raw.rfind(b'\n')+1]
                    _,rs=parse_stream(prefix,bytes(buffers[name]['stderr']),complete=False)
                    if rs:finals[name]=rs[0]
                if len(finals)==2 and not released:
                    for name in ('server','client'):
                        raw=bytes(buffers[name]['stdout']);prefix=raw[:raw.rfind(b'\n')+1]
                        parse_stream(prefix,bytes(buffers[name]['stderr']),complete=True)
                    check_payloads(finals['server'],finals['client'])
                    log('BOTH_TERMINALS_ACCEPTED')
                    with stop.open('x') as handle: handle.write('coordinator terminal release\n')
                    released=True;log('STOP_CREATED')
            for name,(child,item) in list(children.items()):
                if name=='version':continue
                if child.poll() is not None:
                    require(released,'behavior exited before terminal release')
                    require(child.returncode==0,'behavior nonzero exit')
        require(client_started and released,'complete terminal release')
        for name in ('server','client'):
            child,_=children[name];child.wait(timeout=max(.001,deadline-time.monotonic()));finish(name)
            require(child.returncode==0,'behavior final exit')
            _,rs=parse_stream(bytes(buffers[name]['stdout']),bytes(buffers[name]['stderr']))
            write(out/(name+'.json'),rs[0])
        receipt['source_after']=manifest();receipt['binary_after']=sha(pathlib.Path(EXE))
        equal(receipt['source_after'],receipt['source_before'],'source identity')
        require(receipt['binary_after']==BINARY,'binary after')
        receipt.update(status='PASS',version_processes=1,behavior_processes=2)
        receipt['output_sha256']={p.name:sha(p) for p in out.iterdir() if p.suffix in ('.stdout','.stderr') or p.name in ('server.json','client.json')}
        save()
        from consumer import consume
        consume(ROOT,out)
        write(SUMMARY,{'status':'PASS','uuid':out.name,'receipt_sha256':sha(out/'receipt.json')})
        print(json.dumps({'status':'PASS','uuid':out.name,'version_processes':1,'behavior_processes':2}))
    except BaseException as error:
        receipt['status']='FAIL';receipt['failure']=type(error).__name__+': '+str(error)
        for name,(child,item) in children.items():
            if child.poll() is None:
                item['cleanup_attempted_utc']=utc()
                try: os.killpg(child.pid,signal.SIGKILL);item['killpg']='sent'
                except OSError as problem:item['killpg_error']=str(problem)
                try: child.wait(timeout=3)
                except subprocess.TimeoutExpired:item['wait_timeout']=True
            if name=='version' and item.get('status')!='RETURNED':
                try:
                    tailout,tailerr=child.communicate(timeout=.5)
                    buffers[name]={'stdout':bytearray(tailout or b''),'stderr':bytearray(tailerr or b'')}
                except subprocess.TimeoutExpired as problem:
                    buffers[name]={'stdout':bytearray(problem.output or b''),'stderr':bytearray(problem.stderr or b'')}
                    item['drain_error']='version drain timeout'
        drain_deadline=time.monotonic()+1
        while selector.get_map() and time.monotonic()<drain_deadline:
            for key,_ in selector.select(max(0,drain_deadline-time.monotonic())):
                name,stream=key.data
                try: chunk=os.read(key.fileobj.fileno(),65536)
                except OSError as problem:
                    children[name][1]['drain_error']=str(problem);chunk=b''
                if chunk: buffers[name][stream].extend(chunk)
                else: selector.unregister(key.fileobj);key.fileobj.close()
        if selector.get_map():receipt['drain_incomplete']=True
        for name in children: finish(name)
        for name in buffers:
            for stream,data in buffers[name].items(): (out/(name+'.'+stream)).write_bytes(data)
        receipt['source_after']=manifest();receipt['binary_after']=sha(pathlib.Path(EXE))
        receipt['attempted_processes']=len(receipt['processes']);receipt['launched_processes']=len(children)
        receipt['output_sha256']={p.name:sha(p) for p in out.iterdir() if p.suffix in ('.stdout','.stderr')}
        save();print(json.dumps({'status':'FAIL','uuid':out.name,'failure':receipt['failure']}));return 1
    finally: selector.close()
    return 0
if __name__=='__main__': raise SystemExit(main())
