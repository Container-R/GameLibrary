"""One original glTF runtime import; literal independent acceptance, no renderer claim."""
import base64
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import struct
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
(OUT / 'summary.json').unlink(missing_ok=True)
if not __debug__:
    raise SystemExit('optimized invocation unsupported')

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def text_output(value):
    return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else value or ''

sources = ['run.py', 'main.gd', 'project.godot', 'contract.json', 'mesh.gltf']
manifest = {name: sha(ROOT / name) for name in sources}
binary = Path(os.environ.get('GODOT_BINARY', '/usr/local/bin/godot'))
binary_hash = sha(binary)
require(manifest['mesh.gltf'] == '883939499a958e58d1fff1041345ca2b8819f2febf7a43f8447b2ec09d91d50b', 'input JSON bytes changed')
asset = json.loads((ROOT / 'mesh.gltf').read_text())
raw = base64.b64decode(asset['buffers'][0]['uri'].split(',', 1)[1], validate=True)
require(len(raw) == 160 and hashlib.sha256(raw).hexdigest() == '06572d2d89cac7d7dc8c9586ecde6325b82fe0615dfe0e5d4236d7e37a16f268', 'input buffer identity')
source_indices = list(struct.unpack_from('<6H', raw, 128))
require(source_indices == [0,1,2,2,1,3], 'original source indices')
require(set(asset['meshes'][0]['primitives'][0]['attributes']) == {'POSITION','NORMAL'}, 'source attributes')
command = [str(binary), '--headless', '--path', str(ROOT), '--script', str(ROOT / 'main.gd')]
with tempfile.TemporaryDirectory(prefix='gltf-import-home-') as home:
    env = dict(os.environ, HOME=home, XDG_CACHE_HOME=home+'/cache', XDG_CONFIG_HOME=home+'/config', XDG_DATA_HOME=home+'/data')
    receipt = {'command': command, 'timeout_seconds': 30, 'isolated_home_xdg': True}
    try:
        proc = subprocess.run(command, env=env, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired as error:
        (OUT/'import.stdout.txt').write_text(text_output(error.stdout))
        (OUT/'import.stderr.txt').write_text(text_output(error.stderr))
        receipt['timed_out'] = True
        (OUT/'process.json').write_text(json.dumps(receipt, indent=2)+'\n')
        raise
    receipt.update(returncode=proc.returncode, timed_out=False)
    (OUT/'process.json').write_text(json.dumps(receipt, indent=2)+'\n')
    (OUT/'import.stdout.txt').write_text(proc.stdout)
    (OUT/'import.stderr.txt').write_text(proc.stderr)
require(proc.returncode == 0, 'engine process failed; retained raw output')
require(proc.stderr == '', 'unexpected engine stderr; retained')
lines = [line[len('RESULT_JSON='):] for line in proc.stdout.splitlines() if line.startswith('RESULT_JSON=')]
require(len(lines) == 1, 'expected exactly one result payload')
data = json.loads(lines[0])
(OUT/'import.json').write_text(json.dumps(data, indent=2)+'\n')
require(data['import_return_code'] == 0, 'import return code')
require(data['state'] == {'meshes':1,'nodes':1,'accessors':3,'buffer_views':2,'buffer_lengths':[160]}, 'state inventory')
require(data['gltf_mesh_class'] == 'GLTFMesh' and data['array_mesh_null'] is False, 'resource classes')
positions = [[1,2,3],[5,2,3],[1,8,3],[5,8,3]]
indices = [0,2,1,2,3,1]
for key, cls in [('importer','ImporterMesh'), ('array_mesh','ArrayMesh')]:
    stage = data[key]
    require(stage['class'] == cls and len(stage['surfaces']) == 1, key+' surface/class')
    surface = stage['surfaces'][0]
    require(surface['primitive'] == 3 and surface['indices'] == indices, key+' primitive/winding')
    require(surface['positions'] == positions, key+' exact positions')
    require(len(surface['normals']) == 4, key+' normal count')
    for normal in surface['normals']:
        require(len(normal) == 3 and all(math.isfinite(v) and abs(v-e) <= 0.0001 for v,e in zip(normal,[0,0,1])), key+' normals')
    require(surface['uv_count'] == 0, key+' absent UV')
    require([surface[x] for x in ['position_type','normal_type','index_type']] == ['PackedVector3Array','PackedVector3Array','PackedInt32Array'], key+' array types')
    for offset in [0,3]:
        a,b,c = [surface['positions'][i] for i in indices[offset:offset+3]]
        cross_z = (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
        require(cross_z == -24, key+' literal triangle orientation')
# AABB is a recorded diagnostic, not the extra zero-depth assumption from v1.
# Frozen position/index/normal acceptance remains unchanged.
require({name:sha(ROOT/name) for name in sources} == manifest, 'source mutated during run')
summary = {'status':'PASS','actual_import_processes':1,'source_sha256':manifest,'binary_sha256':binary_hash,'binary_path':str(binary),'version':data['engine_version'],'python':sys.version,'platform':platform.platform(),'source_indices':source_indices,'expected_engine_indices':indices,'normal_component_tolerance':0.0001,'provenance':'Runtime self-report is not independently authenticated source/build identity.','result':data}
(OUT/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
print('PASS: one actual import, ImporterMesh and ArrayMesh readback; no rendering claim')
