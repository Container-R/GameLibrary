"""Finite fail-closed target-heading regressions; not Markdown rendering tests."""
import json
from pathlib import Path
import tempfile
import unittest
import check_reader_links as tool

class HTMLHeadingScope(unittest.TestCase):
    def result(self,text,fragment='hidden'):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'reader.md').write_text('[go](target.md#'+fragment+')\n')
            (root/'target.md').write_text(text)
            (root/'manifest.json').write_text(json.dumps({'entries':[{'current_read_path':'reader.md'}]}))
            return tool.check(root,'manifest.json',1)

    def test_raw_contexts_never_certify_target(self):
        cases=[
            '<div>\n# Hidden\n</div>\n',
            '<!--\n# Hidden\n-->\n',
            '<div\n class="box">\n# Hidden\n</div>\n',
            '<!DOCTYPE html>\n# Hidden\n',
            '<script>\n# Hidden\n</script>\n',
            '<style>\n# Hidden\n</style>\n',
            '<?processing\n# Hidden\n?>\n',
            '<![CDATA[\n# Hidden\n]]>\n',
            '   <div>\n# Hidden\n</div>\n',
            '\t<div>\n# Hidden\n',
        ]
        for text in cases:
            with self.subTest(text=text):
                result=self.result(text)
                self.assertEqual(result['status'],'incomplete')
                self.assertEqual(result['target_errors'],[])
                self.assertEqual(result['fragment_errors'],[])
                self.assertEqual([x['reason'] for x in result['unsupported']],['unsupported target heading syntax'])

    def test_whole_target_conservative_even_when_heading_precedes_marker(self):
        for tail in ('<div>\ntext\n</div>\n','inline a < b\n','<https://example.test>\n'):
            with self.subTest(tail=tail):
                self.assertEqual(self.result('# Hidden\n\n'+tail)['status'],'incomplete')

    def test_standalone_code_span_is_not_raw_html(self):
        self.assertEqual(self.result('# Hidden\n\n`<div>`\n')['status'], 'pass')

    def test_supported_fences_do_not_create_html_context(self):
        for fence in ('```','~~~'):
            text=fence+'html\n<div>\n# Fake\n<!--\n'+fence+'\n# Hidden\n'
            self.assertEqual(self.result(text)['status'],'pass')
            self.assertEqual(self.result(text,'fake')['status'],'fail')

    def test_plain_atx_and_duplicates_unchanged(self):
        text='# Hidden\n\n## A\n## A\n## A-1\n'
        for fragment in ('hidden','a','a-1','a-1-1'):
            self.assertEqual(self.result(text,fragment)['status'],'pass')
        self.assertEqual(self.result(text,'missing')['status'],'fail')

    def test_invalid_fence_cannot_hide_html_marker(self):
        text='```bad`\n<div>\n# Hidden\n</div>\n'
        self.assertEqual(self.result(text)['status'],'incomplete')
        # A short would-be closer does not end a longer valid fence.
        text='````\n```\n<div>\n# Hidden\n'
        self.assertEqual(self.result(text)['status'],'fail')

    def test_reference_and_frontmatter_scope_not_relaxed(self):
        self.assertEqual(self.result('---\nid: sample\n---\n# Hidden\n')['status'],'incomplete')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'reader.md').write_text('# Hidden\n[shortcut]\n[go](#hidden)\n')
            (root/'manifest.json').write_text(json.dumps({'entries':[{'current_read_path':'reader.md'}]}))
            result=tool.check(root,'manifest.json',1)
            self.assertEqual(result['status'],'incomplete')
            self.assertIn('unsupported bracket/reference syntax',[x['reason'] for x in result['unsupported']])

if __name__=='__main__': unittest.main()
