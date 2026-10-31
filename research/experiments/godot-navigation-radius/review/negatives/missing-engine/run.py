import hashlib,json,math,os,platform,subprocess,sys,tempfile,uuid
from pathlib import Path
R=Path(__file__).resolve().parent;O=R/'results';O.mkdir(exist_ok=True)
(O/'summary.json').unlink(missing_ok=True)
inv=str(uuid.uuid4());(O/'invocation.json').write_text(json.dumps({'id':inv,'state':'RUNNING'})+'\n')
def need(c,m):
 if not c:raise RuntimeError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def raw(x):return x.decode(errors='replace') if isinstance(x,bytes) else (x or '')
def near(a,b,t=1e-5):return abs(a-b)<t
def distance(a,b):return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
try:
 need(not sys.flags.optimize,'no -O')
 binary=Path('/nonexistent/godot');contract=json.loads((R/'contract.json').read_text())
 summary={'invocation_id':inv,'python':sys.version,'platform':platform.platform(),'binary_sha256':sha(binary),'source_sha256':{n:sha(R/n) for n in ['run.py','main.gd','main.tscn','project.godot','contract.json']},'runs':[]}
 for case,rad in [('small',0.2),('large',1.2)]:
  with tempfile.TemporaryDirectory(prefix='navigation-radius-') as temp:
   env=os.environ.copy()
   for key in ['HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME']:
    path=Path(temp)/key;path.mkdir();env[key]=str(path)
   env['GODOT_SILENCE_ROOT_WARNING']='1'
   cmd=[str(binary),'--headless','--single-threaded-scene','--path',str(R),'--',case]
   status={'command':cmd,'timeout_seconds':30}
   try:p=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=30)
   except subprocess.TimeoutExpired as e:
    (O/(case+'.stdout')).write_text(raw(e.stdout));(O/(case+'.stderr')).write_text(raw(e.stderr));status['timeout']=True;(O/(case+'.status.json')).write_text(json.dumps(status,indent=2)+'\n');raise
   except OSError as e:
    status['spawn_error']=repr(e);(O/(case+'.status.json')).write_text(json.dumps(status,indent=2)+'\n');raise
  (O/(case+'.stdout')).write_text(p.stdout);(O/(case+'.stderr')).write_text(p.stderr);status['returncode']=p.returncode;(O/(case+'.status.json')).write_text(json.dumps(status,indent=2)+'\n')
  need(p.returncode==0 and not p.stderr and 'ERROR' not in p.stdout,'engine failure '+case)
  def record(prefix):
   rs=[json.loads(x[len(prefix):]) for x in p.stdout.splitlines() if x.startswith(prefix)];need(len(rs)==1,'record count '+prefix);return rs[0]
  r=record('RESULT_JSON=');src=record('SOURCE_JSON=');bake=record('BAKE_JSON=')
  (O/(case+'.json')).write_text(json.dumps(r,indent=2)+'\n')
  need(near(r['radius'],rad) and near(r['actual_bake_radius'],rad),'bake radius')
  for k,v in contract['bake_settings'].items():need(near(r['settings'][k],v),'setting '+k)
  need(r['mesh_before']==r['mesh_after']==bake['mesh'] and bake['bake_completed'],'mesh not replaced')
  need(len(r['mesh_before']['polygons'])>0,'polygons')
  need(r['map_iteration']!=0 and r['map_iteration']!=r['initial_iteration'] and r['region_iteration']!=0,'iterations')
  need(r['map_id']==r['region_map_id'] and r['registered_regions']==1 and r['region_enabled'] and r['layers']==1,'ownership')
  need(not r['map_async'] and not r['region_async'] and near(r['map_cell_size'],0.1) and near(r['map_cell_height'],0.1),'map config')
  need(any(x['kind']=='map_changed' for x in r['trace']) and any(x['kind']=='ready' for x in r['trace']),'readiness')
  need(abs(r['start'][0]+4)<0.01 and abs(r['goal'][0]-4)<0.01 and abs(r['start'][2])<0.01 and abs(r['goal'][2])<0.01,'surviving room projection')
  need(len(r['agents'])==2,'agents')
  for a,ar in zip(r['agents'],[0.2,1.2]):
   need(near(a['radius'],ar) and not a['avoidance'] and a['map_id']==r['map_id'],'agent configuration')
   path=a['path'];need(path and all(len(pt)==3 and all(math.isfinite(v) for v in pt) for pt in path),'path finite')
   need(distance(path[0],r['start'])<0.01 and distance(path[-1],a['final'])<0.01,'actual endpoints')
   if case=='small':need(distance(path[-1],r['goal'])<0.01,'small goal')
   else:need(path[-1][0]<0 and distance(path[-1],r['goal'])>1,'large partial')
  need(r['agents'][0]['path']==r['agents'][1]['path'],'radius-only paths equal in this fixture')
  need(r['overlap_small']==[],'small physical occupancy')
  need(sorted(x['name'] for x in r['overlap_large'])==['WallNegative','WallPositive'],'large physical occupancy')
  need([x['name'] for x in r['positive_control']]==['WallPositive'],'positive physics control')
  for w in r['walls']:
   expected=next(x for x in contract['walls'] if x['name']==w['name']);need(w['position']==expected['center'] and w['size']==expected['size'] and w['layer']==2,'wall geometry')
  verts=src['parsed_vertices'];idx=src['parsed_indices'];need(len(idx)==18,'six source triangles')
  for i in range(0,len(idx),3):
   a,b,c=[verts[j*3:j*3+3] for j in idx[i:i+3]];u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)]
   need(u[2]*v[0]-u[0]*v[2]>0,'parsed upward source')
  summary['runs'].append({'case':case,'result':r})
 summary['status']='PASS';(O/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');(O/'invocation.json').write_text(json.dumps({'id':inv,'state':'PASS'})+'\n')
 print('PASS: two actual bake processes, four agent paths, stationary overlap controls')
except BaseException as e:
 (O/'summary.json').unlink(missing_ok=True);(O/'invocation.json').write_text(json.dumps({'id':inv,'state':'FAILED','exception':repr(e)})+'\n');raise
