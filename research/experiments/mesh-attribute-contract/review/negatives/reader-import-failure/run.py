import base64,copy,hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
(OUT/'summary.json').unlink(missing_ok=True)
if not __debug__:raise SystemExit('optimized invocation rejected')
import reader

def need(ok,why):
    if not ok:raise RuntimeError(why)
# Original literal geometry frozen in geometry-contract.md before implementation.
POSITIONS=[(1.,2.,3.),(5.,2.,3.),(1.,8.,3.),(5.,8.,3.)]
NORMALS=[(0.,0.,1.)]*4
INDICES=[0,1,2,2,1,3]
blob=b'\x00'*16+b''.join(struct.pack('<7f',99.,*p,*n) for p,n in zip(POSITIONS,NORMALS))+struct.pack('<6H',*INDICES)+b'\x00'*20
uri='data:application/octet-stream;base64,'+base64.b64encode(blob).decode()
doc={'asset':{'version':'2.0'},'buffers':[{'byteLength':160,'uri':uri}],
 'bufferViews':[{'buffer':0,'byteOffset':16,'byteLength':112,'byteStride':28,'target':34962},
                {'buffer':0,'byteOffset':128,'byteLength':12,'target':34963}],
 'accessors':[{'bufferView':0,'byteOffset':4,'componentType':5126,'count':4,'type':'VEC3','min':[1,2,3],'max':[5,8,3]},
              {'bufferView':0,'byteOffset':16,'componentType':5126,'count':4,'type':'VEC3'},
              {'bufferView':1,'componentType':5123,'count':6,'type':'SCALAR'}],
 'meshes':[{'primitives':[{'attributes':{'POSITION':0,'NORMAL':1},'indices':2,'mode':4}]}],
 'nodes':[{'mesh':0}],'scenes':[{'nodes':[0]}],'scene':0}
(OUT/'mesh.gltf').write_text(json.dumps(doc,indent=2)+'\n')
(OUT/'mesh.bin.base64').write_text(base64.b64encode(blob).decode()+'\n')
# Real JSON roundtrip and base64 materialization before extraction; no URI fetching.
doc=json.loads((OUT/'mesh.gltf').read_text());actual=base64.b64decode(doc['buffers'][0]['uri'].split(',',1)[1],validate=True)
need(actual==blob,'binary roundtrip')
result=reader.read(doc,actual)
need(result['positions']==POSITIONS and result['normals']==NORMALS and result['indices']==INDICES,'semantic values')
expected_triangles=[[(1.,2.,3.),(5.,2.,3.),(1.,8.,3.)],[(1.,8.,3.),(5.,2.,3.),(5.,8.,3.)]]
need(result['triangles']==expected_triangles,'literal topology')
naive=[struct.unpack_from('<3f',actual,20+i*12) for i in range(4)]
need(20+3*12+12<=128 and naive!=POSITIONS,'in-view naive counterexample')
negatives=[]
def reject(name,change,expected,bytes_change=None):
    d=copy.deepcopy(doc);change(d);b=bytearray(actual)
    if bytes_change:bytes_change(b)
    try:reader.read(d,bytes(b))
    except ValueError as e:
        need(str(e)==expected,f'{name} wrong reason {e}')
        negatives.append(dict(name=name,error=str(e),backing_bytes=len(b)))
    else:raise RuntimeError(f'{name} accepted')
reject('view-overrun-large-buffer',lambda d:d['bufferViews'][0].update(byteLength=108),'accessor outside declared view')
reject('stride-not-four',lambda d:d['bufferViews'][0].update(byteStride=26),'stride domain')
reject('stride-smaller-than-element',lambda d:d['bufferViews'][0].update(byteStride=8),'stride domain')
reject('accessor-misaligned',lambda d:d['accessors'][0].update(byteOffset=2),'component alignment')
reject('view-misaligned',lambda d:d['bufferViews'][0].update(byteOffset=18),'component alignment')
reject('indices-stride',lambda d:d['bufferViews'][1].update(byteStride=4),'indices must not have stride')
reject('index-out-of-range',lambda d:None,'index outside vertices',lambda b:struct.pack_into('<H',b,128,4))
reject('index-maximal',lambda d:None,'forbidden maximal index',lambda b:struct.pack_into('<H',b,128,65535))
reject('nonfinite-position',lambda d:None,'nonfinite attribute',lambda b:struct.pack_into('<f',b,20,float('nan')))
summary=dict(status='PASS',scope='original restricted glTF CPU attribute extraction, no official validator or GPU',
 python=sys.version,source_sha256={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ('reader.py','run.py','geometry-contract.md')},
 binary_bytes=len(actual),binary_sha256=hashlib.sha256(actual).hexdigest(),
 gltf_sha256=hashlib.sha256((OUT/'mesh.gltf').read_bytes()).hexdigest(),
 recovered=result,naive_tight_positions=naive,naive_reads_within_declared_view=True,negatives=negatives)
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print('RESULT_JSON '+json.dumps(summary,sort_keys=True))
