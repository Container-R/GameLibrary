"""Prepared independent synthetic challenges; not SQLite observations.
Run only after separate authorization. No runner/child import or invocation.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
FIXTURE = HERE.parent / 'fixture'
ORACLE_HASH = 'c1cf3e7391f7ed14a2898419609ed2a1d699b098607f62aa11c0aa95e151d6a0'
CHECKER_HASH = 'a29d87fccd5171332ee443c9a1709b72df6da5f2f4e6b573fe7fb563d6a398b2'
INPUTS = ('PROTOCOL.md', 'child.py', 'run.py', 'checker.py', 'isolation.py', 'test_checker.py')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load_oracle():
    raw = (HERE / 'oracle.json').read_bytes()
    if digest(raw) != ORACLE_HASH:
        raise ValueError('independent oracle identity changed')
    return json.loads(raw)


class IndependentConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if digest((FIXTURE / 'checker.py').read_bytes()) != CHECKER_HASH:
            raise ValueError('reviewed consumer identity changed')
        spec = importlib.util.spec_from_file_location('reviewed_consumer', FIXTURE / 'checker.py')
        cls.consumer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.consumer)

    def accept(self, obj):
        self.consumer.validate_observation(obj, load_oracle()['fixture_sha256'])

    def reject(self, obj):
        with self.assertRaises(ValueError):
            self.accept(obj)

    def test_literal_positive_and_fixed_step_count(self):
        obj = load_oracle()
        self.assertEqual(len(obj['steps']), 12)
        self.assertEqual(len({s['step'] for s in obj['steps']}), 12)
        self.accept(obj)

    def test_each_missing_duplicate_and_adjacent_reordering(self):
        for index in range(12):
            with self.subTest(missing=index):
                obj = load_oracle()
                obj['steps'].pop(index)
                self.reject(obj)
            with self.subTest(duplicate=index):
                obj = load_oracle()
                obj['steps'].insert(index, obj['steps'][index].copy())
                self.reject(obj)
        for index in range(11):
            with self.subTest(swapped=index):
                obj = load_oracle()
                obj['steps'][index:index+2] = reversed(obj['steps'][index:index+2])
                self.reject(obj)

    def test_both_upgrade_errors_and_active_transaction(self):
        for index in (6, 7):
            for field, value in (('code', 5), ('code', 517.0), ('code', 261),
                                 ('name', 'SQLITE_BUSY'), ('primary_code', 517),
                                 ('in_transaction', False), ('outcome', 'success')):
                with self.subTest(index=index, field=field, value=value):
                    obj = load_oracle()
                    obj['steps'][index][field] = value
                    self.reject(obj)

    def test_snapshot_rollback_and_new_transaction_decision(self):
        for index, field, value in (
            (5, 'balances', [['player-one', 112]]),
            (5, 'operations', [['player-one', 'reward-one', 112]]),
            (8, 'in_transaction', True), (9, 'in_transaction', False),
            (9, 'operations', []), (9, 'balances', [['player-one', 100]]),
            (10, 'branch', 'apply_reward'), (10, 'result_amount', 124),
            (10, 'in_transaction', True)):
            with self.subTest(index=index, field=field):
                obj = load_oracle()
                obj['steps'][index][field] = value
                self.reject(obj)

    def test_committed_rechecked_and_reopened_exact_single_record(self):
        for index in (4, 9, 11):
            for field, value in (
                ('balances', [['player-one', 124]]),
                ('balances', [['player-one', 112], ['other', 0]]),
                ('operations', []),
                ('operations', [['player-one', 'reward-one', 112]] * 2),
                ('operations', [['player-one', 'reward-one', 124]]),
                ('operations', [['player-one', 'different-request', 112]])):
                with self.subTest(index=index, field=field, value=value):
                    obj = load_oracle()
                    obj['steps'][index][field] = value
                    self.reject(obj)

    def test_strict_boolean_integer_and_float_types(self):
        for field, value in (('schema', True), ('connections_opened', 3.0),
                             ('cleanup_complete', 1)):
            obj = load_oracle()
            obj[field] = value
            self.reject(obj)
        for field, value in (('A_busy_timeout', [[False]]), ('B_read_uncommitted', [[False]]),
                             ('A_autocommit', -1.0), ('B_isolation_level', ''),
                             ('distinct_connections', 1), ('B_in_transaction', 0)):
            obj = load_oracle()
            obj['steps'][0][field] = value
            self.reject(obj)
        obj = load_oracle()
        obj['steps'][9]['in_transaction'] = 1
        self.reject(obj)

    def test_json_duplicate_and_nonfinite_rejection(self):
        for raw in (b'{"schema":1,"schema":1}', b'{"x":NaN}', b'{"x":Infinity}',
                    b'{"x":-Infinity}', b'{"x":1e999}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                self.consumer.parse(raw)

    def synthetic_archive(self, root):
        # Independent byte/hash construction; these placeholders are never imported.
        out = root / 'output'
        out.mkdir()
        manifest = {}
        for name in INPUTS:
            raw = ('independent synthetic placeholder: ' + name + '\n').encode()
            (root / name).write_bytes(raw)
            manifest[name] = digest(raw)
        (root / 'INPUT-MANIFEST.json').write_text(json.dumps(manifest), encoding='utf-8')
        obj = load_oracle()
        obj['fixture_sha256'] = manifest['child.py']
        raw = json.dumps(obj).encode()
        (out / 'stdout.json').write_bytes(raw)
        (out / 'stderr.internal.txt').write_bytes(b'')
        receipt = {'schema': 1, 'status': 'PASS', 'input_hashes_before': manifest,
                   'input_hashes_after': manifest, 'native_spawn_attempts': 1,
                   'native_children_started': 1, 'child_exit': 0, 'timed_out': False,
                   'cleanup_complete': True, 'environment_validated': True,
                   'stderr_empty': True, 'stdout_sha256': digest(raw)}
        (out / 'result.json').write_text(json.dumps(receipt), encoding='utf-8')
        return out, receipt

    def test_actual_stderr_file_not_just_receipt_boolean(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out, _ = self.synthetic_archive(root)
            self.consumer.validate_archive(root, out)
            err = out / 'stderr.internal.txt'
            err.write_bytes(b'synthetic diagnostic\n')
            with self.assertRaises(ValueError):
                self.consumer.validate_archive(root, out)
            err.unlink()
            with self.assertRaises(ValueError):
                self.consumer.validate_archive(root, out)
            (out / 'empty.txt').write_bytes(b'')
            err.symlink_to('empty.txt')
            with self.assertRaises(ValueError):
                self.consumer.validate_archive(root, out)

    def test_receipt_and_raw_binding_mutations(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out, receipt = self.synthetic_archive(root)
            self.consumer.validate_archive(root, out)
            for key, value in (('child_exit', False), ('timed_out', 0),
                               ('native_children_started', True), ('stderr_empty', False),
                               ('cleanup_complete', False), ('status', 'FAILED')):
                modified = dict(receipt)
                modified[key] = value
                (out / 'result.json').write_text(json.dumps(modified), encoding='utf-8')
                with self.subTest(key=key), self.assertRaises(ValueError):
                    self.consumer.validate_archive(root, out)
            (out / 'result.json').write_text(json.dumps(receipt), encoding='utf-8')
            (out / 'stdout.json').write_bytes((out / 'stdout.json').read_bytes() + b' ')
            with self.assertRaises(ValueError):
                self.consumer.validate_archive(root, out)


if __name__ == '__main__':
    unittest.main()
