"""Pure parser checks against retained native stdout; never launches Godot."""
import importlib.util, pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('runner',ROOT/'run.py'); runner=importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
RAW=ROOT/'results'/'39536c18-7525-4dcc-b264-ca94a2097a2d'
class ParserTests(unittest.TestCase):
    def streams(self,mode): return (RAW/(mode+'.stdout')).read_text(),(RAW/(mode+'.stderr')).read_text()
    def test_actual_two_records(self):
        for mode in ['direct-shape','deferred-shape']: runner.parse_result(*self.streams(mode),mode)
    def test_stdout_error(self):
        for mode in ['direct-shape','deferred-shape']:
            out,err=self.streams(mode)
            for bad in ['ERROR: injected','SCRIPT ERROR: injected','   ERROR: injected']:
                with self.subTest(mode=mode,bad=bad),self.assertRaises(ValueError): runner.parse_result(out+'\n'+bad,err,mode)
    def test_extra_stderr(self):
        for mode in ['direct-shape','deferred-shape']:
            out,err=self.streams(mode)
            with self.assertRaises(ValueError): runner.parse_result(out,err+'ERROR: extra\n',mode)
    def test_duplicate_or_missing_result(self):
        out,err=self.streams('deferred-shape');line=next(x for x in out.splitlines() if x.startswith('RESULT_JSON='))
        for bad in [out+'\n'+line,out.replace(line,'')]:
            with self.assertRaises(ValueError): runner.parse_result(bad,err,'deferred-shape')
if __name__=='__main__': unittest.main()
