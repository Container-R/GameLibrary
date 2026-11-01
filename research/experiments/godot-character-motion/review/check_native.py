"""Independent observed-layout checker; no author imports or native calls.
Complements, rather than replaces, the full author schema/environment consumer.
Usage: python check_native.py SOURCE_ROOT EVIDENCE_DIR
"""
import sys,json,hashlib,math
from pathlib import Path
if sys.flags.optimize: pass  # checks below are explicit, not assert statements

def need(v,msg):
 if not v: raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def near(a,b,e=1e-5):
 need(len(a)==len(b) and all(type(x) in (float,int) and math.isfinite(x) and abs(x-y)<=e for x,y in zip(a,b)), 'vector mismatch')
def main(root,out):
 r=json.loads((out/'receipt.json').read_text());need(r['status']=='PASS' and r['uuid']==out.name,'receipt')
 need(r['source_sha256']==r['source_after'],'source drift')
 for n,h in r['source_sha256'].items():need(sha(root/n)==h,'source '+n)
 need(r['source_sha256']['main.gd']=='0697b51ff020e9a42dcfcb4e7dd8d2c1cb516cb0f21a8b609fd871a8931a6595','GD pin')
 need(r['binary_before']==r['binary_after']=='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3','binary recorded identity')
 need([p['name'] for p in r['processes']]==['version','behavior'],'process count')
 for p in r['processes']:
  need(p['status']=='RETURNED' and type(p['returncode']) is int and p['returncode']==0,'process outcome')
  for stream in ('stdout','stderr'):need(sha(out/(p['name']+'.'+stream))==p[stream+'_sha256'],'raw hash')
  need((out/(p['name']+'.stderr')).read_bytes()==b'','stderr')
 need((out/'version.stdout').read_text().strip()=='4.6.3.stable.official.7d41c59c4','version')
 lines=(out/'behavior.stdout').read_text().splitlines();payload=[s for s in lines if s.startswith('RESULT_JSON=')]
 need(len(payload)==1 and not any('ERROR' in s or s.startswith('FAIL_JSON=') for s in lines),'raw records')
 d=json.loads(payload[0].split('=',1)[1]);need(d==json.loads((out/'behavior.json').read_text()) and sha(out/'behavior.json')==r['parsed_sha256'],'parsed association')
 c=d['initial'];f=d['final'];w=c['wall'];aa=c['actors'];t=d['trace'];n=d['readiness_attempts']
 need(type(n) is int and 1<=n<=120,'readiness');need(len(t)==n+8,'trace length')
 need(c['backend_setting']=='GodotPhysics3D','configured backend');near(w['transform']['origin'],[2,0,0]);near(w['size'],[1,4,2])
 for i,a in enumerate(aa):
  need(a['class']=='CharacterBody3D' and a['mode']==1 and a['layer']==1 and a['mask']==2 and a['radius']==.5,'actor settings')
  need(type(a['id']) is int and a['id']!=0 and a['owner_object_id']==a['shape_node_id'] and a['owner_shape_resource_id']==a['shape_resource_id'] and a['shape_node_id']!=a['shape_resource_id'],'owner/resource')
  near(a['transform']['origin'],[0,0,4*i]);need(a['shape_parent_id']==a['id'],'shape parent')
 need(w['owner_object_id']==w['shape_node_id'] and w['owner_shape_resource_id']==w['shape_resource_id'],'wall owners')
 queries=t[:n+4];need([e['label'] for e in queries]==['positive']*n+['blocked_start','blocked_endpoint','open_start','open_endpoint'],'query order')
 origins=[[2,0,0]]*n+[[0,0,0],[4,0,0],[0,0,4],[4,0,4]]
 for j,(e,origin) in enumerate(zip(queries,origins)):
  need(e['kind']=='query','kind');near(e['parameters']['transform']['origin'],origin)
  p=e['parameters'];need(p['shape_resource_id']==c['query_resource_id'] and p['shape_rid']==c['query_rid'] and p['exclude']==[a['rid'] for a in aa] and p['mask']==2 and p['bodies'] is True and p['areas'] is False and p['margin']==0,'query settings')
  for i,pose in enumerate(e['actors']):near(pose['origin'],[0,0,4*i])
  if j==n-1:
   need(len(e['hits'])==1,'positive hit');h=e['hits'][0];need(h['object_id']==h['collider_id']==w['id'] and h['rid']==w['rid'] and h['shape_index']==0,'wall hit')
  else:need(e['hits']==[],'empty control/pending')
 frame=t[n-1]['frame'];need(all(e['callback']==n and e['frame']==frame for e in t[n-1:]),'same actual callback')
 moves=t[n+4:];need([e['kind'] for e in moves]==['move_enter','move_return']*2,'move order')
 for i in range(2):
  enter,ret=moves[2*i:2*i+2];a=aa[i]
  need(enter['actor']==ret['actor']==i and enter['id']==ret['id']==a['id'],'move identity')
  args=enter['arguments'];need(args=={'motion':[4,0,0],'test_only':False,'safe_margin':.001,'recovery_as_collision':False,'max_collisions':1},'arguments')
  near(enter['transform']['origin'],[0,0,4*i]);near(ret['displacement'],[x-y for x,y in zip(ret['transform']['origin'],enter['transform']['origin'])]);near(f['actors'][i]['transform']['origin'],ret['transform']['origin'])
  if i==0:
   co=ret['collision'];need(co['count']==1 and co['object_id']==co['collider_id']==w['id'] and co['rid']==w['rid'] and co['shape_index']==0,'collision identity')
   need(co['local_shape_node_id']==a['shape_node_id'] and co['collider_shape_node_id']==w['shape_node_id'],'collision owner nodes')
   near(co['travel'],ret['displacement']);near([x+y for x,y in zip(co['travel'],co['remainder'])],[4,0,0],1e-4)
   need(.95<=ret['transform']['origin'][0]<=1.05 and co['remainder'][0]>0,'bounded stop');near(ret['transform']['origin'][1:],[0,0]);near(co['normal'],[-1,0,0],.01);near(co['position'],[1.5,0,0],.05);need(math.isfinite(co['depth']),'finite depth')
  else:need(ret['collision'] is None,'open null');near(ret['transform']['origin'],[4,0,4]);near(ret['displacement'],[4,0,0])
 return {'uuid':r['uuid'],'readiness_attempts':n,'stationary_queries':len(queries),'actual_moves':2,'blocked_travel':moves[1]['collision']['travel'],'remainder':moves[1]['collision']['remainder'],'contact_position':moves[1]['collision']['position'],'normal':moves[1]['collision']['normal'],'depth':moves[1]['collision']['depth'],'open_position':moves[3]['transform']['origin'],'status':'CONSISTENT_OBSERVED_LAYOUT'}
if __name__=='__main__':print(json.dumps(main(Path(sys.argv[1]),Path(sys.argv[2])),indent=2))
