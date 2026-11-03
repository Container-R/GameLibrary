"""Offline strict consumer and finite numerical gates; never loads OpenAL."""
import base64
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import struct

_spec=importlib.util.spec_from_file_location('numeric_contract',Path(__file__).absolute().parent/'contract.py')
K=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(K)

class Reject(Exception): pass

def require(ok, reason):
    if not ok: raise Reject(reason)

def exact(a,b):
    if type(a) is not type(b): return False
    if type(a) is dict: return a.keys()==b.keys() and all(exact(a[k],b[k]) for k in a)
    if type(a) is list: return len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
    return a==b

def strict_json(raw):
    def pairs(items):
        d={}
        for k,v in items:
            require(k not in d,'duplicate_key'); d[k]=v
        return d
    def constant(_): raise Reject('nonfinite_json')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=constant)

def samples(raw):
    require(len(raw)==19200,'sample_byte_length')
    values=struct.unpack('<4800f',raw)
    require(all(math.isfinite(x) for x in values),'nonfinite_sample')
    return values

def metrics(raw_windows, baseline):
    rms=[math.sqrt(math.fsum(x*x for x in samples(raw))/4800) for raw in raw_windows]
    denom=rms if baseline is None else baseline
    require(all(math.isfinite(x) and x>=0.001 for x in denom),'baseline_floor')
    return {'rms':rms,'ratios':[x/y for x,y in zip(rms,denom)]}

def check_metrics(m,case):
    require(len(m['rms'])==2 and len(m['ratios'])==2,'metric_count')
    require(all(math.isfinite(x) for x in m['rms']+m['ratios']),'nonfinite_metric')
    require(abs(m['rms'][0]-m['rms'][1])<=1e-6,'window_stability')
    require(all(abs(x-case['ratio'])<=0.001 for x in m['ratios']),'distance_ratio')
    if case['id']=='linear-max': require(all(x<=1e-6 for x in m['rms']),'linear_zero')

def checks(names): return [{'stage':n,'error':0} for n in names]

def consume(raw):
    require(raw.endswith(b'\n'),'truncated_stream')
    lines=raw.decode('utf-8','strict').splitlines()
    events=[strict_json(line) for line in lines]
    cursor=0
    def take(event,case):
        nonlocal cursor
        require(cursor<len(events),'missing_event')
        e=events[cursor]
        require(type(e) is dict and set(e)=={'seq','event','case','data'},'event_keys')
        require(type(e['seq']) is int and e['seq']==cursor,'sequence')
        require(e['event']==event and e['case']==case,'event_order')
        cursor+=1
        return e['data']
    require(exact(take('begin',None),K.BEGIN),'begin')
    pcm=struct.pack('<48h',*([1024]*24+[-1024]*24))
    require(exact(take('global_ready',None),{'loopback_extension':True,'entries_present':True,
        'checks':checks(K.GLOBAL_CHECKS),'pcm_sha256':hashlib.sha256(pcm).hexdigest()}),'global_ready')
    baseline=None; results=[]
    for case in K.CASES:
        cid=case['id']
        require(exact(take('case_begin',cid),case),'case_parameters')
        r=take('ready',cid)
        require(type(r) is dict and set(r)=={'version','renderer','format','hrtf_status','listener','source','buffer','distance_model','checks'},'ready_keys')
        require(r['version']==K.VERSION and r['renderer']=='OpenAL Soft','identity')
        require(exact(r['format'],K.FORMAT) and type(r['hrtf_status']) is int,'format')
        require(exact(r['listener'],K.LISTENER) and exact(r['source'],K.source_values(case)),'properties')
        require(exact(r['buffer'],K.BUFFER) and type(r['distance_model']) is int and r['distance_model']==case['model'],'buffer_model')
        require(exact(r['checks'],checks(K.ready_checks())),'ready_checks')
        require(exact(take('playing',cid),{'state':0x1012,'checks':checks(['play','get_playing'])}),'playing')
        windows=[]
        for part in K.PARTS:
            w=take('window',cid)
            require(type(w) is dict and set(w)=={'part','frame_count','byte_count','sha256','base64'},'window_keys')
            require(w['part']==part and exact(w['frame_count'],4800) and exact(w['byte_count'],19200),'window_shape')
            require(type(w['base64']) is str and type(w['sha256']) is str,'raw_type')
            data=base64.b64decode(w['base64'],validate=True)
            require(base64.b64encode(data).decode('ascii')==w['base64'],'canonical_base64')
            require(hashlib.sha256(data).hexdigest()==w['sha256'],'raw_hash')
            samples(data)
            require(exact(take('window_checked',cid),{'part':part,'state':0x1012,'checks':checks(['render_alc','render_al','get_playing'])}),'window_checked')
            if part!='warmup': windows.append(data)
        m=metrics(windows,baseline); check_metrics(m,case)
        require(exact(take('case_metrics',cid),m),'metrics_binding')
        require(exact(take('cleanup',cid),{'ok':True,'checks':checks(K.CLEANUP_CHECKS[:-1])+[{'stage':'close_loopback','ok':True}],'failures':[]}),'cleanup')
        require(exact(take('case_pass',cid),{'numeric_ok':True,'cleanup_ok':True}),'case_pass')
        if baseline is None: baseline=m['rms']
        results.append({'id':cid,**m})
    require(exact(take('success',None),{'cases':5,'render_calls':15,'frames':72000,'source_objects':5,'buffer_objects':5,
        'configuration_fully_excluded':False}),'success')
    require(cursor==len(events),'trailing_events')
    return {'status':'PASS','configuration_fully_excluded':False,'cases':results,'render_calls':15,'frames':72000,
            'self_reported_version':K.VERSION,'self_reported_renderer':'OpenAL Soft'}
