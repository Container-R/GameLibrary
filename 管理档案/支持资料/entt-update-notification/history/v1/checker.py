"""Finite consumer only: acceptance additionally requires runner exit 0 and receipt pass."""
import hashlib
import json
from pathlib import Path
EXPECTED_SHA = '7c69434efd6576b5710524306946a7525cd536592a065f1bd1c91171f3ff61c2'
def pairs(items):
    result = {}
    for key, value in items:
        if key in result: raise ValueError('duplicate key')
        result[key] = value
    return result
def invalid(value): raise ValueError('nonfinite JSON')
def parse(data):
    return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid)
def exact(a, b):
    if type(a) is not type(b): return False
    if type(a) is dict: return a.keys() == b.keys() and all(exact(a[k], b[k]) for k in a)
    if type(a) is list: return len(a) == len(b) and all(exact(x,y) for x,y in zip(a,b))
    return a == b
def validate(stdout, stderr, expected_path):
    raw = Path(expected_path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_SHA: raise ValueError('oracle identity')
    if stderr != b'': raise ValueError('child stderr')
    lines = stdout.decode('utf-8').splitlines()
    if len(lines) != 3: raise ValueError('row count')
    observed = [parse(line) for line in lines]
    if not exact(observed, parse(raw)): raise ValueError('observation mismatch')
    return {'result_kind':'consumer_only','cases':3,'match':True}
if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2: raise SystemExit('usage: checker.py RUN_DIRECTORY')
    directory = Path(sys.argv[1])
    print(json.dumps(validate((directory/'native.stdout').read_bytes(),
                             (directory/'native.stderr').read_bytes(),
                             Path(__file__).with_name('expected.json'))))
