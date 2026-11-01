"""Synthetic target-heading probes; no engine, network, or private record inputs."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

CASES = {
 'original_div': ('<div>\n# Hidden\n</div>\n', 'hidden', 'incomplete'),
 'comment': ('<!--\n# Hidden\n-->\n', 'hidden', 'incomplete'),
 'processing': ('<?processor\n# Hidden\n?>\n', 'hidden', 'incomplete'),
 'cdata': ('<![CDATA[\n# Hidden\n]]>\n', 'hidden', 'incomplete'),
 'declaration': ('<!DOCTYPE\n# Hidden\n>\n', 'hidden', 'incomplete'),
 'script_upper': ('  <SCRIPT>\n# Hidden\n</SCRIPT>\n', 'hidden', 'incomplete'),
 'incomplete_tag': ('<div\n# Hidden\n', 'hidden', 'incomplete'),
 'closing_only': ('</div>\n# Hidden\n', 'hidden', 'incomplete'),
 'inline_html': ('text <span>value</span>\n# Hidden\n', 'hidden', 'incomplete'),
 'tab_html': ('\t<div>\n# Hidden\n', 'hidden', 'incomplete'),
 'comment_duplicate': ('# Same\n<!--\n# Same\n-->\n# Same\n', 'same-1', 'incomplete'),
 'valid_backtick_code': ('```html\n<div>\n# Hidden\n</div>\n```\n# Visible\n', 'visible', 'pass'),
 'valid_tilde_code': ('~~~html\n<?processor\n<!--\n~~~\n# Visible\n', 'visible', 'pass'),
 'short_close_keeps_code': ('````\n```\n<div>\n# Hidden\n````\n# Visible\n', 'visible', 'pass'),
 'close_then_html': ('```\nplain\n```\n<div>\n# Hidden\n</div>', 'hidden', 'incomplete'),
 'invalid_fence': ('```bad`\n<div>\n# Hidden\n', 'hidden', 'incomplete'),
 'duplicate_plain': ('# Same\n# Same\n# Same-1\n', 'same-1-1', 'pass'),
 'code_hidden_absent': ('```\n# Hidden\n```\n# Visible\n', 'hidden', 'fail'),
}

def run(filename):
    spec=importlib.util.spec_from_file_location('candidate', filename)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    records=[]
    with tempfile.TemporaryDirectory() as folder:
        root=Path(folder)
        (root/'manifest.json').write_text(json.dumps({'entries':[{'current_read_path':'reader.md'}]}))
        for name,(body,fragment,expected) in CASES.items():
            (root/'reader.md').write_text('[Read](target.md#'+fragment+')\n')
            (root/'target.md').write_text(body)
            result=module.check(root,'manifest.json',1)
            records.append({'case':name,'expected':expected,'actual':result['status'],'matched':result['status']==expected,'reasons':[e['reason'] for e in result['errors']]})
    return records

if __name__=='__main__':
    results=run(sys.argv[1])
    print(json.dumps({'cases':results,'matched':sum(r['matched'] for r in results),'total':len(results)},indent=2))
    sys.exit(0 if all(r['matched'] for r in results) else 1)
