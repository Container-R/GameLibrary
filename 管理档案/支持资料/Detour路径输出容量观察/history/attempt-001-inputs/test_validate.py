"""Pure synthetic consumer tests. No compiler, process, or native library calls."""
import copy
import json
from pathlib import Path
import tempfile
import signal
import unittest
from unittest.mock import patch, Mock
import validate as v
import run as runner

def sample():
    x = v.load_expected()
    x['setup']['refs'] = ['16','17','18']
    x['setup']['data_size'] = 1024
    for p in x['setup']['polygons']:
        for link in p['links']:
            link['ref'] = {'A':'16','B':'17','C':'18'}[link['ref']]
    for c in x['cases']:
        c['path'] = [{'A':'16','B':'17','C':'18'}.get(r,r) for r in c['path']]
    return x

class Consumer(unittest.TestCase):
    def test_control(self):
        result=v.validate(sample())
        self.assertEqual(result['cases'], 2)
        self.assertEqual(result['result_kind'], 'consumer_only')
        self.assertEqual(result['overall_acceptance_requires'], 'receipt.json status=pass after identity checks')
    def test_exact_types_and_finite(self):
        for bad in (True, 2.0, '2', None):
            x=sample();x['query_calls']=bad
            with self.subTest(bad=bad), self.assertRaises(ValueError): v.validate(x)
        for bad in (float('nan'),float('inf'),True,1):
            x=sample();x['setup']['filter'][2]=bad
            with self.subTest(bad=bad), self.assertRaises(ValueError): v.validate(x)
    def test_strict_json(self):
        for raw in ('{"a":1,"a":2}','{"a":NaN}','{"a":Infinity}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):v.strict_json(raw)
    def test_oracle_tamper(self):
        x=sample()
        with patch.object(Path,'read_bytes',return_value=b'{}'):
            with self.assertRaises(ValueError):v.validate(x)
    def test_case_cardinality_order_and_unknown_ref(self):
        samples=[]
        x=sample();x['cases'].pop();samples.append(x)
        x=sample();x['cases'].append(copy.deepcopy(x['cases'][0]));samples.append(x)
        x=sample();x['cases'].reverse();samples.append(x)
        x=sample();x['cases'][0]['path'][0]='19';samples.append(x)
        x=sample();x['setup']['refs']=['16','16','18'];samples.append(x)
        x=sample();x['setup']['refs'][0]='016';samples.append(x)
        for x in samples:
            with self.subTest(x=x),self.assertRaises(ValueError):v.validate(x)
    def test_status_count_sentinel_setup(self):
        samples=[]
        for key,value in [('status',1073741824),('path_count',3),('indices',[0,1,2]),('path',['16','17','18'])]:
            x=sample();x['cases'][0][key]=value;samples.append(x)
        x=sample();x['setup']['polygons'][1]['links'].reverse();samples.append(x)
        x=sample();x['setup']['vertices'][0][0]=1.0;samples.append(x)
        x=sample();x['setup']['refs_valid']=1;samples.append(x)
        x=sample();x['extra']=0;samples.append(x)
        for x in samples:
            with self.subTest(x=x),self.assertRaises(ValueError):v.validate(x)
    def test_size_and_failure(self):
        for size in (0,-1,True,1024.0,1048577):
            x=sample();x['setup']['data_size']=size
            with self.subTest(size=size),self.assertRaises(ValueError):v.validate(x)
        x=sample();x['status']='fail'
        with self.assertRaises(ValueError):v.validate(x)

class RunnerPureGuards(unittest.TestCase):
    def test_existing_attempt_refused_before_process(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'execution/attempt-001').mkdir(parents=True)
            marker=root/'execution/attempt-001/receipt.json';marker.write_text('historical')
            with patch.object(runner,'ROOT',root),patch.object(runner.subprocess,'Popen') as process:
                with self.assertRaises(FileExistsError):runner.main()
                process.assert_not_called()
            self.assertEqual(marker.read_text(),'historical')
    def test_empty_code_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'CODE-MANIFEST.json').write_text('{}')
            with self.assertRaises(ValueError):runner.identities(root)
    def test_cleanup_targets_group_even_if_leader_exits(self):
        child=Mock();child.pid=123;child.wait.return_value=0
        with patch.object(runner.os,'killpg') as kill:
            self.assertEqual(runner.stop_group(child),[])
            self.assertEqual(kill.call_args_list, [unittest.mock.call(123,signal.SIGTERM),unittest.mock.call(123,signal.SIGKILL)])

if __name__ == '__main__': unittest.main()
