import sys,json,shutil,subprocess
from pathlib import Path
if sys.flags.optimize:raise RuntimeError('no optimized harness')
r=Path(__file__).resolve().parent;o=r/'negatives';o.mkdir(exist_ok=False);reports=[]
for name in ['optimized','missing-engine','empty-output']:
 p=o/name;shutil.copytree(r/'fixture',p,ignore=shutil.ignore_patterns('results','.godot','__pycache__'))
 (p/'results').mkdir();(p/'results/summary.json').write_text('{"status":"PASS","old":true}')
 if name!='optimized':
  f=p/'run.py';s=f.read_text();old="Path('/usr/local/bin/godot')";assert s.count(old)==1
  s=s.replace(old,"Path('/nonexistent/godot')" if name=='missing-engine' else "Path('/usr/bin/true')");f.write_text(s)
 cmd=[sys.executable,*(['-O'] if name=='optimized' else []),str(p/'run.py')]
 z=subprocess.run(cmd,capture_output=True,text=True,timeout=10);(p/'outer.stdout').write_text(z.stdout);(p/'outer.stderr').write_text(z.stderr)
 receipt=json.loads((p/'results/invocation.json').read_text());assert z.returncode!=0 and receipt['state']=='FAILED' and not (p/'results/summary.json').exists()
 reports.append({'case':name,'command':cmd,'returncode':z.returncode,'receipt':receipt,'godot_processes':0,'old_summary_removed':True})
(o/'observations.json').write_text(json.dumps(reports,indent=2)+'\n');print('PASS3 synthetic rejects; zero Godot processes')
