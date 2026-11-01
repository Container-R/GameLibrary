"""Independent static graph/receipt checker. No author imports or engine calls."""
import argparse
import hashlib
import json
import math
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path


def need(ok, reason):
    if not ok: raise ValueError(reason)


def read(p):
    b=p.read_bytes(); need(len(b)<4000000,'oversized file'); return b


def sha(p): return hashlib.sha256(read(p)).hexdigest()


def reject(x): raise ValueError('invalid JSON '+x)


def pairs(xs):
    d={}
    for k,v in xs:
        need(k not in d,'duplicate key'); d[k]=v
    return d


def parse(b):
    v=json.loads(b,object_pairs_hook=pairs,parse_constant=reject)
    def finite(x):
        if type(x) is float: need(math.isfinite(x),'nonfinite')
        elif type(x) is list:
            for y in x: finite(y)
        elif type(x) is dict:
            for y in x.values(): finite(y)
    finite(v); return v


def load(p): return parse(read(p))


def same(a,b):
    if type(a) is not type(b): return False
    if type(a) is list: return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    if type(a) is dict: return a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
    return a==b


def keys(v, names): need(type(v) is dict and set(v)==set(names.split()),'schema '+names)


def ident(v):
    need(type(v) is str and re.fullmatch(r'-?[1-9][0-9]*',v) is not None,'ID'); return v


def integer(v, wanted=None):
    need(type(v) is int and (wanted is None or v==wanted),'integer'); return v


def nums(v,w):
    need(type(v) is list and len(v)==len(w),'numeric shape')
    for a,b in zip(v,w): need(type(a) in (int,float) and math.isfinite(a) and a==b,'literal number')


def validate_graph(result, expected):
    keys(result,'schema invocation_uuid mode process_id engine_version constants setup stages')
    integer(result['schema'],1); need(integer(result['process_id'])>0,'PID')
    mode=result['mode']; need(mode in expected['modes'],'mode')
    ev=result['engine_version']
    need(type(ev) is dict,'version')
    for k,n in [('major',4),('minor',6),('patch',3)]: integer(ev.get(k),n)
    for k,v in [('status','stable'),('build','official'),('hash','7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3')]: need(ev.get(k)==v,'selfreport')
    need(same(result['constants'],{'type_array':28,'storage':2,'always':524288,'never':1048576,'none':0,'internal':1,'all':2}),'constants')
    s=result['setup']; keys(s,'property typed_array a b c script_path a_graph a2_graph held_b held_c cached_c cached_root_id')
    keys(s['property'],'name type usage'); need(s['property']['name']=='entries','property'); integer(s['property']['type'],28)
    usage=integer(s['property']['usage']); need(usage>=0 and usage&2 and not usage&(524288|1048576),'usage')
    need(s['typed_array'] is False and s['script_path']=='res://config.gd','script/type')
    ids={label:ident(s[key]['id']) for label,key in [('A','a'),('B','b'),('C','c')]}
    ids['S']=ident(s['a_graph']['script_id'])
    for key,cls,path,built in [('a','Resource','res://config.tres',False),('b','Gradient',None,True),('c','Gradient','res://external.tres',False)]:
        m=s[key]; keys(m,'id class path built_in local_to_scene')
        need(m['class']==cls and m['built_in'] is built and m['local_to_scene'] is False,'resource metadata')
        need(type(m['path']) is str,'path type')
        need(m['path']==path if path else m['path'].startswith('res://config.tres::') and len(m['path'])>len('res://config.tres::'),'original path')
    stages=result['stages']; need(type(stages) is list and len(stages)==4,'stages')
    ids['D']=ident(stages[0]['d']['root_id'])
    copy_symbols=expected['modes'][mode]['copy_entry_ids']
    for symbol,value in zip(copy_symbols,stages[0]['d']['first3_ids']):
        value=ident(value)
        if symbol in ids: need(ids[symbol]==value,'initial alias')
        else: ids[symbol]=value
    need(len(set(ids.values()))==len(ids),'distinct symbolic equivalence classes')
    def gradient(g,symbol,color):
        keys(g,'id class count colors offsets'); need(ident(g['id'])==ids[symbol] and g['class']=='Gradient','Gradient identity')
        integer(g['count'],2); nums(g['offsets'],[0,1]); need(type(g['colors']) is list and len(g['colors'])==2,'colors')
        nums(g['colors'][0],expected['palette'][color]); nums(g['colors'][1],expected['palette']['white'])
    def graph(g,root,symbols,length,sentinel,colors):
        keys(g,'root_id script_id length first3_ids slot3 values')
        need(ident(g['root_id'])==ids[root] and ident(g['script_id'])==ids['S'],'root/script')
        integer(g['length'],length); need(same(g['slot3'],sentinel),'slot3')
        need(same(g['first3_ids'],[ids[x] for x in symbols]),'entry identity list')
        need(type(g['values']) is list and len(g['values'])==3,'three values')
        for g0,symbol,color in zip(g['values'],symbols,colors): gradient(g0,symbol,color)
    for key in ('a_graph','a2_graph'): graph(s[key],'A',['B','B','C'],3,None,['red','red','green'])
    need(ident(s['cached_root_id'])==ids['A'],'cached root')
    gradient(s['held_b'],'B','red'); gradient(s['held_c'],'C','green'); gradient(s['cached_c'],'C','green')
    for actual,wanted in zip(stages,expected['modes'][mode]['stages']):
        keys(actual,'stage a a2 d cached_root_id held_b held_c cached_c same_array')
        need(actual['stage']==wanted['name'],'stage order')
        need(actual['same_array'] is expected['modes'][mode]['same_array'],'Array identity')
        need(ident(actual['cached_root_id'])==ids['A'],'cached root stable')
        for key in ('a','a2'): graph(actual[key],'A',['B','B','C'],wanted['A_length'],wanted['A_sentinel'],wanted['A_point0'])
        graph(actual['d'],'D',copy_symbols,wanted['D_length'],wanted['D_sentinel'],wanted['D_point0'])
        gradient(actual['held_b'],'B',wanted['A_point0'][0]); gradient(actual['held_c'],'C',wanted['A_point0'][2]); gradient(actual['cached_c'],'C',wanted['A_point0'][2])
    return mode


def main():
    p=argparse.ArgumentParser(); p.add_argument('root',type=Path); p.add_argument('evidence',type=Path); p.add_argument('--pins',type=Path,required=True); a=p.parse_args()
    here=Path(__file__).resolve().parent
    need(sha(here/'expected.json')=='8da52809d346f09aec62dbfd38f2043385c6bae9f39a8850122c9132ecb88ee7','literal oracle pin')
    e=load(here/'expected.json'); pins=load(a.pins)
    names={'project.godot','config.gd','config.tres','external.tres','main.gd','PROTOCOL.md','run.py','oracle.py','consumer.py','test_pure.py','isolation.py'}
    need(set(pins)==names,'source set')
    need(pins['PROTOCOL.md']==e['protocol_sha256'] and pins['isolation.py']=='bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970','protocol/helper')
    for name,digest in pins.items(): need(sha(a.root/name)==digest,'source bytes '+name)
    need(same(load(a.root/'SOURCE-SHA256.json'),pins),'source manifest')
    r=load(a.evidence/'receipt.json')
    keys(r,'status uuid processes original_source_directory original_process_directory source_sha256 manifest_sha256 binary_before base_environment selected_environment inputs_before inputs_after parsed_sha256 oracle source_after binary_after behavior_processes version_processes')
    need(r['status']=='PASS','receipt status')
    uid=r['uuid']; need(type(uid) is str and str(uuid.UUID(uid))==uid==a.evidence.name,'UUID')
    need(same(r['source_sha256'],pins) and same(r['source_after'],pins),'source before/after')
    need(r['manifest_sha256']==sha(a.root/'SOURCE-SHA256.json'),'manifest hash')
    need(r['binary_before']==r['binary_after']=='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3','recorded binary')
    src=Path(r['original_source_directory']); old=Path(r['original_process_directory'])
    need(src.is_absolute() and '..' not in src.parts and old==src/'evidence'/uid,'historical paths')
    need(same(r['base_environment'],{'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'}),'base environment')
    need(same(r['selected_environment'],{k:str(old/'environment'/k) for k in ['HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR']}),'selected environment')
    integer(r['behavior_processes'],3); integer(r['version_processes'],1)
    modes=['shallow','internal','all']; inputs=['project.godot','config.gd','config.tres','external.tres','main.gd']
    wanted={m:{n:pins[n] for n in inputs} for m in modes}
    need(same(r['inputs_before'],wanted) and same(r['inputs_after'],wanted),'input receipt')
    need(set(r['parsed_sha256'])==set(modes) and set(r['oracle'])==set(modes),'result map')
    need(type(r['processes']) is list and len(r['processes'])==4,'process count')
    previous=None
    for process,name in zip(r['processes'],['version']+modes):
        keys(process,'name argv cwd timeout_seconds status attempted_utc pid returncode returned_utc stdout_sha256 stderr_sha256')
        work=old if name=='version' else old/'projects'/name
        argv=['/usr/local/bin/godot','--version'] if name=='version' else ['/usr/local/bin/godot','--headless','--path',str(work),'--script',str(work/'main.gd'),'--',name,uid]
        need(process['name']==name and same(process['argv'],argv) and process['cwd']==str(work),'argv/cwd')
        need(process['status']=='RETURNED','process status'); integer(process['returncode'],0); need(integer(process['pid'])>0,'child PID')
        integer(process['timeout_seconds'],10 if name=='version' else 20)
        start,end=[datetime.fromisoformat(process[k]) for k in ['attempted_utc','returned_utc']]
        need(start.utcoffset()==end.utcoffset()==timezone.utc.utcoffset(None) and start<=end and (previous is None or previous<=start),'UTC ordering'); previous=end
        out=a.evidence/(name+'.stdout'); err=a.evidence/(name+'.stderr')
        need(sha(out)==process['stdout_sha256'] and sha(err)==process['stderr_sha256'] and read(err)==b'','current raw streams')
        if name=='version': need(read(out).strip()==b'4.6.3.stable.official.7d41c59c4','version output'); continue
        for n in inputs: need(sha(a.evidence/'projects'/name/n)==pins[n],'copied input '+n)
        lines=[s for s in read(out).decode('utf-8').splitlines() if s]
        need(len(lines)==2 and lines[0]=='Godot Engine v4.6.3.stable.official.7d41c59c4 - https://godotengine.org' and lines[1].startswith('RESULT_JSON:'),'raw envelope')
        actual=parse(lines[1][len('RESULT_JSON:'):]); need(validate_graph(actual,e)==name,'mode binding')
        need(actual['invocation_uuid']==uid and actual['process_id']==process['pid'],'child binding')
        parsed=a.evidence/(name+'.json'); need(sha(parsed)==r['parsed_sha256'][name] and same(load(parsed),actual),'raw/parsed')
        need(same(r['oracle'][name],{'mode':name,'stages':4,'mutable_payload_scope_verified':True}),'recorded verdict')
    print(json.dumps({'status':'PASS','behavior_modes':3,'stages_per_mode':4,'version_processes':1,'receipt_sha256':sha(a.evidence/'receipt.json'),'pins_sha256':sha(a.pins),'scope':'static literal/identity/archive consistency; no current binary or execution authenticity claim'}))

if __name__=='__main__': main()
