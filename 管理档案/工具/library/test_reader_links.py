import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import check_reader_links as tool


class LinksTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.write('books/a.md', '# Start\n')
        self.write('books/中文.md', '# 中文标题\n## Repeated\n## Repeated\n')
        self.write('manifest.json', json.dumps({'entries': [{'current_read_path': 'books/a.md'}]}))

    def write(self, path, text):
        p = self.root/path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')

    def result(self, text):
        self.write('books/a.md', text)
        return tool.check(self.root, 'manifest.json', 1)

    def test_chinese_and_encoded(self):
        r = self.result('[中文](中文.md#中文标题) [编码](%E4%B8%AD%E6%96%87.md#%E4%B8%AD%E6%96%87%E6%A0%87%E9%A2%98)')
        self.assertEqual(r['status'], 'pass')
        self.assertEqual(r['local_links_checked'], 2)

    def test_same_document(self):
        self.assertEqual(self.result('# Same\n[go](#same)')['status'], 'pass')

    def test_duplicate_titles(self):
        self.assertEqual(self.result('[go](中文.md#repeated-1)')['status'], 'pass')
        self.assertEqual(self.result('[go](中文.md#repeated-2)')['status'], 'fail')

    def test_duplicate_collision(self):
        slugs, partial = tool.headings('# A\n# A\n# A-1\n')
        self.assertEqual(slugs, {'a', 'a-1', 'a-1-1'})
        self.assertFalse(partial)

    def test_code_blocks_not_links(self):
        r = self.result('# Start\n```md\n[x](missing.md)\n```\n~~~\n[x](../missing.md)\n~~~\n`[x](missing.md)`\n')
        self.assertEqual(r['status'], 'pass')
        self.assertEqual(r['local_links_checked'], 0)

    def test_wrong_parent(self):
        self.assertEqual(self.result('[go](../中文.md)')['status'], 'fail')

    def test_missing_target(self):
        self.assertEqual(self.result('[go](missing.md)')['status'], 'fail')

    def test_escape(self):
        self.assertEqual(self.result('[go](../../outside.md)')['status'], 'fail')

    def test_encoded_escape(self):
        self.assertEqual(self.result('[go](%2e%2e/%2e%2e/outside.md)')['status'], 'fail')

    def test_absolute_and_authority(self):
        for dest in ['/outside/example.md', '//host/x', 'file:///outside/example.md']:
            with self.subTest(dest=dest):
                self.assertEqual(self.result('[x]('+dest+')')['status'], 'fail')

    def test_missing_fragment(self):
        self.assertEqual(self.result('[go](中文.md#no-such-heading)')['status'], 'fail')

    def test_missing_manifest(self):
        with self.assertRaises(ValueError):
            tool.check(self.root, 'absent.json', 1)

    def test_empty_manifest(self):
        self.write('manifest.json', '{"entries":[]}')
        with self.assertRaises(ValueError):
            tool.check(self.root, 'manifest.json', 1)

    def test_bad_expected_count(self):
        for count in (0, -1, True, 2):
            with self.subTest(count=count), self.assertRaises(ValueError):
                tool.check(self.root, 'manifest.json', count)

    def test_bad_manifest(self):
        for content in ['[]', '{"entries":[],"entries":[]}', '{}', '{"entries":[{}]}']:
            self.write('manifest.json', content)
            with self.subTest(content=content), self.assertRaises(ValueError):
                tool.check(self.root, 'manifest.json', 1)

    def test_duplicate_reader(self):
        self.write('manifest.json', json.dumps({'entries': [{'current_read_path': 'books/a.md'}]*2}))
        with self.assertRaises(ValueError):
            tool.check(self.root, 'manifest.json', 2)

    def test_external_reported_not_checked(self):
        r = self.result('[x](https://example.test/x#none) <http://example.test>')
        self.assertEqual(r['status'], 'pass')
        self.assertEqual(r['external_links_not_checked'], 2)

    def test_unsupported_syntax(self):
        for text in ['[x][ref]', '[ref]: target.md', '[x](中文.md "title")', '<a href="中文.md">x</a>', '[shortcut]', '[x](a(b).md)', '[x](open']:
            with self.subTest(text=text):
                self.assertNotEqual(self.result(text)['status'], 'pass')

    def test_unsupported_heading_not_pass(self):
        self.assertEqual(self.result('# **Fancy**\n[x](#fancy)')['status'], 'incomplete')

    def test_bad_encoding_and_query(self):
        for text in ['[x](%ZZ.md)', '[x](中文.md?q=1)', '[x](中文.md#)']:
            with self.subTest(text=text):
                self.assertNotEqual(self.result(text)['status'], 'pass')

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as other:
            out = Path(other)/'out.md'
            out.write_text('# Outside')
            (self.root/'books/out.md').symlink_to(out)
            self.assertEqual(self.result('[x](out.md)')['status'], 'fail')

    def test_numeric_citations_are_prose(self):
        self.assertEqual(self.result('Text [1][2].')['status'], 'pass')
        self.assertEqual(self.result('Text [1], also [2].')['status'], 'pass')

    def test_setext_is_explicitly_unsupported(self):
        self.assertEqual(self.result('Title\n-----\n[x](#title)')['status'], 'incomplete')

    def test_fenced_heading_not_target(self):
        self.assertEqual(self.result('```\n# Hidden\n```\n[x](#hidden)')['status'], 'fail')

    def test_missing_reader_fails_configuration(self):
        (self.root/'books/a.md').unlink()
        with self.assertRaises(ValueError):
            tool.check(self.root, 'manifest.json', 1)

    def test_empty_reader_configuration(self):
        for text in ('', '  \n\t'):
            self.write('books/a.md', text)
            with self.subTest(text=text), self.assertRaises(ValueError):
                tool.check(self.root, 'manifest.json', 1)

    def test_indented_ambiguous_links_not_silent(self):
        for text in ('Paragraph\n    [x](absent.md)', '- Item\n    [x](absent.md)', '    [x](absent.md)'):
            with self.subTest(text=text):
                self.assertNotEqual(self.result(text)['status'], 'pass')

    def test_multiline_label_not_silent(self):
        self.assertNotEqual(self.result('[hello\n world](absent.md)')['status'], 'pass')

    def test_html_and_email_not_silent(self):
        for text in ('<object data="absent.md"></object>', '<person@example.test>'):
            with self.subTest(text=text):
                self.assertEqual(self.result(text)['status'], 'incomplete')

    def test_nonempty_without_links(self):
        self.assertEqual(self.result('A short paragraph.')['status'], 'pass')

    def test_invalid_fence_opener_not_silent(self):
        self.assertNotEqual(self.result('```bad`\n[x](absent.md)\n')['status'], 'pass')
        self.assertEqual(self.result('```bad`\nplain\n')['status'], 'incomplete')

    def test_multiline_html_not_silent(self):
        self.assertEqual(self.result('<object\n data="absent.svg">\n')['status'], 'incomplete')

    def test_ambiguous_inline_code_not_broken(self):
        for text in ('`unclosed [x](absent.md)', '`start\n[x](absent.md)\nend`'):
            r = self.result(text)
            self.assertEqual(r['status'], 'incomplete')
            self.assertEqual(r['target_errors'], [])

    def test_entity_destination_not_broken(self):
        r = self.result('[x](a&amp;b.md)')
        self.assertEqual(r['status'], 'incomplete')
        self.assertEqual(r['target_errors'], [])

    def test_cli_different_cwd_and_relocated_tool(self):
        self.write('tools/check.py', Path(tool.__file__).read_text())
        cmd = [sys.executable] + (['-O'] if sys.flags.optimize else []) + [str(self.root/'tools/check.py'), '--root', str(self.root), '--manifest', 'manifest.json', '--expected-count', '1']
        r = subprocess.run(cmd, cwd=self.root/'books', capture_output=True, text=True, timeout=10)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout)['readers_checked'], 1)
        r = subprocess.run(cmd[:-1]+['0'], cwd=self.root/'books', capture_output=True, text=True, timeout=10)
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn('"status": "pass"', r.stdout)


if __name__ == '__main__':
    unittest.main()
