"""Original isolated consumer and process-boundary tests; never run an engine."""
import copy
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import uuid
import harness as h

class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        override=os.environ.get('FRESH_POSITIVE_INVOCATION')
        positive=h.read(h.HERE/'positive.json') if not override else {'directory':override,'id':Path(override).name}
        self.ident=positive['id']
        original=Path(positive['directory'])
        self.inv=self.root/self.ident
        self.inv.mkdir()
        # Copy only files the consumer verifies, not whole runtime environment.
        receipt=h.read(original/'receipt.json')
        rels=set(receipt['artifacts'])|{'receipt.json'}|{'work/'+p for p in receipt['source_sha256']}
        for rel in rels:
            dst=self.inv/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original/rel,dst)
    def modify_receipt(self, fn):
        r=h.read(self.inv/'receipt.json');fn(r);h.write(self.inv/'receipt.json',r)
    def test_positive_consumer(self):
        self.assertEqual(h.consumer(self.inv,self.ident)['status'],'ACCEPTED')
    def test_expected_id(self):
        with self.assertRaises(h.Rejected):h.consumer(self.inv,str(uuid.uuid4()))
    def test_started_rejected(self):
        self.modify_receipt(lambda r:r.update(status='STARTED'))
        with self.assertRaises(h.Rejected):h.consumer(self.inv,self.ident)
    def test_nonzero_even_with_success_summary(self):
        self.modify_receipt(lambda r:r['process'].update(exit_code=1))
        with self.assertRaises(h.Rejected):h.consumer(self.inv,self.ident)
    def test_optimized_never_accepted(self):
        self.modify_receipt(lambda r:r.update(optimize_child=True))
        with self.assertRaises(h.Rejected):h.consumer(self.inv,self.ident)
    def test_missing_summary(self):
        (self.inv/'work/results/summary.json').unlink()
        with self.assertRaises(h.Rejected):h.consumer(self.inv,self.ident)
    def test_changed_output(self):
        (self.inv/'stdout.txt').write_text('changed')
        with self.assertRaises(h.Rejected):h.consumer(self.inv,self.ident)
    def test_changed_source(self):
        (self.inv/'work/main.gd').write_text('changed')
        with self.assertRaises(h.Rejected):h.consumer(self.inv,self.ident)
    def test_changed_trusted_pins(self):
        self.modify_receipt(lambda r:r.update(registry_sha256='0'*64))
        with self.assertRaises(h.Rejected):h.consumer(self.inv,self.ident)
    def test_escape_symlink_and_unregistered_output(self):
        p=self.inv/'stdout.txt';data=p.read_bytes();p.unlink();other=self.root/'outside.txt';other.write_bytes(data);p.symlink_to(other)
        with self.assertRaises(h.Rejected):h.consumer(self.inv,self.ident)
    def test_normalized_paths(self):
        for rel in ('../outside','/tmp/out','a/../b','a//b','C:/out','a\\b'):
            with self.subTest(rel=rel),self.assertRaises(h.Rejected):h.contained(self.inv,rel,False)
    def save_process(self, label, directory, result):
        destination=Path(os.environ.get('FRESH_TEST_OUTPUT',str(h.HERE/'synthetic-results')))
        destination.mkdir(parents=True,exist_ok=True)
        h.write(destination/(label+'.json'),result)
        for name in ('stdout.txt','stderr.txt'):
            (destination/(label+'.'+name)).write_bytes((directory/name).read_bytes())
    def test_timeout_partial_output(self):
        d=self.root/'timeout';d.mkdir()
        p=h.launch([sys.executable,'-B','-c',"import time; print('PARTIAL',flush=True); time.sleep(30)"],d,os.environ.copy(),d,0.2)
        self.save_process('timeout',d,p)
        self.assertTrue(p['timed_out']);self.assertIn('PARTIAL',(d/'stdout.txt').read_text())
        with self.assertRaises(h.Rejected):h.process_acceptable(p)
    def test_real_nonzero_child_writes_pass(self):
        d=self.root/'nonzero';d.mkdir()
        p=h.launch([sys.executable,'-B','-c',"from pathlib import Path;Path('summary.json').write_text('{\"status\":\"PASS\"}');raise SystemExit(7)"],d,os.environ.copy(),d,2)
        self.save_process('nonzero-pass',d,p)
        self.assertTrue((d/'summary.json').exists());self.assertEqual(p['exit_code'],7)
        with self.assertRaises(h.Rejected):h.process_acceptable(p)
    def test_real_zero_child_missing_summary(self):
        d=self.root/'missing';d.mkdir()
        p=h.launch([sys.executable,'-B','-c',"print('no summary')"],d,os.environ.copy(),d,2)
        self.save_process('zero-missing',d,p)
        h.process_acceptable(p)
        with self.assertRaises(h.Rejected):h.validate_summary(d,'godot-focus-boundary',h.registry()['godot-focus-boundary'])
    def test_origin_historical_pass_not_copied(self):
        source=self.root/'origin';row=h.registry()['godot-focus-boundary'];folder=source/row['directory'];folder.mkdir(parents=True)
        original=self.inv/'work'
        for rel in row['sources']:
            dest=folder/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original/rel,dest)
        (folder/'results').mkdir();sentinel=folder/'results/summary.json';sentinel.write_text('{"status":"PASS","historical_sentinel":true}')
        before=sentinel.read_bytes();inv,rec=h.invoke(source,self.root/'negative-output','godot-focus-boundary',True)
        self.assertEqual(rec['status'],'REJECTED');self.assertEqual(rec['process']['exit_code'],1)
        self.assertFalse((inv/'work/results/summary.json').exists());self.assertEqual(sentinel.read_bytes(),before)

if __name__=='__main__':unittest.main(verbosity=2)
