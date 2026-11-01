import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from check_taxonomy import FOLDERS, LEGACY_IDS, check, validate

class Checks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.tax = {'disciplines': [{'id': i} for i in sorted(LEGACY_IDS | {'A11Y','LOC'})]}
        next(n for n in self.tax['disciplines'] if n['id']=='ACCESS').update(name_en='Accessibility and localization', split_into=['A11Y','LOC'], state='legacy-umbrella')
        self.write('管理档案/规范/tax.json', self.tax)
        self.man = {'entries': [{'internal_id':'SOL-A-001', 'reader_title':'Readable', 'canonical_reader_path':'GameLibrary/A/book.md','current_read_path':'GameLibrary/A/book.md'}]}
        self.write('管理档案/books.json',self.man)
        p=self.root/'GameLibrary/A/book.md';p.parent.mkdir(parents=True);p.write_text('# Readable\nNo frontmatter.\n')
    def write(self,name,data):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data))
    def reader(self,n=1):
        return check(self.root,'管理档案/规范/tax.json','reader',n,'管理档案/books.json')
    def legacy(self):
        for folder in FOLDERS:(self.root/folder).mkdir(exist_ok=True)
        (self.root/'roles/one.md').write_text('---\nid: ROLE-A-001\nprimary_discipline: GFX\nrelated_disciplines: [TA]\n---\n# Old\n')
    def test_reader_nonempty_no_yaml(self):
        self.assertEqual(self.reader()['documents_checked'],1)
    def test_legacy_nonempty(self):
        self.legacy();self.assertEqual(check(self.root,'管理档案/规范/tax.json','legacy',1)['documents_checked'],1)
    def test_missing_legacy_directory(self):
        self.legacy();(self.root/'comparisons').rmdir()
        with self.assertRaisesRegex(ValueError,'directory missing'):check(self.root,'管理档案/规范/tax.json','legacy',1)
    def test_zero_legacy_documents(self):
        self.legacy();(self.root/'roles/one.md').unlink()
        with self.assertRaisesRegex(ValueError,'found 0'):check(self.root,'管理档案/规范/tax.json','legacy',1)
    def test_empty_reader_entries(self):
        self.write('管理档案/books.json',{'entries':[]})
        with self.assertRaises(ValueError):self.reader()
    def test_missing_reader_file(self):
        (self.root/'GameLibrary/A/book.md').unlink()
        with self.assertRaises(OSError):self.reader()
    def test_missing_inputs(self):
        for name in ['管理档案/规范/tax.json','管理档案/books.json']:
            p=self.root/name;old=p.read_bytes();p.unlink()
            with self.assertRaises(OSError):self.reader()
            p.write_bytes(old)
    def test_count_cannot_shrink_silently(self):
        with self.assertRaises(ValueError):self.reader(2)
        with self.assertRaises(ValueError):self.reader(0)
    def test_duplicate_id_and_path(self):
        self.man['entries'].append(copy.deepcopy(self.man['entries'][0]));self.write('管理档案/books.json',self.man)
        with self.assertRaisesRegex(ValueError,'duplicate document ID'):self.reader(2)
        self.man['entries'][1]['internal_id']='SOL-A-002';self.write('管理档案/books.json',self.man)
        with self.assertRaisesRegex(ValueError,'duplicate resolved'):self.reader(2)
    def test_wrong_h1(self):
        (self.root/'GameLibrary/A/book.md').write_text('# Other\n')
        with self.assertRaises(ValueError):self.reader()
    def test_path_escape_and_noncanonical(self):
        for path in ['../outside.md','GameLibrary/../roles/a.md','roles/one.md']:
            self.man['entries'][0].update(canonical_reader_path=path,current_read_path=path);self.write('管理档案/books.json',self.man)
            with self.assertRaises(ValueError):self.reader()
    def test_external_symlink(self):
        with tempfile.TemporaryDirectory() as external:
            p=Path(external)/'book.md';p.write_text('# Readable\n')
            target=self.root/'GameLibrary/A/book.md';target.unlink();target.symlink_to(p)
            with self.assertRaisesRegex(ValueError,'escapes'):self.reader()
    def test_graph_legacy_id_missing(self):
        self.tax['disciplines']=[n for n in self.tax['disciplines'] if n['id']!='PROG']
        with self.assertRaises(ValueError):validate(self.tax)
    def test_graph_duplicate_missing_cycle_alias(self):
        for kind in ['duplicate','missing','cycle','alias','single']:
            t=copy.deepcopy(self.tax); access=next(n for n in t['disciplines'] if n['id']=='ACCESS')
            if kind=='duplicate':t['disciplines'].append({'id':'GFX'})
            if kind=='missing':access['split_into']=['A11Y','ABSENT']
            if kind=='cycle':next(n for n in t['disciplines'] if n['id']=='A11Y')['split_into']=['ACCESS','LOC']
            if kind=='alias':access['alias_of']='A11Y'
            if kind=='single':access['split_into']=['A11Y']
            with self.subTest(kind=kind),self.assertRaises(ValueError):validate(t)
    def test_legacy_unknown_discipline(self):
        self.legacy();p=self.root/'roles/one.md';p.write_text(p.read_text().replace('GFX','NOTREAL'))
        with self.assertRaises(ValueError):check(self.root,'管理档案/规范/tax.json','legacy',1)
    def test_cli_other_working_directory_and_missing_argument(self):
        tool=Path(__file__).with_name('check_taxonomy.py').resolve()
        with tempfile.TemporaryDirectory() as other:
            cmd=[sys.executable,'-B',str(tool),'--root',str(self.root),'--taxonomy','管理档案/规范/tax.json','--mode','reader','--expected-count','1','--manifest','管理档案/books.json']
            result=subprocess.run(cmd,cwd=other,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr+result.stdout)
            self.assertEqual(json.loads(result.stdout)['documents_checked'],1)
            result=subprocess.run([sys.executable,'-B',str(tool)],cwd=other,capture_output=True,text=True)
            self.assertEqual(result.returncode,2)
    def test_required_reader_manifest(self):
        with self.assertRaises(ValueError):check(self.root,'管理档案/规范/tax.json','reader',1)
    def test_duplicate_json_key(self):
        (self.root/'管理档案/books.json').write_text('{"entries":[],"entries":[]}')
        with self.assertRaises(ValueError):self.reader()

if __name__=='__main__':unittest.main(verbosity=2)
