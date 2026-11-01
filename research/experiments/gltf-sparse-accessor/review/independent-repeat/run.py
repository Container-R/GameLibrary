"""Seven frozen cases: standard-library CPU only; no external native probe or arbitrary URI fetch."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
(OUT / 'summary.json').unlink(missing_ok=True)
if sys.flags.optimize:
    raise SystemExit('optimized_execution_unsupported')
import base64
import copy
import hashlib
import json
import platform
import traceback
from reader import decode, Rejected

HEX = ('000020410000a0410000f04100002042'
       'abcd01000300ef12'
       'aabbccdd0000e040000010411122334455667788')

def need(ok, message):
    if not ok:
        raise RuntimeError(message)

def main():
    blob = bytes.fromhex(HEX)
    need(len(blob) == 44, 'literal_byte_count')
    uri = 'data:application/octet-stream;base64,' + base64.b64encode(blob).decode('ascii')
    doc = {'asset':{'version':'2.0'},'buffers':[{'byteLength':44,'uri':uri}],
           'bufferViews':[{'buffer':0,'byteOffset':0,'byteLength':16},
                          {'buffer':0,'byteOffset':16,'byteLength':8},
                          {'buffer':0,'byteOffset':24,'byteLength':20}],
           'accessors':[{'componentType':5126,'count':4,'type':'SCALAR','bufferView':0,'byteOffset':0,
                         'sparse':{'count':2,'indices':{'bufferView':1,'byteOffset':2,'componentType':5123},
                                   'values':{'bufferView':2,'byteOffset':4}}}]}
    records = []
    for name, expected, addresses in [('dense',[10,7,30,9],[0,4,8,12]),('zero',[0,7,0,9],[None]*4)]:
        d = copy.deepcopy(doc)
        if name == 'zero':
            del d['accessors'][0]['bufferView']; del d['accessors'][0]['byteOffset']
        path = OUT / (name+'.gltf.json')
        path.write_text(json.dumps(d,indent=2)+'\n')
        loaded = json.loads(path.read_text())
        embedded = loaded['buffers'][0]['uri']
        prefix = 'data:application/octet-stream;base64,'
        need(embedded.startswith(prefix), 'local_data_uri')
        raw = base64.b64decode(embedded[len(prefix):],validate=True)
        need(raw == blob, 'embedded_identity')
        result = decode(loaded,raw)
        need(result == {'values':expected,'base_addresses':addresses,'index_addresses':[18,20],
                        'value_addresses':[28,32],'indices':[1,3],'replacement_values':[7,9]}, 'literal_oracle_'+name)
        row = {'case':name,'result':result}; records.append(row)
        print('CASE_JSON '+json.dumps(row),flush=True)
    cases = [('duplicate','sparse_indices_not_strictly_increasing'),
             ('descending','sparse_indices_not_strictly_increasing'),
             ('range','sparse_index_out_of_range'),('short_view','sparse_values_view_bounds'),
             ('stride','sparse_view_layout_forbidden')]
    for name, expected in cases:
        d = copy.deepcopy(doc); raw = bytearray(blob)
        if name == 'duplicate': raw[20:22] = b'\x01\x00'
        elif name == 'descending': raw[18:22] = b'\x03\x00\x01\x00'
        elif name == 'range': raw[20:22] = b'\x04\x00'
        elif name == 'short_view': d['bufferViews'][2]['byteLength'] = 11
        elif name == 'stride': d['bufferViews'][1]['byteStride'] = 4
        d['buffers'][0]['uri'] = 'data:application/octet-stream;base64,' + base64.b64encode(raw).decode('ascii')
        try:
            decode(d,bytes(raw))
        except Rejected as e:
            need(str(e) == expected, 'wrong_rejection_'+name+':'+str(e))
        else:
            raise RuntimeError('accepted_negative_'+name)
        row = {'case':name,'rejected':expected}; records.append(row)
        print('CASE_JSON '+json.dumps(row),flush=True)
    sources = {f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ['reader.py','run.py','protocol.md']}
    artifacts = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [OUT/'dense.gltf.json',OUT/'zero.gltf.json']}
    summary = {'status':'PASS','python':sys.version,'platform':platform.platform(),'hex':HEX,
               'byte_count':len(blob),'blob_sha256':hashlib.sha256(blob).hexdigest(),'cases':records,
               'sources':sources,'artifacts':artifacts,'native_calls':0}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print('RESULT_JSON '+json.dumps(summary),flush=True)

if __name__ == '__main__':
    try:
        main()
    except BaseException:
        (OUT/'summary.json').unlink(missing_ok=True)
        traceback.print_exc()
        raise SystemExit(1)
