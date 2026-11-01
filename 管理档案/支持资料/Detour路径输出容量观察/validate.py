"""Finite literal consumer; does not load or invoke Detour."""
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import sys

EXPECTED_SHA256 = 'c30414c81af4d665d787312aba22f0f259556bde645013dac4bba43efc609140'

def require(condition, message):
    if not condition:
        raise ValueError(message)

def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def reject(_):
        raise ValueError('nonfinite JSON')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=reject)

def exact(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(exact(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(exact(x, y) for x, y in zip(a, b))
    if type(a) is float:
        return math.isfinite(a) and math.isfinite(b) and a == b
    return a == b

def load_expected():
    raw = Path(__file__).with_name('expected.json').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256, 'literal oracle identity')
    return strict_json(raw)

def validate(observation):
    expected = copy.deepcopy(load_expected())
    require(type(observation) is dict, 'observation object')
    setup = observation.get('setup')
    require(type(setup) is dict, 'setup object')
    refs = setup.get('refs')
    require(type(refs) is list and len(refs) == 3, 'three references')
    require(all(type(r) is str and re.fullmatch(r'[1-9][0-9]*', r) and int(r) <= 4294967295 for r in refs), 'canonical nonzero 32-bit references')
    require(len(set(refs)) == 3, 'distinct references')
    size = setup.get('data_size')
    require(type(size) is int and 0 < size <= 1048576, 'bounded positive tile data size')
    expected['setup']['data_size'] = size
    mapping = dict(zip(('A', 'B', 'C'), refs))
    expected['setup']['refs'] = refs[:]
    for polygon in expected['setup']['polygons']:
        for link in polygon['links']:
            link['ref'] = mapping[link['ref']]
    for case in expected['cases']:
        case['path'] = [mapping.get(r, r) for r in case['path']]
    require(exact(observation, expected), 'literal observation mismatch')
    return {'status':'pass', 'result_kind':'consumer_only',
            'overall_acceptance_requires':'receipt.json status=pass after identity checks',
            'cases':2, 'query_calls':2,
            'scope':'One synthetic three-polygon mesh; output capacities 2 and 3 only'}

def main():
    raw = Path(sys.argv[1]).read_bytes()
    result = validate(strict_json(raw))
    result['observation_sha256'] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
