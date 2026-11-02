"""Independent read-only comparison against frozen pre-execution literal."""
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent

def pairs(items):
    out = {}
    for k, v in items:
        if k in out:
            raise ValueError('duplicate key')
        out[k] = v
    return out

def reject_constant(value):
    raise ValueError('nonfinite number')

def read(raw):
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=reject_constant)

def same(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b

def main():
    if len(sys.argv) != 2:
        raise ValueError('one observation directory required')
    root = Path(sys.argv[1])
    literal = (HERE / 'oracle.json').read_bytes()
    if hashlib.sha256(literal).hexdigest() != 'c1cf3e7391f7ed14a2898419609ed2a1d699b098607f62aa11c0aa95e151d6a0':
        raise ValueError('literal identity')
    expected = read(literal)
    raw = (root / 'stdout.json').read_bytes()
    actual = read(raw)
    versions = actual['versions']
    if type(versions) is not dict or set(versions) != {'python', 'sqlite'}:
        raise ValueError('version keys')
    for v in versions.values():
        if type(v) is not str or re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:[a-z]+[0-9]+)?', v) is None:
            raise ValueError('version format')
    if tuple(map(int, versions['python'].split('.')[:2])) < (3, 12):
        raise ValueError('python capability')
    # No numeric version oracle: these are the actual child self-reports.
    expected['versions'] = versions
    if not same(actual, expected):
        raise ValueError('independent literal mismatch')
    receipt = read((root / 'result.json').read_bytes())
    manifest_raw = (HERE.parent / 'fixture' / 'INPUT-MANIFEST.json').read_bytes()
    if hashlib.sha256(manifest_raw).hexdigest() != 'fc8629602fdbff7f36412d5fb35a44eccd58b13bfc76e29f7238ecc32fb3e39a':
        raise ValueError('manifest identity')
    manifest = read(manifest_raw)
    expected_receipt = {'schema':1,'status':'PASS','input_hashes_before':manifest,
        'input_hashes_after':manifest,'native_spawn_attempts':1,'native_children_started':1,
        'child_exit':0,'timed_out':False,'cleanup_complete':True,'environment_validated':True,
        'stderr_empty':True,'stdout_sha256':hashlib.sha256(raw).hexdigest()}
    if not same(receipt, expected_receipt):
        raise ValueError('receipt mismatch')
    stderr = root / 'stderr.internal.txt'
    if stderr.is_symlink() or not stderr.is_file() or stderr.read_bytes() != b'':
        raise ValueError('actual stderr')
    if (root / 'owned-work').exists():
        raise ValueError('work remains')
    print(json.dumps({'status':'ACCEPTED','steps':len(actual['steps']),
        'versions_self_reported':versions,'stdout_sha256':hashlib.sha256(raw).hexdigest(),
        'scope':'independent literal/receipt readback, not another SQLite invocation'}, sort_keys=True))

if __name__ == '__main__':
    main()
