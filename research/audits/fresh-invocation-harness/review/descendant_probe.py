import sys,json,os
from pathlib import Path
r=Path(__file__).resolve().parent;sys.path.insert(0,str(r/'tool'));import harness as h
out=r/'descendant-probe';out.mkdir(exist_ok=False)
code="import subprocess,sys; subprocess.Popen([sys.executable,'-c','import time; time.sleep(2)']); print('LEADER EXIT',flush=True)"
p=h.launch([sys.executable,'-B','-c',code],out,os.environ.copy(),out,5)
h.write(out/'process.json',p)
if not p.get('unexpected_descendants'):raise RuntimeError('descendant not detected')
try:h.process_acceptable(p)
except h.Rejected as e:h.write(out/'rejection.json',{'reason':str(e),'native_engine_runs':0})
else:raise RuntimeError('incorrect acceptance')
print('PASS normal-exit leader with own-group descendant rejected')
