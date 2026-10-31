"""Bounded offline integration checks; never executes engine/runtime fixtures."""
from pathlib import Path
import subprocess,json,hashlib,sys,os,datetime
R=Path('gamelibrary-publish-telemetry').resolve();O=Path(__file__).resolve().parent
(O/'summary.json').unlink(missing_ok=True)
checks=[('models',[sys.executable,str(R/'scripts/run_model_tests.py')]),('taxonomy',[sys.executable,str(R/'scripts/test_taxonomy.py')]),('navigation',[sys.executable,str(R/'scripts/navigation/test_routes.py')]),('archive-unit',[sys.executable,str(R/'scripts/evidence/test_verify.py')]),('archive-normal',[sys.executable,str(R/'scripts/evidence/verify.py'),str(R)]),('archive-optimized',[sys.executable,'-O',str(R/'scripts/evidence/verify.py'),str(R)]),('navigation-current',[sys.executable,str(R/'scripts/navigation/build_routes.py'),str(R),'--registry',str(R/'taxonomy/reading-routes.json'),'--output',str(R/'DISCOVERY.md'),'--check'])]
rows=[]
for name,cmd in checks:
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=60,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 (O/(name+'-stdout.txt')).write_text(p.stdout);(O/(name+'-stderr.txt')).write_text(p.stderr)
 rows.append(dict(name=name,command=cmd,exit=p.returncode))
 if p.returncode:raise RuntimeError(name+' failed')
if (O/'archive-normal-stdout.txt').read_bytes()!=(O/'archive-optimized-stdout.txt').read_bytes():raise RuntimeError('optimized archive mismatch')
summary=dict(observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_head='6bf41a3cc51cb70f3c0c8fe3754f9e2f97276113',scope='Original isolated teaching-model/unit tests plus read-only archive/navigation checks; no Godot/Pillow/SQLite/ICU/ink fixture reruns',checks=rows,archive_normal_equals_optimized=True)
(O/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
