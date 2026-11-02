import copy
import contextlib
import io
from unittest.mock import patch
import json
from pathlib import Path
import tempfile
import unittest
from check_reader_counts import check, strict_json, main


class CountsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'GameLibrary/S').mkdir(parents=True)
        (self.root / '管理档案').mkdir()
        (self.root / '.agent').mkdir()
        for name in ('a.md', 'b.md', 'README.md'):
            (self.root / 'GameLibrary/S' / name).write_text('# Title\n', encoding='utf-8')
        self.catalog = {'entries': [{'canonical_reader_path': 'GameLibrary/S/' + n} for n in ('a.md', 'b.md')],
                        'reader_books_total': 2, 'post_baseline_research_books': 1,
                        'rewritten_reader_books': 1, 'accounted_for_original_items': 1}
        self.state = {'reader_baseline': {'reader_books_total': 2, 'rewritten_reader_books': 1,
                                         'accounted_for_original_items': 1},
                      'publication': {'reader_books_total': 2, 'post_baseline_research_books': 1}}
        self.save()

    def save(self):
        for path, value in [('管理档案/图书目录.json', self.catalog), ('.agent/state.json', self.state)]:
            (self.root / path).write_text(json.dumps(value), encoding='utf-8')

    def bad(self):
        self.save()
        with self.assertRaises((ValueError, OSError)):
            check(self.root, 1)

    def test_valid_and_readme_excluded(self):
        result = check(self.root, 1)
        self.assertEqual(result['status'], 'pass')
        self.assertEqual(result['actual_reader_bodies'], 2)
        self.assertEqual(result['post_baseline_research_books'], 1)

    def test_all_count_fields_fail_closed(self):
        originals = copy.deepcopy((self.catalog, self.state))
        for section in ('catalog', 'baseline', 'publication'):
            fields = {'catalog': ['reader_books_total', 'post_baseline_research_books', 'rewritten_reader_books', 'accounted_for_original_items'],
                      'baseline': ['reader_books_total', 'rewritten_reader_books', 'accounted_for_original_items'],
                      'publication': ['reader_books_total', 'post_baseline_research_books']}[section]
            for field in fields:
                for bad in (None, True, False, '2', 2.0, -1, 99):
                    with self.subTest(section=section, field=field, value=bad):
                        self.catalog, self.state = copy.deepcopy(originals)
                        obj = self.catalog if section == 'catalog' else self.state['reader_baseline' if section == 'baseline' else 'publication']
                        if bad is None:
                            del obj[field]
                        else:
                            obj[field] = bad
                        self.bad()

    def test_duplicate_canonical(self):
        self.catalog['entries'][1] = copy.deepcopy(self.catalog['entries'][0])
        self.bad()

    def test_same_length_wrong_set(self):
        self.catalog['entries'][1]['canonical_reader_path'] = 'GameLibrary/S/absent.md'
        self.bad()

    def test_unlisted_body(self):
        (self.root / 'GameLibrary/S/extra.md').write_text('# Extra')
        self.bad()

    def test_missing_body(self):
        (self.root / 'GameLibrary/S/a.md').unlink()
        self.bad()

    def test_empty_library(self):
        for path in (self.root / 'GameLibrary/S').glob('*.md'):
            path.unlink()
        self.catalog['entries'] = []
        self.bad()

    def test_invalid_paths(self):
        for path in ('GameLibrary/S/README.md', '../outside.md', 'GameLibrary/S/../a.md',
                     'GameLibrary//a.md', '/GameLibrary/a.md', 'GameLibrary\\a.md',
                     'Other/a.md', 'GameLibrary/S/a.md#x', True, None):
            with self.subTest(path=path):
                self.catalog['entries'][0]['canonical_reader_path'] = path
                self.bad()

    def test_missing_state_and_sections(self):
        (self.root / '.agent/state.json').unlink()
        with self.assertRaises(OSError):
            check(self.root, 1)
        for section in ('reader_baseline', 'publication'):
            old = self.state.pop(section)
            self.bad()
            self.state[section] = old

    def test_explicit_frozen_only(self):
        for value in (None, True, False, 1.0, '1', 0, -1, 3):
            with self.subTest(value=value), self.assertRaises(ValueError):
                check(self.root, value)

    def test_cli_failure_not_pass(self):
        self.catalog['reader_books_total'] = 99
        self.save()
        output = io.StringIO()
        with patch('sys.argv', ['checker', '--root', str(self.root), '--frozen-count', '1']), contextlib.redirect_stdout(output):
            self.assertEqual(main(), 1)
        self.assertEqual(json.loads(output.getvalue())['status'], 'fail')

    def test_json_rejections(self):
        for text in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":1e999}'):
            with self.assertRaises(ValueError):
                strict_json(text)

    def test_symlinks_rejected(self):
        body = self.root / 'GameLibrary/S/b.md'
        body.unlink()
        body.symlink_to('a.md')
        self.bad()
        body.unlink()
        body.write_text('# B')
        (self.root / 'GameLibrary/alias').symlink_to('S', target_is_directory=True)
        self.bad()

    def test_missing_entries_and_wrong_shapes(self):
        for value in (None, [], {}, [True], [{'other': 'x'}]):
            self.catalog['entries'] = value
            self.bad()
        self.catalog = []
        self.bad()


if __name__ == '__main__':
    unittest.main()
