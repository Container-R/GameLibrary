import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from verify import IntegrityError
from verify_relocated import run

class RelocationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.records=self.root/'管理档案/研究记录';self.records.mkdir(parents=True)
        source=b'original technical source\n';(self.records/'source.py').write_bytes(source)
        summary={'source_sha256':{'research/source.py':hashlib.sha256(source).hexdigest()},'result':{'failure_preserved':True},'synthetic_identity':'fixture-only'}
        self.original=json.dumps(summary).encode();(self.records/'summary.json').write_bytes(self.original)
        self.registry={'checks':[{'id':'source','kind':'manifest','document':'research/summary.json','field':['source_sha256'],'files':{'research/source.py':'research/source.py'}}]}
        self.bytes=json.dumps(self.registry).encode()
        self.policy={'version':1,'expected_checks':1,'registry_sha256':hashlib.sha256(self.bytes).hexdigest(),'prefixes':{'research':'管理档案/研究记录'},'retired_checks':{}}
    def call(self):return run(self.root,self.bytes,self.policy)
    def test_unchanged_manifest_keys_and_bytes(self):
        self.assertTrue(self.call()['complete']);self.assertEqual((self.records/'summary.json').read_bytes(),self.original)
    def test_no_legacy_directory_needed(self):
        self.assertFalse((self.root/'research').exists());self.assertEqual(self.call()['passed'],1)
    def test_missing_source_fails(self):
        (self.records/'source.py').unlink();self.assertEqual(self.call()['failed'],1)
    def test_altered_source_not_rehashed_into_history(self):
        (self.records/'source.py').write_text('changed');self.assertEqual(self.call()['failed'],1)
    def test_count_rejects_empty_missing_extra(self):
        for n in (0,-1,2,True):
            with self.subTest(n=n),self.assertRaises(IntegrityError):self.policy['expected_checks']=n;self.call()
    def test_empty_registry_rejected(self):
        self.bytes=b'{"checks":[]}';self.policy['registry_sha256']=hashlib.sha256(self.bytes).hexdigest()
        with self.assertRaises(IntegrityError):self.call()
    def test_boolean_version_rejected(self):
        self.policy['version']=True
        with self.assertRaises(IntegrityError):self.call()
    def test_registry_bytes_pin(self):
        self.bytes+=b' '
        with self.assertRaises(IntegrityError):self.call()
    def test_retirement_never_full_pass(self):
        self.policy['retired_checks']={'source':'public derivative removes execution identity'}
        r=self.call();self.assertFalse(r['complete']);self.assertEqual(r['passed'],0);self.assertEqual(r['retired'][0]['status'],'not_revalidated')
    def test_unknown_or_reasonless_retirement(self):
        for value in ({'unknown':'reason'},{'source':''}):
            self.policy['retired_checks']=value
            with self.assertRaises(IntegrityError):self.call()
    def test_escape_and_absolute_mapping_rejected(self):
        for bad in ('../out','/out','x/../out','x\\out','x//out'):
            self.policy['prefixes']={'research':bad}
            with self.subTest(bad=bad),self.assertRaises(IntegrityError):self.call()
    def test_overlapping_mapping_rejected(self):
        for m in ({'research':'new','research/sub':'other'},{'research':'new','scripts':'new/sub'}):
            self.policy['prefixes']=m
            with self.assertRaises(IntegrityError):self.call()
    def test_external_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as out:
            f=Path(out)/'file';f.write_text('data');(self.records/'source.py').unlink();(self.records/'source.py').symlink_to(f)
            self.assertEqual(self.call()['failed'],1)
    def test_log_derivative_does_not_equal_old_parsed(self):
        (self.records/'stdout.txt').write_text('RESULT_JSON={"v":2}\n');(self.records/'parsed.json').write_text('{"v":1}')
        self.registry={'checks':[{'id':'log','kind':'log','log':'research/stdout.txt','parsed':'research/parsed.json'}]};self.bytes=json.dumps(self.registry).encode();self.policy['registry_sha256']=hashlib.sha256(self.bytes).hexdigest()
        self.assertEqual(self.call()['failed'],1)
    def test_cli_relocated_cwd_and_retirement_exit(self):
        script=Path(__file__).with_name('verify_relocated.py').resolve()
        registry=self.root/'registry.json';registry.write_bytes(self.bytes)
        policy=self.root/'policy.json';policy.write_text(json.dumps(self.policy))
        cmd=[sys.executable]+(['-O'] if sys.flags.optimize else [])+[str(script),'--root',str(self.root),'--registry',str(registry),'--policy',str(policy)]
        result=subprocess.run(cmd,cwd=self.records,capture_output=True,text=True);self.assertEqual(result.returncode,0)
        self.policy['retired_checks']={'source':'intentional derivative'};policy.write_text(json.dumps(self.policy))
        result=subprocess.run(cmd,cwd=self.records,capture_output=True,text=True);self.assertEqual(result.returncode,2);self.assertFalse(json.loads(result.stdout)['complete'])
    def test_missing_cli_input_fails(self):
        script=Path(__file__).with_name('verify_relocated.py').resolve()
        result=subprocess.run([sys.executable,str(script),'--root',str(self.root),'--registry','missing','--policy','missing'],cwd=self.records,capture_output=True,text=True)
        self.assertEqual(result.returncode,1);self.assertNotIn('PASS',result.stdout)

if __name__=='__main__':unittest.main()
