import importlib.util,json,sys
from pathlib import Path
if sys.flags.optimize:raise SystemExit('Refusing optimized assertions')
p=Path(sys.argv[1]);spec=importlib.util.spec_from_file_location('reviewed_report',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.report([],100)
assert r['completion_per_started_attempt']==[0,0]
assert r['actors_with_completion_per_starting_actor']==[0,0]
assert r['finished_only_fraction']==[0,0]
assert not r['completed'] and not r['failed'] and not r['unresolved']
print(json.dumps(dict(status='PASS',report=r,interpretation='zero-denominator pairs; no defined percentage'),indent=2))
