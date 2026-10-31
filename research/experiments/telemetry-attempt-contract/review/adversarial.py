import copy,importlib.util,json,shutil,subprocess,sys
from pathlib import Path
if sys.flags.optimize:raise SystemExit('Refusing optimized probes')
R=Path(__file__).resolve().parent;F=R/'fixture';O=R/'adversarial';O.mkdir(exist_ok=True);(O/'observations.json').unlink(missing_ok=True)
spec=importlib.util.spec_from_file_location('reviewed_report',F/'report.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows=json.loads((F/'results/fictional-events.json').read_text());notes=[]
def record(name,**kw):notes.append(dict(name=name,**kw))
a=m.report(rows,36);b=m.report(rows,37);assert 'd1' in a['completed'] and 'd1' not in b['completed'] and 'd1' in b['unresolved'];assert len(b['completed'])==len(a['completed'])-1;record('late-conflict-reduces-completed',before=a['completed'],after=b['completed'])
base=m.report(rows,200);d=copy.deepcopy(rows);retry=copy.deepcopy(rows[2]);retry['arrival_time']=190;d.append(retry);x=m.report(d,200);assert x['completed']==base['completed'] and x['conflict_ids']==['x-d1'] and x['retry_extra_rows']==3;record('transport-only-retry',retry_extra_rows=3)
d=copy.deepcopy(rows);change=copy.deepcopy(rows[2]);change.update(assistance='assisted',arrival_time=190);d.append(change);x=m.report(d,200);assert 'c-a1' in x['conflict_ids'] and 'a1' in x['unresolved'] and 'a1' not in x['completed'];record('semantic-conflict-whole-id',conflicts=x['conflict_ids'],unresolved=x['unresolved'])
# Changed semantic event outside event window still conflicts before event-time selection.
d=copy.deepcopy(rows);change=copy.deepcopy(rows[2]);change.update(event_time=120,arrival_time=190);d.append(change);x=m.report(d,200);assert 'a1' in x['unresolved'];record('conflict-before-event-window',unresolved=x['unresolved'])
# Future arrivals cannot change earlier knowledge.
x=m.report(rows+[dict(rows[2],assistance='assisted',arrival_time=201)],200);assert x==base;record('future-arrival-no-leak')
def reject(name,added,reason):
 try:m.report(rows+[added],200)
 except ValueError as e:assert str(e)==reason;record(name,error=str(e))
 else:raise RuntimeError('accepted '+name)
reject('distinct-start',dict(rows[0],event_id='new-start'), 'multiple distinct starts')
reject('distinct-terminal',dict(rows[2],event_id='new-terminal'), 'multiple distinct terminals')
reject('actor-mismatch',dict(rows[2],event_id='other-actor',actor_id='OTHER'), 'actor mismatch')
reject('before-start',dict(rows[2],event_id='too-early',event_time=9), 'outcome before start')
for name in ('optimized','report-import-failure'):
 d=O/name
 if d.exists():raise RuntimeError('refuse prior directory')
 shutil.copytree(F,d)
 if name=='report-import-failure':(d/'report.py').write_text("raise ImportError('synthetic report failure')\n")
 cmd=[sys.executable]+(['-O'] if name=='optimized' else [])+[str(d/'run.py')];p=subprocess.run(cmd,capture_output=True,text=True,timeout=10)
 (d/'stdout.txt').write_text(p.stdout);(d/'stderr.txt').write_text(p.stderr);assert p.returncode==1 and not (d/'results/summary.json').exists();record(name,command=cmd,exit=1,summary_exists=False)
(O/'observations.json').write_text(json.dumps(notes,indent=2)+'\n');print(json.dumps(notes,indent=2))
