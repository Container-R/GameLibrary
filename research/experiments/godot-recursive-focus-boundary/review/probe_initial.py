import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'initial-code'))
from test_pure import synthetic
from oracle import check,load
cases={}
o=synthetic();next(r for r in o['trace'] if r['kind']=='focus_exited')['owner_id']=-14
cases['exit_still_owns']=o
o=synthetic();next(r for r in o['trace'] if r['kind']=='gui_focus_changed')['owner_id']=0
cases['gain_without_owner']=o
o=synthetic();o['version']={'major':99,'string':'not matching engine'};cases['arbitrary_embedded_version']=o
for name,obj in cases.items():
 try: print(name,'ACCEPTED',check(obj))
 except Exception as e:print(name,'REJECTED',repr(e))
print('nonfinite_json',repr(load('{"ignored":NaN}')))
