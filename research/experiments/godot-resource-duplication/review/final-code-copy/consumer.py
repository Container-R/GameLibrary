"""Read-only exact-source evidence consumer; never launches an engine."""
import hashlib, json, uuid
from pathlib import Path
from datetime import datetime
from oracle import need, load, check, integer
BINARY='/usr/local/bin/godot'
BINARY_HASH='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3'
PROTOCOL='748ab0748d80145721fa8ca3095b0264bf393b47d3062da424fe60f5605a5d0c'
HELPER='bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970'
INPUTS=('project.godot','config.gd','config.tres','external.tres','main.gd')
SOURCES=INPUTS+('PROTOCOL.md','run.py','oracle.py','consumer.py','test_pure.py','isolation.py')
MODES=('shallow','internal','all')
KEYS=('HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR')
BANNER='Godot Engine v4.6.3.stable.official.7d41c59c4 - https://godotengine.org'
def sha(data):return hashlib.sha256(data).hexdigest()
def hashes(root,names):return {n:sha((Path(root)/n).read_bytes()) for n in names}
def parse_stdout(raw):
    lines=[s for s in raw.decode('utf-8',errors='strict').splitlines() if s]
    need(len(lines)==2 and lines[0]==BANNER and lines[1].startswith('RESULT_JSON:'),'exact stdout envelope')
    result=load(lines[1][len('RESULT_JSON:'):]);check(result);return result

def exact_json_equal(a,b):
    """JSON structural identity including scalar/container types, not Python coercion."""
    if type(a) is not type(b):return False
    if type(a) is dict:
        return set(a)==set(b) and all(exact_json_equal(a[k],b[k]) for k in a)
    if type(a) is list:
        return len(a)==len(b) and all(exact_json_equal(x,y) for x,y in zip(a,b))
    return a==b

def verify(root,out):
    root,out=Path(root),Path(out);r=load((out/'receipt.json').read_bytes())
    need(r['status']=='PASS' and str(uuid.UUID(r['uuid']))==out.name==r['uuid'],'successful UUID receipt')
    frozen=load((root/'SOURCE-SHA256.json').read_bytes())
    need(set(frozen)==set(SOURCES) and hashes(root,SOURCES)==frozen==r['source_sha256']==r['source_after'],'source bindings')
    need(frozen['PROTOCOL.md']==PROTOCOL and frozen['isolation.py']==HELPER,'protocol/helper pin')
    need(r['manifest_sha256']==sha((root/'SOURCE-SHA256.json').read_bytes()),'manifest binding')
    need(r['binary_before']==r['binary_after']==BINARY_HASH,'binary binding')
    old=Path(r['original_process_directory']);src=Path(r['original_source_directory'])
    need(src.is_absolute() and old==src/'evidence'/r['uuid'] and '..' not in old.parts,'original paths')
    need(r['base_environment']=={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'},'base environment')
    need(r['selected_environment']=={k:str(old/'environment'/k) for k in KEYS},'runtime isolation paths')
    need(integer(r['behavior_processes'])==3 and integer(r['version_processes'])==1,'counts')
    processes=r['processes'];need(type(processes) is list and len(processes)==4,'four processes')
    need(set(r['inputs_before'])==set(MODES) and r['inputs_before']==r['inputs_after'],'input maps unchanged')
    need(set(r['parsed_sha256'])==set(MODES) and set(r['oracle'])==set(MODES),'all parsed results')
    prev=None;results={}
    for p,name in zip(processes,('version',)+MODES):
        need(set(p)=={'name','argv','cwd','timeout_seconds','status','attempted_utc','pid','returncode','returned_utc','stdout_sha256','stderr_sha256'},'process schema')
        work=old/'projects'/name
        argv=[BINARY,'--version'] if name=='version' else [BINARY,'--headless','--path',str(work),'--script',str(work/'main.gd'),'--',name,r['uuid']]
        need(p['name']==name and p['argv']==argv and p['cwd']==str(old if name=='version' else work),'command binding')
        need(p['status']=='RETURNED' and integer(p['returncode'])==0 and integer(p['pid'])>0,'successful process')
        need(integer(p['timeout_seconds'])==(10 if name=='version' else 20),'timeout')
        start=datetime.fromisoformat(p['attempted_utc']);end=datetime.fromisoformat(p['returned_utc'])
        need(start.utcoffset() is not None and start.utcoffset().total_seconds()==0 and end.utcoffset()==start.utcoffset() and start<=end and (prev is None or prev<=start),'ordered UTC');prev=end
        raw=(out/f'{name}.stdout').read_bytes();err=(out/f'{name}.stderr').read_bytes()
        need(sha(raw)==p['stdout_sha256'] and sha(err)==p['stderr_sha256'] and err==b'','stream integrity')
        if name=='version':need(raw.strip()==b'4.6.3.stable.official.7d41c59c4','version banner');continue
        need(r['inputs_before'][name]=={n:frozen[n] for n in INPUTS}==hashes(out/'projects'/name,INPUTS),'copied inputs')
        actual=parse_stdout(raw)
        need(actual['mode']==name and actual['invocation_uuid']==r['uuid'] and actual['process_id']==p['pid'],'result process association')
        parsed=(out/f'{name}.json').read_bytes();need(sha(parsed)==r['parsed_sha256'][name] and exact_json_equal(load(parsed),actual),'raw/parsed association')
        results[name]=check(actual);need(exact_json_equal(results[name],r['oracle'][name]),'derived oracle')
    return results

def verify_summary(root):
    root=Path(root);s=load((root/'summary.json').read_bytes())
    need(set(s)=={'status','uuid','receipt_sha256'} and s['status']=='PASS','summary schema')
    need(str(uuid.UUID(s['uuid']))==s['uuid'],'summary UUID')
    out=root/'evidence'/s['uuid'];need(sha((out/'receipt.json').read_bytes())==s['receipt_sha256'],'summary binding')
    return verify(root,out)
if __name__=='__main__':
    import sys
    need(len(sys.argv)==2,'usage: consumer.py SOURCE_ROOT')
    print(json.dumps(verify_summary(sys.argv[1]),sort_keys=True))
