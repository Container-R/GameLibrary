"""Reviewer-only temporary fixtures; no candidate or stage mutation."""
import contextlib,io,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from check_reader_counts import check, main

class Independent(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.r=Path(self.t.name)
  for p in ['GameLibrary/S','管理档案','.agent']:(self.r/p).mkdir(parents=True)
  for p in ['a.md','b.md']:(self.r/'GameLibrary/S'/p).write_text('# body')
  self.c={'entries':[{'canonical_reader_path':'GameLibrary/S/'+p} for p in ['a.md','b.md']], 'reader_books_total':2,'post_baseline_research_books':1,'rewritten_reader_books':1,'accounted_for_original_items':1}
  self.s={'reader_baseline':{'reader_books_total':2,'rewritten_reader_books':1,'accounted_for_original_items':1},'publication':{'reader_books_total':2,'post_baseline_research_books':1}}
  self.save()
 def save(self):
  (self.r/'管理档案/图书目录.json').write_text(json.dumps(self.c));(self.r/'.agent/state.json').write_text(json.dumps(self.s))
 def test_self_consistent_wrong_frozen_is_not_authority(self):
  for d in [self.c,self.s['reader_baseline']]:d['rewritten_reader_books']=2;d['accounted_for_original_items']=2
  self.c['post_baseline_research_books']=0;self.s['publication']['post_baseline_research_books']=0;self.save()
  with self.assertRaises(ValueError):check(self.r,1)
 def test_catalog_missing(self):
  (self.r/'管理档案/图书目录.json').unlink()
  with self.assertRaises(OSError):check(self.r,1)
 def test_metadata_symlink(self):
  p=self.r/'.agent/state.json';p.rename(self.r/'state-copy.json');p.symlink_to('../state-copy.json')
  with self.assertRaises(ValueError):check(self.r,1)
 def test_unreadable_traversal_fail_closed(self):
  def walk(*args,**kwargs):kwargs['onerror'](PermissionError('synthetic'));return iter([])
  with patch('check_reader_counts.os.walk',side_effect=walk),self.assertRaises(OSError):check(self.r,1)
 def test_cwd_independent_explicit_root(self):
  old=Path.cwd()
  try:
   os.chdir(self.r/'GameLibrary/S');self.assertEqual(check(self.r,1)['canonical_paths'],2)
  finally:os.chdir(old)
 def test_missing_required_cli(self):
  for args in [[],['--root',str(self.r)],['--frozen-count','1']]:
   with patch('sys.argv',['checker']+args),contextlib.redirect_stderr(io.StringIO()),contextlib.redirect_stdout(io.StringIO()),self.assertRaises(SystemExit) as e:main()
   self.assertEqual(e.exception.code,2)
 def test_nested_duplicate_key(self):
  p=self.r/'.agent/state.json';p.write_text(p.read_text().replace('"reader_books_total": 2','"reader_books_total": 2, "reader_books_total": 2',1))
  with self.assertRaises(ValueError):check(self.r,1)
 def test_same_count_coordinated_replacement_is_declared_boundary(self):
  # Exact current inventory, but not golden historical identity preservation.
  (self.r/'GameLibrary/S/b.md').rename(self.r/'GameLibrary/S/c.md');self.c['entries'][1]['canonical_reader_path']='GameLibrary/S/c.md';self.save()
  self.assertEqual(check(self.r,1)['status'],'pass')

if __name__=='__main__':unittest.main()
