"""Validate captured bytes only. This module never starts Detour."""
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent

def require(ok, message):
    if not ok:
        raise ValueError(message)

def strict_json(raw):
    if isinstance(raw, bytes):
        raw = raw.decode('utf-8', errors='strict')
    require(type(raw) is str, 'JSON input type')
    def pairs(items):
        value = {}
        for key, item in items:
            require(key not in value, 'duplicate key: '+key)
            value[key] = item
        return value
    def constant(value):
        raise ValueError('nonfinite token: '+value)
    result = json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    def finite(value):
        if type(value) is float:
            require(math.isfinite(value), 'nonfinite number')
        elif type(value) is dict:
            for item in value.values(): finite(item)
        elif type(value) is list:
            for item in value: finite(item)
    finite(result)
    return result

def numeric_position(path):
    # Only these declared physical numeric positions accept JSON int OR float.
    if path[:2] == ('setup', 'vertices'): return True
    if path[:3] in (('setup','input','vertices'), ('setup','input','bounds'), ('setup','input','walkable')): return True
    if path in (('setup','input','cs'), ('setup','input','ch'), ('setup','float_max'), ('setup','filter',2)): return True
    if len(path) >= 3 and path[0] == 'cases' and path[2] in ('start','end','t','hit_normal'): return True
    return False

def validate(value, expected=None):
    if expected is None:
        expected = strict_json((ROOT/'expected.json').read_bytes())
    require(type(value) is dict, 'top object')
    require(type(value.get('setup')) is dict, 'setup object')
    refs = value['setup'].get('refs')
    require(type(refs) is list and len(refs)==3, 'three refs')
    require(all(type(r) is str and re.fullmatch(r'[1-9][0-9]*',r,flags=re.ASCII) for r in refs), 'canonical nonzero refs')
    require(len(set(refs))==3, 'distinct refs')
    bindings = dict(zip(('$P0','$P1','$P2'), refs))
    def match(actual, wanted, path=()):
        where = '/'.join(map(str,path)) or '<root>'
        if type(wanted) is str and wanted in bindings:
            require(type(actual) is str and actual==bindings[wanted], where+' bound ref'); return
        if wanted == '$POSITIVE_INT':
            require(type(actual) is int and actual>0, where+' positive int'); return
        if type(wanted) is dict:
            require(type(actual) is dict and set(actual)==set(wanted), where+' keys')
            for key in wanted: match(actual[key],wanted[key],path+(key,))
        elif type(wanted) is list:
            require(type(actual) is list and len(actual)==len(wanted), where+' length')
            for i,item in enumerate(wanted): match(actual[i],item,path+(i,))
        elif type(wanted) in (int,float) and numeric_position(path):
            require(type(actual) in (int,float) and math.isfinite(actual) and actual==wanted, where+' numeric')
        else:
            require(type(actual) is type(wanted) and actual==wanted, where+' literal')
    match(value,expected)
    return {'validation':'consumer_only','status':'pass','cases':4,'raycast_calls':3,'findPath_calls':1}

def main():
    require(len(sys.argv)==2, 'usage: consumer.py captured.json')
    result=validate(strict_json(Path(sys.argv[1]).read_bytes()))
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__': main()
