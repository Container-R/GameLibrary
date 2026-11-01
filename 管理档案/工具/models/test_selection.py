from pathlib import Path
import json,subprocess,sys,tempfile,unittest
from run_model_tests import select, execute, positive_timeout
from unittest.mock import patch
import argparse
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.folder=self.root/'管理档案/研究记录/experiments/m';self.folder.mkdir(parents=True);(self.folder/'test_x.py').write_text('raise RuntimeError("must not run in list mode")\n');self.directory='管理档案/研究记录/experiments'
 def test_invalid_timeout(self):
  for value in ('0','-1','nan','inf'):
   with self.assertRaises(argparse.ArgumentTypeError):positive_timeout(value)
 def test_timeout_recorded_without_running_model(self):
  with patch('run_model_tests.subprocess.run',side_effect=subprocess.TimeoutExpired('synthetic',1)):
   r=execute(self.root,[self.folder/'test_x.py'],1)
  self.assertEqual(r[0]['reason'],'timeout')
 def test_nonzero_retained_without_running_model(self):
  with patch('run_model_tests.subprocess.run',return_value=subprocess.CompletedProcess('synthetic',7)) as run:
   r=execute(self.root,[self.folder/'test_x.py'],1)
   self.assertEqual('-O' in run.call_args.args[0],bool(sys.flags.optimize))
  self.assertEqual(r[0]['exit_code'],7)
 def test_good(self):self.assertEqual(len(select(self.root,self.directory,['m/test_x.py'])),1)
 def test_empty(self):
  with self.assertRaises(ValueError):select(self.root,self.directory,[])
 def test_mismatch(self):
  with self.assertRaises(ValueError):select(self.root,self.directory,['m/test_other.py'])
 def test_missing(self):
  with self.assertRaises(ValueError):select(self.root,'research/experiments',['m/test_x.py'])
 def test_duplicate(self):
  with self.assertRaises(ValueError):select(self.root,self.directory,['m/test_x.py','m/test_x.py'])
 def test_escape(self):
  with self.assertRaises(ValueError):select(self.root,'../out',['m/test_x.py'])
 def test_cli_lists_without_execution_different_cwd(self):
  ids=self.root/'suites.json';ids.write_text('["m/test_x.py"]');script=Path(__file__).with_name('run_model_tests.py').resolve()
  cmd=[sys.executable]+(['-O'] if sys.flags.optimize else [])+[str(script),'--root',str(self.root),'--models-dir',self.directory,'--expected-suites',str(ids)]
  r=subprocess.run(cmd,cwd=self.folder,capture_output=True,text=True);self.assertEqual(r.returncode,0);self.assertEqual(json.loads(r.stdout)['status'],'selected_not_executed')
if __name__=='__main__':unittest.main()
