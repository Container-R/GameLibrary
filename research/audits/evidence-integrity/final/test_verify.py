import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from verify import IntegrityError, inside, strict_json, verify

class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        (self.root/'source').write_bytes(b'original')
        (self.root/'summary.json').write_text(json.dumps({'source_sha256':{'source':hashlib.sha256(b'original').hexdigest()}}))
        self.entry={'id':'source','kind':'manifest','document':'summary.json','field':['source_sha256'],'files':{'source':'source'}}
    def result(self,entry=None): return verify(self.root,{'checks':[entry or self.entry]})
    def test_good_source(self): self.assertEqual(self.result()['failed'],0)
    def test_corruption_detected(self):
        (self.root/'source').write_bytes(b'changed')
        self.assertEqual(self.result()['failed'],1)
    def test_missing_file_detected(self):
        (self.root/'source').unlink()
        self.assertEqual(self.result()['failed'],1)
    def test_path_escape_rejected(self):
        for path in ['../outside','/tmp/outside','a/../../outside']:
            with self.subTest(path=path),self.assertRaises(IntegrityError): inside(self.root,path)
    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as external:
            target=Path(external)/'outside';target.write_text('outside')
            (self.root/'link').symlink_to(target)
            with self.assertRaises(IntegrityError):inside(self.root,'link')
    def test_bad_json_rejected(self):
        for data in ['{','{"a":1,"a":2}','{"a":NaN}','{"a":1e999}','{"a":-1e999}']:
            with self.subTest(data=data),self.assertRaises(ValueError):strict_json(data)
        (self.root/'summary.json').write_text('{')
        self.assertEqual(self.result()['failed'],1)
    def test_manifest_omission_rejected(self):
        (self.root/'summary.json').write_text('{"source_sha256":{}}')
        self.assertEqual(self.result()['failed'],1)
    def test_log_records(self):
        entry={'id':'log','kind':'log','log':'run.log','parsed':'parsed.json'}
        (self.root/'parsed.json').write_text('{"v":1}')
        (self.root/'run.log').write_text('header\nRESULT_JSON={"v":1}\n')
        self.assertEqual(self.result(entry)['failed'],0)
        for raw in ['header','RESULT_JSON={bad}','RESULT_JSON={"v":true}','RESULT_JSON={"v":1}\nRESULT_JSON={"v":1}']:
            (self.root/'run.log').write_text(raw)
            self.assertEqual(self.result(entry)['failed'],1)
    def test_empty_or_duplicate_registry_rejected(self):
        for entries in [[],[self.entry,self.entry]]:
            with self.assertRaises(IntegrityError):verify(self.root,{'checks':entries})

if __name__=='__main__': unittest.main(verbosity=2)
