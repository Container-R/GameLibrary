"""Pure synthetic tests only: never invokes a compiler, tracer, or native fixture."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import consumer as c
import run

RUN = '11111111-1111-4111-8111-111111111111'
ROOT = Path(__file__).resolve().parent

def raw(records):
    return ('\n'.join(json.dumps(x) for x in records)+'\n').encode()

class Checks(unittest.TestCase):
    def test_frozen_records_and_malformed_rows(self):
        records = c.expected_records(RUN)
        self.assertEqual(len(c.check_raw(raw(records),RUN)),19)
        bad = []
        x=copy.deepcopy(records); x.pop(5); bad.append(x)
        x=copy.deepcopy(records); x.insert(5,x[5]); bad.append(x)
        for field,value in [('result',True),('freed_before',False),('other_empty',1)]:
            x=copy.deepcopy(records); x[1][field]=value; bad.append(x)
        x=copy.deepcopy(records); x[1]['ordinary'][0][0]=134; bad.append(x)
        x=copy.deepcopy(records); x[1]['ordinary'][0][3]=43; bad.append(x)
        x=copy.deepcopy(records); x[1]['packet'][0]=2; bad.append(x)
        x=copy.deepcopy(records); x[1]['reliable']=x[1]['ordinary']; x[1]['ordinary']=[]; bad.append(x)
        x=copy.deepcopy(records); x[-2]['cleanup'][0]=0; bad.append(x)
        for value in bad:
            with self.subTest(value=value[1]):
                with self.assertRaises(ValueError): c.check_raw(raw(value),RUN)
        for value in ('{"a":0,"a":1}','{"x":NaN}','{"x":Infinity}'):
            with self.assertRaises(ValueError): c.decode(value)

    def test_exact_reviewed_build_diagnostic_only(self):
        reviewed=(ROOT/'reviewed-build.stderr').read_bytes()
        c.check_build_diagnostic(b'',reviewed)
        c.check_build_diagnostic(reviewed,reviewed)
        for altered in (reviewed+b' ', reviewed.replace(b'warning:',b'WARNING:',1),
                        reviewed+b'fixture.c:1: warning: unrelated diagnostic\n'):
            with self.assertRaises(ValueError): c.check_build_diagnostic(altered,reviewed)
        with self.assertRaises(ValueError): c.check_build_diagnostic(b'',reviewed+b' ')
        with tempfile.TemporaryDirectory() as tmp:
            e=Path(tmp); receipt=self.make_archive(e)
            (e/'build.stderr').write_bytes(reviewed)
            receipt['commands'][1]['stderr_sha256']=c.sha(e/'build.stderr')
            (e/'receipt.json').write_text(json.dumps(receipt))
            self.assertEqual(c.verify(ROOT,e)['rows'],17)
            (e/'build.stderr').write_bytes(reviewed+b'fixture.c:1: warning: new\n')
            receipt['commands'][1]['stderr_sha256']=c.sha(e/'build.stderr')
            (e/'receipt.json').write_text(json.dumps(receipt))
            with self.assertRaises(ValueError): c.verify(ROOT,e)

    def test_trace_requires_only_normal_exit(self):
        for trace in (b'+++ exited with 0 +++\n',b'100  +++ exited with 0 +++\n'):
            c.check_trace(trace)
        for trace in (b'',b'\n',b'100 socket(AF_INET, SOCK_DGRAM, 0) = 3\n100 +++ exited with 0 +++\n',
                      b'100 +++ exited with 1 +++\n', b'100 --- SIGTERM ---\n',
                      b'100 +++ exited with 0 +++\n101 +++ exited with 0 +++\n'):
            with self.subTest(trace=trace),self.assertRaises(ValueError): c.check_trace(trace)

    def test_source_manifest_and_git_blob(self):
        c.source_snapshot(ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)
            for name in c.source_snapshot(ROOT):
                p=target/name; p.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(ROOT/name,p)
            manifest=c.decode((target/'SOURCE-MANIFEST.json').read_text())
            (target/'fixture.c').write_text('changed source')
            with self.assertRaises(ValueError): c.source_snapshot(target)
            shutil.copyfile(ROOT/'fixture.c',target/'fixture.c')
            empty={'files':{}}
            (target/'SOURCE-MANIFEST.json').write_text(json.dumps(empty))
            with self.assertRaises(ValueError): c.source_snapshot(target)
            (target/'SOURCE-MANIFEST.json').write_text(json.dumps(manifest))
            up=c.decode((target/'UPSTREAM-SOURCE-MANIFEST.json').read_text())
            up['files'][0]['git_blob']='0'*40
            (target/'UPSTREAM-SOURCE-MANIFEST.json').write_text(json.dumps(up))
            manifest['files']['UPSTREAM-SOURCE-MANIFEST.json']=c.sha(target/'UPSTREAM-SOURCE-MANIFEST.json')
            (target/'SOURCE-MANIFEST.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError,'git blob'): c.source_snapshot(target)

    def make_archive(self,e):
        records=c.expected_records(RUN)
        (e/'fixture.stdout').write_bytes(raw(records)); (e/'fixture.stderr').write_bytes(b'')
        (e/'version.stdout').write_bytes(b'SYNTHETIC COMPILER RECORD\n'); (e/'version.stderr').write_bytes(b'')
        (e/'build.stdout').write_bytes(b''); (e/'build.stderr').write_bytes(b'')
        (e/'network.trace').write_bytes(b'100 +++ exited with 0 +++\n')
        (e/'queue_fixture').write_bytes(b'SYNTHETIC NOT EXECUTABLE')
        (e/'parsed.json').write_text(json.dumps(records))
        cmds=[]
        for name,t,argv in [('version',5,['cc','--version']),('build',60,c.BUILD),
                            ('fixture',20,['strace','-f','-e','trace=network','-o','network.trace','./queue_fixture',RUN])]:
            cmd={'name':name,'argv':argv,'timeout_seconds':t,'returncode':0,'timed_out':False,'process_id':100}
            for stream in ('stdout','stderr'):
                cmd[stream]=name+'.'+stream; cmd[stream+'_sha256']=c.sha(e/cmd[stream])
            cmds.append(cmd)
        snap=c.source_snapshot(ROOT)
        tools={x:{'resolved':'synthetic-'+x,'sha256':'0'*64} for x in ('cc','strace')}
        receipt={'schema':1,'run':RUN,'status':'PASS','commands':cmds,'source_before':snap,'source_after':snap,
                 'work_source_after':snap,'tools_before':tools,'tools_after':tools,
                 'trace_sha256':c.sha(e/'network.trace'),'parsed_sha256':c.sha(e/'parsed.json'),
                 'binary_sha256':c.sha(e/'queue_fixture')}
        (e/'receipt.json').write_text(json.dumps(receipt))
        return receipt

    def test_archive_bindings_and_failure_receipts(self):
        with tempfile.TemporaryDirectory() as tmp:
            e=Path(tmp); receipt=self.make_archive(e)
            self.assertEqual(c.verify(ROOT,e)['rows'],17)
            for mutate in ('raw','parsed_bool','parsed_number','trace','binary','failed_build','timeout','argv','source','missing_trace','missing_tools'):
                with self.subTest(mutate=mutate):
                    receipt=self.make_archive(e)
                    if mutate=='raw': (e/'fixture.stdout').write_bytes(b'altered')
                    if mutate.startswith('parsed_'):
                        parsed=c.decode((e/'parsed.json').read_text())
                        if mutate=='parsed_bool': parsed[1]['result']=False
                        else: parsed[1]['other_empty']=1
                        (e/'parsed.json').write_text(json.dumps(parsed)); receipt['parsed_sha256']=c.sha(e/'parsed.json')
                    if mutate=='trace':
                        (e/'network.trace').write_bytes(b'100 socket() = 1\n100 +++ exited with 0 +++\n')
                        receipt['trace_sha256']=c.sha(e/'network.trace')
                    if mutate=='binary': (e/'queue_fixture').write_bytes(b'changed')
                    if mutate=='failed_build': receipt['commands'][1]['returncode']=1
                    if mutate=='timeout': receipt['commands'][2]['timed_out']=True
                    if mutate=='argv': receipt['commands'][2]['argv']=['./queue_fixture',RUN]
                    if mutate=='source': receipt['source_after']={}
                    if mutate=='missing_trace': (e/'network.trace').unlink()
                    if mutate=='missing_tools': receipt['tools_before']=receipt['tools_after']={}
                    (e/'receipt.json').write_text(json.dumps(receipt))
                    with self.assertRaises((ValueError,OSError)): c.verify(ROOT,e)

    def test_stale_pass_removed_before_startup_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            for name in ('summary.json','result.json'): (p/name).write_text('{"status":"PASS"}')
            with patch.object(run.subprocess,'Popen',side_effect=AssertionError('must not spawn')):
                with self.assertRaises(RuntimeError): run.startup(p,True)
            self.assertFalse((p/'summary.json').exists()); self.assertFalse((p/'result.json').exists())

    def test_timeout_first_error_survives_stream_finalization(self):
        class Child:
            pid=100; returncode=None
            def wait(self,timeout): raise subprocess.TimeoutExpired('synthetic',timeout)
            def poll(self): return None
        with tempfile.TemporaryDirectory() as tmp:
            e=Path(tmp); rec={'name':'fixture','argv':['synthetic'],'timeout_seconds':20,'returncode':None,
                             'timed_out':False,'stdout':'x.stdout','stderr':'x.stderr'}
            with patch.object(run.subprocess,'Popen',return_value=Child()),patch.object(run,'stop_owned',return_value=[]) as cleanup,patch.object(run,'digest',side_effect=OSError('synthetic read failure')):
                with self.assertRaises(subprocess.TimeoutExpired): run.command(rec,e,e,{})
            self.assertTrue(rec['timed_out']); self.assertEqual(cleanup.call_count,1)
            self.assertEqual(len(rec['finalization_errors']),2)

    def test_owned_group_cleanup_even_after_leader_exit(self):
        class ExitedLeader:
            pid=100; returncode=1
            def wait(self,timeout): return 1
            def poll(self): return 1
        child=ExitedLeader()
        with patch.object(run.os,'killpg') as kill:
            self.assertEqual(run.stop_owned(child),[])
            self.assertEqual(kill.call_args_list, [unittest.mock.call(100,run.signal.SIGTERM),unittest.mock.call(100,run.signal.SIGKILL)])
        with tempfile.TemporaryDirectory() as tmp:
            e=Path(tmp); rec={'name':'fixture','argv':['synthetic'],'timeout_seconds':20,'returncode':None,
                             'timed_out':False,'stdout':'f.stdout','stderr':'f.stderr'}
            with patch.object(run.subprocess,'Popen',return_value=child),patch.object(run,'stop_owned',return_value=[]) as cleanup:
                with self.assertRaisesRegex(RuntimeError,'nonzero'): run.command(rec,e,e,{})
            self.assertEqual(cleanup.call_count,1)

    def test_success_finalization_failure_and_failed_launch_stop(self):
        class Child:
            pid=100; returncode=0
            def wait(self,timeout): return 0
            def poll(self): return 0
        with tempfile.TemporaryDirectory() as tmp:
            e=Path(tmp)
            for launch in (False,True):
                rec={'name':'build','argv':['synthetic'],'timeout_seconds':60,'returncode':None,
                     'timed_out':False,'stdout':'b.stdout','stderr':'b.stderr'}
                with patch.object(run.subprocess,'Popen',side_effect=OSError('synthetic launch failure') if launch else None,return_value=Child()),patch.object(run,'digest',side_effect=OSError('synthetic read failure')):
                    with self.assertRaisesRegex(OSError,'launch failure' if launch else 'read failure'):
                        run.command(rec,e,e,{})

if __name__=='__main__': unittest.main()
