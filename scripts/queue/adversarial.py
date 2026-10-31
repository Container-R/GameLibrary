import copy,json,unittest,tempfile
from pathlib import Path
from test_queue import QueueTests
from validate_queue import validate,Invalid,read
class Added(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.r=Path(self.t.name)
  self.tax={'disciplines':[{'id':'GFX'}]};self.q={'tasks':[{'id':'T','discipline':'GFX','status':'published','artifact_paths':['file']}]};(self.r/'file').write_text('x')
 def test_taxonomy_duplicate_or_invalid(self):
  for nodes in [[{'id':'GFX'},{'id':'GFX'}],[{'id':True}],[{'id':''}],[None]]:
   with self.subTest(nodes=nodes),self.assertRaises(Invalid):validate({'disciplines':nodes},self.q,self.r)
 def test_core_types(self):
  for field,val in [('id',True),('id',' '),('discipline',None),('discipline',1),('discipline','RENDER')]:
   q=copy.deepcopy(self.q);q['tasks'][0][field]=val
   with self.subTest(field=field,val=val),self.assertRaises(Invalid):validate(self.tax,q,self.r)
 def test_root_symlink_and_inside_link(self):
  (self.r/'inside').symlink_to(self.r/'file');self.q['tasks'][0]['artifact_paths']=['inside']
  self.assertEqual(validate(self.tax,self.q,self.r)['artifact_paths_checked'],1)
  with tempfile.TemporaryDirectory() as d:
   alias=Path(d)/'root';alias.symlink_to(self.r,target_is_directory=True)
   self.assertEqual(validate(self.tax,self.q,alias)['artifact_paths_checked'],1)
 def test_dangling_escape_and_missing(self):
  with tempfile.TemporaryDirectory() as d:
   (self.r/'escape').symlink_to(Path(d)/'notyet');self.q['tasks'][0].update(status='planned',artifact_paths=['escape/file'])
   with self.assertRaises(Invalid):validate(self.tax,self.q,self.r)
  (self.r/'dangling').symlink_to(self.r/'absent');self.q['tasks'][0].update(status='published',artifact_paths=['dangling'])
  with self.assertRaises(Invalid):validate(self.tax,self.q,self.r)
 def test_json_duplicate_constants(self):
  p=self.r/'data.json'
  for text in ['{"tasks":[],"tasks":[]}','{"x":NaN}','{"x":Infinity}']:
   p.write_text(text)
   with self.subTest(text=text),self.assertRaises(Invalid):read(p)
 def test_control_normalization_and_directory(self):
  for path in ['file\n','a\x01b','a\x7fb','C:foo','//server/file',' a','a/./b']:
   self.q['tasks'][0]['artifact_paths']=[path]
   with self.subTest(path=path),self.assertRaises(Invalid):validate(self.tax,self.q,self.r)
  (self.r/'dir').mkdir();self.q['tasks'][0]['artifact_paths']=['dir'];validate(self.tax,self.q,self.r)
if __name__=='__main__':unittest.main(verbosity=2)
