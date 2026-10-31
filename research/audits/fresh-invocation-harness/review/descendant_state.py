import sys,json,os
from pathlib import Path
r=Path(__file__).resolve().parent;sys.path.insert(0,str(r/'tool'));import harness as h
out=r/'descendant-state';out.mkdir(exist_ok=False)
code="import subprocess,sys; p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(2)']); print('OWNED_CHILD_PID='+str(p.pid),flush=True)"
p=h.launch([sys.executable,'-B','-c',code],out,os.environ.copy(),out,5)
text=(out/'stdout.txt').read_text();pid=int(next(x.split('=')[1] for x in text.splitlines() if x.startswith('OWNED_CHILD_PID=')))
stat=Path('/proc')/str(pid)/'stat'
if stat.exists():
 raw=stat.read_text();parts=raw[raw.rfind(')')+2:].split();state=parts[0];ppid=int(parts[1]);pgid=int(parts[2]);observation={'pid':pid,'state':state,'ppid':ppid,'pgid':pgid,'same_owned_group':pgid==p['pid'],'raw_stat':raw}
else:observation={'pid':pid,'state':'gone'}
h.write(out/'observation.json',{'process':p,'child':observation,'no_additional_signals':True})
if observation['state'] not in ['Z','gone']:raise RuntimeError('owned child not confirmed nonrunning')
try:h.process_acceptable(p)
except h.Rejected as e:print('REJECTED',str(e),'child state',observation['state'])
else:raise RuntimeError('unexpected acceptance')
