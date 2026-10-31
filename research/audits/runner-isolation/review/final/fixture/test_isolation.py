"""Finite pure/filesystem checks plus exactly one synthetic Python child."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from isolation import KEYS, prepare_environment, validate_environment

CHILD_COUNT = 0
CHILD_RECORD = None

class IsolationTests(unittest.TestCase):
    def test_prepare_copy_and_two_roots(self):
        with tempfile.TemporaryDirectory() as tmp:
            roots=[Path(tmp)/name for name in ['a','b']]
            for root in roots: root.mkdir()
            base={k:'/inherited/outside' for k in KEYS};base.update(PATH='path-sentinel',PRIVATE_TEST_VALUE='not-for-receipt')
            original=dict(base)
            env,manifest=prepare_environment(base,roots[0]);other,_=prepare_environment(base,roots[1])
            self.assertEqual(base,original)
            self.assertEqual(env['PATH'],'path-sentinel')
            self.assertEqual(set(manifest),set(KEYS))
            self.assertNotIn('PRIVATE_TEST_VALUE',manifest)
            self.assertEqual(validate_environment(env,roots[0]),manifest)
            self.assertTrue(all(Path(env[k]).is_dir() and env[k]!=other[k] for k in KEYS))

    def test_missing_and_redirected_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); env,_=prepare_environment({},root)
            for key in KEYS:
                with self.subTest(key=key,kind='missing'):
                    bad=dict(env);del bad[key]
                    with self.assertRaises(ValueError):validate_environment(bad,root)
                with self.subTest(key=key,kind='redirect'):
                    bad=dict(env);bad[key]=str(root)
                    with self.assertRaises(ValueError):validate_environment(bad,root)

    def test_missing_directory_and_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            outer=Path(tmp);root=outer/'owned';root.mkdir();outside=outer/'outside';outside.mkdir()
            sentinel=outside/'sentinel';sentinel.write_text('untouched')
            env,_=prepare_environment({},root);target=Path(env['XDG_DATA_HOME']);target.rmdir()
            with self.assertRaises(ValueError):validate_environment(env,root)
            target.symlink_to(outside,target_is_directory=True)
            with self.assertRaises(ValueError):validate_environment(env,root)
            self.assertEqual(sentinel.read_text(),'untouched')
            self.assertEqual(sorted(p.name for p in outside.iterdir()),['sentinel'])

    def test_invalid_root_and_reserved_reuse(self):
        # Guard test cannot write to / even if production guard regresses.
        with patch.object(Path, 'mkdir', side_effect=AssertionError('root mkdir forbidden')) as mkdir:
            with self.assertRaises(ValueError):prepare_environment({},Path('/'))
            mkdir.assert_not_called()
        with tempfile.TemporaryDirectory() as tmp:
            outer=Path(tmp);root=outer/'owned';root.mkdir();alias=outer/'alias';alias.symlink_to(root,target_is_directory=True)
            for bad in [alias,outer/'missing',Path('relative-owned')]:
                with self.subTest(root=str(bad)):
                    with self.assertRaises(ValueError):prepare_environment({},bad)
            reserved=root/'XDG_DATA_HOME';reserved.mkdir()
            with self.assertRaises(ValueError):prepare_environment({},root)
            self.assertEqual([p.name for p in root.iterdir()],['XDG_DATA_HOME'])
            reserved.rmdir();env,_=prepare_environment({},root)
            with self.assertRaises(ValueError):prepare_environment({},root)
            with self.assertRaises(ValueError):validate_environment(env,alias)

    def test_one_synthetic_child(self):
        global CHILD_COUNT, CHILD_RECORD
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);env,manifest=prepare_environment(os.environ,root)
            validate_environment(env,root)
            # Literal child knows no helper implementation, reports no unrelated env.
            code="""import os,json
from pathlib import Path
keys=['HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR']
for key in keys: (Path(os.environ[key])/'child-sentinel.txt').write_text(key)
print(json.dumps({key:os.environ[key] for key in keys},sort_keys=True))
"""
            command=[sys.executable,'-I','-c',code];CHILD_COUNT+=1
            proc=subprocess.run(command,env=env,capture_output=True,text=True,timeout=5)
            CHILD_RECORD={'argv':command,'returncode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr,'selected_environment':manifest,'timeout_seconds':5}
            self.assertEqual(proc.returncode,0);self.assertEqual(proc.stderr,'')
            self.assertEqual(json.loads(proc.stdout),manifest)
            for key in KEYS:self.assertEqual((Path(manifest[key])/'child-sentinel.txt').read_text(),key)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(IsolationTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if CHILD_COUNT!=1: raise RuntimeError('exactly one synthetic child required')
    sources={name:hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest() for name in ['isolation.py','test_isolation.py','protocol.json']}
    print('RESULT_JSON='+json.dumps({'status':'PASS' if result.wasSuccessful() else 'FAIL','test_methods':result.testsRun,'optimization':sys.flags.optimize,'synthetic_children':CHILD_COUNT,'engine_processes':0,'source_sha256':sources,'child':CHILD_RECORD},sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() else 1)
