"""Pure archive validation: no sqlite import, native probe or child launch."""
import hashlib
import json
import math
from pathlib import Path
import re
import sys


def require(ok, label):
    if not ok:
        raise ValueError(label)


def exact(actual, expected):
    if type(actual) is not type(expected):
        return False
    if type(expected) is dict:
        return actual.keys() == expected.keys() and all(exact(actual[k], v) for k, v in expected.items())
    if type(expected) is list:
        return len(actual) == len(expected) and all(exact(a, b) for a, b in zip(actual, expected))
    return actual == expected


def parse(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate_json_key')
            result[key] = value
        return result
    def constant(_):
        raise ValueError('nonfinite_json')
    def floating(token):
        value = float(token)
        require(math.isfinite(value), 'nonfinite_json')
        return value
    require(type(raw) is bytes and len(raw) <= 131072, 'raw_size')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=constant, parse_float=floating)


def expected_steps():
    def state(step, amount, found, active):
        return {'step': step, 'balances': [['player-one', amount]],
                'operations': [['player-one', 'reward-one', 112]] if found else [],
                'in_transaction': active}
    result = [{'step': 'configuration', 'set_mode': [['wal']],
               'A_mode': [['wal']], 'B_mode': [['wal']],
               'A_busy_timeout': [[0]], 'B_busy_timeout': [[0]],
               'A_read_uncommitted': [[0]], 'B_read_uncommitted': [[0]],
               'A_autocommit': -1, 'B_autocommit': -1,
               'A_isolation_level': None, 'B_isolation_level': None,
               'distinct_connections': True, 'A_in_transaction': False, 'B_in_transaction': False},
              state('initialized', 100, False, False),
              state('A_initial_read', 100, False, True),
              state('B_before_write', 100, False, True),
              state('B_committed', 112, True, False),
              state('A_old_snapshot', 100, False, True)]
    for step in ('A_upgrade_attempt_1', 'A_upgrade_attempt_2'):
        result.append({'step': step, 'outcome': 'exception', 'code': 517,
                       'name': 'SQLITE_BUSY_SNAPSHOT', 'primary_code': 5, 'in_transaction': True})
    result += [{'step': 'A_rollback', 'in_transaction': False},
               state('A_recheck', 112, True, True),
               {'step': 'A_duplicate_committed', 'branch': 'duplicate_result',
                'result_amount': 112, 'in_transaction': False},
               state('fresh_connection', 112, True, False)]
    return result


def validate_observation(obj, fixture_hash):
    require(type(obj) is dict, 'report_type')
    require(set(obj) == {'schema', 'status', 'steps', 'fixture_sha256', 'versions',
                        'connections_opened', 'connections_closed', 'cleanup_complete'}, 'report_keys')
    for k, v in {'schema': 1, 'status': 'OBSERVED', 'fixture_sha256': fixture_hash,
                 'connections_opened': 3, 'connections_closed': 3, 'cleanup_complete': True}.items():
        require(exact(obj[k], v), 'report_' + k)
    versions = obj['versions']
    require(type(versions) is dict and set(versions) == {'python', 'sqlite'}, 'versions_keys')
    for version in versions.values():
        require(type(version) is str and re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:[a-z]+[0-9]+)?', version) is not None, 'version_format')
    require(tuple(int(v) for v in versions['python'].split('.')[:2]) >= (3, 12), 'python_minimum')
    require(exact(obj['steps'], expected_steps()), 'literal_steps')


INPUTS = ('PROTOCOL.md', 'child.py', 'run.py', 'checker.py', 'isolation.py', 'test_checker.py')


def source_hashes(root):
    result = {}
    for name in INPUTS:
        p = root / name
        require(p.is_file() and not p.is_symlink(), 'input_missing_or_symlink')
        result[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def validate_archive(root, output):
    manifest = parse((root / 'INPUT-MANIFEST.json').read_bytes())
    require(exact(manifest, source_hashes(root)), 'source_manifest')
    for name in ('result.json', 'stdout.json', 'stderr.internal.txt'):
        require((output / name).is_file() and not (output / name).is_symlink(), 'archive_file')
    require((output / 'stderr.internal.txt').read_bytes() == b'', 'actual_stderr_not_empty')
    receipt = parse((output / 'result.json').read_bytes())
    raw = (output / 'stdout.json').read_bytes()
    expected = {'schema': 1, 'status': 'PASS', 'input_hashes_before': manifest,
                'input_hashes_after': manifest, 'native_spawn_attempts': 1,
                'native_children_started': 1, 'child_exit': 0, 'timed_out': False,
                'cleanup_complete': True, 'environment_validated': True,
                'stderr_empty': True, 'stdout_sha256': hashlib.sha256(raw).hexdigest()}
    require(exact(receipt, expected), 'terminal_receipt')
    validate_observation(parse(raw), manifest['child.py'])


if __name__ == '__main__':
    try:
        require(len(sys.argv) == 2, 'one_archive_argument_required')
        validate_archive(Path(__file__).resolve().parent, Path(sys.argv[1]))
    except Exception as exc:
        print('REJECTED: ' + type(exc).__name__)
        raise SystemExit(1)
    print('PASS: literal archive consistency only; no native execution')
