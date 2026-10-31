"""Literal geometry-contract oracle; no author reader imports."""
import base64,hashlib,json,struct,sys
from pathlib import Path
if sys.flags.optimize:raise SystemExit('Refusing optimized oracle')
r=Path(sys.argv[1]);d=json.loads((r/'mesh.gltf').read_text());s=json.loads((r/'summary.json').read_text())
b=base64.b64decode((r/'mesh.bin.base64').read_text().strip(),validate=True)
assert b==base64.b64decode(d['buffers'][0]['uri'].split(',',1)[1],validate=True)
assert len(b)==160 and b[:16]==bytes(16) and b[140:]==bytes(20)
expected=[[1,2,3],[5,2,3],[1,8,3],[5,8,3]]
p=[list(struct.unpack_from('<3f',b,o)) for o in (20,48,76,104)]
n=[list(struct.unpack_from('<3f',b,o)) for o in (32,60,88,116)]
i=list(struct.unpack_from('<6H',b,128));assert p==expected and n==[[0,0,1]]*4 and i==[0,1,2,2,1,3]
assert all(struct.unpack_from('<f',b,o)==(99.,) for o in (16,44,72,100))
triangles=[[expected[j] for j in t] for t in [(0,1,2),(2,1,3)]]
assert s['recovered']==dict(positions=p,normals=n,indices=i,triangles=triangles)
naive=[list(struct.unpack_from('<3f',b,o)) for o in (20,32,44,56)]
assert naive==[[1,2,3],[0,0,1],[99,5,2],[3,0,0]] and naive!=p and s['naive_tight_positions']==naive
assert s['binary_bytes']==160 and s['binary_sha256']==hashlib.sha256(b).hexdigest()
assert s['gltf_sha256']==hashlib.sha256((r/'mesh.gltf').read_bytes()).hexdigest()
assert d['bufferViews']==[dict(buffer=0,byteOffset=16,byteLength=112,byteStride=28,target=34962),dict(buffer=0,byteOffset=128,byteLength=12,target=34963)]
# Literal geometric cross products: +Z24 for both, unlike normal unit magnitude1.
for a,c,e in triangles:
 u=[c[k]-a[k] for k in range(3)];v=[e[k]-a[k] for k in range(3)]
 assert [u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]==[0,0,24]
assert len(s['negatives'])==9
print(json.dumps(dict(status='PASS',positions=p,indices=i,naive=naive,triangle_cross_products=[[0,0,24]]*2,binary_sha256=hashlib.sha256(b).hexdigest()),indent=2))
