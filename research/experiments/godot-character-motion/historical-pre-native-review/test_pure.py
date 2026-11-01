"""Synthetic evidence only. No Godot invocation or collision simulation."""
import copy,json,hashlib,uuid,unittest,tempfile,subprocess,sys,shutil
from pathlib import Path
from oracle import check,load,VERSION
from consumer import verify,SOURCES
ROOT=Path(__file__).resolve().parent

def xf(p):return {'origin':p,'basis':[[1,0,0],[0,1,0],[0,0,1]]}
def fixture():
 def body(i,pos):
  w=i==0;b={'id':10+i,'rid':200+i,'class':'StaticBody3D' if w else 'CharacterBody3D','parent_id':1,'transform':xf(pos),'layer':2 if w else 1,'mask':1 if w else 2,'locks':[False]*6,'exceptions':[],'mode':0 if w else 1,'shape_node_id':20+i,'shape_parent_id':10+i,'shape_transform':xf([0,0,0]),'disabled':False,'shape_resource_id':30+i,'shape_rid':210+i,'owners':[0],'owner':0,'owner_object_id':20+i,'shape_count':1,'owner_shape_resource_id':30+i,'shape_index':0,'owner_disabled':False}
  if w:b.update(size=[1,4,2],linear_velocity=[0,0,0],angular_velocity=[0,0,0])
  else:b.update(radius=.5,velocity=[0,0,0],character_safe_margin=.001)
  return b
 c={'root_id':1,'root_transform':xf([0,0,0]),'backend_setting':'GodotPhysics3D','server_class':'PhysicsServer3D','wall':body(0,[2,0,0]),'actors':[body(1,[0,0,0]),body(2,[0,0,4])],'query_resource_id':40,'query_rid':220,'query_radius':.5,'static_mode':0,'kinematic_mode':1}
 trace=[]
 for label,point in [('positive',[2,0,0]),('blocked_start',[0,0,0]),('blocked_endpoint',[4,0,0]),('open_start',[0,0,4]),('open_endpoint',[4,0,4])]:
  trace.append({'kind':'query','label':label,'callback':1,'frame':5,'delta':1/60,'parameters':{'shape_resource_id':40,'shape_rid':220,'transform':xf(point),'margin':0,'motion':[0,0,0],'mask':2,'bodies':True,'areas':False,'exclude':[201,202],'max_results':4},'hits':[{'object_id':10,'collider_id':10,'rid':200,'shape_index':0}] if label=='positive' else [],'actors':[xf([0,0,0]),xf([0,0,4])]})
 for i in range(2):
  base={'actor':i,'callback':1,'frame':5,'delta':1/60,'id':11+i}
  trace.append(dict(base,kind='move_enter',arguments={'motion':[4,0,0],'test_only':False,'safe_margin':.001,'recovery_as_collision':False,'max_collisions':1},transform=xf([0,0,4*i])))
  hit={'count':1,'travel':[.999,0,0],'remainder':[3.001,0,0],'depth':0,'object_id':10,'collider_id':10,'rid':200,'collider_shape_node_id':20,'local_shape_node_id':21,'shape_index':0,'normal':[-1,0,0],'position':[1.5,0,0],'velocity':[0,0,0]} if i==0 else None
  trace.append(dict(base,kind='move_return',transform=xf([.999,0,0] if i==0 else [4,0,4]),displacement=[.999,0,0] if i==0 else [4,0,0],collision=hit))
 final=copy.deepcopy(c);final['actors'][0]['transform']=xf([.999,0,0]);final['actors'][1]['transform']=xf([4,0,4])
 return {'version':VERSION.copy(),'initial':c,'final':final,'readiness_attempts':1,'trace':trace}

def synthetic_archive(base):
 root=base/'source';root.mkdir()
 for n in SOURCES:shutil.copy(ROOT/n,root/n)
 out=root/'evidence'/str(uuid.uuid4());out.mkdir(parents=True)
 def sha(b):return hashlib.sha256(b).hexdigest()
 d=fixture();parsed=(json.dumps(d)+'\n').encode();stdout=b'Godot Engine v4.6.3.stable.official.7d41c59c4 - https://godotengine.org\nRESULT_JSON='+json.dumps(d).encode()+b'\n'
 (out/'behavior.json').write_bytes(parsed)
 processes=[]
 for index,(name,raw,argv) in enumerate([('version',b'4.6.3.stable.official.7d41c59c4\n',['/usr/local/bin/godot','--version']),('behavior',stdout,['/usr/local/bin/godot','--headless','--path',str(root),'--single-threaded-scene','--script',str(root/'main.gd')])]):
  (out/(name+'.stdout')).write_bytes(raw);(out/(name+'.stderr')).write_bytes(b'')
  processes.append({'name':name,'argv':argv,'timeout_seconds':10 if index==0 else 20,'status':'RETURNED','attempted_utc':f'2026-11-01T01:00:0{index*2}+00:00','returned_utc':f'2026-11-01T01:00:0{index*2+1}+00:00','pid':100+index,'returncode':0,'stdout_sha256':sha(raw),'stderr_sha256':sha(b'')})
 hashes={n:sha((root/n).read_bytes()) for n in SOURCES}
 r={'status':'PASS','uuid':out.name,'source_sha256':hashes,'source_after':hashes.copy(),'binary_before':'f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3','binary_after':'f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3','original_source_directory':str(root),'original_process_directory':str(out),'base_environment':{'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'},'selected_environment':{k:str(out/'environment'/k) for k in ('HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR')},'behavior_processes':1,'version_processes':1,'processes':processes,'parsed_sha256':sha(parsed),'oracle':check(d)}
 (out/'receipt.json').write_text(json.dumps(r));return root,out,r
class Pure(unittest.TestCase):
 def test_control(self):self.assertEqual(check(fixture())['actual_moves'],2)
 def test_motion_and_ownership(self):
  mutations=[lambda d:d['trace'][6]['collision'].update(local_shape_node_id=31),lambda d:d['trace'][6]['collision'].update(collider_shape_node_id=30),lambda d:d['trace'][6]['collision'].update(remainder=[4,0,0]),lambda d:d['trace'][6]['collision'].update(normal=[1,0,0]),lambda d:d['trace'][6]['collision'].update(position=[2.5,0,0]),lambda d:d['trace'][6].update(displacement=[4,0,0]),lambda d:d['trace'][8].update(collision={}),lambda d:d['initial']['wall'].update(shape_index=False)]
  for mutate in mutations:
   d=fixture();mutate(d)
   with self.assertRaises(ValueError):check(d)
 def test_query_phase(self):
  mutations=[lambda d:d['trace'][0]['parameters'].update(exclude=[]),lambda d:d['trace'][2].update(hits=[{'object_id':10,'collider_id':10,'rid':200,'shape_index':0}]),lambda d:d['trace'][0]['parameters'].update(motion=[4,0,0]),lambda d:d['trace'][4].update(frame=6),lambda d:d['trace'][5]['arguments'].update(test_only=True),lambda d:d.update(readiness_attempts=True)]
  for mutate in mutations:
   d=fixture();mutate(d)
   with self.assertRaises(ValueError):check(d)
 def test_pending_visibility(self):
  d=fixture();pending=copy.deepcopy(d['trace'][0]);pending['hits']=[]
  for e in d['trace']:e['callback']=2;e['frame']=6
  d['trace'].insert(0,pending);d['readiness_attempts']=2;self.assertEqual(check(d)['stationary_queries'],6)
  d['trace'][0]['hits']=[{'object_id':999,'collider_id':999,'rid':999,'shape_index':0}]
  with self.assertRaises(ValueError):check(d)
 def test_json(self):
  for s in ['{"x":1,"x":2}','{"x":NaN}','{"x":1e999}']:
   with self.assertRaises(ValueError):load(s)
 def test_archive(self):
  with tempfile.TemporaryDirectory() as tmp:
   root,out,r=synthetic_archive(Path(tmp));self.assertEqual(verify(root,out)['status'],'PASS');saved=copy.deepcopy(r)
   mutations=[lambda z:z['source_sha256'].update({'main.gd':'0'*64}),lambda z:z['processes'][1]['argv'].append('--bad'),lambda z:z['selected_environment'].update(HOME='/tmp/elsewhere'),lambda z:z['processes'][1].update(timeout=True),lambda z:z['processes'][1].update(cleanup_error='synthetic'),lambda z:z['processes'][1].update(returned_utc='2026-11-01T00:00:00+00:00')]
   for mutate in mutations:
    r=copy.deepcopy(saved);mutate(r);(out/'receipt.json').write_text(json.dumps(r))
    with self.assertRaises(ValueError):verify(root,out)
   r=copy.deepcopy(saved);d=load((out/'behavior.json').read_bytes());d['synthetic_extra']=True;b=json.dumps(d).encode();(out/'behavior.json').write_bytes(b);r['parsed_sha256']=hashlib.sha256(b).hexdigest();(out/'receipt.json').write_text(json.dumps(r))
   with self.assertRaises(ValueError):verify(root,out)
 def test_startup(self):
  for optimize in [True,False]:
   with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp);shutil.copy(ROOT/'run.py',p/'run.py');(p/'summary.json').write_text('{"status":"PASS","synthetic":true}')
    result=subprocess.run([sys.executable]+(['-O'] if optimize else [])+[str(p/'run.py')],capture_output=True,timeout=5)
    self.assertNotEqual(result.returncode,0);self.assertFalse((p/'summary.json').exists());self.assertFalse((p/'evidence').exists());self.assertIn(b'optimized runner rejected' if optimize else b'No module named',result.stderr)
if __name__=='__main__':unittest.main()
