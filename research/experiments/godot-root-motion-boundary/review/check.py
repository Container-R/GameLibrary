import pathlib,json,hashlib,math
root=pathlib.Path(__file__).resolve().parent;out=pathlib.Path(json.loads((root/'run.stdout').read_text())['output'])
def req(v,m):
 if not v:raise RuntimeError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def near(a,b):req(len(a)==len(b) and all(type(x) in (int,float) and math.isfinite(x) and abs(x-y)<=1e-5 for x,y in zip(a,b)),'numeric mismatch')
def yaw(q,degrees):
 req(len(q)==4 and all(type(v) in (int,float) and math.isfinite(v) for v in q),'quaternion');near([sum(v*v for v in q)],[1]);x,y,z,w=q
 # Rotation matrix is invariant to the sign of the entire quaternion.
 matrix=[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]
 c=math.cos(math.radians(degrees));s=math.sin(math.radians(degrees));near(matrix,[c,0,s,0,1,0,-s,0,c])
s=json.loads((out/'summary.json').read_text());req(s['status']=='PASS' and s['invocation_id']==out.name,'terminal');req([x['name'] for x in s['commands']]==['version','pose','extract'],'commands')
for c in s['commands']:req(c['exit_code']==0 and c['timed_out'] is False,'command result')
for p,h in s['source_sha256'].items():req(sha(root/'fixture'/p)==h,'source')
for p,h in s['outputs_sha256'].items():req(sha(out/p)==h,'output')
req(sha(pathlib.Path(s['engine_path']))==s['engine_sha256']=='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3','binary')
for mode in ['pose','extract']:
 lines=[l[12:] for l in (out/(mode+'.stdout')).read_text().splitlines() if l.startswith('RESULT_JSON=')];req(len(lines)==1,'single result');d=json.loads(lines[0]);req(d==json.loads((out/(mode+'.json')).read_text()),'raw association');req(not (out/(mode+'.stderr')).read_bytes(),'stderr')
 req(d['mode']==mode and d['manual']==2 and d['root_motion_local'] is False,'mode');req(d['root_motion_track']==('' if mode=='pose' else 'Skeleton:root'),'track')
 req(d['calls']==['advance(0)','advance(0.5)']+(['advance(0.25)'] if mode=='extract' else []),'advances')
 snaps=d['snapshots'];req([x['label'] for x in snaps]==['initial','first_read','second_read_no_advance']+(['next_evaluation'] if mode=='extract' else []),'snapshots')
 for x in snaps:near(x['actor']['position'],[0,0,0]);yaw(x['actor']['rotation'],0)
 for k in ['delta_position','delta_rotation','bone_position','bone_rotation']:req(snaps[1][k]==snaps[2][k],'repeat equality')
 if mode=='pose':
  near(snaps[0]['bone_position'],[0,0,0]);yaw(snaps[0]['bone_rotation'],0)
  for x in snaps[1:]:near(x['bone_position'],[1,0,0]);yaw(x['bone_rotation'],22.5)
  req(d['receivers']==[],'pose receivers')
 else:
  for x in snaps:near(x['bone_position'],[0,0,0]);yaw(x['bone_rotation'],0)
  for x in snaps[1:3]:near(x['delta_position'],[1,0,0]);yaw(x['delta_rotation'],22.5)
  near(snaps[3]['delta_position'],[.5,0,0]);yaw(snaps[3]['delta_rotation'],11.25)
  req(len(d['receivers'])==3,'receivers')
  for i,x in enumerate(d['receivers']):req(x['application_count']==i,'count');near(x['pose']['position'],[i,0,0]);yaw(x['pose']['rotation'],22.5*i)
print(json.dumps({'status':'PASS','invocation_id':out.name,'behavior_processes':2,'version_commands':1,'source_sha256':s['source_sha256'],'oracle':'literal positions and sign-invariant quaternion-to-matrix expected Y rotations'},indent=2))
