import copy,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
from build_routes import Invalid, reader_documents, render

class ReaderTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  (self.root/'GameLibrary').mkdir();(self.root/'管理档案/草稿').mkdir(parents=True)
  self.man='管理档案/books.json';self.entries=[]
  for id,name in [('ROLE-A-001','Role'),('SOL-A-001','Book')]:
   path='GameLibrary/'+name+'.md';(self.root/path).write_text('# '+name+'\nNo YAML\n')
   self.entries.append(dict(internal_id=id,reader_title=name,current_read_path=path,canonical_reader_path=path))
  self.save()
  self.reg={'schema_version':1,'routes':[dict(id='role-a',title='Role',kind='role',subject_profile_id='ROLE-A-001',entries=[dict(document_id='SOL-A-001',question='Q',rationale='R')])]}
  self.registry=self.root/'registry.json';self.registry.write_text(json.dumps(self.reg))
  self.output=self.root/'管理档案/草稿/draft.md';self.tool=Path(__file__).with_name('build_routes.py').resolve()
 def save(self): (self.root/self.man).write_text(json.dumps({'entries':self.entries}))
 def render(self,**kw):return render(self.root,self.reg,self.output,reader_manifest=self.man,expected_count=kw.pop('expected_count',2),**kw)
 def cli(self,*args):return subprocess.run([sys.executable,'-B',*(['-O'] if sys.flags.optimize else []),str(self.tool),str(self.root),'--registry',str(self.registry),'--output',str(self.output),*map(str,args)],capture_output=True,text=True,cwd=self.root)
 def test_nonempty_no_yaml(self):
  text=self.render();self.assertIn('GameLibrary/Book.md',text);self.assertNotIn('source-backed',text)
 def test_empty(self):
  self.entries=[];self.save()
  with self.assertRaises(Invalid):self.render()
 def test_missing_manifest(self):
  (self.root/self.man).unlink()
  with self.assertRaises(OSError):self.render()
 def test_missing_reader(self):
  (self.root/'GameLibrary/Book.md').unlink()
  with self.assertRaises(OSError):self.render()
 def test_count(self):
  for count in (None,0,-1,1,3,True):
   with self.subTest(count=count),self.assertRaises(Invalid):self.render(expected_count=count)
 def test_duplicate_id_path(self):
  baseline=copy.deepcopy(self.entries)
  for key in ('internal_id','path'):
   self.entries=copy.deepcopy(baseline)
   if key=='internal_id':self.entries[1][key]=self.entries[0][key]
   else:
    for k in ('current_read_path','canonical_reader_path','reader_title'):self.entries[1][k]=self.entries[0][k]
   self.save()
   with self.assertRaises(Invalid):self.render()
 def test_id_and_h1(self):
  self.entries[0]['internal_id']='bad';self.save()
  with self.assertRaises(Invalid):self.render()
  self.entries[0]['internal_id']='ROLE-A-001';self.save();(self.root/'GameLibrary/Role.md').write_text('# Wrong')
  with self.assertRaises(Invalid):self.render()
 def test_path_policy(self):
  for p in ('../x.md','GameLibrary/../x.md','/tmp/x.md','GameLibrary//x.md','GameLibrary/x\\a.md'):
   self.entries[0].update(current_read_path=p,canonical_reader_path=p);self.save()
   with self.subTest(path=p),self.assertRaises(Invalid):self.render()
 def test_current_canonical_mismatch(self):
  self.entries[0]['canonical_reader_path']='GameLibrary/other.md';self.save()
  with self.assertRaises(Invalid):self.render()
 def test_symlink_outside(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'book.md';p.write_text('# Book\n');t=self.root/'GameLibrary/Book.md';t.unlink();t.symlink_to(p)
   with self.assertRaises(Invalid):self.render()
 def test_unresolved_route(self):
  self.reg['routes'][0]['entries'][0]['document_id']='CASE-X-001'
  with self.assertRaises(Invalid):self.render()
 def test_mode_selection(self):
  for args in ([],['--source-dir','old','--reader-manifest',self.man],['--reader-manifest',self.man]):
   self.assertNotEqual(self.cli(*args).returncode,0)
  with self.assertRaises(Invalid):self.render(source_dirs=['old'])
 def test_manifest_as_output(self):
  target=self.root/'管理档案/草稿/input.md';target.write_bytes((self.root/self.man).read_bytes());self.man=target.relative_to(self.root).as_posix();self.output=target;before=target.read_bytes()
  result=self.cli('--reader-manifest',self.man,'--expected-count',2)
  self.assertNotEqual(result.returncode,0);self.assertEqual(target.read_bytes(),before)
 def test_registry_as_output(self):
  self.registry=self.output;self.registry.write_text(json.dumps(self.reg));before=self.registry.read_bytes()
  self.assertNotEqual(self.cli('--reader-manifest',self.man,'--expected-count',2).returncode,0);self.assertEqual(self.registry.read_bytes(),before)
 def test_protected_output_and_hardlink(self):
  for name in ('README.md','DISCOVERY.md','CATALOG.md','GameLibrary/Book.md','管理档案/books.json'):
   with self.subTest(name=name),self.assertRaises(Invalid):render(self.root,self.reg,self.root/name,reader_manifest=self.man,expected_count=2)
  self.output.hardlink_to(self.root/'GameLibrary/Book.md')
  with self.assertRaises(Invalid):self.render()
 def test_cli_relocated(self):
  moved=self.root/'tools/deeper/check.py';moved.parent.mkdir(parents=True);shutil.copyfile(self.tool,moved);self.tool=moved
  result=self.cli('--reader-manifest',self.man,'--expected-count',2);self.assertEqual(result.returncode,0,result.stderr)
  result=self.cli('--reader-manifest',self.man,'--expected-count',2,'--check');self.assertEqual(result.returncode,0,result.stderr)
 def test_manifest_duplicate_json_and_absolute(self):
  (self.root/self.man).write_text('{"entries":[],"entries":[]}')
  with self.assertRaises(Invalid):self.render()
  self.save();self.man=str(self.root/self.man)
  with self.assertRaises(Invalid):self.render()

if __name__=='__main__':unittest.main(verbosity=2)
