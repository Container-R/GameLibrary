import json,shutil,subprocess,sys
from pathlib import Path
if sys.flags.optimize:raise SystemExit('Refusing optimized probes')
R=Path(__file__).resolve().parent;O=R/'negative';O.mkdir(exist_ok=True);(O/'observations.json').unlink(missing_ok=True);rows=[]
for name in ('optimized','missing-tool','nonzero-tool'):
 d=O/name
 if d.exists():raise RuntimeError('refuse old probe directory')
 shutil.copytree(R/'fixture',d)
 if name!='optimized':
  p=d/'run.py';t=p.read_text();t=t.replace("Path('/usr/bin/ffmpeg')", "Path("+repr(str(d/'absent-ffmpeg') if name=='missing-tool' else '/usr/bin/false')+")");p.write_text(t)
 cmd=[sys.executable]+(['-O'] if name=='optimized' else [])+[str(d/'run.py')];p=subprocess.run(cmd,capture_output=True,text=True,timeout=15)
 (d/'stdout.txt').write_text(p.stdout);(d/'stderr.txt').write_text(p.stderr);assert p.returncode==1 and not (d/'results/summary.json').exists()
 rows.append(dict(name=name,command=cmd,exit=1,summary_exists=False))
(O/'observations.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
