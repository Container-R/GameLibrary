"""Independent finite raw observation check; stdlib only, no engine/author imports."""
import json,hashlib,sys
from pathlib import Path

def require(value,label):
 if not value:raise ValueError(label)
def check(p):
 r=json.loads((p/'receipt.json').read_text());require(r['status']=='PASS','receipt')
 require(len(r['processes'])==2 and [x['name'] for x in r['processes']]==['version','behavior'],'counts')
 for proc in r['processes']:
  require(proc['status']=='RETURNED' and type(proc['returncode']) is int and proc['returncode']==0,'exit')
  for stream in ('stdout','stderr'):
   data=(p/(proc['name']+'.'+stream)).read_bytes();require(hashlib.sha256(data).hexdigest()==proc[stream+'_sha256'],'rawhash')
   if stream=='stderr':require(data==b'','diagnostics')
 require(r['source_sha256']==r['source_after'] and r['binary_before']==r['binary_after'],'beforeafter')
 lines=(p/'behavior.stdout').read_text().splitlines();payload=[x[12:] for x in lines if x.startswith('RESULT_JSON=')];require(len(payload)==1,'result')
 obj=json.loads(payload[0]);rows=obj['trace'];require(len(rows)==20,'row count')
 ids={k:n['id'] for k,n in rows[0]['nodes'].items()};require(all(type(x) is int and x!=0 for x in ids.values()) and len(set(ids.values()))==5,'node identities')
 op,de=ids['opener'],ids['default'];vp=obj['viewport_id']
 parent={'fixture':vp,'background':ids['fixture'],'modal':ids['fixture'],'opener':ids['background'],'default':ids['modal']}
 markers=[('initial',0,2,0,2),('before_baseline_grab',0,2,0,2),('baseline_after_grab',op,2,0,2),('before_parent_disable',op,2,0,2),('after_parent_disable',0,1,0,0),('before_modal_grab',0,1,0,0),('modal_after_grab',de,1,0,0),('before_child_enable',de,1,0,0),('after_child_enable',de,1,2,2),('before_naive_grab',de,1,2,2),('naive_after_grab',op,1,2,2),('deferred_final',op,1,2,2)]
 mi=0;events=[];phase=None
 for i,row in enumerate(rows,1):
  require(row['sequence']==i,'sequence')
  for k,n in row['nodes'].items():
   require(type(n['id']) is int and n['id']==ids[k] and n['parent_id']==parent[k] and n['viewport_id']==vp,'tree')
   require(n['inside_tree'] is True and n['visible_in_tree'] is True and n['in_modal'] is (k=='default'),'scope')
  kind=row['kind']
  if kind in ('focus_entered','focus_exited','gui_focus_changed'):
   require(row['phase']==phase,'callback phase');target=row['target_id'];require(target in (op,de),'callback target')
   require(row['owner_id']==(0 if kind=='focus_exited' else target),'callback actual owner');events.append((phase,kind,target));continue
  label,owner,bg,child,eff=markers[mi];mi+=1;phase=label
  require(kind==row['phase']==label and row['owner_id']==owner,'marker actual owner')
  n=row['nodes'];require((n['background']['behavior'],n['opener']['behavior'],n['opener']['effective_mode'])==(bg,child,eff),'postcall eligibility')
  require(n['opener']['local_mode']==2 and n['default']['effective_mode']==2,'local/default mode')
 expected=[('before_baseline_grab','gui_focus_changed',op),('before_baseline_grab','focus_entered',op),('before_parent_disable','focus_exited',op),('before_modal_grab','gui_focus_changed',de),('before_modal_grab','focus_entered',de),('before_naive_grab','focus_exited',de),('before_naive_grab','gui_focus_changed',op),('before_naive_grab','focus_entered',op)]
 require(mi==12 and sorted(events)==sorted(expected),'finite events')
 return {'uuid':r['uuid'],'status':'ACCEPTED_OBSERVATION','version_processes':1,'behavior_processes':1,'markers':mi,'signals':len(events),'parent_disable_callback_effective_mode':[x['nodes']['opener']['effective_mode'] for x in rows if x['phase']=='before_parent_disable' and x['kind']=='focus_exited'][0]}
if __name__=='__main__':print(json.dumps(check(Path(sys.argv[1])),indent=2))
