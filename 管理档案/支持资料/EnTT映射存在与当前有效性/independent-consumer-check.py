"""Synthetic records only; never invokes runner/compiler/native fixture."""
import copy, hashlib, importlib.util, json
from pathlib import Path
B=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('reviewed_checker',B/'checker.py'); c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
def h(n): return {'full':n,'index':n&0xfffff,'version':n>>20}
# Deliberately synthetic identities, not observed allocation output.
r=[dict(kind='declaration',schema=1,cplusplus=201703,gcc=None,clang=None,entt=[3,13,2],entity_mask=1048575,version_mask=4095)]
r += [dict(kind='token',index=i,type=t,value=v) for i,t,v in [(0,'uint32',1),(1,'uint32',1),(2,'entity',7)]]
for name,now,initial,con,valid,count,iv,consumed in [('before_load',0xffffffff,None,False,False,1,None,None),('loaded',9,9,True,True,2,True,3),('externally_destroyed',9,9,True,False,1,False,None),('reloaded',1048585,9,True,True,2,False,3)]:
 r.append(dict(kind='stage',stage=name,source=h(7),seed=h(8),mapped_now=h(now),mapped_initial=None if initial is None else h(initial),contains=con,mapped_nonnull=con,mapped_valid=valid,active_count=count,initial_valid=iv,source_valid=True,seed_valid=True,input_consumed=consumed))
def raw(x): return ('\n'.join(json.dumps(a,separators=(',',':')) for a in x)+'\n').encode()
c.check(raw(r),B/'independent-oracle.json')
checks=[]
def bad(name,x):
 try: c.check(x,B/'independent-oracle.json')
 except (ValueError,KeyError,TypeError): checks.append(name)
 else: raise RuntimeError('accepted invalid '+name)
def change(name,row,key,value):
 x=copy.deepcopy(r); x[row][key]=value; bad(name,raw(x))
change('bool schema',0,'schema',True)
change('bool compiler macro',0,'gcc',[True,2,3])
change('wrong version',0,'entt',[3,13,3])
change('bool count',5,'active_count',True)
change('int boolean',5,'contains',1)
change('wrong decomposition',5,'mapped_now',{'full':9,'index':8,'version':0})
change('negative handle',5,'mapped_now',h(-1))
change('oversized handle',5,'mapped_now',h(2**32))
change('initial missing loaded',5,'mapped_initial',None)
change('destroyed map changed',6,'mapped_now',h(10))
change('reloaded old identity',7,'mapped_now',h(9))
change('source changed',7,'source',h(10))
change('archive wrong source',3,'value',8)
change('archive bool count',1,'value',True)
change('wrong consumption',7,'input_consumed',2)
change('wrong phase',6,'stage','loaded')
x=copy.deepcopy(r); x[4]['extra']=1; bad('extra field',raw(x))
x=copy.deepcopy(r); del x[4]['contains']; bad('missing field',raw(x))
bad('seven lines',raw(r[:-1])); bad('nine lines',raw(r+[r[-1]]))
bad('duplicate key',raw(r).replace(b'"schema":1',b'"schema":1,"schema":1',1))
bad('nonfinite',raw(r).replace(b'"cplusplus":201703',b'"cplusplus":NaN',1))
bad('no final LF',raw(r)[:-1]); bad('CRLF',raw(r).replace(b'\n',b'\r\n'))
bad('invalid UTF8',b'\xff'+raw(r))
m=json.loads((B/'INPUT-MANIFEST.json').read_text())
for name,sha in m['files'].items():
 if hashlib.sha256((B/name).read_bytes()).hexdigest()!=sha: raise RuntimeError('binding '+name)
s=(B/'source/entt.hpp').read_bytes()
if len(s)!=3085766 or hashlib.sha1(b'blob '+str(len(s)).encode()+b'\0'+s).hexdigest()!='b3a763a203cb7c2acc467de1dc97920562721989': raise RuntimeError('source blob')
print(json.dumps({'synthetic_positive':1,'synthetic_rejections':len(checks),'input_hashes':len(m['files']),'upstream_git_blob':'matched','native_calls':0}))
