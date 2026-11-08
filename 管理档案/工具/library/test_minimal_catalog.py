"""Schema 3 inventory regression checks; no editorial certification."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from check_reader_counts import check as counts
from check_reader_routes import check as routes
from check_reader_links import check as links

class MinimalCatalog(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.path='GameLibrary/F/A/S/book.md';p=self.root/self.path;p.parent.mkdir(parents=True);p.write_text('# Book\n')
  p.with_name('README.md').write_text('[Book](book.md)\n')
  (self.root/'管理档案').mkdir()
  self.entry={'internal_id':'ID-1','reader_title':'Book','canonical_reader_path':self.path,'reader_body_status':'published','reader_sha256':'unused-by-these-checks'}
  self.data={'schema_version':3,'entries':[self.entry]};self.save()
 def save(self):
  (self.root/'管理档案/图书目录.json').write_text(json.dumps(self.data))
 def test_minimal_without_state_or_redundant_counts(self):
  result=counts(self.root);self.assertEqual(result['canonical_paths'],1);self.assertIn('legacy count/state checks not applicable',result['scope'])
  self.assertEqual(routes(self.root,1,['ID-1'])['errors'],[])
  self.assertEqual(links(self.root,'管理档案/图书目录.json',1)['status'],'pass')
 def test_missing_canonical(self):
  del self.entry['canonical_reader_path'];self.save()
  with self.assertRaises(ValueError):counts(self.root)
 def test_duplicate(self):
  self.data['entries'].append(copy.deepcopy(self.entry));self.save()
  with self.assertRaises(ValueError):counts(self.root)
 def test_unregistered_body(self):
  (self.root/self.path).with_name('extra.md').write_text('# Extra')
  with self.assertRaises(ValueError):counts(self.root)
 def test_missing_body(self):
  (self.root/self.path).unlink()
  with self.assertRaises(ValueError):counts(self.root)
 def test_invalid_paths(self):
  for value in ['../outside.md','/absolute.md','GameLibrary/F/A/S/../book.md','GameLibrary/F/A/S/README.md','GameLibrary\\bad.md',None]:
   with self.subTest(path=value):
    self.entry['canonical_reader_path']=value;self.save()
    with self.assertRaises(ValueError):counts(self.root)
 def test_empty_catalog(self):
  self.data['entries']=[];self.save()
  with self.assertRaises(ValueError):counts(self.root)
 def test_alias_conflict(self):
  self.entry['current_read_path']='GameLibrary/F/A/S/other.md';self.save()
  with self.assertRaises(ValueError):counts(self.root)
  with self.assertRaises(ValueError):links(self.root,'管理档案/图书目录.json',1)
  self.assertTrue(routes(self.root,1,['ID-1'])['errors'])
 def test_derived_shelf_not_legacy_override(self):
  self.entry['shelf']='Wrong';self.save()
  self.assertTrue(routes(self.root,1,['ID-1'])['errors'])
 def test_missing_shelf_link(self):
  (self.root/self.path).with_name('README.md').write_text('# Shelf')
  self.assertTrue(routes(self.root,1,['ID-1'])['errors'])
 def test_legacy_path_alias_for_links_and_routes(self):
  self.entry['current_read_path']=self.entry.pop('canonical_reader_path');self.save()
  self.assertEqual(routes(self.root,1,['ID-1'])['errors'],[])
  self.assertEqual(links(self.root,'管理档案/图书目录.json',1)['status'],'pass')
