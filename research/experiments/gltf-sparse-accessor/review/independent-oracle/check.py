"""Read-only seven-case archive check; never imports/runs the author decoder."""
import argparse
import base64
import hashlib
import json
import math
from pathlib import Path


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    data = path.read_bytes()
    require(len(data) <= 1048576, 'archive file too large: '+str(path))
    return data


def digest(path):
    return hashlib.sha256(read(path)).hexdigest()


def pairs(items):
    obj = {}
    for key, value in items:
        require(key not in obj, 'duplicate JSON key')
        obj[key] = value
    return obj


def bad_constant(value):
    raise ValueError('nonfinite JSON constant: '+value)


def load_text(text):
    value = json.loads(text, object_pairs_hook=pairs, parse_constant=bad_constant)
    def finite(v):
        if type(v) is float:
            require(math.isfinite(v), 'nonfinite JSON number')
        elif type(v) is dict:
            for x in v.values(): finite(x)
        elif type(v) is list:
            for x in v: finite(x)
    finite(value)
    return value


def load(path):
    return load_text(read(path).decode('utf-8'))


def equal(a, b):
    # Structural metadata uses exact JSON types, so True cannot stand in for 1.
    if type(a) is not type(b): return False
    if type(a) is dict: return a.keys() == b.keys() and all(equal(a[k], b[k]) for k in a)
    if type(a) is list: return len(a) == len(b) and all(equal(x, y) for x, y in zip(a, b))
    return a == b


def numeric_list(a, b):
    return (type(a) is list and len(a) == len(b)
            and all(type(x) in (int, float) and math.isfinite(x) and x == y for x, y in zip(a, b)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('--stdout', type=Path, required=True)
    parser.add_argument('--stderr', type=Path, required=True)
    parser.add_argument('--exit-code', type=Path, required=True)
    parser.add_argument('--source-pins', type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    expected_path = here/'expected.json'
    require(digest(expected_path) == 'b936312a481fe04c51d8f61ae965f7a43ba8589246d39138e831245859787623', 'independent oracle changed')
    expected = load(expected_path)
    pins = load(args.source_pins)
    require(set(pins) == {'reader.py', 'run.py', 'protocol.md'}, 'source pin keys')
    require(pins['protocol.md'] == 'de8c9bd74299fb409d58859a099de8b5ff2802df6b78ba1308400762b294172d', 'protocol pin')
    for name, sha in pins.items():
        require(type(sha) is str and len(sha) == 64 and all(c in '0123456789abcdef' for c in sha), 'source digest syntax')
        require(digest(args.root/name) == sha, 'source identity '+name)
    require(read(args.stderr) == b'', 'nonempty process stderr')
    require(read(args.exit_code).strip() == b'0', 'nonzero/malformed recorded process status')
    summary = load(args.root/'results'/'summary.json')
    require(set(summary) == {'status','python','platform','hex','byte_count','blob_sha256','cases','sources','artifacts','native_calls'}, 'summary shape')
    require(summary['status'] == 'PASS', 'summary status')
    require(equal(summary['sources'], pins), 'source manifest association')
    require(type(summary['byte_count']) is int and summary['byte_count'] == 44, 'byte count')
    require(type(summary['native_calls']) is int and summary['native_calls'] == 0, 'scope count')
    require(all(type(summary[k]) is str and summary[k] for k in ('python','platform')), 'runtime selfreport fields')
    require(summary['hex'] == expected['backing_hex'], 'literal hex')
    blob = bytes.fromhex(expected['backing_hex'])
    require(len(blob) == 44 and summary['blob_sha256'] == hashlib.sha256(blob).hexdigest(), 'blob binding')
    require(type(summary['cases']) is list and len(summary['cases']) == 7, 'seven cases')
    for row, name, values, addresses in zip(summary['cases'][:2], ('dense','zero'),
            (expected['dense_expected'], expected['zero_base_expected']), ([0,4,8,12],[None]*4)):
        require(set(row) == {'case','result'} and row['case'] == name, 'positive row')
        result = row['result']
        require(set(result) == {'values','base_addresses','index_addresses','value_addresses','indices','replacement_values'}, 'result shape')
        require(numeric_list(result['values'], values), 'literal full values')
        require(numeric_list(result['replacement_values'], [7,9]), 'replacement values')
        for key, literal in [('base_addresses',addresses),('index_addresses',[18,20]),('value_addresses',[28,32]),('indices',[1,3])]:
            require(equal(result[key], literal), 'literal '+key)
    names = ['duplicate','descending','range','short_view','stride']
    for row, name, mutation in zip(summary['cases'][2:], names, expected['mutations']):
        require(equal(row, {'case':name,'rejected':mutation['expected_error']}), 'negative label '+name)
    lines = read(args.stdout).decode('utf-8').splitlines()
    require(len(lines) == 8, 'exact seven case lines plus result')
    for line, row in zip(lines[:7], summary['cases']):
        require(line.startswith('CASE_JSON '), 'case raw prefix')
        require(equal(load_text(line[len('CASE_JSON '):]),row), 'case raw association')
    require(lines[-1].startswith('RESULT_JSON '), 'terminal raw prefix')
    require(equal(load_text(lines[-1][len('RESULT_JSON '):]), summary), 'terminal raw association')
    require(set(summary['artifacts']) == {'dense.gltf.json','zero.gltf.json'}, 'artifact set')
    for name in ('dense','zero'):
        filename = name+'.gltf.json'
        path = args.root/'results'/filename
        require(summary['artifacts'][filename] == digest(path), 'artifact digest')
        document = load(path)
        literal = {'asset':{'version':'2.0'}, 'buffers':[{'byteLength':44,'uri':'data:application/octet-stream;base64,'+base64.b64encode(blob).decode('ascii')}],
                   'bufferViews':[{'buffer':0,'byteOffset':0,'byteLength':16},{'buffer':0,'byteOffset':16,'byteLength':8},{'buffer':0,'byteOffset':24,'byteLength':20}],
                   'accessors':[{'componentType':5126,'count':4,'type':'SCALAR','sparse':{'count':2,'indices':{'bufferView':1,'byteOffset':2,'componentType':5123},'values':{'bufferView':2,'byteOffset':4}}}]}
        if name == 'dense': literal['accessors'][0].update(bufferView=0,byteOffset=0)
        require(equal(document, literal), 'literal input document '+name)
    print(json.dumps({'status':'PASS','semantic_cases':7,'success_configurations':2,'expected_rejections':5,
                      'scope':'static archive consistency and frozen literals, not execution authentication',
                      'source_pins_sha256':digest(args.source_pins),'stdout_sha256':digest(args.stdout),
                      'stderr_sha256':digest(args.stderr),'summary_sha256':digest(args.root/'results'/'summary.json')}))

if __name__ == '__main__': main()
