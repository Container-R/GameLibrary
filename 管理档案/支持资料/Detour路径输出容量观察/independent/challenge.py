"""Independent pure challenges. All runner process creation is mocked/forbidden."""
import sys, json, copy, shutil, tempfile, unittest, contextlib, io
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch, Mock
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import validate as v
import run as r

def observation():
    x=json.loads((ROOT/'expected.json').read_text())
    refs=['64','65','66'];m=dict(zip('ABC',refs));x['setup']['refs']=refs;x['setup']['data_size']=1024
    for p in x['setup']['polygons']:
        for link in p['links']:link['ref']=m[link['ref']]
    for c in x['cases']:c['path']=[m.get(i,i) for i in c['path']]
    return x

class Independent(unittest.TestCase):
    def test_literal_two_rows(self):
        x=observation()
        self.assertEqual([(c['status'],c['path_count'],c['indices']) for c in x['cases']],[(0x40000010,2,[0,1,None]),(0x40000000,3,[0,1,2])])
        self.assertEqual(v.validate(x)['query_calls'],2)
    def test_failure_bits_counts_setup(self):
        changes=[('status',0x40000050),('status',0x40000030),('status',0xc0000010),('status',0x60000010),('status_hex','0x40000000')]
        for key,value in changes:
            x=observation();x['cases'][0][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):v.validate(x)
        for field,value in [('builder_calls',0),('nav_init_calls',2),('query_init_calls',2),('node_capacity',32),('header',[3,8,3,6,0,0,13])]:
            x=observation();x['setup'][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):v.validate(x)
    def test_actual_link_ref_target_disagreement(self):
        x=observation();x['setup']['polygons'][0]['links'][0]['ref']='66'
        with self.assertRaises(ValueError):v.validate(x)
        x=observation();x['setup']['polygons'][0]['links'][0]['target']=2
        with self.assertRaises(ValueError):v.validate(x)
    def test_missing_null_unknown_inputs(self):
        for raw in [b'',b'null',b'{}',b'{"status":"pass","status":"fail"}',b'{}{}']:
            with self.subTest(raw=raw),self.assertRaises((ValueError,TypeError)):v.validate(v.strict_json(raw))
        x=observation();x['setup']['input']['cs']=float('inf')
        with self.assertRaises(ValueError):v.validate(x)
    def test_real_bound_input_set(self):
        self.assertEqual(len(r.identities(ROOT)),24)
    def simulated_run(self,outputs, mutate_after=False):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'root';root.mkdir()
            for name in r.CODE_FILES|{'CODE-MANIFEST.json'}:shutil.copyfile(ROOT/name,root/name)
            shutil.copytree(ROOT/'upstream',root/'upstream')
            calls=[]
            def command(work,argv,timeout,label,receipt):
                calls.append(label)
                receipt['processes'].append({'stage':label,'returncode':0})
                if mutate_after and label=='native':(root/'fixture.cpp').write_text('changed')
                out=outputs[len(calls)-1]
                if isinstance(out,Exception):raise out
                return out
            # Simulate the runner's required normal-mode invocation even when this test interpreter uses -O.
            with patch.object(r.sys,'flags',SimpleNamespace(**{name:(0 if name=='optimize' else getattr(sys.flags,name)) for name in dir(sys.flags) if not name.startswith('_') and not callable(getattr(sys.flags,name))})),patch.object(r,'ROOT',root),patch.object(r,'command',side_effect=command),patch.object(r.subprocess,'Popen',side_effect=AssertionError('forbidden real process')),contextlib.redirect_stdout(io.StringIO()):
                rc=r.main()
            receipt=json.loads((root/'execution/attempt-002/receipt.json').read_text())
            return rc,calls,receipt['status']
    def test_runner_synthetic_control_and_missing_output(self):
        good=json.dumps(observation()).encode()
        self.assertEqual(self.simulated_run([(b'',b''),(good,b'')]),(0,['build','native'],'pass'))
        self.assertEqual(self.simulated_run([(b'',b''),(b'',b'')]),(1,['build','native'],'fail'))
    def test_runner_diagnostic_and_build_failure_stop_before_native(self):
        for outputs in [[(b'',b'warning')],[(b'anything',b'')],[ValueError('nonzero build')]]:
            self.assertEqual(self.simulated_run(outputs),(1,['build'],'fail'))
    def test_runner_native_failure_and_after_identity(self):
        good=json.dumps(observation()).encode()
        self.assertEqual(self.simulated_run([(b'',b''),ValueError('nonzero native')]),(1,['build','native'],'fail'))
        self.assertEqual(self.simulated_run([(b'',b''),(good,b'')],True),(1,['build','native'],'fail'))
    def test_exact_warning_pass_and_nonzero_reject(self):
        raw=(ROOT/'reviewed-build-stderr.txt').read_bytes()
        self.assertEqual(r.validate_build(b'',raw,0),'reviewed_warning')
        for err in [raw+b' ',raw.replace(b'warning:',b'note:',1),raw[:-1]]:
            with self.subTest(err=err),self.assertRaises(ValueError):r.validate_build(b'',err,0)
        for code in [1,-1,True,0.0]:
            with self.subTest(code=code),self.assertRaises(ValueError):r.validate_build(b'',raw,code)
        good=json.dumps(observation()).encode()
        self.assertEqual(self.simulated_run([(b'',raw),(good,b'')]),(0,['build','native'],'pass'))
    def test_trusted_warning_missing_or_modified_even_for_empty_build(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            with patch.object(r,'ROOT',root):
                with self.assertRaises(FileNotFoundError):r.validate_build(b'',b'',0)
                (root/'reviewed-build-stderr.txt').write_bytes(b'changed')
                with self.assertRaises(ValueError):r.validate_build(b'',b'',0)
    def test_command_nonzero_and_timeout_are_failures(self):
        import subprocess
        for outcome in [(b'partial',b'bad'),subprocess.TimeoutExpired('synthetic',1,output=b'partial')]:
            with tempfile.TemporaryDirectory() as temp:
                child=Mock();child.returncode=7
                if isinstance(outcome,Exception):child.communicate.side_effect=outcome
                else:child.communicate.return_value=outcome
                receipt={'processes':[]}
                with patch.object(r.subprocess,'Popen',return_value=child),patch.object(r,'stop_group',return_value=[]) as cleanup:
                    with self.assertRaises((ValueError,subprocess.TimeoutExpired)):r.command(Path(temp),['synthetic'],1,'fake',receipt)
                    cleanup.assert_called_once_with(child)
                self.assertEqual((Path(temp)/'fake.stdout').read_bytes(),b'partial')

if __name__=='__main__':unittest.main(verbosity=2)
