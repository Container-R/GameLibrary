"""Bounded synthetic negatives; original evidence never modified."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
if sys.flags.optimize: raise SystemExit('Refusing optimized negative harness')
ROOT=Path(__file__).resolve().parent
SOURCE=Path(sys.argv[1]).resolve(); CHECKER=Path(sys.argv[2]).resolve()
(ROOT/'observations.json').unlink(missing_ok=True)
RUN=ROOT/'cases'; RUN.mkdir(exist_ok=True)
rows=[]
def case(name,kind,change,optimized=False):
 d=RUN/name
 if d.exists():raise RuntimeError('Refuse overwrite '+str(d))
 d.mkdir();shutil.copy2(SOURCE/'run.py',d/'run.py');shutil.copy2(SOURCE/'model.py',d/'model.py');shutil.copytree(SOURCE/'results',d/'results');shutil.copy2(CHECKER,d/'check_raw.py')
 change(d)
 before=(d/'results/summary.json').read_bytes() if (d/'results/summary.json').exists() else None
 cmd=[sys.executable]+(['-O'] if optimized else [])+[str(d/('run.py' if kind=='runner' else 'check_raw.py'))]
 if kind=='checker':cmd.append(str(d/'results'))
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=15,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 (d/'stdout.txt').write_text(p.stdout);(d/'stderr.txt').write_text(p.stderr)
 after=(d/'results/summary.json').read_bytes() if (d/'results/summary.json').exists() else None
 row=dict(name=name,kind=kind,command=cmd,exit=p.returncode,stdout_bytes=len(p.stdout.encode()),stderr_bytes=len(p.stderr.encode()),prior_summary_retained=before is not None and before==after,summary_exists=after is not None)
 (d/'receipt.json').write_text(json.dumps(row,indent=2)+'\n'); rows.append(row)
def replace(p,a,b):
 t=p.read_text(); assert a in t;p.write_text(t.replace(a,b))
case('optimized-prior-pass','runner',lambda d:None,True)
case('dependency-import-failure','runner',lambda d:(d/'PIL.py').write_text("raise ImportError('synthetic dependency failure')\n"))
case('model-import-failure','runner',lambda d:(d/'model.py').write_text("raise RuntimeError('synthetic model import failure')\n"))
case('wrong-numeric-model','runner',lambda d:replace(d/'model.py',"'BC7': 16","'BC7': 17"))
case('wrong-payload-offset','runner',lambda d:replace(d/'model.py','payload_offset=offset - 128','payload_offset=offset - 127'))
case('wrong-blocks-x','runner',lambda d:replace(d/'model.py','blocks_x=bx','blocks_x=bx+1'))
case('wrong-blocks-y','runner',lambda d:replace(d/'model.py','blocks_y=by','blocks_y=by+1'))
case('missing-artifact','checker',lambda d:(d/'results/markers.dds.base64').unlink())
case('malformed-summary','checker',lambda d:(d/'results/summary.json').write_text('{'))
case('missing-summary','checker',lambda d:(d/'results/summary.json').unlink())
case('optimized-checker','checker',lambda d:None,True)
# For fixed runner this terminal checker rejects missing summary; v1 retained the actual offset-oracle detection.
d=RUN/'wrong-payload-offset';cmd=[sys.executable,str(d/'check_raw.py'),str(d/'results')];p=subprocess.run(cmd,capture_output=True,text=True,timeout=15)
(d/'checker-stdout.txt').write_text(p.stdout);(d/'checker-stderr.txt').write_text(p.stderr);rows.append(dict(name='wrong-payload-offset-independent-check',command=cmd,exit=p.returncode))
(ROOT/'observations.json').write_text(json.dumps(dict(source_sha256={f:hashlib.sha256((SOURCE/f).read_bytes()).hexdigest() for f in ('model.py','run.py')},checker_sha256=hashlib.sha256(CHECKER.read_bytes()).hexdigest(),cases=rows),indent=2)+'\n')
print(json.dumps(rows,indent=2))
