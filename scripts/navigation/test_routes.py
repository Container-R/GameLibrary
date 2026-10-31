import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from build_routes import Invalid, metadata, render, scalar

class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);(self.root/'roles').mkdir();(self.root/'solutions').mkdir()
        self.doc('roles/profile.md','ROLE-A-001','role')
        self.doc('solutions/one.md','SOL-A-001','solution')
        self.reg={'schema_version':1,'routes':[{'id':'role-a','title':'Role A','kind':'role','subject_profile_id':'ROLE-A-001','entries':[{'document_id':'SOL-A-001','question':'Question','rationale':'Reason'}]}]}
    def doc(self,path,id,type,status='source-backed',title='Title'):
        (self.root/path).write_text(f'---\nid: {id}\ntitle: {title}\ntype: {type}\nstatus: {status}\nprimary_discipline: PROG\n---\nBody\n')
    def test_determinism_and_status(self):
        self.assertEqual(render(self.root,self.reg),render(self.root,self.reg))
        self.assertIn('`source-backed`',render(self.root,self.reg))
    def test_duplicate_document(self):
        self.doc('solutions/two.md','SOL-A-001','solution')
        with self.assertRaises(Invalid):render(self.root,self.reg)
    def test_missing_id(self):
        self.reg['routes'][0]['entries'][0]['document_id']='SOL-MISSING-001'
        with self.assertRaises(Invalid):render(self.root,self.reg)
    def test_unknown_or_unfinished_status(self):
        for status in ['unknown','needs-research']:
            self.doc('solutions/one.md','SOL-A-001','solution',status)
            with self.assertRaises(Invalid):render(self.root,self.reg)
    def test_role_profile_mismatch(self):
        self.reg['routes'][0]['subject_profile_id']='SOL-A-001'
        with self.assertRaises(Invalid):render(self.root,self.reg)
    def test_move_preserves_id(self):
        (self.root/'solutions/one.md').rename(self.root/'solutions/new name.md')
        output=render(self.root,self.reg)
        self.assertIn('solutions/new%20name.md',output);self.assertNotIn('solutions/one.md',output)
    def test_malformed_registry(self):
        variants=[{},dict(self.reg,schema_version=True),dict(self.reg,routes=[])]
        dup=copy.deepcopy(self.reg);dup['routes']*=2;variants.append(dup)
        wrong=copy.deepcopy(self.reg);wrong['routes'][0]['extra']='x';variants.append(wrong)
        for reg in variants:
            with self.subTest(reg=reg),self.assertRaises(Invalid):render(self.root,reg)
    def test_output_escaping(self):
        self.doc('solutions/one.md','SOL-A-001','solution',title='<script>[bad](evil)*')
        self.reg['routes'][0]['entries'][0]['question']='<img src=x> [click](evil)'
        out=render(self.root,self.reg)
        self.assertNotIn('<script>',out);self.assertNotIn('<img',out)
        self.assertNotIn('[click](evil)',out);self.assertIn('&#91;click&#93;',out)
    def test_unsupported_required_frontmatter(self):
        raw=(self.root/'solutions/one.md').read_text()
        for bad in [raw.replace('title: Title','title: |\n  multiline'),raw.replace('title: Title','title: Title\n  continuation'),raw.replace('title: Title','title: Title\ntitle: duplicate'),raw.replace('title: Title','title: Title\ntitle : replaced'),raw.replace('title: Title','title: Title\n"title": replaced'),raw.replace('title: Title',"title: Title\n'title': replaced")]:
            with self.assertRaises(Invalid):metadata(bad)
    def test_ambiguous_scalar_rejected(self):
        for value in ['# only comment','foo\t# comment','foo: bar','foo:','null','false','123','1e9','2026-01-01']:
            with self.subTest(value=value),self.assertRaises(Invalid):scalar(value)
        for value in ['"null"', '"foo: bar"', "'Ordinary title'"]:
            self.assertEqual(scalar(value),value[1:-1])

    def test_cli_check_and_no_overwrite_on_error(self):
        reg=self.root/'routes.json';reg.write_text(json.dumps(self.reg))
        out=self.root/'DISCOVERY.md'
        cmd=[sys.executable,str(Path(__file__).with_name('build_routes.py')),str(self.root),'--registry',str(reg),'--output',str(out)]
        self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,0)
        before=out.read_bytes();mtime=out.stat().st_mtime_ns
        self.assertEqual(subprocess.run(cmd+['--check'],capture_output=True).returncode,0)
        self.assertEqual(out.stat().st_mtime_ns,mtime)
        reg.write_text('{}')
        self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,2)
        self.assertEqual(out.read_bytes(),before)

if __name__=='__main__':unittest.main(verbosity=2)
