"""Pure archived-record checks only; no native calls."""
import sys,json,copy
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,sys.argv[1])
from consume import validate_report
from child import abi, LOADER, LOADER_SHA
base={'category':'INSTANCE_CREATION_FAILED','trace':[{'call':1,'name':'create','phase':'attempt'},{'call':1,'name':'create','phase':'returned','result':-9}], 'create_result':-9,'abi':abi()[0], 'loader':{'requested':LOADER,'resolved':'/usr/lib/x86_64-linux-gnu/libvulkan.so.1.4.309','sha256':LOADER_SHA},'loader_after_sha256':LOADER_SHA,'result_name':'VK_ERROR_INCOMPATIBLE_DRIVER'}
records=[('consistent API negative',base,True)]
for name,mutate in [('wrong ABI',lambda r:r.update(abi={})),('wrong loader',lambda r:r['loader'].update(sha256='wrong')),('missing after hash',lambda r:r.pop('loader_after_sha256')),('empty failure trace',lambda r:r.update(trace=[])),('wrong negative category',lambda r:r.update(category='ENUMERATION_FAILED')),('unfinished call',lambda r:r.update(trace=r['trace'][:1]))]:
 r=copy.deepcopy(base); mutate(r); records.append((name,r,False))
records.append(('missing ABI guard evidence',{'category':'ABI_GUARD_FAILED','trace':[]},False))
out=[]
for name,r,expected in records:
 try: category=validate_report(r,r['trace']); accepted=True; reason=category
 except Exception as e: accepted=False; reason=type(e).__name__+': '+str(e)
 out.append({'case':name,'accepted':accepted,'expected_acceptance':expected,'matches':accepted==expected,'reason':reason})
print(json.dumps({'native_calls':0,'cases':out},indent=2))
raise SystemExit(0 if all(x['matches'] for x in out) else 1)
