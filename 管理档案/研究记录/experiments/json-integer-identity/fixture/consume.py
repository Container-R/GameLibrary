"""Finite strict archive consumer. No Node launch, imports, or version probe."""
import hashlib
import json
from pathlib import Path
import re

ORACLE_SHA = 'e110a0c04879d4e135ef93381954bbe3e0f30304487889a5e4f1d3e8cb792734'
INPUTS = ('PROTOCOL.md', 'EXPECTED-INDEPENDENT.json', 'isolation.py', 'observe.mjs',
          'run.py', 'consume.py', 'test_consume.py')
HERE = Path(__file__).resolve().parent


def require(condition, code):
    if not condition:
        raise ValueError(code)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def regular(path):
    path = Path(path)
    require(not any(p.is_symlink() for p in (path, *path.parents)), 'symlink')
    require(path.is_file(), 'missing_regular_file')
    require(path.stat().st_size <= 1024 * 1024, 'oversized_file')
    return path.read_bytes()


def strict_load(data):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate_json_key')
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('nonfinite_or_float_json')
    return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid, parse_float=invalid)


def same(actual, expected):
    require(type(actual) is type(expected), 'exact_type')
    if isinstance(expected, dict):
        require(actual.keys() == expected.keys(), 'keys')
        for key in expected:
            same(actual[key], expected[key])
    elif isinstance(expected, list):
        require(len(actual) == len(expected), 'length')
        for a, e in zip(actual, expected):
            same(a, e)
    else:
        require(actual == expected, 'literal_value')


def source_map():
    manifest = strict_load(regular(HERE / 'INPUT-MANIFEST.json'))
    require(type(manifest) is dict and set(manifest) == set(INPUTS), 'input_set')
    actual = {name: digest(regular(HERE / name)) for name in INPUTS}
    same(actual, manifest)
    require(actual['EXPECTED-INDEPENDENT.json'] == ORACLE_SHA, 'oracle_identity')
    return actual


def validate_output(raw):
    oracle = regular(HERE / 'EXPECTED-INDEPENDENT.json')
    require(digest(oracle) == ORACLE_SHA, 'oracle_identity')
    expected = strict_load(oracle)
    result = strict_load(raw)
    require(type(result) is dict and set(result) == {'schema', 'node_version', 'observations'}, 'report_keys')
    same(result['schema'], expected['schema_proposal'])
    require(type(result['node_version']) is str and
            re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?', result['node_version']) is not None,
            'version_format')
    same(result['observations'], expected['expected_observations'])
    return result


def validate_archive(root, allow_pending=False):
    root = Path(root)
    receipt = strict_load(regular(root / 'receipt.json'))
    sources = source_map()
    expected_keys = {'schema', 'status', 'stage', 'spawn_attempts', 'children_started', 'returncode',
                     'timed_out', 'termination_confirmed', 'environment_validated', 'error_category',
                     'inputs_before', 'inputs_after', 'stdout_sha256', 'stderr_sha256', 'secondary_errors'}
    require(type(receipt) is dict and set(receipt) == expected_keys, 'receipt_keys')
    same(receipt['schema'], 'json-integer-identity-receipt-v1')
    require(receipt['status'] in (('PENDING_VALIDATION', 'PASS') if allow_pending else ('PASS',)), 'not_pass')
    same(receipt['stage'], 'collected')
    same(receipt['secondary_errors'], [])
    for key, value in {'spawn_attempts': 1, 'children_started': 1, 'returncode': 0,
                       'timed_out': False, 'termination_confirmed': True,
                       'environment_validated': True, 'error_category': None}.items():
        same(receipt[key], value)
    same(receipt['inputs_before'], sources)
    same(receipt['inputs_after'], sources)
    stdout = regular(root / 'stdout.txt')
    stderr = regular(root / 'stderr.internal.txt')
    require(stderr == b'', 'nonempty_stderr')
    same(receipt['stdout_sha256'], digest(stdout))
    same(receipt['stderr_sha256'], digest(stderr))
    return validate_output(stdout)


if __name__ == '__main__':
    import sys
    try:
        require(len(sys.argv) == 2, 'usage')
        validate_archive(Path(sys.argv[1]))
    except Exception as error:
        print('REJECT: ' + type(error).__name__)
        raise SystemExit(1)
    print('PASS: finite archive consistency; not execution authentication')
