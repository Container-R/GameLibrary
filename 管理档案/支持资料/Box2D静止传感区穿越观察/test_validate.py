"""Pure synthetic controls and mocked runner failures. Never starts any subprocess."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
import validate as v
import run as runner

ROOT=Path(__file__).resolve().parent

def control():
    rows=[];ids={}
    for spec in v.expected():
        case,phase,key=spec['case'],spec['phase'],spec['key'];rule=spec['rule']
        value=copy.deepcopy(spec['value'])
        if rule=='bind':
            if spec['kind']=='world':value=[1,0 if case=='events_on' else 1]
            else:value=[1 if key.startswith('sensor') else 2,0,0]
            ids[(case,key)]=value
        elif rule=='ref':value=copy.deepcopy(ids[(case,value)])
        elif rule=='positive':value=.1963495463
        rows.append(dict(case=case,phase=phase,key=key,value=value))
    return rows

def encoded(rows):return ('\n'.join(json.dumps(x,allow_nan=False) for x in rows)+'\n').encode()
def location(rows,case,phase,key):return next(r for r in rows if (r['case'],r['phase'],r['key'])==(case,phase,key))

class ConsumerTests(unittest.TestCase):
    def test_valid_and_scope(self):
        result=v.validate(encoded(control()))
        self.assertEqual(result['worlds'],2);self.assertEqual(result['steps'],6)
        self.assertEqual(result['result_kind'],'consumer_only')
        self.assertEqual(result['overall_acceptance_requires'],'receipt.json status=pass after identity checks')
        self.assertEqual(result['records'],len(control()));self.assertGreater(result['records'],300)

    def test_types_keys_and_nonfinite(self):
        raw=encoded(control())
        for bad in [raw.replace(b'"value": [3, 2, 0]',b'"value": [3, 2, false]',1),raw.replace(b'"value": 1.0',b'"value": true',1),raw.replace(b'"value": 1.0',b'"value": NaN',1),raw.replace(b'"value": 1.0',b'"value": 1e999',1),raw.replace(b'"key": "version"',b'"key": "version", "key": "version"',1)]:
            with self.subTest(bad=bad[:100]),self.assertRaises(ValueError):v.validate(bad)
        for value in [1,True,None,0.,-1.]:
            rows=control();location(rows,'events_on','setup','visitor.mass')['value']=value
            with self.subTest(mass=value),self.assertRaises(ValueError):v.validate(encoded(rows))

    def test_cardinality_order_and_extra_fields(self):
        rows=control()
        variants=[rows[:-1],rows+[rows[-1]],rows[1:]+rows[:1]]
        extra=copy.deepcopy(rows);extra[0]['unexpected']=0;variants.append(extra)
        for value in variants:
            with self.subTest(size=len(value)),self.assertRaises(ValueError):v.validate(encoded(value))
        with self.assertRaises(ValueError):v.validate(encoded(rows).rstrip())

    def test_setup_and_live_id_guards(self):
        edits=[('visitor.sensor_events',False),('visitor.min_extent',.5),('visitor.safety_factor',1.),('visitor.awake',False),('visitor.mass',0.),('polygon.vertex.0',[0.,0.]),('sensor.body',[2,0,0]),('visitor.id',[1,0,0]),('world.id',[0,0]),('visitor_body.id',[2,1,0]),('visitor.id',[2,0,False])]
        for key,value in edits:
            rows=control();location(rows,'events_on','setup',key)['value']=value
            with self.subTest(key=key),self.assertRaises(ValueError):v.validate(encoded(rows))

    def test_events_motion_cache_and_geometry(self):
        edits=[('begin_count',0),('end_count',1),('begin.visitor',[1,0,0]),('cache_capacity',0),('cache_visitor',[1,0,0]),('sensor.sensor_events',False),('visitor.pose',[2.00002,0.,1.,0.]),('visitor.velocity',[128.,0.]),('projection',[-.125,.125,-.25,.25]),('gap',0.),('dx',0.)]
        for key,value in edits:
            rows=control();location(rows,'events_on','step_1',key)['value']=value
            with self.subTest(key=key),self.assertRaises(ValueError):v.validate(encoded(rows))
        rows=control();location(rows,'visitor_events_off','step_1','begin_count')['value']=1
        with self.assertRaises(ValueError):v.validate(encoded(rows))

    def test_oracle_identity(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'expected.json';path.write_bytes((ROOT/'expected.json').read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'oracle identity'):v.validate(encoded(control()),path)

class RunnerTests(unittest.TestCase):
    def setUp(self):
        # Exercise mocked workflow under both interpreter modes without disabling
        # the real runner guard. The dedicated guard test explicitly sets 1.
        actual=runner.sys.flags
        class FlagsProxy:
            optimize=0
            def __getattr__(self,name):return getattr(actual,name)
        patch=mock.patch.object(runner.sys,'flags',FlagsProxy())
        patch.start();self.addCleanup(patch.stop)

    def prepare(self,path):
        for name in (*runner.CODE_FILES,'CODE-MANIFEST.json'):shutil.copyfile(ROOT/name,path/name)
        return hashlib.sha256((path/'CODE-MANIFEST.json').read_bytes()).hexdigest()

    def test_identity_and_source_set(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);digest=self.prepare(p)
            self.assertEqual(len(runner.code_snapshot(p,digest)),10)
            (p/'fixture.c').write_text('changed')
            with self.assertRaises(ValueError):runner.code_snapshot(p,digest)
            with self.assertRaises(ValueError):runner.source_snapshot(p,p/'SOURCE-MANIFEST.json')
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);self.prepare(p);doc=json.loads((p/'CODE-MANIFEST.json').read_text());doc['files'].pop('fixture.c');runner.save(p/'CODE-MANIFEST.json',doc)
            digest=runner.sha((p/'CODE-MANIFEST.json').read_bytes())
            with self.assertRaisesRegex(ValueError,'code input set'):runner.code_snapshot(p,digest)

    def test_fresh_and_optimized_guard_before_import(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/'attempts').mkdir();old=p/'attempts'/'old';old.mkdir();(old/'receipt.json').write_text('{"status":"pass"}')
            with mock.patch.object(runner,'consumer') as load,mock.patch.object(runner.subprocess,'Popen') as process:
                with self.assertRaises(FileExistsError):runner.operate('execute','old','unused',root=p)
                with mock.patch.object(runner.sys,'flags',SimpleNamespace(optimize=1)):
                    with self.assertRaises(ValueError):runner.operate('execute','fresh','unused',root=p)
                load.assert_not_called();process.assert_not_called()
            self.assertFalse((p/'attempts'/'fresh'/'receipt.json').exists())

    def test_command_warnings_nonzero_and_timeout_cleanup(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            for rc,err in [(0,b'warning'),(1,b'')]:
                child=mock.Mock(returncode=rc);child.communicate.return_value=(b'',err)
                with mock.patch.object(runner.subprocess,'Popen',return_value=child),mock.patch.object(runner.os,'killpg'):
                    with self.assertRaises(ValueError):runner.command(['mock'],p,20,{},'mock')
            child=mock.Mock(pid=123,returncode=-15);child.communicate.side_effect=[subprocess.TimeoutExpired(['mock'],20,output=b'partial',stderr=b''),(b'partial',b'')];child.wait.return_value=-15
            with mock.patch.object(runner.subprocess,'Popen',return_value=child),mock.patch.object(runner.os,'killpg') as kill:
                with self.assertRaises(subprocess.TimeoutExpired):runner.command(['mock'],p,20,{},'timeout')
                self.assertEqual([c.args[1] for c in kill.call_args_list],[runner.signal.SIGTERM,runner.signal.SIGKILL])
                self.assertEqual((p/'timeout.stdout').read_bytes(),b'partial')

    def test_rejected_returned_child_cleans_entire_group(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            for rc,out,err,empty in [(1,b'',b'',False),(0,b'',b'warning',False),(0,b'unexpected',b'',True)]:
                child=mock.Mock(pid=123,returncode=rc);child.communicate.return_value=(out,err);child.wait.return_value=rc
                with self.subTest(rc=rc,out=out,err=err),mock.patch.object(runner.subprocess,'Popen',return_value=child),mock.patch.object(runner.os,'killpg') as kill:
                    with self.assertRaises(ValueError):runner.command(['mock'],p,20,{},'rejected',empty_stdout=empty)
                    self.assertEqual([c.args[1] for c in kill.call_args_list],[runner.signal.SIGTERM,runner.signal.SIGKILL])
                self.assertEqual(json.loads((p/'rejected.json').read_text())['status'],'rejected_result')

    def test_reviewed_build_diagnostic_exact_bytes(self):
        trusted=(ROOT/'reviewed-build-stderr.txt').read_bytes()
        self.assertEqual(len(trusted),32263)
        self.assertEqual(runner.build_diagnostics(trusted,ROOT/'reviewed-build-stderr.txt'),'reviewed_exact_warning')
        self.assertEqual(runner.build_diagnostics(b'',ROOT/'reviewed-build-stderr.txt'),'empty')
        variants=[trusted[:-1],b'X'+trusted[1:],trusted+b'fixture.c: warning: different\n',b'fixture.c: warning: unrelated\n']
        for raw in variants:
            with self.subTest(size=len(raw)),self.assertRaises(ValueError):runner.build_diagnostics(raw,ROOT/'reviewed-build-stderr.txt')
        with tempfile.TemporaryDirectory() as t:
            changed=Path(t)/'reviewed-build-stderr.txt';changed.write_bytes(trusted+b' ')
            for raw in [trusted,b'']:
                with self.assertRaisesRegex(ValueError,'reviewed diagnostic identity'):runner.build_diagnostics(raw,changed)

    def test_reviewed_build_warning_does_not_relax_exit_stdout_or_native(self):
        trusted=(ROOT/'reviewed-build-stderr.txt').read_bytes()
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/'reviewed-build-stderr.txt').write_bytes(trusted)
            for rc,out,err,build,accepted in [(0,b'',trusted,True,True),(0,b'',b'',True,True),(1,b'',trusted,True,False),(0,b'x',trusted,True,False),(0,b'',trusted,False,False)]:
                child=mock.Mock(pid=123,returncode=rc);child.communicate.return_value=(out,err);child.wait.return_value=rc
                with self.subTest(rc=rc,build=build,out=out),mock.patch.object(runner.subprocess,'Popen',return_value=child),mock.patch.object(runner.os,'killpg'):
                    if accepted:
                        _,info=runner.command(['mock'],p,120,{},'mock',empty_stdout=build)
                        self.assertEqual(info['diagnostic_policy'],'empty' if err==b'' else 'reviewed_exact_warning')
                    else:
                        with self.assertRaises(ValueError):runner.command(['mock'],p,120,{},'mock',empty_stdout=build)

    def test_primary_error_and_post_spawn_cleanup(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);child=mock.Mock(pid=123,returncode=0);child.communicate.side_effect=[OSError('communication'),(b'',b'')];child.wait.return_value=0
            with mock.patch.object(runner.subprocess,'Popen',return_value=child),mock.patch.object(runner.os,'killpg') as kill,mock.patch.object(Path,'write_bytes',side_effect=OSError('write')):
                with self.assertRaisesRegex(OSError,'communication'):runner.command(['mock'],p,20,{},'failed')
                self.assertEqual(kill.call_count,2)
            doc=json.loads((p/'failed.json').read_text());self.assertEqual(doc['status'],'communication_error');self.assertIn('OSError',doc['secondary_errors'])

    def test_build_failure_does_not_execute(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);digest=self.prepare(p)
            with mock.patch.object(runner,'source_snapshot',return_value={'fake':'synthetic'}),mock.patch.object(runner,'copy_sources'),mock.patch.object(runner,'command',side_effect=ValueError('diagnostic')) as command,mock.patch.object(runner,'consumer') as consume:
                with self.assertRaises(ValueError):runner.operate('build','build-fail',digest,sources=p,root=p)
                self.assertEqual(command.call_count,1);consume.assert_not_called()
            result=json.loads((p/'attempts'/'build-fail'/'receipt.json').read_text());self.assertEqual(result['status'],'fail');self.assertEqual(result['stage'],'compile')

    def test_execute_requires_accepted_artifact_and_after_check(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);digest=self.prepare(p)
            def mock_build(argv,work,timeout,env,prefix,**kwargs):
                (work/'sensor_fixture').write_bytes(b'synthetic-not-executable');return b'',{'status':'mocked'}
            with mock.patch.object(runner,'source_snapshot',return_value={'fake':'synthetic'}),mock.patch.object(runner,'copy_sources'),mock.patch.object(runner,'command',side_effect=mock_build):
                result=runner.operate('build','build-ok',digest,sources=p,root=p)
            self.assertEqual(result['status'],'pass')
            raw=encoded(control())
            def mock_execute(argv,work,timeout,env,prefix):
                self.assertEqual(argv,['./sensor_fixture']);self.assertEqual(timeout,20);(work/'native.stdout').write_bytes(raw)
                return raw,{'status':'mocked'}
            def mock_consumer(work):
                def checked(data,path):
                    result=v.validate(data,path)
                    # Pure mock: failure after the consumer, not a native mutation.
                    (work/'fixture.c').write_text('changed by synthetic consumer mock')
                    return result
                return SimpleNamespace(validate=checked)
            with mock.patch.object(runner,'source_snapshot',return_value={'fake':'synthetic'}),mock.patch.object(runner,'copy_sources'),mock.patch.object(runner,'command',side_effect=mock_execute),mock.patch.object(runner,'consumer',side_effect=mock_consumer):
                with self.assertRaises(ValueError):runner.operate('execute','execute-fail',digest,build_name='build-ok',root=p)
            work=p/'attempts'/'execute-fail'
            self.assertEqual(json.loads((work/'validation.json').read_text())['result_kind'],'consumer_only')
            self.assertEqual(json.loads((work/'receipt.json').read_text())['status'],'fail')
            (p/'attempts'/'build-ok'/'sensor_fixture').write_bytes(b'tampered')
            with mock.patch.object(runner,'source_snapshot',return_value={'fake':'synthetic'}),mock.patch.object(runner,'command') as command:
                with self.assertRaises(ValueError):runner.operate('execute','tampered',digest,build_name='build-ok',root=p)
                command.assert_not_called()

if __name__=='__main__':unittest.main()
