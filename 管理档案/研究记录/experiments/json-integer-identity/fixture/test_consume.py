"""Synthetic consumer tests only: no Node, subprocess, or execution claims."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import consume


def synthetic():
    expected = consume.strict_load(consume.regular(consume.HERE / 'EXPECTED-INDEPENDENT.json'))
    return dict(schema=expected['schema_proposal'], node_version='v1.2.3',
                observations=copy.deepcopy(expected['expected_observations']))


class Tests(unittest.TestCase):
    def test_valid_synthetic(self):
        consume.validate_output(json.dumps(synthetic()))

    def test_bool_alias(self):
        value = synthetic()
        value['observations']['number_equal'] = 1
        with self.assertRaises(ValueError):
            consume.validate_output(json.dumps(value))

    def test_changed_decimal(self):
        value = synthetic()
        value['observations']['number_parse'][1]['decimal'] = '9007199254740993'
        with self.assertRaises(ValueError):
            consume.validate_output(json.dumps(value))

    def test_missing_extra_reordered(self):
        for kind in ('missing', 'extra', 'reversed'):
            value = synthetic()
            if kind == 'missing':
                del value['observations']['string_equal']
            elif kind == 'extra':
                value['additional'] = True
            else:
                value['observations']['string_parse'].reverse()
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                consume.validate_output(json.dumps(value))

    def test_json_invalid_forms(self):
        raw = json.dumps(synthetic())
        for changed in (raw.replace('"number_equal": true', '"number_equal": NaN'),
                        raw.replace('"number_equal": true', '"number_equal": 1e999'),
                        raw.replace('"number_equal": true', '"number_equal": true, "number_equal": true'),
                        raw + '\n{}'):
            with self.subTest(), self.assertRaises(ValueError):
                consume.validate_output(changed)

    def test_stringify_diagnostics_reject(self):
        for field, value in [('threw', False), ('error_name', 'RangeError'),
                             ('returned', True), ('return_type', 'undefined')]:
            observed = synthetic()
            observed['observations']['default_bigint_stringify'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                consume.validate_output(json.dumps(observed))

    def test_version(self):
        for version in (None, '', 123, 'unknown', 'v1.2'):
            value = synthetic()
            value['node_version'] = version
            with self.subTest(version=version), self.assertRaises(ValueError):
                consume.validate_output(json.dumps(value))

    def make_archive(self, root):
        raw = json.dumps(synthetic()).encode()
        (root / 'stdout.txt').write_bytes(raw)
        (root / 'stderr.internal.txt').write_bytes(b'')
        sources = consume.source_map()
        receipt = dict(schema='json-integer-identity-receipt-v1', status='PASS', stage='collected',
                       spawn_attempts=1, children_started=1, returncode=0, timed_out=False,
                       termination_confirmed=True, environment_validated=True, error_category=None, secondary_errors=[],
                       inputs_before=sources, inputs_after=sources,
                       stdout_sha256=consume.digest(raw), stderr_sha256=consume.digest(b''))
        (root / 'receipt.json').write_text(json.dumps(receipt))
        return receipt

    def test_actual_stderr_file(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.make_archive(root)
            consume.validate_archive(root)
            (root / 'stderr.internal.txt').unlink()
            with self.assertRaises(ValueError):
                consume.validate_archive(root)
            (root / 'stderr.internal.txt').write_bytes(b'ERROR')
            with self.assertRaises(ValueError):
                consume.validate_archive(root)
            (root / 'stderr.internal.txt').unlink()
            (root / 'empty').write_bytes(b'')
            (root / 'stderr.internal.txt').symlink_to(root / 'empty')
            with self.assertRaises(ValueError):
                consume.validate_archive(root)

    def test_receipt_conditions(self):
        changes = {'status': 'FAILED_OR_INCOMPLETE', 'returncode': False, 'timed_out': True,
                   'termination_confirmed': False, 'children_started': 0, 'environment_validated': False,
                   'inputs_after': {}, 'stdout_sha256': '0' * 64}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for key, value in changes.items():
                receipt = self.make_archive(root)
                receipt[key] = value
                (root / 'receipt.json').write_text(json.dumps(receipt))
                with self.subTest(key=key), self.assertRaises(ValueError):
                    consume.validate_archive(root)

    def test_input_oracle_binding(self):
        good = json.dumps(synthetic())
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in (*consume.INPUTS, 'INPUT-MANIFEST.json'):
                (root / name).write_bytes((consume.HERE / name).read_bytes())
            with patch.object(consume, 'HERE', root):
                consume.source_map()
                (root / 'observe.mjs').write_text('changed')
                with self.assertRaises(ValueError):
                    consume.source_map()
                (root / 'observe.mjs').unlink()
                with self.assertRaises(ValueError):
                    consume.source_map()
                (root / 'EXPECTED-INDEPENDENT.json').write_text('{}')
                with self.assertRaises(ValueError):
                    consume.validate_output(good)


if __name__ == '__main__':
    unittest.main()
