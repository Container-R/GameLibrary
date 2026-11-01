"""Independent synthetic consumer probes; never builds or invokes native code."""
from pathlib import Path
import copy, json, subprocess, sys, tempfile
base=Path(__file__).parent
oracle=(base/'expected.json').read_bytes()
e=json.loads(oracle)
o={'schema':1,'generated':1,'output_count':6,'callback_order':[5,4,3,2,1,0],'new_indices':[[0,1,2],[3,4,5]],'raw':e['raw'],'reindexed':copy.deepcopy(e['raw'])}
for direction in ('forward','reverse'):
 rows=copy.deepcopy(e['raw'])
 for row,sign in zip(rows,e[direction+'_signs']):row[14]=sign
 o[direction+'_readback']=rows
cases=[('valid_synthetic',o,oracle,True)]
def mutate(name,change):
 x=copy.deepcopy(o);change(x);cases.append((name,x,oracle,False))
mutate('missing_corner',lambda x:x['raw'].pop())
mutate('bad_identity',lambda x:x['raw'][0].__setitem__(0,1))
mutate('wrong_sign',lambda x:x['raw'][3].__setitem__(14,1))
mutate('bad_position',lambda x:x['reindexed'][0].__setitem__(3,1))
mutate('wrong_index',lambda x:x['new_indices'][1].__setitem__(0,0))
mutate('duplicate_callback',lambda x:x.__setitem__('callback_order',[0]*6))
mutate('boolean_numeric',lambda x:x['raw'][0].__setitem__(11,True))
mutate('outside_tolerance',lambda x:x['raw'][0].__setitem__(12,0.000002))
mutate('wrong_replay',lambda x:x['reverse_readback'][3].__setitem__(14,-1))
cases.append(('shortened_oracle',o,json.dumps(dict(e,raw=[])).encode(),False))
cases.append(('oracle_whitespace_mutation',o,oracle+b' ',False))
cases.append(('duplicate_json_key','{"schema":1,"schema":1}',oracle,False))
cases.append(('nonfinite_json','{"schema":NaN}',oracle,False))
results=[]
with tempfile.TemporaryDirectory() as folder:
 root=Path(folder)
 (root/'validate.py').write_bytes((base/'validate.py').read_bytes())
 for name,obs,expected,good in cases:
  (root/'expected.json').write_bytes(expected)
  (root/'observation.json').write_text(obs if isinstance(obs,str) else json.dumps(obs))
  proc=subprocess.run([sys.executable,*(['-O'] if sys.flags.optimize else []),'-B',str(root/'validate.py'),str(root/'observation.json')],capture_output=True,text=True,timeout=10)
  passed=proc.returncode==0 and '"result": "PASS"' in proc.stdout
  matched=passed if good else (proc.returncode!=0 and '"result": "PASS"' not in proc.stdout)
  results.append({'case':name,'expected_accept':good,'accepted':passed,'matched':matched})
print(json.dumps({'scope':'synthetic consumer only; no native invocation','mode':'optimized' if sys.flags.optimize else 'normal','cases':results},indent=2))
if not all(r['matched'] for r in results):raise SystemExit(1)
