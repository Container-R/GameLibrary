import hashlib,json,random,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
(OUT/'summary.json').unlink(missing_ok=True)
if not __debug__:raise SystemExit('optimized invocation rejected')
import report

def need(ok,why):
    if not ok:raise RuntimeError(why)
rowspec=[
 ('s-a1','a1','P','start',10,11,None),('s-a1','a1','P','start',10,12,None),
 ('c-a1','a1','P','complete',20,21,'unassisted'),('c-a1','a1','P','complete',20,22,'unassisted'),
 ('s-a2','a2','P','start',30,31,None),('f-a2','a2','P','fail',40,41,None),
 ('s-b1','b1','Q','start',12,13,None),('c-b1','b1','Q','complete',25,26,'assisted'),
 ('s-c1','c1','R','start',14,15,None),('c-c1','c1','R','complete',50,150,None),
 ('s-d1','d1','S','start',16,17,None),('x-d1','d1','S','complete',35,36,None),
 ('x-d1','d1','S','fail',35,37,None),('c-z','z','U','complete',45,46,None),
 ('s-e1','e1','T','start',18,19,None),('s-old','old','W','start',-10,1,None),
 ('c-old','old','W','complete',60,61,None),('future-a2','a2','P','complete',110,111,None)]
rows=[]
for eid,aid,actor,kind,et,at,assist in rowspec:
    r=dict(event_id=eid,attempt_id=aid,actor_id=actor,kind=kind,event_time=et,arrival_time=at)
    if assist is not None:r['assistance']=assist
    rows.append(r)
(OUT/'fictional-events.json').write_text(json.dumps(rows,indent=2)+'\n')
rows=json.loads((OUT/'fictional-events.json').read_text())
expected_common=dict(event_window=[0,100],retry_extra_rows=2,conflict_ids=['x-d1'],quarantined_rows=2,
 cohort_attempts=['a1','a2','b1','c1','d1','e1'],cohort_actors=['P','Q','R','S','T'],failed=['a2'],
 conflict_affected_unresolved=['d1'],orphan_event_ids=['c-z'],out_of_cohort_event_ids=['c-old'])
expected={
100:dict(asof=100,visible_rows=16,raw_fraction=[6,7],completed=['a1','b1'],unresolved=['c1','d1','e1'],
 completion_per_started_attempt=[2,6],actors_with_completion_per_starting_actor=[2,5],completed_actors=['P','Q'],
 finished_only_fraction=[2,3],assistance={'unassisted':1,'assisted':1,'unknown':0}),
200:dict(asof=200,visible_rows=18,raw_fraction=[7,7],completed=['a1','b1','c1'],unresolved=['d1','e1'],
 completion_per_started_attempt=[3,6],actors_with_completion_per_starting_actor=[3,5],completed_actors=['P','Q','R'],
 finished_only_fraction=[3,4],assistance={'unassisted':1,'assisted':1,'unknown':1})}
reports={};orders=[('original',rows),('reverse',list(reversed(rows)))]
for seed in (0,1,7,42):
    perm=list(rows);random.Random(seed).shuffle(perm);orders.append((f'shuffle-{seed}',perm))
for cutoff in (100,200):
    want={**expected_common,**expected[cutoff]}
    for name,batch in orders:
        got=report.report(batch,cutoff);need(got==want,f'{cutoff}/{name} mismatch: {got}')
    reports[str(cutoff)]=want
    (OUT/f'asof-{cutoff}.json').write_text(json.dumps(want,indent=2)+'\n')
summary=dict(status='PASS',python=sys.version,scope='fictional complete-batch metric model, no vendor execution',
 source_sha256={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ('report.py','run.py','contract.md')},
 fixture_sha256=hashlib.sha256((OUT/'fictional-events.json').read_bytes()).hexdigest(),
 reports=reports,order_checks=[name for name,_ in orders],total_report_comparisons=12)
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print('RESULT_JSON '+json.dumps(summary,sort_keys=True))
