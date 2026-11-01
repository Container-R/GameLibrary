"""Finite literal trace oracle. No Godot imports or native calls."""
import json, math
VERSION={'major':4,'minor':6,'patch':3,'hex':263683,'status':'stable','build':'official','hash':'7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3','timestamp':0,'string':'4.6.3-stable (official)'}
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
def equal(a,b,msg):
 need(type(a) is type(b),msg+' type')
 if type(a) is dict:
  need(set(a)==set(b),msg+' keys')
  for k in a:equal(a[k],b[k],msg)
 elif type(a) is list:
  need(len(a)==len(b),msg+' length')
  for x,y in zip(a,b):equal(x,y,msg)
 else:need(a==b,msg)

def transform(t,origin):
 need(type(t) is dict and set(t)=={'origin','basis'},'transform schema');vec(t['origin'],origin)
 need(type(t['basis']) is list and len(t['basis'])==3,'basis shape')
 for col,wanted in zip(t['basis'],[[1,0,0],[0,1,0],[0,0,1]]):vec(col,wanted)
def typed_id(x):need(integer(x) and x!=0,'opaque identity')
def config(c,origins):
 typed_id(c['root_id']);transform(c['root_transform'],[0,0,0]);equal(c['backend_setting'],'GodotPhysics3D','selected backend');need(type(c['server_class']) is str and bool(c['server_class']),'diagnostic class')
 equal(c['static_mode'],0,'static enum');equal(c['kinematic_mode'],1,'kinematic enum');need(type(c['actors']) is list and len(c['actors'])==2,'actors');near(c['query_radius'],.5)
 ids=[c['root_id'],c['query_resource_id']];rids=[c['query_rid']]
 for i,b in enumerate([c['wall']]+c['actors']):
  for key in ['id','shape_node_id','shape_resource_id']:typed_id(b[key]);ids.append(b[key])
  for key in ['rid','shape_rid']:typed_id(b[key]);rids.append(b[key])
  equal(b['class'],'StaticBody3D' if i==0 else 'CharacterBody3D','class');equal(b['parent_id'],c['root_id'],'body parent');equal(b['shape_parent_id'],b['id'],'shape parent')
  equal(b['layer'],2 if i==0 else 1,'layer');equal(b['mask'],1 if i==0 else 2,'mask');equal(b['locks'],[False]*6,'locks');equal(b['exceptions'],[],'exceptions');equal(b['mode'],0 if i==0 else 1,'mode')
  equal(b['disabled'],False,'disabled');equal(b['owner_disabled'],False,'owner disabled');need(integer(b['owner']) and b['owner']>=0,'owner integer');equal(b['owners'],[b['owner']],'owners');equal(b['owner_object_id'],b['shape_node_id'],'owner node');equal(b['owner_shape_resource_id'],b['shape_resource_id'],'owner resource');equal(b['shape_count'],1,'shape count');equal(b['shape_index'],0,'shape index')
  transform(b['shape_transform'],[0,0,0]);transform(b['transform'],[2,0,0] if i==0 else origins[i-1])
  if i==0:vec(b['size'],[1,4,2]);vec(b['linear_velocity'],[0,0,0]);vec(b['angular_velocity'],[0,0,0])
  else:near(b['radius'],.5);vec(b['velocity'],[0,0,0]);near(b['character_safe_margin'],.001)
 for x in ids+rids:typed_id(x)
 need(len(set(ids))==len(ids) and len(set(rids))==len(rids),'distinct IDs/resources/RIDs')
def check(d):
 equal(d['version'],VERSION,'version');c=d['initial'];config(c,[[0,0,0],[0,0,4]])
 n=d['readiness_attempts'];need(integer(n) and 1<=n<=120,'readiness attempts');trace=d['trace'];need(type(trace) is list and len(trace)==n+8,'query and move record counts')
 wall=c['wall'];actors=c['actors'];previous_frame=-1;ready_frame=None;ready_delta=None
 def query(e,label,origin,callback,hits):
  nonlocal previous_frame,ready_frame,ready_delta
  equal(e['kind'],'query','query kind');equal(e['label'],label,'query label');equal(e['callback'],callback,'query callback');need(integer(e['frame']) and e['frame']>=0,'frame type');need(number(e['delta']) and e['delta']>0,'delta')
  if label=='positive':need(e['frame']>previous_frame,'readiness frame advance');previous_frame=e['frame']
  else:equal(e['frame'],ready_frame,'successful callback frame');near(e['delta'],ready_delta,0)
  p=e['parameters'];equal(set(p),{'shape_resource_id','shape_rid','transform','margin','motion','mask','bodies','areas','exclude','max_results'},'query fields')
  equal(p['shape_resource_id'],c['query_resource_id'],'query resource');equal(p['shape_rid'],c['query_rid'],'query RID');transform(p['transform'],origin);near(p['margin'],0,0);vec(p['motion'],[0,0,0]);equal(p['mask'],2,'query mask');equal(p['bodies'],True,'query bodies');equal(p['areas'],False,'query areas');equal(p['exclude'],[a['rid'] for a in actors],'exclusions');equal(p['max_results'],4,'result cap');equal(e['hits'],hits,'query hits');need(len(e['actors'])==2,'query actor count')
  for t,o in zip(e['actors'],[[0,0,0],[0,0,4]]):transform(t,o)
 for i in range(n):
  hits=[] if i<n-1 else [{'object_id':wall['id'],'collider_id':wall['id'],'rid':wall['rid'],'shape_index':0}]
  query(trace[i],'positive',[2,0,0],i+1,hits)
  if i==n-1:ready_frame=trace[i]['frame'];ready_delta=trace[i]['delta']
 for i,(label,origin) in enumerate(zip(['blocked_start','blocked_endpoint','open_start','open_endpoint'],[[0,0,0],[4,0,0],[0,0,4],[4,0,4]])):query(trace[n+i],label,origin,n,[])
 final_origins=[]
 for i in range(2):
  entry,ret=trace[n+4+2*i:n+6+2*i];a=actors[i]
  for e,kind in [(entry,'move_enter'),(ret,'move_return')]:
   equal(e['kind'],kind,'move phase');equal(e['actor'],i,'move order');equal(e['callback'],n,'move callback');equal(e['frame'],ready_frame,'move frame');near(e['delta'],ready_delta,0);equal(e['id'],a['id'],'moving identity')
  args=entry['arguments'];need(set(args)=={'motion','test_only','safe_margin','recovery_as_collision','max_collisions'},'argument fields');vec(args['motion'],[4,0,0]);equal(args['test_only'],False,'actual movement');near(args['safe_margin'],.001,0);equal(args['recovery_as_collision'],False,'recovery flag');equal(args['max_collisions'],1,'max contacts')
  start=[0,0,4*i];transform(entry['transform'],start);end=ret['transform']['origin'];transform(ret['transform'],end);vec(ret['displacement'],[x-y for x,y in zip(end,start)]);final_origins.append(end)
  hit=ret['collision']
  if i==1:need(hit is None,'open collision null');vec(end,[4,0,4]);vec(ret['displacement'],[4,0,0]);continue
  need(type(hit) is dict,'blocked collision');equal(hit['count'],1,'contact count')
  for key,val in [('object_id',wall['id']),('collider_id',wall['id']),('rid',wall['rid']),('collider_shape_node_id',wall['shape_node_id']),('local_shape_node_id',a['shape_node_id']),('shape_index',0)]:equal(hit[key],val,'collision identity '+key)
  need(number(end[0]) and .95<=end[0]<=1.05,'contact progress');near(end[1],0);near(end[2],0);vec(hit['travel'],ret['displacement']);need(0<hit['travel'][0]<4,'positive travel');need(type(hit['remainder']) is list and len(hit['remainder'])==3 and all(number(x) for x in hit['remainder']) and hit['remainder'][0]>0,'positive remainder')
  for x,y,requested in zip(hit['travel'],hit['remainder'],[4,0,0]):near(x+y,requested,1e-4)
  normal=hit['normal'];point=hit['position'];need(type(normal) is list and len(normal)==3 and all(number(x) for x in normal),'normal finite');need(normal[0]<=-.99 and abs(normal[1])<=.01 and abs(normal[2])<=.01 and abs(math.sqrt(sum(x*x for x in normal))-1)<=.01,'normal interval')
  need(type(point) is list and len(point)==3 and all(number(x) for x in point) and 1.45<=point[0]<=1.55 and abs(point[1])<=.1 and abs(point[2])<=.1,'point interval');vec(hit['velocity'],[0,0,0]);need(number(hit['depth']),'depth finite')
 config(d['final'],final_origins)
 before=json.loads(json.dumps(c));after=json.loads(json.dumps(d['final']))
 for a,b in zip(before['actors'],after['actors']):b['transform']=a['transform']
 equal(before,after,'configuration unchanged except actor position')
 return {'status':'PASS','stationary_queries':n+4,'readiness_attempts':n,'actual_moves':2,'blocked_collision':True,'open_collision':False}
