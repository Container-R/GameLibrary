"""Six synthetic record changes; no native or child executions."""
import copy,json,importlib.util
from pathlib import Path
from check import oracle
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('author',HERE/'fixture/run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
d=json.loads((HERE/'evidence/6703fd88-731a-4879-8a5d-6f2ac968b3e2/behavior.json').read_text())
def change_origin(x):x['evaluations'][0]['final']['poses'][1]['global']['origin'][0]=1
def change_order(x):x['evaluations'][1]['before']['children'].reverse()
def change_target(x):x['evaluations'][1]['restored']['targets'][1]['world']['origin'][2]=11
def change_identity(x):x['evaluations'][1]['before']['modifiers'][1]['id']+=1
def change_restore(x):x['evaluations'][0]['restored']['poses'][1]['global']['basis'][0][0]=.5
def change_basis(x):x['evaluations'][1]['final']['poses'][1]['global']['basis']=[[1,0,0],[0,1,0],[0,0,1]]
records=[]
for fn in [change_origin,change_order,change_target,change_identity,change_restore,change_basis]:
 x=copy.deepcopy(d);fn(x);rejected=[]
 for label,check in [('author',m.check),('independent',oracle)]:
  try:check(x)
  except (ValueError,RuntimeError,KeyError,IndexError):rejected.append(label)
  else:raise RuntimeError(fn.__name__+' accepted by '+label)
 records.append({'mutation':fn.__name__,'rejected_by':rejected})
print(json.dumps({'status':'PASS','synthetic_records':6,'native_processes':0,'child_processes':0,'checks':records},indent=2))
