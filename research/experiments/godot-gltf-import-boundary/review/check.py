import pathlib,json,hashlib,base64,struct,math
r=pathlib.Path(__file__).resolve().parent/'fixture'; out=r/'results'
def req(v,m):
 if not v: raise RuntimeError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((out/'summary.json').read_text()); p=json.loads((out/'process.json').read_text())
req(s['status']=='PASS' and s['actual_import_processes']==1 and p['returncode']==0 and not p['timed_out'],'terminal')
lines=[x.removeprefix('RESULT_JSON=') for x in (out/'import.stdout.txt').read_text().splitlines() if x.startswith('RESULT_JSON=')];req(len(lines)==1,'one result');d=json.loads(lines[0]);req(d==s['result']==json.loads((out/'import.json').read_text()),'association')
req(not (out/'import.stderr.txt').read_bytes(),'stderr')
req(d['import_return_code']==0 and d['state']=={'meshes':1,'nodes':1,'accessors':3,'buffer_views':2,'buffer_lengths':[160]},'inventory')
req(d['gltf_mesh_class']=='GLTFMesh' and d['array_mesh_null'] is False,'mesh')
positions=[[1,2,3],[5,2,3],[1,8,3],[5,8,3]]; indices=[0,2,1,2,3,1]
for key,cls in [('importer','ImporterMesh'),('array_mesh','ArrayMesh')]:
 x=d[key];req(x['class']==cls and len(x['surfaces'])==1,'surface');v=x['surfaces'][0]
 req(v['positions']==positions and v['indices']==indices and v['primitive']==3 and v['uv_count']==0,'literal geometry')
 req(len(v['normals'])==4,'normals')
 for n in v['normals']:req(len(n)==3 and all(math.isfinite(a) and abs(a-b)<=1e-4 for a,b in zip(n,[0,0,1])),'normal tolerance')
 req([v[k] for k in ['position_type','normal_type','index_type']]==['PackedVector3Array','PackedVector3Array','PackedInt32Array'],'types')
 for t in [indices[:3],indices[3:]]:
  a,b,c=[positions[i] for i in t];req((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])==-24,'winding')
raw=base64.b64decode(json.loads((r/'mesh.gltf').read_text())['buffers'][0]['uri'].split(',',1)[1],validate=True)
req(len(raw)==160 and hashlib.sha256(raw).hexdigest()=='06572d2d89cac7d7dc8c9586ecde6325b82fe0615dfe0e5d4236d7e37a16f268','input bytes')
req(list(struct.unpack_from('<6H',raw,128))==[0,1,2,2,1,3],'source winding')
for i,pos in enumerate(positions):req(list(struct.unpack_from('<3f',raw,20+28*i))==pos,'original position')
for name,h in s['source_sha256'].items():req(sha(r/name)==h,'source '+name)
req(sha(pathlib.Path(s['binary_path']))==s['binary_sha256']=='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3','binary')
print(json.dumps({'status':'PASS','actual_import_processes':1,'source_sha256':s['source_sha256'],'binary_sha256':s['binary_sha256'],'observed_aabb':d['array_mesh']['aabb']},indent=2))
