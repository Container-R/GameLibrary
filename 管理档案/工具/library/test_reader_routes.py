import json
from pathlib import Path
import tempfile
import unittest
from check_reader_routes import check, strict_json

class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.shelf=self.root/'GameLibrary/F/A/S';self.shelf.mkdir(parents=True);(self.shelf/'book.md').write_text('# Book\n');(self.shelf/'README.md').write_text('[Book](book.md)')
  (self.root/'管理档案').mkdir();self.entry={'internal_id':'ID1','floor':'F','area':'A','shelf':'S','reader_title':'Book','current_read_path':'GameLibrary/F/A/S/book.md','canonical_reader_path':'GameLibrary/F/A/S/book.md'}
  self.entries=[self.entry];self.save()
 def save(self): (self.root/'管理档案/图书目录.json').write_text(json.dumps({'entries':self.entries}))
 def call(self):self.save();return check(self.root,1,['ID1'])
 def test_duplicate_json_key(self):
  with self.assertRaises(ValueError):strict_json('{"entries":[],"entries":[]}')
 def test_nondict_manifest(self):
  (self.root/'管理档案/图书目录.json').write_text('[]')
  with self.assertRaises(ValueError):check(self.root,1,['ID1'])
 def test_valid(self):self.assertEqual(self.call()['errors'],[])
 def test_empty(self):
  self.entries=[]
  with self.assertRaises(ValueError):self.call()
 def test_missing_count(self):
  with self.assertRaises(ValueError):check(self.root,2,['ID1','ID2'])
 def test_duplicate(self):
  self.entries=[self.entry,self.entry];self.save()
  with self.assertRaises(ValueError):check(self.root,2,['ID1','ID2'])
 def test_wrong_id(self):
  self.entry['internal_id']='different'
  with self.assertRaises(ValueError):self.call()
 def test_bad_frozen(self):
  for n,ids in [(0,[]),(-1,[]),(2,['ID1','ID1']),(1,[])]:
   with self.assertRaises(ValueError):check(self.root,n,ids)
 def test_escape(self):
  self.entry['current_read_path']=self.entry['canonical_reader_path']='GameLibrary/../../outside.md';self.assertTrue(self.call()['errors'])
 def test_symlink_escape(self):
  with tempfile.TemporaryDirectory() as o:
   p=Path(o)/'book.md';p.write_text('# Book\n');(self.shelf/'book.md').unlink();(self.shelf/'book.md').symlink_to(p);self.assertTrue(self.call()['errors'])
 def test_bad_h1(self):(self.shelf/'book.md').write_text('# Other\n');self.assertTrue(self.call()['errors'])
 def test_missing_target(self):(self.shelf/'book.md').unlink();self.assertTrue(self.call()['errors'])
 def test_missing_shelf_entry(self):(self.shelf/'README.md').write_text('none');self.assertTrue(self.call()['errors'])
 def test_shelf_escape(self):(self.shelf/'README.md').write_text('[bad](../../../../../../outside)');self.assertTrue(self.call()['errors'])

if __name__=='__main__':unittest.main()
