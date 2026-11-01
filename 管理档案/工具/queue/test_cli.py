"""Synthetic inputs only: never invoke against an inherited repository queue."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('validate_queue.py').resolve()


class CLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'repo'
        self.root.mkdir()
        self.tax = '管理档案/分类/disciplines.json'
        self.queue = '管理档案/队列/tasks.json'
        self.write(self.tax, {'disciplines': [{'id': 'GFX'}, {'id': 'PROG'}]})
        self.write(self.queue, {'tasks': [
            {'id': 'T1', 'discipline': 'GFX', 'status': 'published', 'artifact_paths': ['book.md']},
            {'id': 'T2', 'discipline': 'PROG', 'status': 'planned', 'artifact_paths': ['future.md']}]})
        (self.root / 'book.md').write_text('synthetic fixture', encoding='utf-8')

    def write(self, name, value):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(value), encoding='utf-8')

    def run_cli(self, *args, script=SCRIPT, cwd=None):
        return subprocess.run([sys.executable, *(['-O'] if sys.flags.optimize else []), str(script), *map(str, args)],
                              cwd=cwd or self.base, text=True, capture_output=True)

    def configured(self, **kwargs):
        return self.run_cli(self.root, '--taxonomy', self.tax, '--queue', self.queue, **kwargs)

    def assert_failure(self, result):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertNotIn('"status": "PASS"', result.stdout)

    def test_configured_nonempty_counts(self):
        result = self.configured()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {'status': 'PASS', 'tasks_checked': 2, 'artifact_paths_checked': 2})

    def test_default_compatibility(self):
        for src, dest in [(self.tax, 'taxonomy/disciplines.json'), (self.queue, '.agent/queue.json')]:
            target = self.root / dest
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.root / src, target)
        self.assertEqual(self.run_cli(self.root).returncode, 0)

    def test_missing_inputs_no_fallback(self):
        self.assert_failure(self.run_cli(self.root))
        for name in (self.tax, self.queue):
            path = self.root / name
            saved = path.read_bytes()
            path.unlink()
            self.assert_failure(self.configured())
            path.write_bytes(saved)
        self.assert_failure(self.run_cli(self.root, '--taxonomy', '管理档案', '--queue', self.queue))

    def test_all_tasks_and_categories_checked(self):
        self.write(self.queue, {'tasks': [{'id': 'T1', 'discipline': 'GFX'}, {'id': 'T2', 'discipline': 'UNKNOWN'}]})
        self.assert_failure(self.configured())
        self.write(self.queue, {'tasks': [{'id': 'T1', 'discipline': 'GFX'}]})
        self.write(self.tax, {'disciplines': [{'id': 'GFX'}, {'id': 'PROG'}, {'id': 'PROG'}]})
        self.assert_failure(self.configured())

    def test_cwd_and_tool_relocation(self):
        moved = self.base / 'tools' / 'nested' / 'check.py'
        moved.parent.mkdir(parents=True)
        shutil.copyfile(SCRIPT, moved)
        for cwd, root in [(self.base, 'repo'), (self.root, '.'), (moved.parent, '../../repo')]:
            result = self.run_cli(root, '--taxonomy', self.tax, '--queue', self.queue, script=moved, cwd=cwd)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['tasks_checked'], 2)

    def test_input_path_policy_both_flags(self):
        for flag in ('--taxonomy', '--queue'):
            for value in ('../outside.json', '/tmp/out.json', str(self.root / self.tax), 'C:/x', 'C:x', 'a\\b', './a', 'a//b', 'a/../b', '', ' a', 'a\n', 'a/'):
                with self.subTest(flag=flag, value=value):
                    self.assert_failure(self.run_cli(self.root, '--taxonomy', self.tax, '--queue', self.queue, flag, value))

    def test_input_symlinks(self):
        outside = self.base / 'outside.json'
        outside.write_text('{}')
        link = self.root / 'link.json'
        link.symlink_to(outside)
        self.assert_failure(self.run_cli(self.root, '--taxonomy', 'link.json', '--queue', self.queue))
        self.assert_failure(self.run_cli(self.root, '--taxonomy', self.tax, '--queue', 'link.json'))
        link.unlink()
        link.symlink_to(self.root / self.tax)
        self.assertEqual(self.run_cli(self.root, '--taxonomy', 'link.json', '--queue', self.queue).returncode, 0)

    def test_expected_count_positive_argument(self):
        for count in ('0', '-1'):
            result = self.run_cli(self.root, '--taxonomy', self.tax, '--queue', self.queue,
                                  '--expected-task-count', count)
            self.assert_failure(result)
            self.assertEqual(result.returncode, 2)

    def test_expected_count_exact_nonempty_gate(self):
        for count, success in ((1, False), (2, True), (3, False)):
            result = self.run_cli(self.root, '--taxonomy', self.tax, '--queue', self.queue,
                                  '--expected-task-count', count)
            if success:
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)['tasks_checked'], 2)
            else:
                self.assert_failure(result)
        original = json.loads((self.root / self.queue).read_text())
        for tasks in (original['tasks'][:1], original['tasks'] + [{'id': 'T3', 'discipline': 'PROG'}]):
            self.write(self.queue, {'tasks': tasks})
            self.assert_failure(self.run_cli(self.root, '--taxonomy', self.tax, '--queue', self.queue,
                                             '--expected-task-count', 2))
        self.write(self.queue, {'tasks': []})
        result = self.run_cli(self.root, '--taxonomy', self.tax, '--queue', self.queue,
                              '--expected-task-count', 2)
        self.assert_failure(result)
        default = self.configured()
        self.assertEqual(default.returncode, 0, default.stderr)
        self.assertEqual(json.loads(default.stdout)['tasks_checked'], 0)

    def test_explicit_root_required_and_valid(self):
        self.assert_failure(self.run_cli())
        self.assert_failure(self.run_cli(self.base / 'absent'))
        self.assert_failure(self.run_cli(self.root / 'book.md'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
