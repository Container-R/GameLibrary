#!/usr/bin/env python3
"""Educational single-writer generation protocol and deterministic process-kill tests.
No power-loss simulation. All test stores and logs are under the supplied output path.
"""
import base64, errno, hashlib, json, os, pathlib, platform, shutil, signal, subprocess, sys, time
if not __debug__:
    print(json.dumps({'status':'unsupported_optimized_mode','reason':'validation assertions require normal interpreter mode'}), flush=True)
    sys.exit(4)
P = pathlib.Path
SLOT = 'demo-slot'
PHASES = ['half_chunk','data_done','manifest_done','validated','directories_synced','half_root','root_ready','before_replace','after_replace','root_synced','notified','cleanup_mid']
TRACE = None
STOP = None
FAULT = None

def enc(x): return (json.dumps(x, sort_keys=True, separators=(',',':'))+'\n').encode()
def digest(b): return hashlib.sha256(b).hexdigest()
def event(op, **kw):
    if TRACE:
        with open(TRACE,'a') as f: f.write(json.dumps({'op':op, **kw},sort_keys=True)+'\n'); f.flush()
def barrier(name):
    event('barrier',name=name)
    if STOP == name:
        print(json.dumps({'barrier':name}),flush=True)
        sys.stdin.readline()  # Parent kills this process, never acknowledges this barrier.
def read(p):
    b=p.read_bytes(); event('read',path=str(p),bytes=len(b),sha256=digest(b)); return b

def syncdir(p, final=False):
    fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY)
    try:
        if final and FAULT=='EIO':
            event('fsync_injected_error',path=str(p),errno=errno.EIO)
            raise OSError(errno.EIO,'injected directory fsync error')
        os.fsync(fd); event('fsync_dir',path=str(p),result=0)
    finally: os.close(fd)
def write(p,b,half=None,fail=False):
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    event('open_exclusive',path=str(p),result='ok')
    try:
        if fail and FAULT=='ENOSPC':
            event('write_injected_error',path=str(p),errno=errno.ENOSPC)
            raise OSError(errno.ENOSPC,'injected write error')
        pos=0
        if half:
            n=os.write(fd,b[:len(b)//2]); pos=n
            event('write',path=str(p),requested=len(b)//2,returned=n)
            barrier(half)
        while pos<len(b):
            n=os.write(fd,b[pos:]); event('write',path=str(p),requested=len(b)-pos,returned=n)
            if n<=0: raise OSError('zero write')
            pos+=n
        os.fsync(fd); event('fsync_file',path=str(p),result=0)
    finally:
        os.close(fd); event('close',path=str(p),result=0)

def objects(g):
    revision={'A':1,'B':2,'C':3}[g]
    common={'slot':SLOT,'generation':g,'revision':revision,'schema':1}
    chunks=['town','old'] if g=='A' else ['town','new']
    return {'metadata.json':{**common,'role':'metadata','chunks':chunks},
            'character.json':{**common,'role':'character','key':g!='A'},
            **{f'chunks/{c}.json':{**common,'role':'chunk','id':c,'claimed':g!='A' if c=='town' else False} for c in chunks}}

def envelope(body): return {'body':body,'sha256':digest(enc(body))}
def parse_root(store):
    r=json.loads(read(store/'CURRENT'))
    assert set(r)=={'body','sha256'} and digest(enc(r['body']))==r['sha256'],'root checksum'
    b=r['body']; assert set(b)=={'version','slot','active','previous'} and b['version']==1 and b['slot']==SLOT,'root identity/schema'
    for ref in [b['active'],b['previous']]:
        if ref is None: continue
        assert set(ref)=={'generation','manifest_sha256'},'root reference shape'
        assert isinstance(ref['generation'],str) and ref['generation'].isalnum(),'unsafe generation'
        assert isinstance(ref['manifest_sha256'],str) and len(ref['manifest_sha256'])==64,'bad manifest digest'
    assert b['active'] is not None,'no active root'
    return b

def validate(store,ref):
    g=ref['generation']; folder=store/'generations'/g
    assert not folder.is_symlink(),'symlink generation'
    raw=read(folder/'manifest.json'); assert digest(raw)==ref['manifest_sha256'],'manifest digest'
    m=json.loads(raw)
    assert m['version']==1 and m['slot']==SLOT and m['generation']==g and m['schema']==1,'manifest identity/schema'
    assert isinstance(m['revision'],int) and m['revision']>0,'revision'
    files=m['files']; assert isinstance(files,list),'files list'
    seen=set(); data={}
    for entry in files:
        path=entry['path']; parts=path.split('/')
        assert path not in seen and not path.startswith('/') and all(x not in ('','.','..') for x in parts),'duplicate/unsafe path'
        seen.add(path)
        q=folder
        for part in parts:
            q=q/part; assert not q.is_symlink(),'symlink object'
        raw=read(q); assert len(raw)==entry['length'] and digest(raw)==entry['sha256'],'object bytes'
        obj=json.loads(raw)
        assert all(obj[k]==m[k] for k in ['slot','generation','schema','revision']),'object identity/schema'
        assert obj['role']==entry['role'],'object role'
        data[path]=obj
    meta=data['metadata.json']; char=data['character.json']
    assert meta['role']=='metadata' and char['role']=='character','required roles'
    chunks=meta['chunks']; assert len(chunks)==len(set(chunks)) and 'town' in chunks,'chunk closure'
    assert all(isinstance(c,str) and c.isalnum() for c in chunks),'chunk identifiers'
    assert seen=={'metadata.json','character.json'}|{f'chunks/{c}.json' for c in chunks},'chunk closure'
    for c in chunks:
        obj=data[f'chunks/{c}.json']; assert obj['role']=='chunk' and obj['id']==c,'chunk role/id'
        assert type(obj['claimed']) is bool,'claimed type'
    assert type(char['key']) is bool and char['key']==data['chunks/town.json']['claimed'],'key/chest invariant'
    return {'generation':g,'revision':m['revision'],'key':char['key'],'chunks':sorted(chunks),'claimed':data['chunks/town.json']['claimed']}

def save(store,g,parent):
    previous=None
    if (store/'CURRENT').exists():
        root=parse_root(store)
        if root['active']['generation']==g:
            validate(store,root['active']); return {'status':'observed_active','generation':g,'durability':'not_established','requires_resolution':True}
        assert root['active']['generation']==parent,'stale expected parent'
        validate(store,root['active']); previous=root['active']
    else: assert parent is None,'missing expected parent'
    folder=store/'generations'/g
    if folder.exists():
        return {'status':'candidate_exists','generation':g,'publication':'not_attempted','requires_resolution':True}
    folder.mkdir(); (folder/'chunks').mkdir(); event('mkdir',path=str(folder))
    files=[]
    for path,obj in objects(g).items():
        b=enc(obj); write(folder/path,b,half='half_chunk' if path=='chunks/town.json' else None,fail=path=='character.json')
        files.append({'path':path,'role':obj['role'],'length':len(b),'sha256':digest(b)})
    barrier('data_done')
    m={'version':1,'slot':SLOT,'generation':g,'parent':parent,'schema':1,'revision':objects(g)['metadata.json']['revision'],'files':files}
    b=enc(m); write(folder/'manifest.json',b); ref={'generation':g,'manifest_sha256':digest(b)}
    barrier('manifest_done'); validate(store,ref); barrier('validated')
    for d in [folder/'chunks',folder,store/'generations',store]: syncdir(d)
    barrier('directories_synced')
    body={'version':1,'slot':SLOT,'active':ref,'previous':previous}
    tmp=store/f'CURRENT.{g}.tmp'; b=enc(envelope(body)); write(tmp,b,half='half_root')
    assert read(tmp)==b,'temporary root changed'
    barrier('root_ready'); barrier('before_replace')
    os.replace(tmp,store/'CURRENT'); event('replace',source=str(tmp),destination=str(store/'CURRENT'),result=0)
    barrier('after_replace'); syncdir(store,final=True); barrier('root_synced')
    event('acknowledgement',generation=g); barrier('notified')
    # A separate unreferenced test garbage directory, never a retained generation.
    junk=store/'garbage'
    if junk.exists():
        (junk/'one').unlink(); event('unlink',path=str(junk/'one')); barrier('cleanup_mid')
        (junk/'two').unlink(); junk.rmdir()
    return {'status':'published_visible','generation':g,'final_directory_sync':'returned_success','durability':'platform_contract_required'}

def recover(store):
    live={'generation':'LIVE','sentinel':'unchanged'}
    result={'memory_before':live.copy(),'errors':[]}
    try: root=parse_root(store)
    except Exception as e:
        return {**result,'status':'refused','reason':'root_invalid','errors':[str(e)],'memory_after':live}
    for label,ref in [('active',root['active']),('previous',root['previous'])]:
        if ref is None: continue
        try:
            candidate=validate(store,ref); barrier('recovery_validated')
            # Decoding and reconstruction are private. No live mutation in validate().
            barrier('before_memory_swap'); live=candidate
            return {**result,'status':'loaded' if label=='active' else 'fallback','selected':live['generation'],'memory_after':live}
        except Exception as e: result['errors'].append(label+': '+str(e))
    return {**result,'status':'refused','reason':'no_valid_published_root','memory_after':live}

def snapshot(store):
    out={}
    for p in sorted(store.rglob('*')):
        if p.is_file():
            b=p.read_bytes(); out[str(p.relative_to(store))]={'length':len(b),'sha256':digest(b)}
    return {'files':out,'CURRENT_base64':base64.b64encode((store/'CURRENT').read_bytes()).decode()}

def run_child(store,mode,g=None,parent=None,stop=None,fault=None,log=None):
    cmd=[sys.executable,str(P(__file__).resolve()),'worker',mode,str(store),g or '-',parent or '-',stop or '-',fault or '-',str(log)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if stop:
        line=proc.stdout.readline()
        if not line: raise RuntimeError('worker exited before barrier: '+proc.stderr.read())
        assert json.loads(line)=={'barrier':stop},line
        proc.kill(); stdout,stderr=proc.communicate(timeout=20)
        return {'command':cmd,'barrier':json.loads(line),'exit_code':proc.returncode,'stdout':stdout,'stderr':stderr}
    stdout,stderr=proc.communicate(timeout=20)
    return {'command':cmd,'exit_code':proc.returncode,'stdout':stdout,'stderr':stderr,'result':json.loads(stdout) if stdout.strip() else None}

def init(store):
    store.mkdir(parents=True); (store/'generations').mkdir(); save(store,'A',None)
    (store/'garbage').mkdir(); (store/'garbage/one').write_text('orphan'); (store/'garbage/two').write_text('orphan')

def rewrite_object(store,path,mutate):
    root=parse_root(store); ref=root['active']; folder=store/'generations'/ref['generation']
    obj=json.loads((folder/path).read_bytes()); mutate(obj); b=enc(obj); (folder/path).write_bytes(b)
    m=json.loads((folder/'manifest.json').read_bytes())
    for e in m['files']:
        if e['path']==path: e.update(length=len(b),sha256=digest(b))
    mb=enc(m); (folder/'manifest.json').write_bytes(mb); ref['manifest_sha256']=digest(mb)
    (store/'CURRENT').write_bytes(enc(envelope(root)))

def suite(out):
    out.mkdir(parents=True,exist_ok=False)
    env={'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'python':sys.version,'uname':list(platform.uname()),'platform':platform.platform(),'fixture_sha256':digest(P(__file__).read_bytes()),'plan_sha256':digest(P(__file__).with_name('experiment-plan.md').read_bytes()),'cwd':os.getcwd(),'statvfs':list(os.statvfs(out))}
    (out/'environment.json').write_bytes(enc(env))
    (out/'mountinfo.txt').write_text(P('/proc/self/mountinfo').read_text())
    results=[]
    def add(name,obs,passed):
        row={'case':name,'observed':obs,'passed':bool(passed)};results.append(row)
        with open(out/'results.jsonl','a') as f:f.write(json.dumps(row,sort_keys=True)+'\n')
    for repeat in range(3):
        for i,phase in enumerate(PHASES):
            name=f'kill-{repeat}-{phase}'; store=out/name; init(store)
            killed=run_child(store,'save','B','A',stop=phase,log=out/(name+'.save.jsonl'))
            rec=run_child(store,'recover',log=out/(name+'.recover.jsonl'))
            expected='A' if i<PHASES.index('after_replace') else 'B'
            obs={'writer':killed,'recovery':rec,'snapshot':snapshot(store),'expected':expected}
            r=rec['result']; add(name,obs,killed['exit_code']==-signal.SIGKILL and r['selected']==expected and r['memory_after']['key']==(expected=='B') and r['memory_after']['chunks']==(['old','town'] if expected=='A' else ['new','town']))
    # Independent-path baseline: publish character B, leave parseable A chunks.
    store=out/'baseline'; init(store)
    bad=run_child(store,'baseline',stop='mixed',log=out/'baseline.save.jsonl')
    data=[json.loads((store/p).read_bytes()) for p in ['character.json','town.json']]
    add('independent_paths',{'writer':bad,'all_parseable':True,'character':data[0],'town':data[1],'snapshot':snapshot(store)},data[0]['key']!=data[1]['claimed'])
    for case in ['unpublished','missing','foreign_chunk','wrong_slot','unknown_schema','truncated_root','semantic','closure','both_bad']:
        store=out/case; init(store)
        writer=run_child(store,'save','B','A',stop='before_replace' if case=='unpublished' else None,log=out/(case+'.save.jsonl'))
        folder=store/'generations/B'
        if case in ['missing','both_bad']:(folder/'chunks/town.json').unlink()
        if case=='both_bad':(store/'generations/A/character.json').unlink()
        if case=='foreign_chunk':shutil.copyfile(store/'generations/A/chunks/town.json',folder/'chunks/town.json')
        if case=='wrong_slot':rewrite_object(store,'character.json',lambda o:o.update(slot='wrong-slot'))
        if case=='unknown_schema':rewrite_object(store,'character.json',lambda o:o.update(schema=999))
        if case=='semantic':rewrite_object(store,'character.json',lambda o:o.update(key=False))
        if case=='closure':rewrite_object(store,'metadata.json',lambda o:o.update(chunks=['town','new','missing']))
        if case=='truncated_root':(store/'CURRENT').write_bytes(b'{"body":')
        before=snapshot(store); rec=run_child(store,'recover',log=out/(case+'.recover.jsonl')); after=snapshot(store); r=rec['result']
        expected='refused' if case in ['truncated_root','both_bad'] else 'loaded' if case=='unpublished' else 'fallback'
        passed=r['status']==expected and before==after
        passed &= r.get('selected')=='A' if expected!='refused' else r['memory_after']==r['memory_before']
        add(case,{'writer':writer,'recovery':rec,'snapshot':after,'disk_unchanged':before==after},passed)
    store=out/'retry'; init(store)
    save(store,'B','A'); same=run_child(store,'save','B','A',log=out/'retry.same.jsonl')
    save(store,'C','B'); before=snapshot(store); stale=run_child(store,'save','B','A',log=out/'retry.stale.jsonl'); after=snapshot(store)
    r=recover(store); add('retry',{'same':same,'stale':stale,'recovery':r,'snapshot':after,'disk_unchanged':before==after},same['exit_code']==3 and same['result']['status']=='observed_active' and same['result']['durability']=='not_established' and stale['exit_code']!=0 and before==after and r['selected']=='C')
    for phase in ['recovery_validated','before_memory_swap']:
        store=out/phase; init(store); save(store,'B','A'); before=snapshot(store)
        killed=run_child(store,'recover',stop=phase,log=out/(phase+'.killed.jsonl')); after=snapshot(store)
        r=run_child(store,'recover',log=out/(phase+'.recover.jsonl'))
        add(phase,{'worker':killed,'recovery':r,'disk_unchanged':before==after,'snapshot':after},before==after and r['result']['selected']=='B')
    for fault in ['ENOSPC','EIO']:
        store=out/fault; init(store)
        writer=run_child(store,'save','B','A',fault=fault,log=out/(fault+'.save.jsonl')); r=run_child(store,'recover',log=out/(fault+'.recover.jsonl'))
        add(fault,{'writer':writer,'recovery':r,'snapshot':snapshot(store),'result_class':'not_published' if fault=='ENOSPC' else 'publication_visible_durability_unknown'},writer['exit_code']!=0 and r['result']['selected']==('A' if fault=='ENOSPC' else 'B'))
    summary={'cases':len(results),'passed':sum(x['passed'] for x in results),'failed':[x['case'] for x in results if not x['passed']]}
    (out/'summary.json').write_bytes(enc(summary));print(json.dumps(summary));return 0 if not summary['failed'] else 1

if __name__=='__main__':
    if sys.argv[1]=='suite':sys.exit(suite(P(sys.argv[2]).resolve()))
    _,_,mode,path,g,parent,stop,fault,log=sys.argv
    STOP=None if stop=='-' else stop; FAULT=None if fault=='-' else fault; TRACE=log
    store=P(path)
    try:
        if mode=='save': result=save(store,g,None if parent=='-' else parent)
        elif mode=='recover':result=recover(store)
        elif mode=='baseline':
            (store/'character.json').write_bytes(enc(objects('A')['character.json']))
            (store/'town.json').write_bytes(enc(objects('A')['chunks/town.json']))
            write(store/'character.tmp',enc(objects('B')['character.json']))
            os.replace(store/'character.tmp',store/'character.json');event('replace_baseline_character',result=0);barrier('mixed')
            result={}
        print(json.dumps(result),flush=True)
        if result.get('requires_resolution'): sys.exit(3)
    except Exception as e:
        event('exception',type=type(e).__name__,message=str(e));print(json.dumps({'error':str(e),'type':type(e).__name__}),flush=True);sys.exit(2)
