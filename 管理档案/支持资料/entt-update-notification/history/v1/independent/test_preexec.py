"""Pure synthetic/mocked review only; no compiler, native process, or real signal."""
import importlib.util,json,hashlib,tempfile,unittest,shutil,sys
from pathlib import Path
from unittest.mock import patch,MagicMock
BASE=Path(__file__).resolve().parents[1]
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
c=load('review_checker',BASE/'checker.py');r=load('review_runner',BASE/'runner.py')
ROWS=[dict(case=0,initial=3,value=1,callbacks=0,seen=[],cache=3,valid=True,has_speed=True,connected_initial=True),dict(case=1,initial=3,value=1,callbacks=1,seen=[1],cache=1,valid=True,has_speed=True,connected_initial=True),dict(case=2,initial=3,value=3,callbacks=1,seen=[3],cache=3,valid=True,has_speed=True,connected_initial=True)]
def wire(rows):return ('\n'.join(json.dumps(x) for x in rows)+'\n').encode()
class Review(unittest.TestCase):
 def test_literal_and_rejections(self):
  self.assertTrue(c.validate(wire(ROWS),b'',BASE/'expected.json')['match'])
  bad=[]
  for key,value in [('case',False),('initial',3.0),('valid',1),('callbacks',True)]:
   rows=json.loads(json.dumps(ROWS));rows[0][key]=value;bad.append(wire(rows))
  bad += [wire(ROWS[:2]),wire(ROWS+[ROWS[0]]),wire(ROWS).replace(b'"initial": 3',b'"initial": 3, "initial": 3',1),wire(ROWS).replace(b'"initial": 3',b'"initial": NaN',1)]
  for data in bad:
   with self.subTest(data=data),self.assertRaises(ValueError):c.validate(data,b'',BASE/'expected.json')
  with self.assertRaises(ValueError):c.validate(wire(ROWS),b'warning',BASE/'expected.json')
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'expected.json';p.write_bytes((BASE/'expected.json').read_bytes()+b' ')
   with self.assertRaisesRegex(ValueError,'oracle identity'):c.validate(wire(ROWS),b'',p)
 def test_launch_failure(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);env=r.environment(root,'build');receipt={'processes':[]}
   with patch.object(r.subprocess,'Popen',side_effect=OSError('synthetic')),patch.object(r.os,'killpg') as kill:
    with self.assertRaises(OSError):r.command(['fake'],1,root,env,'build',receipt)
    kill.assert_not_called();self.assertEqual(receipt['processes'][0]['status'],'failed')
 def test_cleanup_and_log_failure(self):
  for failure in ['cleanup','write']:
   with self.subTest(failure=failure),tempfile.TemporaryDirectory() as t:
    root=Path(t);env=r.environment(root,'native');receipt={'processes':[]};child=MagicMock();child.pid=123;child.returncode=0;child.communicate.return_value=(wire(ROWS),b'')
    with patch.object(r.subprocess,'Popen',return_value=child),patch.object(r,'stop_group',return_value=['PermissionError'] if failure=='cleanup' else []):
     if failure=='write':
      with patch.object(Path,'write_bytes',side_effect=OSError('synthetic')):
       with self.assertRaises(OSError):r.command(['fake'],1,root,env,'native',receipt)
     else:
      with self.assertRaises(RuntimeError):r.command(['fake'],1,root,env,'native',receipt)
 def test_group_liveness_gap(self):
  child=MagicMock();child.pid=123;child.wait.return_value=0
  with patch.object(r.os,'killpg') as kill:
   self.assertEqual(r.stop_group(child),[])
   self.assertNotIn(0,[call.args[1] for call in kill.call_args_list])
 def setup_copy(self,t):
  base=Path(t)/'inputs';base.mkdir();(base/'source').mkdir()
  for p in (*r.FILES,'source/entt.hpp','INPUT-MANIFEST.json'):shutil.copyfile(BASE/p,base/p)
  return base,Path(t)/'attempt'
 def test_manifest_change_not_detected(self):
  with tempfile.TemporaryDirectory() as t:
   base,root=self.setup_copy(t)
   def command(argv,timeout,root,env,label,receipt):
    if label=='build':(base/'INPUT-MANIFEST.json').write_text('{}')
    return (b'',b'') if label=='build' else (wire(ROWS),b'')
   with patch.object(r,'BASE',base),patch.object(r,'HEADER',base/'source/entt.hpp'),patch.object(r,'command',side_effect=command),patch.object(r.shutil,'which',return_value='synthetic'),patch.object(sys,'argv',['runner.py',str(root)]):r.main()
   self.assertEqual(json.loads((root/'receipt.json').read_text())['status'],'pass')
 def test_copied_checker_runs_before_tamper_rejection(self):
  with tempfile.TemporaryDirectory() as t:
   base,root=self.setup_copy(t);marker=root/'synthetic-import-marker'
   def command(argv,timeout,root,env,label,receipt):
    if label=='native':
     with (root/'checker.py').open('a') as f:f.write('\nPath(__file__).with_name("synthetic-import-marker").write_text("synthetic only")\n')
    return (b'',b'') if label=='build' else (wire(ROWS),b'')
   with patch.object(r,'BASE',base),patch.object(r,'HEADER',base/'source/entt.hpp'),patch.object(r,'command',side_effect=command),patch.object(r.shutil,'which',return_value='synthetic'),patch.object(sys,'argv',['runner.py',str(root)]):
    with self.assertRaisesRegex(ValueError,'copied input changed'):r.main()
   self.assertTrue(marker.exists());self.assertEqual(json.loads((root/'receipt.json').read_text())['status'],'failed')
 def test_receipt_write_no_canonical_pass(self):
  with tempfile.TemporaryDirectory() as t:
   base,root=self.setup_copy(t)
   def command(argv,timeout,root,env,label,receipt):return (b'',b'') if label=='build' else (wire(ROWS),b'')
   original=Path.open
   def open_(p,*a,**kw):
    if p.name=='receipt.pending.json':raise OSError('synthetic receipt write')
    return original(p,*a,**kw)
   with patch.object(r,'BASE',base),patch.object(r,'HEADER',base/'source/entt.hpp'),patch.object(r,'command',side_effect=command),patch.object(r.shutil,'which',return_value='synthetic'),patch.object(sys,'argv',['runner.py',str(root)]),patch.object(Path,'open',open_):
    with self.assertRaises(OSError):r.main()
   self.assertFalse((root/'receipt.json').exists())
if __name__=='__main__':unittest.main()
