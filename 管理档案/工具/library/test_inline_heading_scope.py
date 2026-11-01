"""Frozen prospective target cases; no renderer claims."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import check_reader_links as tool
import adversarial_reader_html

class InlineHeadingScope(unittest.TestCase):
    def test_frozen_26_plus_8(self):
        all_cases = []
        for name, count, digest in (
            ('CASES.json', 26, 'f93ab085b1277d42a35c5631d301c8b4fd9e7e471442bd29c384ee310b8a0cea'),
            ('EXTRA-CASES.json', 8, '21384704e07b8202267fb9e665a0a153bf6af9018089fe30f37ea7e1342d4148'),
        ):
            raw = Path(__file__).with_name(name).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), digest)
            cases = tool.strict_json(raw.decode())['cases']
            self.assertEqual(len(cases), count)
            all_cases.extend(cases)
        self.assertEqual(len(all_cases), 34)
        self.assertEqual(len({c['name'] for c in all_cases}), 34)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'manifest.json').write_text(json.dumps({'entries':[{'current_read_path':'reader.md'}]}))
            for case in all_cases:
                with self.subTest(case=case['name']):
                    self.assertIn(case['expected_status'], ('pass', 'incomplete', 'fail'))
                    (root/'reader.md').write_text('[Read](target.md#'+case['fragment']+')\n')
                    (root/'target.md').write_text(case['target'])
                    result = tool.check(root, 'manifest.json', 1)
                    self.assertEqual(result['status'], case['expected_status'])
                    for key in ('readers_checked', 'local_links_checked', 'fragments_checked'):
                        self.assertEqual(result[key], 1)
                    self.assertEqual(result['external_links_not_checked'], 0)
                    self.assertEqual(result['target_errors'], [])
                    expected_reason = {'pass':[], 'incomplete':['unsupported target heading syntax'], 'fail':['missing heading fragment']}[case['expected_status']]
                    self.assertEqual([e['reason'] for e in result['errors']], expected_reason)
                    self.assertEqual(len(result['unsupported']), int(case['expected_status']=='incomplete'))
                    self.assertEqual(len(result['fragment_errors']), int(case['expected_status']=='fail'))

    def test_underscore_scope_outside_versus_inside_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'manifest.json').write_text(json.dumps({'entries':[{'current_read_path':'reader.md'}]}))
            (root/'reader.md').write_text('[Read](target.md#hidden)\n')
            for body, status in (
                ('# Hidden\n\nValue _marked_ `a<b`.\n', 'incomplete'),
                ('# Hidden\n\nValue `a_b<c`.\n', 'pass'),
            ):
                with self.subTest(body=body):
                    (root/'target.md').write_text(body)
                    result = tool.check(root, 'manifest.json', 1)
                    self.assertEqual(result['status'], status)
                    self.assertEqual(result['target_errors'], [])
                    self.assertEqual(result['fragment_errors'], [])
                    self.assertEqual([e['reason'] for e in result['unsupported']],
                                     ['unsupported target heading syntax'] if status == 'incomplete' else [])

    def test_raw_title_underscore_is_conservatively_unsupported(self):
        for title in ('_Hidden_', '__Hidden__', 'word_internal'):
            with self.subTest(title=title):
                slugs, partial = tool.headings('# '+title+'\n')
                self.assertTrue(partial)
                self.assertEqual(slugs, set())

    def test_existing_18_adversarial_cases(self):
        self.assertEqual(len(adversarial_reader_html.CASES), 18)
        results = adversarial_reader_html.run(Path(__file__).with_name('check_reader_links.py'))
        self.assertEqual(len(results), 18)
        self.assertEqual(len({r['case'] for r in results}), 18)
        for result in results:
            with self.subTest(case=result['case']):
                self.assertTrue(result['matched'])

if __name__ == '__main__':
    unittest.main()
