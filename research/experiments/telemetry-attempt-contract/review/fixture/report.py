"""Original finite fictional reporting policy, not a telemetry service."""
import json
from collections import defaultdict

def need(ok,msg):
    if not ok:raise ValueError(msg)

def report(rows,asof):
    visible=[r for r in rows if r['arrival_time']<=asof]
    groups=defaultdict(list)
    for r in visible:groups[r['event_id']].append(r)
    canonical=lambda r:json.dumps({k:v for k,v in r.items() if k!='arrival_time'},sort_keys=True,separators=(',',':'))
    conflicts=sorted(eid for eid,items in groups.items() if len({canonical(r) for r in items})>1)
    clean=[json.loads(canonical(items[0])) for eid,items in sorted(groups.items()) if eid not in conflicts]
    conflict_attempts=sorted({r['attempt_id'] for eid in conflicts for r in groups[eid]})
    retries=sum(len(items)-1 for eid,items in groups.items() if eid not in conflicts)
    starts={}
    for r in clean:
        if r['kind']=='start':
            need(r['attempt_id'] not in starts,'multiple distinct starts')
            starts[r['attempt_id']]=r
    cohort={aid:r for aid,r in starts.items() if 0<=r['event_time']<100}
    terminals=defaultdict(list);orphans=[];outside=[]
    for r in clean:
        if r['kind']=='start' or not 0<=r['event_time']<100:continue
        need(r['kind'] in ('complete','fail'),'unknown kind')
        aid=r['attempt_id']
        if aid not in starts:orphans.append(r['event_id']);continue
        need(starts[aid]['actor_id']==r['actor_id'],'actor mismatch')
        need(r['event_time']>=starts[aid]['event_time'],'outcome before start')
        if aid not in cohort:outside.append(r['event_id']);continue
        terminals[aid].append(r)
    completed=[];failed=[];unresolved=[];assistance={'unassisted':0,'assisted':0,'unknown':0}
    for aid in sorted(cohort):
        ts=terminals[aid];need(len(ts)<=1,'multiple distinct terminals')
        if not ts:unresolved.append(aid)
        elif ts[0]['kind']=='fail':failed.append(aid)
        else:
            completed.append(aid);context=ts[0].get('assistance','unknown')
            need(context in assistance,'assistance enum');assistance[context]+=1
    actors=sorted({r['actor_id'] for r in cohort.values()})
    completed_actors=sorted({cohort[a]['actor_id'] for a in completed})
    raw=[r for r in visible if 0<=r['event_time']<100]
    raw_start=sum(r['kind']=='start' for r in raw);raw_complete=sum(r['kind']=='complete' for r in raw)
    return dict(asof=asof,event_window=[0,100],visible_rows=len(visible),raw_fraction=[raw_complete,raw_start],
      retry_extra_rows=retries,conflict_ids=conflicts,quarantined_rows=sum(len(groups[x]) for x in conflicts),
      cohort_attempts=sorted(cohort),cohort_actors=actors,completed=completed,failed=failed,unresolved=unresolved,
      conflict_affected_unresolved=sorted(set(unresolved)&set(conflict_attempts)),
      orphan_event_ids=sorted(orphans),out_of_cohort_event_ids=sorted(outside),
      completion_per_started_attempt=[len(completed),len(cohort)],
      actors_with_completion_per_starting_actor=[len(completed_actors),len(actors)],
      completed_actors=completed_actors,finished_only_fraction=[len(completed),len(completed)+len(failed)],assistance=assistance)
