import sys,json,hashlib,math
from pathlib import Path
if sys.flags.optimize:raise RuntimeError('assertions required')
p=Path(__file__).resolve().parent/'fixture';o=p/'results';h=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
s=json.loads((o/'summary.json').read_text());i=json.loads((o/'invocation.json').read_text());assert s['status']==i['state']=='PASS' and s['invocation_id']==i['id']
assert all(h(p/n)==v for n,v in s['source_sha256'].items()) and s['binary_sha256']==h(Path('/usr/local/bin/godot'))
faces=[]
for x0,x1,z0,z1 in [(-6,-2,-4,4),(-2,2,-1,1),(2,6,-4,4)]:
 a=[x0,0,z0];b=[x1,0,z0];c=[x1,0,z1];d=[x0,0,z1];faces += [a,b,c,a,c,d]
def cross_y(a,b,c):return (b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2])
def dist(a,b):return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
for case,rad in [('small',.2),('large',1.2)]:
 lines=(o/(case+'.stdout')).read_text().splitlines()
 def rec(prefix):
  rs=[json.loads(x[len(prefix):]) for x in lines if x.startswith(prefix)];assert len(rs)==1;return rs[0]
 r=rec('RESULT_JSON=');src=rec('SOURCE_JSON=');bake=rec('BAKE_JSON=')
 assert src['faces']==faces
 for j in range(0,18,3):assert cross_y(*faces[j:j+3])<0
 verts=src['parsed_vertices'];idx=src['parsed_indices'];assert len(idx)==18
 parsed=[]
 for j in range(0,18,3):
  tri=[verts[k*3:k*3+3] for k in idx[j:j+3]];assert cross_y(*tri)>0;parsed.append(sorted(map(tuple,tri)))
 assert sorted(parsed)==sorted(sorted(map(tuple,faces[j:j+3])) for j in range(0,18,3))
 assert abs(r['actual_bake_radius']-rad)<1e-5 and r['mesh_before']==r['mesh_after']==bake['mesh'] and bake['bake_completed']
 assert r['map_id']==r['region_map_id'] and r['registered_regions']==1 and r['layers']==1 and r['region_enabled']
 assert r['map_iteration']>0 and r['map_iteration']!=r['initial_iteration'] and r['region_iteration']>0
 assert r['map_async'] is False and r['region_async'] is False
 ready=[x for x in r['trace'] if x['kind']=='ready'];assert len(ready)==1 and any(x['kind']=='map_changed' for x in r['trace'])
 assert abs(r['start'][0]+4)<.01 and abs(r['goal'][0]-4)<.01
 for a,ar in zip(r['agents'],[.2,1.2]):
  assert abs(a['radius']-ar)<1e-5 and a['avoidance'] is False and a['map_id']==r['map_id']
  path=a['path'];assert path and all(len(pt)==3 and all(math.isfinite(v) for v in pt) for pt in path)
  assert dist(path[0],r['start'])<.01 and dist(path[-1],a['final'])<.01
  assert dist(path[-1],r['goal'])<.01 if case=='small' else path[-1][0]<0 and dist(path[-1],r['goal'])>1
 assert len(r['agents'])==2 and r['agents'][0]['path']==r['agents'][1]['path']
 assert not r['overlap_small'] and sorted(x['name'] for x in r['overlap_large'])==['WallNegative','WallPositive']
 assert [x['name'] for x in r['positive_control']]==['WallPositive']
 for w in r['walls']:
  assert w['size']==[4,4,3] and w['layer']==2 and w['position']==[0,2,2.5 if w['name']=='WallPositive' else -2.5]
 assert not (o/(case+'.stderr')).read_text() and json.loads((o/(case+'.status.json')).read_text())['returncode']==0
 print(case,'literal geometry/source winding/path/ownership/overlap PASS',r['start'],r['goal'],r['agents'][0]['final'])
