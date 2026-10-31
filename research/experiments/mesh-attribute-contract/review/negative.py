"""Finite supplemental semantic/freshness probes, isolated copies only."""
import base64,copy,importlib.util,json,shutil,struct,subprocess,sys
from pathlib import Path
if sys.flags.optimize:raise SystemExit('Refusing optimized probe')
ROOT=Path(__file__).resolve().parent;F=ROOT/'fixture';OUT=ROOT/'negatives';OUT.mkdir(exist_ok=True)
(OUT/'observations.json').unlink(missing_ok=True)
rows=[]
for name in ('optimized','reader-import-failure'):
 d=OUT/name
 if d.exists():raise RuntimeError('refuse old probe directory')
 shutil.copytree(F,d)
 if name=='reader-import-failure':(d/'reader.py').write_text("raise ImportError('synthetic reader import failure')\n")
 cmd=[sys.executable]+(['-O'] if name=='optimized' else [])+[str(d/'run.py')]
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=10);(d/'stdout.txt').write_text(p.stdout);(d/'stderr.txt').write_text(p.stderr)
 assert p.returncode==1 and not (d/'results/summary.json').exists()
 rows.append(dict(name=name,command=cmd,exit=p.returncode,summary_exists=False))
spec=importlib.util.spec_from_file_location('reviewed_reader',F/'reader.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
doc=json.loads((F/'results/mesh.gltf').read_text());blob=base64.b64decode((F/'results/mesh.bin.base64').read_text())
def reject(name,change,exc,reason):
 d=copy.deepcopy(doc);b=bytearray(blob);change(d,b)
 try:m.read(d,bytes(b))
 except exc as e:assert str(e)==reason;rows.append(dict(name=name,exception=type(e).__name__,reason=str(e)))
 else:raise RuntimeError('accepted '+name)
reject('missing-view',lambda d,b:d['accessors'][0].pop('bufferView'),KeyError,"'bufferView'")
reject('invalid-view-index',lambda d,b:d['accessors'][0].update(bufferView=8),ValueError,'view index')
reject('backing-valid-view-short',lambda d,b:d['bufferViews'][0].update(byteLength=108),ValueError,'accessor outside declared view')
reject('incorrect-position-bounds',lambda d,b:d['accessors'][0].update(max=[6,8,3]),ValueError,'position bounds')
reject('nonunit-normal',lambda d,b:struct.pack_into('<f',b,40,2),ValueError,'normal unit length')
reject('unequal-count',lambda d,b:d['accessors'][1].update(count=3),ValueError,'attribute count mismatch')
# Valid structure alone does not identify intended attribute semantics: literal geometry oracle still needed.
d=copy.deepcopy(doc);d['accessors'][0].update(byteOffset=16,min=[0,0,1],max=[0,0,1]);result=m.read(d,blob)
assert result['positions']==[(0.,0.,1.)]*4 and result['positions']!=[(1.,2.,3.),(5.,2.,3.),(1.,8.,3.),(5.,8.,3.)]
rows.append(dict(name='inbounds-other-attribute-with-consistent-bounds',reader_accepts=True,intended_geometry_matches=False,positions=result['positions']))
(OUT/'observations.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
