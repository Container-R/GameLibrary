"""Literal membership oracle, does not import report/run."""
import json,hashlib,sys
from pathlib import Path
if sys.flags.optimize:raise SystemExit('Refusing optimized oracle')
r=Path(sys.argv[1]);rows=json.loads((r/'fictional-events.json').read_text());s=json.loads((r/'summary.json').read_text());assert len(rows)==18
assert [x['event_id'] for x in rows]==['s-a1','s-a1','c-a1','c-a1','s-a2','f-a2','s-b1','c-b1','s-c1','c-c1','s-d1','x-d1','x-d1','c-z','s-e1','s-old','c-old','future-a2']
assert [(x['event_time'],x['arrival_time']) for x in rows]==[(10,11),(10,12),(20,21),(20,22),(30,31),(40,41),(12,13),(25,26),(14,15),(50,150),(16,17),(35,36),(35,37),(45,46),(18,19),(-10,1),(60,61),(110,111)]
expected={100:(['a1','b1'],['c1','d1','e1'],[2,6],[2,5],[2,3],0,16,[6,7]),200:(['a1','b1','c1'],['d1','e1'],[3,6],[3,5],[3,4],1,18,[7,7])}
for cutoff,(completed,unresolved,attempt,actors,finished,unknown,visible,raw) in expected.items():
 a=json.loads((r/f'asof-{cutoff}.json').read_text());assert a==s['reports'][str(cutoff)]
 want=dict(asof=cutoff,event_window=[0,100],visible_rows=visible,raw_fraction=raw,retry_extra_rows=2,conflict_ids=['x-d1'],quarantined_rows=2,cohort_attempts=['a1','a2','b1','c1','d1','e1'],cohort_actors=['P','Q','R','S','T'],completed=completed,failed=['a2'],unresolved=unresolved,conflict_affected_unresolved=['d1'],orphan_event_ids=['c-z'],out_of_cohort_event_ids=['c-old'],completion_per_started_attempt=attempt,actors_with_completion_per_starting_actor=actors,completed_actors=['P','Q']+(['R'] if cutoff==200 else []),finished_only_fraction=finished,assistance=dict(unassisted=1,assisted=1,unknown=unknown))
 assert a==want
assert s['total_report_comparisons']==12 and s['order_checks']==['original','reverse','shuffle-0','shuffle-1','shuffle-7','shuffle-42']
assert s['fixture_sha256']==hashlib.sha256((r/'fictional-events.json').read_bytes()).hexdigest()
print(json.dumps(dict(status='PASS',literal_memberships={k: v[:2] for k,v in expected.items()},comparisons_recorded=12),indent=2))
