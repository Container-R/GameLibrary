"""Read-only archive consistency checks. Never executes archived code or engine."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re

class IntegrityError(ValueError):
    pass

def inside(root, relative):
    if not isinstance(relative,str) or not relative or Path(relative).is_absolute() or '..' in Path(relative).parts:
        raise IntegrityError('invalid relative path: '+repr(relative))
    path=(root/relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise IntegrityError('path escapes archive: '+relative)
    if not path.is_file():
        raise IntegrityError('missing file: '+relative)
    return path

def strict_json(text):
    def pairs(items):
        result={}
        for k,v in items:
            if k in result: raise IntegrityError('duplicate JSON key: '+k)
            result[k]=v
        return result
    def constant(value): raise IntegrityError('nonfinite JSON: '+value)
    def finite_float(value):
        number=float(value)
        if not math.isfinite(number): raise IntegrityError('nonfinite JSON number: '+value)
        return number
    return json.loads(text,object_pairs_hook=pairs,parse_constant=constant,parse_float=finite_float)

def read_json(root,path):
    return strict_json(inside(root,path).read_text(encoding='utf-8'))

def field(obj,keys):
    for key in keys: obj=obj[key]
    return obj

def same(a,b):
    return json.dumps(a,sort_keys=True,allow_nan=False)==json.dumps(b,sort_keys=True,allow_nan=False)

def digest(root,path,expected):
    if not isinstance(expected,str) or not re.fullmatch('[0-9a-f]{64}',expected):
        raise IntegrityError('invalid SHA256 declaration: '+path)
    actual=hashlib.sha256(inside(root,path).read_bytes()).hexdigest()
    if actual!=expected: raise IntegrityError('hash mismatch: '+path+' expected='+expected+' actual='+actual)

def check(root,item):
    kind=item['kind']
    if kind=='manifest':
        obj=field(read_json(root,item['document']),item['field'])
        if not isinstance(obj,dict) or set(obj)!=set(item['files']):
            raise IntegrityError('manifest keys differ from explicit current registry')
        for key,target in item['files'].items(): digest(root,target,obj[key])
    elif kind=='hash':
        digest(root,item['target'],field(read_json(root,item['document']),item['field']))
    elif kind=='equal':
        a=field(read_json(root,item['left']),item['field'])
        b=field(read_json(root,item['right']),item.get('right_field',item['field']))
        if not same(a,b): raise IntegrityError('metadata differs: '+'.'.join(item['field']))
        if item.get('sha256') and not re.fullmatch('[0-9a-f]{64}',a):
            raise IntegrityError('invalid binary SHA256 metadata')
    elif kind=='log':
        lines=[s[len('RESULT_JSON='):] for s in inside(root,item['log']).read_text(encoding='utf-8').splitlines() if s.startswith('RESULT_JSON=')]
        if len(lines)!=1: raise IntegrityError('expected exactly one RESULT_JSON record')
        if not same(strict_json(lines[0]),read_json(root,item['parsed'])):
            raise IntegrityError('RESULT_JSON differs from parsed archive')
    else: raise IntegrityError('unknown registry check: '+kind)

def verify(root,registry):
    if not isinstance(registry,dict) or not isinstance(registry.get('checks'),list) or not registry['checks']:
        raise IntegrityError('registry requires nonempty checks')
    ids=[item.get('id') for item in registry['checks'] if isinstance(item,dict)]
    if len(ids)!=len(registry['checks']) or any(not isinstance(i,str) or not i for i in ids) or len(set(ids))!=len(ids):
        raise IntegrityError('registry check IDs must be unique nonempty strings')
    results=[]
    for item in registry['checks']:
        try:
            check(root,item)
            results.append({'id':item['id'],'status':'pass'})
        except (ValueError,TypeError,KeyError,OSError) as exc:
            results.append({'id':item['id'],'status':'fail','detail':str(exc)})
    return {'scope':'Declared archive consistency only; not genuine execution, binary authenticity or semantic correctness',
            'checks':results,'passed':sum(r['status']=='pass' for r in results),
            'failed':sum(r['status']=='fail' for r in results)}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive',type=Path)
    parser.add_argument('--registry',type=Path,default=Path(__file__).with_name('registry.json'))
    args=parser.parse_args()
    report=verify(args.archive.resolve(),strict_json(args.registry.read_text()))
    print(json.dumps(report,indent=2))
    raise SystemExit(bool(report['failed']))
