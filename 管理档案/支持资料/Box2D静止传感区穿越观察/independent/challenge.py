"""Independent finite synthetic challenges; no compiler or native subprocess."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import copy,hashlib,json,re,shutil,tempfile,unittest
from unittest import mock
from contextlib import ExitStack
import run as r
import validate as v
import test_validate as author
ROOT=Path(__file__).resolve().parents[1]

class Review(unittest.TestCase):
 def setUp(self):
  actual=sys.flags
  class Flags:
   optimize=0
   def __getattr__(self,n):return getattr(actual,n)
  for patch in [mock.patch.object(r.sys,'flags',Flags()),mock.patch.object(r.subprocess,'Popen',side_effect=AssertionError('real subprocess forbidden'))]:
   patch.start();self.addCleanup(patch.stop)
 def prepare(self,p):
  for n in (*r.CODE_FILES,'CODE-MANIFEST.json'):shutil.copyfile(ROOT/n,p/n)
  return r.sha((p/'CODE-MANIFEST.json').read_bytes())
 def build(self,p,d):
  def cmd(argv,work,*a,**k):
   (work/'sensor_fixture').write_bytes(b'not executable synthetic artifact');return b'',{'status':'mock'}
  with mock.patch.object(r,'source_snapshot',return_value={'synthetic':'bound'}),mock.patch.object(r,'copy_sources'),mock.patch.object(r,'command',side_effect=cmd):
   return r.operate('build','b',d,sources=p,root=p)
 def patches(self):
  s=ExitStack();s.enter_context(mock.patch.object(r,'source_snapshot',return_value={'synthetic':'bound'}));s.enter_context(mock.patch.object(r,'copy_sources'));return s
 def test_literal_schema_and_six_oracle_rows(self):
  spec=v.expected();self.assertEqual(len(spec),314)
  rows=author.control();self.assertEqual(v.validate(author.encoded(rows))['steps'],6)
  for case,event,cache in [('events_on',[(1,0),(0,1),(0,0)],[1,0,0]),('visitor_events_off',[(0,0)]*3,[0,0,0])]:
   for i in range(1,4):
    slots={x['key']:x['value'] for x in spec if x['case']==case and x['phase']==f'step_{i}'}
    self.assertEqual((slots['begin_count'],slots['end_count']),event[i-1]);self.assertEqual(slots['cache_count'],cache[i-1]);self.assertEqual(slots['visitor.pose'],[float(-2+4*i),0.,1.,0.])
  for case,phase,key,value in [('events_on','step_2','end_count',0),('events_on','step_3','cache_count',1),('visitor_events_off','step_2','visitor.sensor_events',True),('events_on','setup','polygon.normal.0',[0.,1.]),('events_on','step_1','begin.sensor',[1,0,65536])]:
   bad=copy.deepcopy(rows);author.location(bad,case,phase,key)['value']=value
   with self.subTest(key=key),self.assertRaises(ValueError):v.validate(author.encoded(bad))
 def test_missing_partial_and_duplicate_output(self):
  raw=author.encoded(author.control())
  for bad in [b'',raw[:-2],raw+b'\n',raw.replace(b'"case":',b'"case":"wrong", "case":',1)]:
   with self.assertRaises(ValueError):v.validate(bad)
 def test_copied_artifact_rejected_before_command(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);d=self.prepare(p);self.build(p,d);original=shutil.copyfile
   def altered(src,dst,*a,**kw):
    result=original(src,dst,*a,**kw)
    if Path(dst).name=='sensor_fixture':Path(dst).write_bytes(b'altered copy')
    return result
   with self.patches(),mock.patch.object(r.shutil,'copyfile',side_effect=altered),mock.patch.object(r,'command') as command:
    with self.assertRaisesRegex(ValueError,'copied artifact identity'):r.operate('execute','e',d,build_name='b',root=p)
    command.assert_not_called()
   self.assertEqual(r.read_json(p/'attempts/e/receipt.json')['status'],'fail')
 def test_changed_consumer_never_imported(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);d=self.prepare(p);self.build(p,d)
   def cmd(argv,work,*a,**kw):
    (work/'validate.py').write_text('raise RuntimeError("must not import")');return author.encoded(author.control()),{'status':'mock'}
   with self.patches(),mock.patch.object(r,'command',side_effect=cmd),mock.patch.object(r,'consumer') as load:
    with self.assertRaisesRegex(ValueError,'validate.py identity'):r.operate('execute','e',d,build_name='b',root=p)
    load.assert_not_called()
 def test_build_receipt_mutation_rejected_after_consumer(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);d=self.prepare(p);self.build(p,d)
   def cmd(*a,**kw):
    f=p/'attempts/b/receipt.json';f.write_bytes(f.read_bytes()+b' ')
    return author.encoded(author.control()),{'status':'mock'}
   with self.patches(),mock.patch.object(r,'command',side_effect=cmd):
    with self.assertRaisesRegex(ValueError,'build receipt changed'):r.operate('execute','e',d,build_name='b',root=p)
   self.assertEqual(r.read_json(p/'attempts/e/validation.json')['result_kind'],'consumer_only')
   self.assertEqual(r.read_json(p/'attempts/e/receipt.json')['status'],'fail')
 def test_source_set_and_argv_static(self):
  upstream=ROOT.parent/'box2d-sensor-native-gate/upstream'
  self.assertEqual(len(r.source_snapshot(upstream,ROOT/'SOURCE-MANIFEST.json')),84)
  c=re.findall(r'^\s+(\w+\.c)$',(upstream/'src/CMakeLists.txt').read_text(),re.M)
  argv=r.read_json(ROOT/'BUILD-ARGV.json')
  self.assertEqual([x for x in argv if x.startswith('upstream/src/')],['upstream/src/'+x for x in c]);self.assertEqual(len(c),43)
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);shutil.copytree(upstream,p/'upstream');(p/'upstream/src/sensor.c').unlink()
   with self.assertRaisesRegex(ValueError,'source set mismatch'):r.source_snapshot(p/'upstream',ROOT/'SOURCE-MANIFEST.json')
 def test_stale_and_failed_build_do_not_launch(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);d=self.prepare(p);self.build(p,d)
   f=p/'attempts/b/receipt.json';doc=r.read_json(f);doc['status']='fail';r.save(f,doc)
   with mock.patch.object(r,'command') as cmd:
    with self.assertRaisesRegex(ValueError,'accepted build required'):r.operate('execute','e',d,build_name='b',root=p)
    with self.assertRaises(FileExistsError):r.operate('execute','e',d,build_name='b',root=p)
    cmd.assert_not_called()
 def test_v2_diagnostic_identity_and_exactness(self):
  trusted=(ROOT/'reviewed-build-stderr.txt').read_bytes()
  self.assertEqual(hashlib.sha256(trusted).hexdigest(),'c55f639fa5da94fed9737ff07f07048c47386213d14fe39dbefaf75e281ff4b5')
  self.assertEqual(len(trusted),32263)
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);f=p/'reviewed-build-stderr.txt'
   with self.assertRaises(FileNotFoundError):r.build_diagnostics(b'',f)
   f.write_bytes(trusted)
   self.assertEqual(r.build_diagnostics(trusted,f),'reviewed_exact_warning')
   for bad in [trusted[:-1],trusted+b'fixture warning',trusted.replace(b'warning:',b'error:',1),b'unrelated']:
    with self.assertRaises(ValueError):r.build_diagnostics(bad,f)
   f.write_bytes(trusted+b' ')
   with self.assertRaises(ValueError):r.build_diagnostics(b'',f)
 def test_v2_rebound_bad_trustfile_and_native_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);self.prepare(p);f=p/'reviewed-build-stderr.txt';trusted=f.read_bytes();f.write_bytes(b'new allowed diagnostics')
   doc=r.read_json(p/'CODE-MANIFEST.json');doc['files']['reviewed-build-stderr.txt']=r.sha(f.read_bytes());r.save(p/'CODE-MANIFEST.json',doc)
   with self.assertRaisesRegex(ValueError,'reviewed diagnostic identity'):r.code_snapshot(p,r.sha((p/'CODE-MANIFEST.json').read_bytes()))
   f.write_bytes(trusted)
   for rc,out,build in [(0,b'',False),(1,b'',True),(0,b'nonempty',True)]:
    child=mock.Mock(pid=123,returncode=rc);child.communicate.return_value=(out,trusted);child.wait.return_value=rc
    with mock.patch.object(r.subprocess,'Popen',return_value=child),mock.patch.object(r.os,'killpg') as kill:
     with self.assertRaises(ValueError):r.command(['mock'],p,20,{},'mock',empty_stdout=build)
     self.assertEqual(kill.call_count,2)
if __name__=='__main__':unittest.main(verbosity=2)
