import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from build_routes import Invalid, metadata, render as render_routes, scalar, documents

def render(root, registry, output=None):
    return render_routes(root, registry, output, source_dirs=["roles", "solutions"])

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
        out=self.root/'管理档案'/'草稿'/'旧路线候选.md'
        out.parent.mkdir(parents=True)
        cmd=[sys.executable,str(Path(__file__).with_name('build_routes.py')),str(self.root),'--registry',str(reg),'--source-dir','roles','--source-dir','solutions','--output',str(out)]
        self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,0)
        before=out.read_bytes();mtime=out.stat().st_mtime_ns
        self.assertEqual(subprocess.run(cmd+['--check'],capture_output=True).returncode,0)
        self.assertEqual(out.stat().st_mtime_ns,mtime)
        reg.write_text('{}')
        self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,2)
        self.assertEqual(out.read_bytes(),before)

    def command(self, out):
        reg=self.root/'routes.json';reg.write_text(json.dumps(self.reg))
        return [sys.executable,str(Path(__file__).with_name('build_routes.py')),str(self.root),'--registry',str(reg),'--source-dir','roles','--source-dir','solutions','--output',str(out)]

    def test_protected_roots_refused_in_write_and_check(self):
        for name in ('README.md','DISCOVERY.md','CATALOG.md'):
            out=self.root/name;out.write_text('reader entry')
            for flags in ([],['--check']):
                result=subprocess.run(self.command(out)+flags,capture_output=True)
                self.assertEqual(result.returncode,2)
                self.assertIn(b'protected reader entry',result.stderr)
                self.assertEqual(out.read_text(),'reader entry')
            # Even byte-matching generated content cannot bless a protected entry.
            out.write_text(render(self.root,self.reg))
            before=out.read_bytes()
            self.assertEqual(subprocess.run(self.command(out)+['--check'],capture_output=True).returncode,2)
            self.assertEqual(out.read_bytes(),before)

    def test_canonical_and_outside_draft_refused(self):
        for name in ('管理档案/图书目录.json','GameLibrary/README.md','preview.md','管理档案/草稿/no.json'):
            result=subprocess.run(self.command(self.root/name),capture_output=True)
            self.assertEqual(result.returncode,2)
            self.assertFalse((self.root/name).exists())

    def test_draft_relative_links_and_check_mismatch(self):
        out=self.root/'管理档案/草稿/nested/preview.md';out.parent.mkdir(parents=True)
        cmd=self.command(out)
        self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,0)
        text=out.read_text()
        self.assertIn('../../../solutions/one.md',text)
        self.assertIn('../../../GameLibrary/README.md',text)
        self.assertEqual(subprocess.run(cmd+['--check'],capture_output=True).returncode,0)
        out.write_text('stale')
        self.assertEqual(subprocess.run(cmd+['--check'],capture_output=True).returncode,1)
        self.assertEqual(out.read_text(),'stale')
        out.unlink()
        self.assertEqual(subprocess.run(cmd+['--check'],capture_output=True).returncode,1)
        self.assertFalse(out.exists())

    def test_symlink_cannot_overwrite_root(self):
        out=self.root/'管理档案/草稿/alias.md';out.parent.mkdir(parents=True)
        target=self.root/'README.md';target.write_text('reader entry');out.symlink_to(target)
        for flags in ([],['--check']):
            self.assertEqual(subprocess.run(self.command(out)+flags,capture_output=True).returncode,2)
            self.assertEqual(target.read_text(),'reader entry')

    def test_draft_directory_symlink_escape(self):
        (self.root/'管理档案').mkdir();(self.root/'管理档案/草稿').symlink_to(self.root, target_is_directory=True)
        out=self.root/'管理档案/草稿/escape.md'
        self.assertEqual(subprocess.run(self.command(out),capture_output=True).returncode,2)
        self.assertFalse((self.root/'escape.md').exists())

    def test_declared_nonempty_scanning(self):
        docs = documents(self.root, ['roles', 'solutions'])
        self.assertEqual(set(docs), {'ROLE-A-001', 'SOL-A-001'})
        self.assertEqual(len(docs), 2)

    def test_no_declaration_rejected(self):
        for folders in (None, [], (), 'roles'):
            with self.subTest(folders=folders), self.assertRaises(Invalid):
                documents(self.root, folders)
        with self.assertRaises(Invalid):
            render_routes(self.root, self.reg)

    def test_missing_declared_folder_even_when_routes_resolve(self):
        with self.assertRaisesRegex(Invalid, 'missing declared'):
            documents(self.root, ['roles', 'solutions', 'missing'])

    def test_empty_declared_folder_rejected(self):
        (self.root / 'empty').mkdir()
        with self.assertRaisesRegex(Invalid, 'no Markdown'):
            documents(self.root, ['roles', 'solutions', 'empty'])

    def test_no_documents_rejected(self):
        (self.root / 'roles/profile.md').unlink()
        (self.root / 'solutions/one.md').unlink()
        with self.assertRaisesRegex(Invalid, 'no Markdown'):
            documents(self.root, ['roles', 'solutions'])

    def test_bad_source_paths_rejected(self):
        for value in ('', '.', './roles', '../roles', '/roles', 'roles/',
                      'roles//x', 'roles/../solutions', 'C:/roles',
                      'roles\\nested', ' roles', 'roles\n'):
            with self.subTest(value=value), self.assertRaises(Invalid):
                documents(self.root, [value])
        with self.assertRaisesRegex(Invalid, 'missing declared'):
            documents(self.root, ['roles/profile.md'])

    def test_duplicate_or_nested_sources_rejected(self):
        (self.root / 'roles/nested').mkdir()
        for dirs in (['roles', 'roles'], ['roles', 'roles/nested'],
                     ['roles/nested', 'roles']):
            with self.subTest(dirs=dirs), self.assertRaisesRegex(Invalid, 'overlapping'):
                documents(self.root, dirs)

    def test_source_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as other:
            (self.root / 'escaped').symlink_to(other, target_is_directory=True)
            with self.assertRaisesRegex(Invalid, 'escapes root'):
                documents(self.root, ['escaped'])
            target = Path(other) / 'foreign.md'
            target.write_text((self.root / 'roles/profile.md').read_text())
            (self.root / 'roles/foreign.md').symlink_to(target)
            with self.assertRaisesRegex(Invalid, 'escapes root'):
                documents(self.root, ['roles'])

    def test_reader_content_is_not_legacy_input(self):
        (self.root / 'GameLibrary').mkdir()
        (self.root / 'GameLibrary/book.md').write_text('# Reader article\n')
        with self.assertRaisesRegex(Invalid, 'missing frontmatter'):
            documents(self.root, ['GameLibrary'])

    def test_relocated_inputs_and_tool_from_different_cwd(self):
        import shutil
        archive = self.root / '管理档案/历史输入'
        archive.mkdir(parents=True)
        (self.root / 'roles').rename(archive / 'profiles')
        (self.root / 'solutions').rename(archive / 'solutions')
        tool = self.root / '管理档案/工具/navigation/build_routes.py'
        tool.parent.mkdir(parents=True)
        shutil.copy2(Path(__file__).with_name('build_routes.py'), tool)
        reg = self.root / 'routes.json'; reg.write_text(json.dumps(self.reg))
        out = self.root / '管理档案/草稿/preview.md';out.parent.mkdir()
        cmd = [sys.executable, str(tool), str(self.root), '--registry', str(reg),
               '--source-dir', '管理档案/历史输入/profiles',
               '--source-dir', '管理档案/历史输入/solutions', '--output', str(out)]
        with tempfile.TemporaryDirectory() as cwd:
            self.assertEqual(subprocess.run(cmd, cwd=cwd, capture_output=True).returncode, 0)
            before = out.read_bytes()
            self.assertEqual(subprocess.run(cmd + ['--check'], cwd=cwd, capture_output=True).returncode, 0)
            self.assertIn('../%E5%8E%86%E5%8F%B2%E8%BE%93%E5%85%A5/solutions/one.md', out.read_text())
            (archive / 'solutions/one.md').unlink()
            failed = subprocess.run(cmd, cwd=cwd, capture_output=True)
            self.assertEqual(failed.returncode, 2)
            self.assertEqual(out.read_bytes(), before)

    def test_cli_requires_declared_input_and_preserves_output(self):
        out = self.root / '管理档案/草稿/preview.md';out.parent.mkdir(parents=True)
        out.write_text('keep')
        reg = self.root / 'routes.json';reg.write_text(json.dumps(self.reg))
        cmd = [sys.executable, str(Path(__file__).with_name('build_routes.py')),
               str(self.root), '--registry', str(reg), '--output', str(out)]
        self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 2)
        self.assertEqual(out.read_text(), 'keep')

    def test_output_cannot_overwrite_declared_input(self):
        folder = self.root / '管理档案/草稿/input';folder.mkdir(parents=True)
        target = folder / 'one.md'
        target.write_bytes((self.root / 'solutions/one.md').read_bytes())
        before = target.read_bytes()
        reg = self.root / 'routes.json';reg.write_text(json.dumps(self.reg))
        cmd = [sys.executable, str(Path(__file__).with_name('build_routes.py')),
               str(self.root), '--registry', str(reg), '--source-dir', 'roles',
               '--source-dir', '管理档案/草稿/input', '--output', str(target)]
        for flags in ([], ['--check']):
            result = subprocess.run(cmd + flags, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn(b'output overlaps declared source', result.stderr)
            self.assertEqual(target.read_bytes(), before)

    def test_new_output_inside_source_and_source_alias_rejected(self):
        folder = self.root / '管理档案/草稿/input';folder.mkdir(parents=True)
        (folder / 'one.md').write_bytes((self.root / 'solutions/one.md').read_bytes())
        (self.root / 'history-alias').symlink_to(folder, target_is_directory=True)
        out = folder / 'new.md'
        for source in ('管理档案/草稿/input', 'history-alias'):
            with self.assertRaisesRegex(Invalid, 'output overlaps declared source'):
                render_routes(self.root, self.reg, out, source_dirs=['roles', source])
            self.assertFalse(out.exists())

if __name__=='__main__':unittest.main(verbosity=2)
