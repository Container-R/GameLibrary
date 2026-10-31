"""Independent pure malformed-record probes; no CDLL/native calls."""
import copy,importlib.util,json,sys
from pathlib import Path
src=Path(sys.argv[1]).resolve();sys.path.insert(0,str(src))
import test_pure as author
cases=[]
r=author.record('en_full');r['inputs']=list(r['inputs']);r['inputs'][0]=False;cases.append(('report input bool replacing zero',r))
r=author.record('ar_omit_few');r['intent_acceptance']['accepted']=0;cases.append(('intent bool replaced numeric zero',r))
r=author.record('en_full');r['trace'][4]['input']=False;cases.append(('attempt input bool replacing zero',r))
for name,r in cases:
    try: author.check(r); result='ACCEPTED'
    except Exception as e:result='REJECTED '+type(e).__name__
    print(json.dumps({'case':name,'result':result}))
