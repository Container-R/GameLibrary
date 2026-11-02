"""Pure synthetic consumer tests, not SQLite observations. Await run approval."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('pure_checker', ROOT / 'checker.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
HASH = 'a' * 64


def golden():
    # Author synthetic baseline; independent reviewer must derive its own oracle.
    return {'schema': 1, 'status': 'OBSERVED', 'steps': checker.expected_steps(),
            'fixture_sha256': HASH, 'versions': {'python': '3.12.0', 'sqlite': '3.45.0'},
            'connections_opened': 3, 'connections_closed': 3, 'cleanup_complete': True}


class ConsumerTests(unittest.TestCase):
    def reject(self, obj):
        with self.assertRaises(ValueError):
            checker.validate_observation(obj, HASH)

    def test_synthetic_positive(self):
        checker.validate_observation(golden(), HASH)

    def test_boolean_and_float_not_integer(self):
        for value in (True, 1.0):
            item = golden()
            item['schema'] = value
            self.reject(item)
        for value in (False, 0.0):
            item = golden()
            item['steps'][0]['A_busy_timeout'] = [[value]]
            self.reject(item)

    def test_order_duplicate_missing(self):
        item = golden()
        item['steps'][1:3] = list(reversed(item['steps'][1:3]))
        self.reject(item)
        item = golden()
        item['steps'].append(copy.deepcopy(item['steps'][-1]))
        self.reject(item)
        item = golden()
        item['steps'].pop()
        self.reject(item)

    def test_codes_and_transaction(self):
        for field, value in (('code', 5), ('name', 'SQLITE_BUSY'), ('primary_code', False), ('in_transaction', False)):
            item = golden()
            item['steps'][6][field] = value
            self.reject(item)

    def test_modes_and_final_rows(self):
        item = golden()
        item['steps'][0]['B_mode'] = [['delete']]
        self.reject(item)
        item = golden()
        item['steps'][-1]['balances'][0][1] = 124
        self.reject(item)

    def test_connection_property_values(self):
        for field, value in (('A_autocommit', False), ('B_autocommit', True),
                             ('A_autocommit', -1.0), ('A_isolation_level', ''),
                             ('B_isolation_level', 'DEFERRED')):
            item = golden()
            item['steps'][0][field] = value
            self.reject(item)

    def test_failure_identity_cleanup(self):
        for key, value in (('status', 'FAILED'), ('fixture_sha256', 'b' * 64),
                           ('cleanup_complete', False), ('connections_closed', 2)):
            item = golden()
            item[key] = value
            self.reject(item)

    def test_json_rejections(self):
        for raw in (b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}',
                    b'{"a":1e999}', b'{} {}', b'not json'):
            with self.assertRaises((ValueError, UnicodeError)):
                checker.parse(raw)

    def test_extra_key_and_versions(self):
        item = golden()
        item['unknown'] = 1
        self.reject(item)
        for version in ('3.11.9', '/private/location', False):
            item = golden()
            item['versions']['python'] = version
            self.reject(item)

    def test_archive_binding_and_dependency(self):
        # No source execution: placeholder files exercise archive hash binding.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / 'output'
            output.mkdir()
            for name in checker.INPUTS:
                (root / name).write_text('synthetic input ' + name)
            manifest = checker.source_hashes(root)
            (root / 'INPUT-MANIFEST.json').write_text(json.dumps(manifest))
            item = golden()
            item['fixture_sha256'] = manifest['child.py']
            raw = json.dumps(item).encode()
            (output / 'stdout.json').write_bytes(raw)
            (output / 'stderr.internal.txt').write_bytes(b'')
            receipt = {'schema': 1, 'status': 'PASS', 'input_hashes_before': manifest,
                       'input_hashes_after': manifest, 'native_spawn_attempts': 1,
                       'native_children_started': 1, 'child_exit': 0, 'timed_out': False,
                       'cleanup_complete': True, 'environment_validated': True,
                       'stderr_empty': True, 'stdout_sha256': hashlib.sha256(raw).hexdigest()}
            (output / 'result.json').write_text(json.dumps(receipt))
            checker.validate_archive(root, output)
            (output / 'stderr.internal.txt').write_bytes(b'unexpected diagnostic')
            with self.assertRaises(ValueError):
                checker.validate_archive(root, output)
            (output / 'stderr.internal.txt').unlink()
            with self.assertRaises(ValueError):
                checker.validate_archive(root, output)
            (output / 'stderr.internal.txt').symlink_to(output / 'stdout.json')
            with self.assertRaises(ValueError):
                checker.validate_archive(root, output)
            (output / 'stderr.internal.txt').unlink()
            (output / 'stderr.internal.txt').write_bytes(b'')
            (root / 'child.py').write_text('changed')
            with self.assertRaises(ValueError):
                checker.validate_archive(root, output)
            (root / 'child.py').unlink()
            with self.assertRaises(ValueError):
                checker.validate_archive(root, output)


if __name__ == '__main__':
    unittest.main()
