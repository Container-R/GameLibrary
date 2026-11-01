"""Finite literal trace oracle. No Godot imports or native calls."""
import json, math
VERSION={'major':4,'minor':6,'patch':3,'hex':263683,'status':'stable','build':'official','hash':'7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3','timestamp':0,'string':'4.6.3-stable (official)'}
TARGETS=[[8,0,2],[22,0,2]];ENDS=[[8,0,2],[10,0,2]]
CALLS=['get_next_path_position','is_navigation_finished','is_target_reachable','get_final_position']
SETTINGS={'navigation_layers':1,'avoidance_enabled':False,'path_height_offset':0,'path_desired_distance':.1,'target_desired_distance':.1,'path_max_distance':1,'simplify_path':False,'path_return_max_length':0,'path_return_max_radius':0,'path_search_max_distance':0,'path_search_max_polygons':4096,'pathfinding_algorithm':0,'path_postprocessing':0,'path_metadata_flags':7}
def need(x,msg):
 if not x:raise ValueError(msg)
def pairs(items):
 d={}
 for k,v in items:need(k not in d,'duplicate JSON key');d[k]=v
 return d
def load(raw):
 def reject(x):raise ValueError('nonfinite JSON constant')
 d=json.loads(raw,object_pairs_hook=pairs,parse_constant=reject)
 def walk(v):
  if isinstance(v,float):need(math.isfinite(v),'nonfinite JSON number')
  elif isinstance(v,dict):
   for x in v.values():walk(x)
  elif isinstance(v,list):
   for x in v:walk(x)
 walk(d);return d
def integer(x):return type(x) is int
def number(x):return type(x) in (int,float) and math.isfinite(x)
def near(a,b,e=1e-5):
 need(number(a) and number(b) and abs(a-b)<=e,'numeric mismatch')
def vec(a,b):
 need(type(a) is list and len(a)==3,'vector shape')
 for x,y in zip(a,b):near(x,y)
def equal(a,b,msg):need(type(a) is type(b) and a==b,msg)
def check(d):
 equal(d['version'],VERSION,'version self report')
 for k,v in VERSION.items():equal(d['version'][k],v,'version field type')
 need(integer(d['root_id']) and d['root_id']!=0,'root identity')
 r=d['ready'];need(integer(r['readiness_callbacks']) and 1<=r['readiness_callbacks']<=240,'readiness bound');need(integer(r['map_id']) and r['map_id']!=0,'map identity')
 equal(r['initial_iteration'],0,'initial iteration');need(integer(r['iteration']) and r['iteration']>0,'map iteration');equal(r['matched'],True,'map signal')
 equal(r['active'],True,'map active');equal(r['async'],False,'map async');equal(r['edge_connections'],False,'edges');equal(r['links'],0,'links');vec(r['up'],[0,1,0]);near(r['cell_size'],.25);near(r['cell_height'],.25)
 need(len(r['regions'])==2,'regions');rid=[]
 for z in r['regions']:
  need(integer(z['id']) and z['id']!=0,'region id');rid.append(z['id']);need(integer(z['iteration']) and z['iteration']>0,'region ready');equal(z['map'],r['map_id'],'region map');equal(z['enabled'],True,'region enabled');equal(z['layers'],1,'region layer');equal(z['async'],False,'region async')
 need(len(set(rid))==2 and sorted(r['registered'])==sorted(rid) and all(integer(x) for x in r['registered']),'registered regions')
 need(len(r['projections'])==3,'projections')
 for q,p,o in zip(r['projections'],[[2,0,2]]+TARGETS,[rid[0],rid[0],rid[1]]):vec(q['input'],p);vec(q['point'],p);equal(q['owner'],o,'projected owner')
 need(len(d['geometry'])==2 and len(d['identities'])==2,'geometry/identity count')
 ids=[]
 for i,(g,a) in enumerate(zip(d['geometry'],d['identities'])):
  x=20*i;expected=[[x,0,0],[x,0,4],[x+10,0,4],[x+10,0,0]]
  equal(g['vertices'],expected,'literal geometry');equal(g['polygon'],[0,1,2,3],'polygon')
  equal(a['label'],['Reachable','Partial'][i],'label')
  for key in ('agent_id','parent_id'):need(integer(a[key]) and a[key]!=0,'instance ID');ids.append(a[key])
  equal(a['actual_parent_id'],a['parent_id'],'actual parent');equal(a['root_id'],d['root_id'],'actual root');equal(a['map_id'],r['map_id'],'agent map');vec(a['target'],TARGETS[i]);need(set(a['settings'])==set(SETTINGS),'settings keys')
  for k,v in SETTINGS.items():
   if type(v) is bool:equal(a['settings'][k],v,'bool setting')
   elif type(v) is int and k not in ('path_height_offset','path_max_distance','path_return_max_length','path_return_max_radius','path_search_max_distance'):equal(a['settings'][k],v,'int setting')
   else:near(a['settings'][k],v)
 need(len(set(ids+[d['root_id']]))==5,'unique nodes')
 need(len(d['initial_identities'])==2,'initial identities')
 for initial,final in zip(d['initial_identities'],d['identities']):equal(initial,{k:v for k,v in final.items() if k!='target'},'pre-movement config binding')
 need(integer(d['steps']) and 1<=d['steps']<=48,'driver count')
 events=d['events'];need(type(events) is list and len(events)<3000,'event bound');at=0;positions=[[2,0,2],[2,0,2]];done=[False,False];target_counts=[0,0];finish_counts=[0,0];moves=[0,0];snaps=[];paths=[None,None];last_frame=-1
 def take(kind,i,step,call='none',phase='queries'):
  nonlocal at,last_frame
  need(at<len(events),'trace missing');e=events[at];at+=1
  equal(e['kind'],kind,'event kind');equal(e['agent'],i,'event agent');equal(e['step'],step,'step');equal(e['call'],call,'call');equal(e['phase'],phase,'phase')
  need(integer(e['frame']) and e['frame']>=last_frame,'frame order');last_frame=e['frame'];a=d['identities'][i];equal(e['agent_id'],a['agent_id'],'event node');equal(e['parent_id'],a['parent_id'],'event parent');vec(e['position'],positions[i]);return e
 for step in range(1,d['steps']+1):
  rows={};step_frame=None
  for i in range(2):
   if done[i]:continue
   e=take('before_update',i,step);frame=e['frame'];need(step_frame is None or step_frame==frame,'same callback frame');step_frame=frame
   values={}
   for call in CALLS:
    take('call_enter',i,step,call)
    while at<len(events) and events[at]['kind']=='signal':
     e=take('signal',i,step,call);s=e['signal'];need(s in ('path_changed','waypoint_reached','target_reached','navigation_finished'),'signal name')
     if s=='target_reached':need(i==0 and not done[i],'unexpected target');target_counts[i]+=1;need(target_counts[i]==1,'duplicate target')
     if s=='navigation_finished':
      need(not done[i] and (i==1 or target_counts[i]==1),'finish ordering');finish_counts[i]+=1;done[i]=True
     if s=='waypoint_reached':need(type(e['waypoint']) is list,'waypoint details');near(e['waypoint'][1],0);near(e['waypoint'][2],2)
     if s=='path_changed':need(step==1,'unexpected repath')
    values[call]=take('call_return',i,step,call)['value']
   row=take('after_queries',i,step)['snapshot'];snaps.append(row);rows[i]=row
   equal(row['agent'],i,'snapshot agent');equal(row['step'],step,'snapshot step');equal(row['frame'],frame,'snapshot frame');vec(row['parent'],positions[i]);vec(row['next'],values[CALLS[0]]);equal(row['finished'],values[CALLS[1]],'finished call binding');equal(row['reachable'],values[CALLS[2]],'reachable binding');vec(row['final'],values[CALLS[3]])
   equal(row['finished'],done[i],'finish latch');equal(row['reachable'],i==0,'reachable state');equal(row['reached'],target_counts[i]==1,'reached state');near(row['distance'],math.dist(positions[i],TARGETS[i]))
   p=row['path'];need(type(p) is list and 2<=len(p)<=64,'path bounds');vec(p[0],[2,0,2]);vec(p[-1],ENDS[i]);vec(row['final'],ENDS[i]);prev=2
   for v in p:
    need(type(v) is list and len(v)==3 and all(number(x) for x in v),'path finite');near(v[1],0);near(v[2],2);need(prev-1e-5<=v[0]<=ENDS[i][0]+1e-5,'path range/order');prev=v[0]
   if paths[i] is None:paths[i]=p
   else:equal(p,paths[i],'path changed')
   need(integer(row['index']) and 0<=row['index']<len(p),'path index');vec(row['next'],p[row['index']])
   if step==1:need(not done[i] and not row['reached'],'premature completion')
   if done[i]:need(math.dist(positions[i],ENDS[i])<.1 and (i==0 or math.dist(positions[i],TARGETS[i])>.1),'terminal distance')
  for i,row in rows.items():
   if done[i]:continue
   old=positions[i][:];n=row['next'];length=math.dist(old,n);fraction=min(1,.5/length) if length else 0;new=[a+(b-a)*fraction for a,b in zip(old,n)];positions[i]=new
   e=take('position_assigned',i,step,phase='movement');vec(e['old'],old);vec(e['next'],n);vec(e['computed'],new);moves[i]+=1
  if all(done):need(step==d['steps'],'extra driver callback')
 need(at==len(events),'trailing events');equal(d['snapshots'],snaps,'snapshot association');equal(d['initial_paths'],paths,'initial path association');need(done==[True,True] and target_counts==[1,0] and finish_counts==[1,1] and all(moves),'terminal counts')
 return {'status':'PASS','agents':2,'target_signals':target_counts,'finish_signals':finish_counts,'driver_callbacks':d['steps'],'position_assignments':moves}
