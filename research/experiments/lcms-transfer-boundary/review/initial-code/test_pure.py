"""Synthetic checks; two guarded Python startup children, zero target CMM calls."""
import copy,json,unittest
from pathlib import Path
from check import *

def synthetic():
 ref=load((Path(__file__).parent/'protocol-reference.json').read_text())
 decoded=[float(x) for x in ref['source_linear']];src=[128/255,64/255,192/255]
 data={'status':'PASS','configuration':copy.deepcopy(CONFIG),'abi':copy.deepcopy(ABI),'library_before':LIB_SHA,'library_after':LIB_SHA,'version':2190,'calls':expected_calls(),'errors':[],'callback_errors':[],'cleanup_complete':True,'lcms_mappings':['1000-2000 r-xp 00000000 00:00 1 '+LIB],'source_encoded':src,'decoded':decoded,'operations':[{'name':'decode','input':src,'output':decoded}],'conditions':[]}
 for i,(name,alpha) in enumerate((('main',128/255),('opaque',1.0))):
  working=[x*alpha for x in decoded];output=[float(x) for x in ref['rows'][i]['encoded_from_linear']]
  data['operations'].append({'name':name,'input':working,'output':output})
  data['conditions'].append({'name':name,'alpha':alpha,'working':working,'output':output,'encoded_direct':[x*alpha for x in src],'output_alpha':1.0})
 return data,ref

def raw(data):
 lines=[]
 for call in data['calls']:
  lines.append('CALL_JSON='+json.dumps({'phase':'ENTER','index':call['index'],'name':call['name'],'arguments':call['arguments']}))
  lines.append('CALL_JSON='+json.dumps({'phase':'RETURN','index':call['index'],'name':call['name'],'result':call['result']}))
 lines.append('RESULT_JSON='+json.dumps(data));return ('\n'.join(lines)+'\n').encode()

class FiniteTests(unittest.TestCase):
 def test_literal_control_and_raw(self):
  d,r=synthetic();self.assertEqual(check_payload(d,r)['conversion_calls'],3);same(parse_stdout(raw(d)),d,'synthetic raw')
 def test_numeric_binding_and_channel_negative(self):
  for mutation in ('working','reverse_input','swapped','nan','callback','format','count'):
   d,r=synthetic()
   if mutation=='working':d['conditions'][0]['working'][0]+=.001
   if mutation=='reverse_input':d['operations'][1]['input']=[0.0,0.0,0.0]
   if mutation=='swapped':d['operations'][1]['output']=list(reversed(d['operations'][1]['output']))
   if mutation=='nan':d['operations'][0]['output'][0]=float('nan')
   if mutation=='callback':d['callback_errors']=['injected']
   if mutation=='format':d['calls'][8]['result']=True
   if mutation=='count':d['calls'].pop()
   with self.assertRaises(ValueError,msg=mutation):check_payload(d,r)
 def test_raw_mismatch_and_json(self):
  d,_=synthetic();good=raw(d)
  for bad in (good+b'ERROR injected\n',good+b'RESULT_JSON={}\n',good.replace(b'"phase": "ENTER"',b'"phase": "RETURN"',1)):
   with self.assertRaises(ValueError):parse_stdout(bad)
  for text in ('{"x":1,"x":2}','{"x":NaN}','{"x":1e999}'):
   with self.assertRaises(ValueError):load(text)
 def test_startup_freshness(self):
  import tempfile,subprocess,shutil,sys
  source=Path(__file__).resolve().parent
  for kind in ('optimized','import-failure'):
   with tempfile.TemporaryDirectory() as temp:
    target=Path(temp)
    for name in SOURCES:shutil.copy2(source/name,target/name)
    (target/'summary.json').write_text('{"status":"PASS","synthetic":true}')
    if kind=='import-failure':(target/'check.py').write_text('raise RuntimeError("synthetic local import failure")\n')
    argv=[sys.executable,*(['-O'] if kind=='optimized' else []),str(target/'run.py')]
    result=subprocess.run(argv,capture_output=True,text=True,timeout=5)
    self.assertNotEqual(result.returncode,0)
    self.assertFalse((target/'summary.json').exists())
    self.assertFalse((target/'evidence').exists())
    self.assertIn('optimized runner rejected' if kind=='optimized' else 'synthetic local import failure',result.stderr)

 def test_tolerance_not_exact_quantization(self):
  d,r=synthetic();d['operations'][1]['output'][1]-=.000095;d['conditions'][0]['output']=d['operations'][1]['output']
  self.assertEqual(check_payload(d,r)['status'],'PASS')
  self.assertEqual(math.floor(d['operations'][1]['output'][1]*255+.5),44)

if __name__=='__main__':unittest.main()
