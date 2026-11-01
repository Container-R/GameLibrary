"""Portable receipt integrity consumer; reconstructs literals, imports no author oracle.
Integrity is not proof a recorded process was actually executed.
"""
import hashlib
import json
import math
import re
import struct
import uuid
from datetime import datetime, timedelta
from pathlib import Path

BIN = '/usr/bin/ffmpeg'
LIB = '/lib/x86_64-linux-gnu/libavfilter.so.10'
PINS = {BIN: 'e8a8d46f5225f3062cec7c07fb145d58ae73c603cb740dcd5bad34bfb54e455a',
        LIB: '420fe0833b4a7062a7ed811ce854c8cbdf566979aa32657a23ffe51dbea0d053'}
PROTOCOL = '04beb14e9feab0215f5493fe4eda59426f2f4be75a22e1ba1fb3d9588e386f36'
HELPER = 'bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970'
SOURCES = ('PROTOCOL.md', 'isolation.py', 'signals.py', 'consumer.py', 'run.py', 'test_pure.py')
MODES = ('full-normalized', 'short-normalized', 'short-unscaled')
BASE = {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C'}
ENVKEYS = ('HOME', 'XDG_CACHE_HOME', 'XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'TMPDIR')
BANNER = b'ffmpeg version 7.1.5-0+deb13u1'

def need(ok, message):
    if not ok:
        raise ValueError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def exact(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(exact(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(exact(x, y) for x, y in zip(a, b))
    return a == b

def load(data):
    def pairs(items):
        d = {}
        for k, v in items:
            need(k not in d, 'duplicate JSON key')
            d[k] = v
        return d
    def bad(value):
        raise ValueError('nonfinite JSON number: ' + value)
    result = json.loads(data, object_pairs_hook=pairs, parse_constant=bad)
    def finite(x):
        if type(x) is float:
            need(math.isfinite(x), 'overflowed JSON number')
        elif type(x) is dict:
            for v in x.values(): finite(v)
        elif type(x) is list:
            for v in x: finite(v)
    finite(result)
    return result

def hashes(root):
    return {n: sha((root / n).read_bytes()) for n in SOURCES}

def inputs():
    # Independently restated protocol table, not signals.inputs().
    return {'A': b'\x00\x00\x00\x3f' * 4096,
            'B-full': b'\x00' * 16384, 'B-short': b'\x00' * 8192}

def expected(mode):
    low, high = b'\x00\x00\x80\x3e', b'\x00\x00\x00\x3f'
    return {'full-normalized': low * 4096,
            'short-normalized': low * 2048 + high * 2048,
            'short-unscaled': high * 4096}[mode]

def argv_for(mode, directory):
    if mode == 'version': return [BIN, '-version']
    b = 'B-full' if mode == 'full-normalized' else 'B-short'
    n = '0' if mode == 'short-unscaled' else '1'
    graph = ('[0:a]asetnsamples=n=256:p=0[a];[1:a]asetnsamples=n=256:p=0[b];'
             '[a][b]amix=inputs=2:duration=longest:dropout_transition=0:weights=1 1:normalize=' + n + '[out]')
    return [BIN, '-hide_banner', '-loglevel', 'error', '-nostdin', '-n',
            '-f', 'f32le', '-ar', '48000', '-ac', '1', '-i', str(directory / 'A.f32le'),
            '-f', 'f32le', '-ar', '48000', '-ac', '1', '-i', str(directory / (b + '.f32le')),
            '-filter_complex_threads', '1', '-filter_complex', graph, '-map', '[out]',
            '-c:a', 'pcm_f32le', '-f', 'f32le', str(directory / (mode + '.f32le'))]

def archive(directory, name, data):
    (directory / (name + '.hex')).write_text(data.hex() + '\n', encoding='ascii')
    return {'bytes': len(data), 'sha256': sha(data)}

def read_archive(directory, name, record):
    raw = (directory / (name + '.hex')).read_bytes()
    need(re.fullmatch(b'(?:[0-9a-f]{2})*\n', raw) is not None, 'noncanonical hex')
    data = bytes.fromhex(raw.decode('ascii'))
    need(exact(record, {'bytes': len(data), 'sha256': sha(data)}), 'archive binding')
    binary = directory / (name + '.f32le')
    if binary.exists(): need(binary.read_bytes() == data, 'optional binary differs from archive')
    return data

def verify(root, summary_required=True, invocation=None):
    root = Path(root)
    manifest_raw = (root / 'SOURCE-SHA256.json').read_bytes()
    manifest = load(manifest_raw)
    need(exact(manifest, hashes(root)), 'frozen source manifest')
    need(manifest['PROTOCOL.md'] == PROTOCOL and manifest['isolation.py'] == HELPER, 'fixed source pins')
    summary = load((root / 'summary.json').read_bytes()) if summary_required else None
    if summary_required:
        uid = summary['uuid']
    else:
        need(type(invocation) is str, 'explicit invocation required without summary')
        uid = invocation
    need(type(uid) is str and str(uuid.UUID(uid)) == uid, 'canonical UUID')
    out = root / 'evidence' / uid
    rr = (out / 'receipt.json').read_bytes(); r = load(rr)
    need(set(r) == {'status','uuid','original_directory','manifest_sha256','source_before','source_after',
                   'tools_before','tools_after','inputs','processes','outputs'}, 'receipt fields')
    need(exact(r['status'], 'PASS') and exact(r['uuid'], uid), 'receipt identity/status')
    need(r['manifest_sha256'] == sha(manifest_raw), 'manifest association')
    need(exact(r['source_before'], manifest) and exact(r['source_after'], manifest), 'source before/after')
    need(exact(r['tools_before'], PINS) and exact(r['tools_after'], PINS), 'selected tool bindings')
    original = Path(r['original_directory'])
    need(original.is_absolute() and '..' not in original.parts and original.name == uid and original.parent.name == 'evidence', 'original directory')
    literal_inputs = inputs(); ih = {k: sha(v) for k,v in literal_inputs.items()}
    need(set(r['inputs']) == set(literal_inputs), 'input names')
    for k,v in literal_inputs.items():
        need(read_archive(out, k, r['inputs'][k]) == v, 'input literal')
    need(type(r['processes']) is list and len(r['processes']) == 4, 'exact four processes')
    previous = None
    for mode,p in zip(('version',) + MODES, r['processes']):
        need(set(p) == {'name','argv','cwd','environment','timeout_seconds','status','pid','attempted_utc',
                        'returned_utc','returncode','stdout_sha256','stderr_sha256','inputs_before','inputs_after'}, 'process fields')
        env = dict(BASE); env.update({k: str(original / 'environment' / mode / k) for k in ENVKEYS})
        for key,value in {'name':mode,'argv':argv_for(mode,original),'cwd':str(original),
                          'environment':env,'timeout_seconds':20,'status':'RETURNED','returncode':0,
                          'inputs_before':ih,'inputs_after':ih}.items():
            need(exact(p[key],value), 'process exact field ' + key)
        need(type(p['pid']) is int and p['pid'] > 0, 'PID integer')
        need(type(p['attempted_utc']) is str and type(p['returned_utc']) is str, 'timestamp strings')
        start,end = datetime.fromisoformat(p['attempted_utc']), datetime.fromisoformat(p['returned_utc'])
        need(start.utcoffset() == timedelta(0) and end.utcoffset() == timedelta(0) and start <= end, 'timestamps')
        need(previous is None or previous <= start, 'sequential chronology'); previous=end
        for stream in ('stdout','stderr'):
            raw = (out / (mode + '.' + stream)).read_bytes()
            need(type(p[stream+'_sha256']) is str and sha(raw) == p[stream+'_sha256'], 'raw log hash')
            if mode == 'version' and stream == 'stdout':
                need(raw.splitlines()[0].startswith(BANNER + b' ') or raw.splitlines()[0] == BANNER, 'version banner')
            else: need(raw == b'', 'unexpected native diagnostic')
    need(set(r['outputs']) == set(MODES), 'output names')
    for mode in MODES:
        o = r['outputs'][mode]
        need(set(o) == {'archive','check'}, 'output fields')
        data = read_archive(out, mode, o['archive'])
        need(len(data)==16384 and all(math.isfinite(x[0]) for x in struct.iter_unpack('<f', data)), 'finite full waveform')
        need(data == expected(mode), 'independent literal output')
        need(exact(o['check'], {'frames':4096,'bytes':16384,'all_samples_equal':True}), 'derived check exact types')
    if summary_required:
        need(exact(summary, {'status':'PASS','uuid':uid,'receipt_sha256':sha(rr),'processes':4,'mixing_conditions':3}), 'summary exact binding')
    return {'uuid':uid,'processes':4,'mixing_conditions':3}

if __name__ == '__main__':
    import sys
    print(json.dumps(verify(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent), sort_keys=True))
