"""Literal read-only geometry, history and archive checker; no engine execution."""
import base64,hashlib,json,math,struct,sys,difflib
from pathlib import Path

def require(ok,msg):
    if not ok:raise ValueError(msg)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(root):
    reports=[]
    for label,folder,current in [('author',root,True),('review',root/'review/fixture',True),('historical-failed-extra-aabb',root/'historical-zero-depth-aabb',False)]:
        out=folder/'results';process=json.loads((out/'process.json').read_text());require(process['returncode']==0 and process['timed_out'] is False,'actual child status')
        lines=[x[len('RESULT_JSON='):] for x in (out/'import.stdout.txt').read_text().splitlines() if x.startswith('RESULT_JSON=')];require(len(lines)==1,'one raw record');d=json.loads(lines[0]);require(d==json.loads((out/'import.json').read_text()),'raw association');require(not (out/'import.stderr.txt').read_bytes(),'stderr')
        require(d['import_return_code']==0 and d['state']=={'meshes':1,'nodes':1,'accessors':3,'buffer_views':2,'buffer_lengths':[160]},'import inventory')
        require(d['gltf_mesh_class']=='GLTFMesh' and d['array_mesh_null'] is False,'mesh classes')
        pos=[[1,2,3],[5,2,3],[1,8,3],[5,8,3]];indices=[0,2,1,2,3,1]
        for key,cls in [('importer','ImporterMesh'),('array_mesh','ArrayMesh')]:
            stage=d[key];require(stage['class']==cls and len(stage['surfaces'])==1,'one stage surface');v=stage['surfaces'][0]
            require(v['positions']==pos and v['indices']==indices and v['primitive']==3 and v['uv_count']==0,'literal arrays')
            require(len(v['normals'])==4,'normal count')
            for normal in v['normals']:require(len(normal)==3 and all(math.isfinite(a) and abs(a-b)<=1e-4 for a,b in zip(normal,[0,0,1])),'frozen normal tolerance')
            for t in (indices[:3],indices[3:]):
                a,b,c=[pos[i] for i in t];require((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])==-24,'clockwise topology')
        require(d['importer']['surfaces'][0]['normals']==[[0,0,1]]*4,'observed exact importer normals')
        raw=base64.b64decode(json.loads((folder/'mesh.gltf').read_text())['buffers'][0]['uri'].split(',',1)[1],validate=True)
        require(digest(folder/'mesh.gltf')=='883939499a958e58d1fff1041345ca2b8819f2febf7a43f8447b2ec09d91d50b' and len(raw)==160 and hashlib.sha256(raw).hexdigest()=='06572d2d89cac7d7dc8c9586ecde6325b82fe0615dfe0e5d4236d7e37a16f268','original input')
        require(list(struct.unpack_from('<6H',raw,128))==[0,1,2,2,1,3],'source indices')
        for i,v in enumerate(pos):require(list(struct.unpack_from('<3f',raw,20+28*i))==v,'source position')
        if current:
            summary=json.loads((out/'summary.json').read_text());require(summary['status']=='PASS' and summary['result']==d,'current acceptance')
            for name,h in summary['source_sha256'].items():require(digest(folder/name)==h,'source '+name)
            require(summary['binary_sha256']=='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3','recorded binary metadata')
        else:
            require(not (out/'summary.json').exists(),'historical full runner must remain failed')
            failure=(folder/'run-output.txt').read_text();require('RuntimeError' in failure and 'AABB' in failure,'preserved failure')
            for line in (folder/'SHA256SUMS').read_text().splitlines():
                h,p=line.split(maxsplit=1);require(digest(folder/Path(p).name)==h,'historical source receipt')
        reports.append({'scope':label,'import_return_code':0,'full_runner_acceptance':'PASS' if current else 'FAILED extra AABB assertion','observed_aabb':d['array_mesh']['aabb'],'new_engine_executions':0})
    old=(root/'historical-zero-depth-aabb/run.py').read_text().splitlines();new=(root/'run.py').read_text().splitlines();diff='\n'.join(difflib.unified_diff(old,new,fromfile='historical/run.py',tofile='current/run.py',lineterm=''))
    print(json.dumps({'scope':'Read-only retained data and failure-history acceptance; no engine rerun or binary authentication','results':reports,'source_diff':diff},indent=2))
if __name__=='__main__':main(Path(sys.argv[1]).resolve())
