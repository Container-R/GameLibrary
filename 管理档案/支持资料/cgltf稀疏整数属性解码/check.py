"""Finite author-side consumer, not a native observation or independent oracle."""
import json
import math

CASES = ('dense-normalized.json', 'zero-normalized.json', 'dense-raw.json')
EXPECTED = ([1,0,0,0,64/255,191/255,0,0], [0,0,0,0,64/255,191/255,0,0], [255,0,0,0,64,191,0,0])

def pairs(items):
    d = {}
    for k,v in items:
        if k in d: raise ValueError('duplicate key')
        d[k] = v
    return d

def check(data):
    if len(data)>8192: raise ValueError('output bound')
    lines = data.decode('ascii').splitlines()
    if len(lines)!=3: raise ValueError('three rows required')
    rows=[]
    for ci,line in enumerate(lines):
        r=json.loads(line, object_pairs_hook=pairs, parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite token')))
        if type(r)!=dict or set(r)!={'case','parse','load','validate','query_count','unpack_count','read_float','values'}: raise ValueError('schema')
        if r['case']!=CASES[ci] or r['read_float'] is not False: raise ValueError('case/read')
        for key,value in [('parse',0),('load',0),('validate',0),('query_count',8),('unpack_count',8)]:
            if type(r[key]) is not int or r[key]!=value: raise ValueError('status/count')
        if type(r['values']) is not list or len(r['values'])!=8: raise ValueError('values')
        for i,(v,w) in enumerate(zip(r['values'],EXPECTED[ci])):
            if type(v) not in (int,float) or not math.isfinite(v): raise ValueError('numeric value')
            if ci<2 and i in (4,5):
                if abs(v-w)>1e-7: raise ValueError('fraction tolerance')
            elif v!=w: raise ValueError('exact value')
        rows.append(r)
    return rows
