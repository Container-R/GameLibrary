import sys,unittest,json,subprocess,copy
from pathlib import Path
if len(sys.argv) < 2:
    raise SystemExit('usage: adversarial.py NAVIGATION_SOURCE_DIRECTORY')
NAV = Path(sys.argv.pop(1)).resolve()
sys.path.insert(0, str(NAV))
from test_routes import Tests
from build_routes import render,Invalid,registry_load
class Adversarial(Tests):
    def test_external_symlink_rejected(self):
        outside=self.root.parent/(self.root.name+'-external.md')
        outside.write_text((self.root/'solutions/one.md').read_text());self.addCleanup(outside.unlink)
        (self.root/'solutions/link.md').symlink_to(outside)
        with self.assertRaises(Invalid):render(self.root,self.reg)
    def test_duplicate_json_rejected(self):
        path=self.root/'reg.json';path.write_text('{"schema_version":1,"schema_version":1,"routes":[]}')
        with self.assertRaises(Invalid):registry_load(path)
    def test_problem_cannot_claim_profile(self):
        self.reg['routes'][0]['kind']='problem'
        with self.assertRaises(Invalid):render(self.root,self.reg)
    def test_special_path_encoded(self):
        (self.root/'solutions/one.md').rename(self.root/'solutions/a) [b]#?.md')
        out=render(self.root,self.reg)
        self.assertIn('solutions/a%29%20%5Bb%5D%23%3F.md',out)
    def test_wrong_check_does_not_write(self):
        reg=self.root/'reg.json';reg.write_text(json.dumps(self.reg));out=self.root/'out.md';out.write_text('sentinel')
        cmd=[sys.executable,str(NAV/'build_routes.py'),str(self.root),'--registry',str(reg),'--output',str(out),'--check']
        before=out.stat().st_mtime_ns
        self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,1)
        self.assertEqual(out.read_text(),'sentinel');self.assertEqual(before,out.stat().st_mtime_ns)
del Tests
if __name__=='__main__':unittest.main(verbosity=2)
