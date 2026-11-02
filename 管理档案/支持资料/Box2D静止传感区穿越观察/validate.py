"""Finite author-side raw-observation consumer; no engine imports or calls."""
import hashlib
import json
import math
from pathlib import Path

EXPECTED_SHA256='42db20a5ed693dff27b96789976d3db53661b28bb5fc8b4de2a67fc817f1e7c5'
TOL=1e-5

def need(ok,message):
    if not ok: raise ValueError(message)

def pairs(items):
    result={}
    for key,value in items:
        need(key not in result,'duplicate JSON key')
        result[key]=value
    return result

def invalid_constant(value): raise ValueError('nonfinite JSON constant: '+value)

def loads(text):
    value=json.loads(text,object_pairs_hook=pairs,parse_constant=invalid_constant)
    def finite(x):
        if type(x) is float: need(math.isfinite(x),'nonfinite float')
        elif type(x) is list:
            for y in x: finite(y)
        elif type(x) is dict:
            for y in x.values(): finite(y)
    finite(value)
    return value

def same(a,b):
    if type(a) is not type(b): return False
    if type(a) is list: return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    if type(a) is dict: return a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
    return a==b

def near(a,b):
    if type(a) is not type(b): return False
    if type(a) is list: return len(a)==len(b) and all(near(x,y) for x,y in zip(a,b))
    return type(a) is float and math.isfinite(a) and abs(a-b)<=TOL

def expected(path=None):
    path=Path(path) if path else Path(__file__).with_name('expected.json')
    raw=path.read_bytes();need(hashlib.sha256(raw).hexdigest()==EXPECTED_SHA256,'oracle identity')
    return loads(raw)['rows']

def transform(p,t):
    return [t[0]+t[2]*p[0]-t[3]*p[1],t[1]+t[3]*p[0]+t[2]*p[1]]

def validate(raw,expected_path=None):
    need(type(raw) is bytes,'raw bytes required')
    need(raw.endswith(b'\n'),'incomplete stream')
    lines=raw.decode('utf-8').splitlines();spec=expected(expected_path)
    need(len(lines)==len(spec),'record cardinality')
    values={};ids={};bound={}
    for index,(line,rule) in enumerate(zip(lines,spec)):
        row=loads(line);need(type(row) is dict and set(row)=={'case','phase','key','value'},'record schema')
        for key in ['case','phase','key']: need(same(row[key],rule[key]),f'record {index} {key}')
        case,phase,key,value=row['case'],row['phase'],row['key'],row['value'];kind=rule['rule'];want=rule['value']
        at=(case,phase,key);need(at not in values,'duplicate record');values[at]=value
        if kind=='exact': need(same(value,want),f'exact {at}')
        elif kind=='motion': need(near(value,want),f'motion {at}')
        elif kind=='positive': need(type(value) is float and math.isfinite(value) and value>0,'positive mass')
        elif kind=='bind':
            category=rule['kind'];length=2 if category=='world' else 3
            need(type(value) is list and len(value)==length and all(type(x) is int for x in value),'ID type')
            need(1<=value[0]<=(65535 if category=='world' else 2147483647),'ID index')
            need(all(0<=x<=65535 for x in value[1:]),'ID fields')
            if category!='world':need(value[1]==ids[(case,'world.id')][0]-1,'ID world association')
            old=bound.setdefault((case,category),[]);need(value not in old,'distinct live objects');old.append(value)
            ids[(case,key)]=value
        elif kind=='ref':need(same(value,ids[(case,want)]),'live object identity')
        elif kind=='projection':
            need(near(value,want),'nominal endpoint projection')
            st=values[(case,phase,'sensor.pose')];vt=values[(case,phase,'visitor.pose')]
            vertices=[values[(case,'setup',f'polygon.vertex.{i}')] for i in range(4)]
            xs=[transform(p,st)[0] for p in vertices]
            center=transform(values[(case,'setup','circle.center')],vt);r=values[(case,'setup','circle.radius')]
            recomputed=[min(xs),max(xs),center[0]-r,center[0]+r]
            need(near(value,recomputed),'raw geometry projection')
        elif kind=='gap':
            need(near(value,want),'nominal gap')
            p=values[(case,phase,'projection')];gap=p[0]-p[3] if phase=='initial' else p[2]-p[1]
            need(near(value,gap) and value>1. and gap>1.,'endpoint separation')
        elif kind=='dx':
            need(near(value,want),'nominal displacement')
            step=int(phase[-1]);previous='initial' if step==1 else f'step_{step-1}'
            delta=values[(case,phase,'visitor.pose')][0]-values[(case,previous,'visitor.pose')][0]
            threshold=values[(case,phase,'visitor.min_extent')]*values[(case,phase,'visitor.safety_factor')]
            need(near(value,delta) and delta>threshold,'fast input displacement')
        else:raise ValueError('unknown frozen oracle rule')
    return {'status':'pass','result_kind':'consumer_only','overall_acceptance_requires':'receipt.json status=pass after identity checks','worlds':2,'steps':6,'records':len(spec),'raw_sha256':hashlib.sha256(raw).hexdigest(),'oracle_sha256':EXPECTED_SHA256}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('observation');args=parser.parse_args()
    print(json.dumps(validate(Path(args.observation).read_bytes()),indent=2))
