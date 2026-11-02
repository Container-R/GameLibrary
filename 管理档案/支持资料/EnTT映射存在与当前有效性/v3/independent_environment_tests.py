"""Independent pure filesystem/mock challenges: no real Popen or signals."""
import tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
import runner,isolation

class Independent(unittest.TestCase):
 def test_each_key_each_phase_tampering(self):
  for phase in ['build','native']:
   for key in isolation.KEYS:
    for mutation in ['deletekey','redirect','rmdir','symlink']:
     with self.subTest(phase=phase,key=key,mutation=mutation),tempfile.TemporaryDirectory() as d:
      root=Path(d);real=runner.prepare_environment;record={'processes':[]}
      def prepare(env,owned):
       e,m=real(env,owned)
       if mutation=='deletekey':del e[key]
       elif mutation=='redirect':e[key]='relative'
       elif mutation=='rmdir':(owned/key).rmdir()
       else:(owned/key).rmdir();(owned/key).symlink_to(owned/'unrelated')
       return e,m
      with patch.object(runner,'prepare_environment',side_effect=prepare),patch.object(runner.subprocess,'Popen') as launch,patch.object(runner.os,'killpg') as kill:
       with self.assertRaises(ValueError):runner.process(['synthetic'],root,phase,10,record)
       launch.assert_not_called();kill.assert_not_called()
      self.assertFalse((root/('environment-'+phase)).exists())
 def test_both_phase_actual_launch_arguments(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);seen=[]
   def launch(*a,**kw):
    env=kw['env'];seen.append(env)
    for key in isolation.KEYS:self.assertTrue(Path(env[key]).is_absolute());self.assertTrue(Path(env[key]).is_dir())
    self.assertEqual(set(env),set(isolation.KEYS)|{'PATH','LANG','LC_ALL'})
    p=Mock();p.wait.return_value=0;return p
   with patch.object(runner.subprocess,'Popen',side_effect=launch),patch.object(runner.os,'killpg',side_effect=ProcessLookupError()):
    for phase in ['build','native']:runner.process(['synthetic'],root,phase,10,{'processes':[]})
   self.assertTrue(all(seen[0][k]!=seen[1][k] for k in isolation.KEYS))
 def test_success_cleanup_failure_rejects(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);p=Mock();p.wait.return_value=0;record={'processes':[]}
   with patch.object(runner.subprocess,'Popen',return_value=p),patch.object(runner.os,'killpg',side_effect=ProcessLookupError()),patch.object(runner.shutil,'rmtree',side_effect=OSError('synthetic')):
    with self.assertRaisesRegex(runner.Stop,'build_environment_cleanup'):runner.process(['synthetic'],root,'build',10,record)
   self.assertEqual(record['processes'][0]['environment_cleanup'],'FAILED')
 def test_launch_failure_keeps_first_error(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);record={'processes':[]}
   with patch.object(runner.subprocess,'Popen',side_effect=OSError('launch-first')),patch.object(runner.os,'killpg') as kill,patch.object(runner.shutil,'rmtree',side_effect=OSError('second')):
    with self.assertRaisesRegex(OSError,'launch-first'):runner.process(['synthetic'],root,'native',10,record)
    kill.assert_not_called()
   self.assertEqual(record['processes'][0]['environment_cleanup'],'FAILED')
 def test_preexisting_symlink_not_deleted(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);other=root/'other';other.mkdir();(other/'keep').write_text('synthetic');link=root/'environment-build';link.symlink_to(other,target_is_directory=True)
   with patch.object(runner.subprocess,'Popen') as launch,patch.object(runner.shutil,'rmtree') as delete:
    with self.assertRaises(FileExistsError):runner.process(['synthetic'],root,'build',10,{'processes':[]})
    launch.assert_not_called();delete.assert_not_called()
   self.assertTrue(link.is_symlink());self.assertEqual((other/'keep').read_text(),'synthetic')
if __name__=='__main__':unittest.main()
