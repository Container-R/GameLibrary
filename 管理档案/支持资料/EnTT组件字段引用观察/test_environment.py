"""Temporary directories and mocked launch only; no child or real signal."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import runner
import isolation

class EnvironmentTests(unittest.TestCase):
    def test_five_exist_at_launch_and_phase_root_removed(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); record={'processes':[]}; proc=Mock(pid=123); proc.wait.return_value=0
            def launch(*args, **kw):
                self.assertEqual(set(kw['env']),set(isolation.KEYS)|{'PATH','LANG','LC_ALL'})
                for key in isolation.KEYS:
                    self.assertTrue(Path(kw['env'][key]).is_dir())
                    self.assertEqual(Path(kw['env'][key]),root/'environment-native'/key)
                return proc
            with patch.object(runner.subprocess,'Popen',side_effect=launch), patch.object(runner.os,'killpg'):
                runner.process(['synthetic'],root,'native',10,record)
            self.assertFalse((root/'environment-native').exists())
            self.assertNotIn(str(root),str(record))

    def reject_mutation(self, mutation):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); record={'processes':[]}; original=runner.prepare_environment
            def prepare(env, owned):
                env, mapping=original(env,owned); mutation(env,owned); return env,mapping
            with patch.object(runner,'prepare_environment',side_effect=prepare), patch.object(runner.subprocess,'Popen') as launch:
                with self.assertRaises(ValueError): runner.process(['synthetic'],root,'native',10,record)
                launch.assert_not_called()
            self.assertFalse((root/'environment-native').exists())
    def test_redirect_rejected_before_launch(self):
        self.reject_mutation(lambda env,root: env.update(HOME=str(root/'elsewhere')))
    def test_missing_directory_rejected_before_launch(self):
        self.reject_mutation(lambda env,root: (root/'HOME').rmdir())
    def test_symlink_rejected_before_launch(self):
        def mutate(env,root):
            (root/'HOME').rmdir(); (root/'HOME').symlink_to(root/'TMPDIR',target_is_directory=True)
        self.reject_mutation(mutate)
    def test_partial_preparation_failure_cleans_owned_root(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); record={'processes':[]}
            def fail(env,owned):
                (owned/'HOME').mkdir(); raise ValueError('synthetic first error')
            with patch.object(runner,'prepare_environment',side_effect=fail), patch.object(runner.subprocess,'Popen') as launch:
                with self.assertRaisesRegex(ValueError,'synthetic first error'): runner.process(['synthetic'],root,'native',10,record)
                launch.assert_not_called()
            self.assertFalse((root/'environment-native').exists())
    def test_cleanup_failure_preserves_preparation_error(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); record={'processes':[]}
            with patch.object(runner,'prepare_environment',side_effect=ValueError('first error')), patch.object(runner.shutil,'rmtree',side_effect=OSError('cleanup')), patch.object(runner.subprocess,'Popen') as launch:
                with self.assertRaisesRegex(ValueError,'first error'): runner.process(['synthetic'],root,'native',10,record)
                launch.assert_not_called()
            self.assertEqual(record['processes'][0]['environment_cleanup'],'FAILED')
    def test_existing_root_not_owned_or_removed(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); phase=root/'environment-native'; phase.mkdir(); (phase/'keep').write_text('synthetic')
            with patch.object(runner.subprocess,'Popen') as launch:
                with self.assertRaises(FileExistsError): runner.process(['synthetic'],root,'native',10,{'processes':[]})
                launch.assert_not_called()
            self.assertTrue((phase/'keep').exists())
    def test_process_cleanup_failure_retains_environment(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); proc=Mock(pid=123); proc.wait.return_value=7; record={'processes':[]}
            with patch.object(runner.subprocess,'Popen',return_value=proc),patch.object(runner.os,'killpg',side_effect=PermissionError()):
                with self.assertRaisesRegex(runner.Stop,'native_return'): runner.process(['synthetic'],root,'native',10,record)
            self.assertTrue((root/'environment-native'/'HOME').is_dir())
            self.assertEqual(record['processes'][0]['environment_cleanup'],'RETAINED_PROCESS_CLEANUP_UNCONFIRMED')

if __name__=='__main__': unittest.main()
