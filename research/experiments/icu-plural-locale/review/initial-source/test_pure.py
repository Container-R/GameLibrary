"""Finite synthetic record checks, zero subprocess/native calls."""
import copy,json,unittest
from pathlib import Path
from consume import validate_report,strict
from child import abi
P=json.loads(Path(__file__).with_name('protocol.json').read_text())

def record(config_id):
    c=next(c for c in P['configurations'] if c['id']==config_id)
    loads=[{'name':n,'phase':p} for n in ('icuuc','icui18n') for p in ('attempt','returned')]
    trace=[]
    for i,name in enumerate(['version','open']+['format']*6+['close'],1):
        a={'call':i,'name':name,'phase':'attempt'};b={'call':i,'name':name,'phase':'returned'}
        if name=='version':b.update(result=None,version=[76,1,0,0])
        elif name=='open':b.update(handle_nonnull=True,status=0,pattern_utf16_units=len(c['pattern']),parse_line=-99,parse_offset=-99,pre_context_units=[0]*16,post_context_units=[0]*16)
        elif name=='format':
            n=P['inputs'][i-3];s=c['expected'][i-3];a['input']=n;b.update(input=n,result=len(s),status=-127 if i==3 else 0,capacity_utf16=64,units=[ord(x) for x in s],argument_type='c_double')
        else:b['result']=None
        trace.extend([a,b])
    libs={n:{k:v[k] for k in ('requested','resolved','sha256')} for n,v in P['libraries'].items()}
    r={'uuid':'synthetic','config':config_id,'locale':c['locale'],'pattern':c['pattern'],'inputs':P['inputs'],'category':'COMPLETE_EXPECTED_OUTPUTS','abi':{k:P['abi'][k] for k in ('platform','machine','byteorder','pointer_size','int32_size','uint16_size','double_size','UParseError')},'libraries_before':libs,'libraries_after':copy.deepcopy(libs),'trace':trace,'loads':loads,'outputs':c['expected']}
    if config_id=='ar_omit_few':r['intent_acceptance']={'number':3,'intended':'FEW','actual':'OTHER','accepted':False}
    return r

def check(r):return validate_report(r,r['trace'],r['loads'],P,r['config'],'synthetic')
class Pure(unittest.TestCase):
    def test_local_abi_layout_only(self):
        self.assertEqual(abi(),{k:P['abi'][k] for k in abi()})
    def test_three_synthetic_controls(self):
        for c in P['configurations']:self.assertEqual(check(record(c['id']))['native_calls'],9)
    def test_missing_close(self):
        r=record('en_full');r['trace']=r['trace'][:-2]
        with self.assertRaises(ValueError):check(r)
    def test_output_status_capacity(self):
        for field,value in [('status',1),('result',64),('units',[70]),('input',True),('capacity_utf16',True)]:
            r=record('ar_full');r['trace'][11][field]=value
            with self.assertRaises(ValueError):check(r)
    def test_identity_and_intent(self):
        for field,value in [('locale','en'),('pattern','other'),('intent_acceptance',{'number':3,'intended':'FEW','actual':'OTHER','accepted':True})]:
            r=record('ar_omit_few');r[field]=value
            with self.assertRaises(ValueError):check(r)
    def test_json_rejections(self):
        for text in ('{"a":1,"a":2}','{"a":NaN}','{"a":1e999}'):
            with self.assertRaises(ValueError):strict(text)
if __name__=='__main__':unittest.main()
