"""Pure guard tests. No compiler, native process, install, or network invocation."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import runner

class RunnerTests(unittest.TestCase):
    def test_exact_warning_policy(self):
        raw=(runner.ROOT/'reviewed-build-stderr.txt').read_bytes()
        self.assertEqual(runner.validate_build(b'',b'',0,'empty-only',raw),'empty')
        self.assertEqual(runner.validate_build(b'',raw,0,'reviewed-exact',raw),'reviewed_exact')
        for out,err,rc,policy in ((b'',raw,0,'empty-only'),(b'',raw+b'new warning',0,'reviewed-exact'),(b'',raw[:-1],0,'reviewed-exact'),(b'x',b'',0,'empty-only'),(b'',b'',1,'empty-only')):
            with self.assertRaises(ValueError):runner.validate_build(out,err,rc,policy,raw)
    def test_candidate_tamper(self):
        with self.assertRaises(ValueError):runner.validate_build(b'',b'',0,'empty-only',b'')
    def test_seven_directories(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);env=runner.isolated_env(p)
            self.assertEqual(set(env),set(runner.DIRS)|{'PATH','LC_ALL','LANG'})
            self.assertEqual(len({env[k] for k in runner.DIRS}),7)
            self.assertEqual((p/'runtime').stat().st_mode&0o777,0o700)
            self.assertEqual(env,runner.isolated_env(p))
    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'outside').mkdir();(p/'home').symlink_to(p/'outside',target_is_directory=True)
            with self.assertRaises(ValueError):runner.isolated_env(p)
    def test_nondirectory_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'tmp').write_text('not a dir')
            with self.assertRaises(ValueError):runner.isolated_env(p)
    def test_runtime_mode_revalidated(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);runner.isolated_env(p);(p/'runtime').chmod(0o755)
            with self.assertRaises(ValueError):runner.isolated_env(p)
    def test_environment_failure_does_not_spawn(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'home').write_text('bad');r={'processes':[]}
            with patch.object(runner.subprocess,'Popen') as popen:
                with self.assertRaises(ValueError):runner.invoke(p,['./fixture'],10,'native',r)
                popen.assert_not_called()
            self.assertFalse(r['processes'][0]['attempted'])
            self.assertIsNone(r['processes'][0]['reported_calls'])
    def test_stale_copy_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(runner.subprocess,'Popen') as popen:
                with self.assertRaises(FileExistsError):runner.run_copy(Path(d),'empty-only')
                popen.assert_not_called()
    def test_manifest_guard_and_source_identity(self):
        observed=runner.identities(runner.ROOT,runner.SOURCE_ROOT)
        self.assertEqual(len([x for x in observed if x.startswith('upstream/')]),16)
    def test_no_approval_does_not_create_execution(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(runner,'ROOT',Path(d)),patch('sys.argv',['runner.py']),patch.object(runner.subprocess,'Popen') as popen:
                with self.assertRaises(ValueError):runner.main()
                popen.assert_not_called();self.assertFalse((Path(d)/'execution').exists())

    def test_first_failure_stops_repeat(self):
        with tempfile.TemporaryDirectory() as d:
            failed=({'status':'fail','stage':'build'},ValueError('unreviewed diagnostic'))
            with patch.object(runner,'ROOT',Path(d)),patch('sys.argv',['runner.py','--execute-approved']),patch.object(runner,'run_copy',return_value=failed) as run,patch('builtins.print'):
                self.assertEqual(runner.main(),1);self.assertEqual(run.call_count,1)
                summary=json.loads((Path(d)/'execution'/'summary.json').read_text())
                self.assertEqual([x['name'] for x in summary['executions']],['main'])
    def test_same_operator_two_copies(self):
        with tempfile.TemporaryDirectory() as d:
            passed=({'status':'pass','stage':'complete'},None)
            with patch.object(runner,'ROOT',Path(d)),patch('sys.argv',['runner.py','--execute-approved']),patch.object(runner,'run_copy',return_value=passed) as run,patch('builtins.print'):
                self.assertEqual(runner.main(),0)
                self.assertEqual([c.args[0].name for c in run.call_args_list],['main','repeat'])
    def test_second_failure_retains_first(self):
        with tempfile.TemporaryDirectory() as d:
            outcomes=[({'status':'pass','stage':'complete'},None),({'status':'fail','stage':'native'},ValueError('native'))]
            with patch.object(runner,'ROOT',Path(d)),patch('sys.argv',['runner.py','--execute-approved']),patch.object(runner,'run_copy',side_effect=outcomes),patch('builtins.print'):
                self.assertEqual(runner.main(),1)
                summary=json.loads((Path(d)/'execution'/'summary.json').read_text())
                self.assertEqual([x['status'] for x in summary['executions']],['pass','fail'])
    def test_mock_crash_count_unknown(self):
        class Child:
            returncode=-11
            def communicate(self,timeout):return b'',b'crash'
        with tempfile.TemporaryDirectory() as d:
            r={'processes':[]}
            with patch.object(runner.subprocess,'Popen',return_value=Child()),patch.object(runner,'cleanup_group',return_value=[]):
                with self.assertRaises(ValueError):runner.invoke(Path(d),['./fixture'],10,'native',r)
            self.assertTrue(r['processes'][0]['attempted'])
            self.assertIsNone(r['processes'][0]['reported_calls'])
            self.assertFalse(r['processes'][0]['reported_calls_validated'])
            self.assertEqual((Path(d)/'native.stderr').read_bytes(),b'crash')
    def test_mock_timeout_count_unknown(self):
        class Child:
            returncode=-9
            calls=0
            def communicate(self,timeout):
                self.calls+=1
                if self.calls==1:raise runner.subprocess.TimeoutExpired('synthetic',timeout,output=b'{',stderr=b'')
                return b'{',b''
        with tempfile.TemporaryDirectory() as d:
            r={'processes':[]}
            with patch.object(runner.subprocess,'Popen',return_value=Child()),patch.object(runner,'cleanup_group',return_value=[]):
                with self.assertRaises(runner.subprocess.TimeoutExpired):runner.invoke(Path(d),['./fixture'],10,'native',r)
            self.assertTrue(r['processes'][0]['timeout'])
            self.assertIsNone(r['processes'][0]['reported_calls'])
            self.assertEqual((Path(d)/'native.stdout').read_bytes(),b'{')
    def test_mock_explicit_failure_reports_prefix(self):
        counts={'builder':1,'nav_init':1,'query_init':1,'raycast':2,'findPath':0}
        raw=json.dumps({'status':'fail','calls':counts}).encode()
        class Child:
            returncode=1
            def communicate(self,timeout):return raw,b''
        with tempfile.TemporaryDirectory() as d:
            r={'processes':[]}
            with patch.object(runner.subprocess,'Popen',return_value=Child()),patch.object(runner,'cleanup_group',return_value=[]):
                with self.assertRaises(ValueError):runner.invoke(Path(d),['./fixture'],10,'native',r)
            self.assertEqual(r['processes'][0]['reported_calls'],counts)
            self.assertFalse(r['processes'][0]['reported_calls_validated'])

if __name__=='__main__':unittest.main(verbosity=2)
