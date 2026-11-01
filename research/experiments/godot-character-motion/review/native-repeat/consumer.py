"""Portable exact-source archive checker; no installed engine dependency/authentication."""
import hashlib, uuid, json
from datetime import datetime
from pathlib import Path
from oracle import need, load, check
SOURCES={'PROTOCOL.md','main.gd','project.godot','run.py','oracle.py','consumer.py','test_pure.py','isolation.py'}
def sha(b):return hashlib.sha256(b).hexdigest()
def parse_stdout(raw):
    text=raw.decode('utf-8',errors='strict')
    lines=[line for line in text.splitlines() if line]
    need(len(lines)==2,'stdout exact banner plus result')
    need(lines[0]=='Godot Engine v4.6.3.stable.official.7d41c59c4 - https://godotengine.org','engine banner')
    need(lines[1].startswith('RESULT_JSON='),'single result')
    obj=load(lines[1][len('RESULT_JSON='):]);check(obj);return obj

def verify(root,out):
    root,out=Path(root),Path(out);r=load((out/'receipt.json').read_text())
    need(r['status']=='PASS','not PASS')
    need(str(uuid.UUID(r['uuid']))==out.name==r['uuid'],'UUID association')
    need(set(r['source_sha256'])==SOURCES and r['source_after']==r['source_sha256'],'source set/delta')
    for name,h in r['source_sha256'].items():need(sha((root/name).read_bytes())==h,'source hash')
    need(r['source_sha256']['PROTOCOL.md']=='193a8a05c6034ed59152b5c6c948139a1bc4c44068a27232ce38b1b971cfca41','protocol pin')
    need(r['source_sha256']['isolation.py']=='bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970','helper pin')
    need(r['binary_before']==r['binary_after']=='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3','recorded binary')
    old=Path(r['original_process_directory']);src=Path(r['original_source_directory'])
    need(old.is_absolute() and src.is_absolute() and '..' not in old.parts and '..' not in src.parts and old==src/'evidence'/r['uuid'],'recorded path association')
    need(r['base_environment']=={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'},'base env')
    need(r['selected_environment']=={k:str(old/'environment'/k) for k in ('HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR')},'selected paths')
    for k in ('behavior_processes','version_processes'):need(type(r[k]) is int and r[k]==1,'process count type')
    cmds=[['/usr/local/bin/godot','--version'],['/usr/local/bin/godot','--headless','--path',str(src),'--single-threaded-scene','--script',str(src/'main.gd')]]
    need(len(r['processes'])==2,'process list');prev=None
    for p,name,argv in zip(r['processes'],('version','behavior'),cmds):
        need(set(p)=={'name','argv','timeout_seconds','status','attempted_utc','pid','returncode','returned_utc','stdout_sha256','stderr_sha256'},'successful process fields')
        need(p['name']==name and p['argv']==argv and p['status']=='RETURNED','process association')
        need(type(p['returncode']) is int and p['returncode']==0 and type(p['timeout_seconds']) is int and p['timeout_seconds']==(10 if name=='version' else 20),'process status types')
        need(type(p['pid']) is int and p['pid']>0,'process PID')
        start=datetime.fromisoformat(p['attempted_utc']);end=datetime.fromisoformat(p['returned_utc'])
        need(start.utcoffset() is not None and start.utcoffset().total_seconds()==0 and end.utcoffset()==start.utcoffset() and start<=end and (prev is None or prev<=start),'UTC process order');prev=end
        for stream in ('stdout','stderr'):
            b=(out/f'{name}.{stream}').read_bytes();need(sha(b)==p[stream+'_sha256'],'raw stream hash')
            if stream=='stderr':need(b==b'','stderr diagnostic')
            elif name=='version':need(b.strip()==b'4.6.3.stable.official.7d41c59c4','version text')
    actual=parse_stdout((out/'behavior.stdout').read_bytes())
    b=(out/'behavior.json').read_bytes();need(sha(b)==r['parsed_sha256'],'parsed hash')
    need(json.dumps(actual,sort_keys=True,separators=(',',':'))==json.dumps(load(b),sort_keys=True,separators=(',',':')),'raw parsed association')
    result=check(actual);need(json.dumps(result,sort_keys=True,separators=(',',':'))==json.dumps(r['oracle'],sort_keys=True,separators=(',',':')),'oracle association');return result
if __name__=='__main__':
    import sys,json
    need(len(sys.argv)==3,'usage: consumer.py SOURCE_ROOT EVIDENCE_UUID_DIR')
    print(json.dumps(verify(sys.argv[1],sys.argv[2]),sort_keys=True))
