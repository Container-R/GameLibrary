"""Hand-built synthetic schema exercise, not an author or OpenAL trace."""
import copy,hashlib,json,struct
from selftest import fixture
from check_numeric import CASES, PARTS, check_cases, consume, Invalid

checks=[{'stage':'synthetic-only','error':0}]
a=fixture(); metrics=check_cases(a);rows=[]
def add(event,case,data):rows.append({'seq':len(rows),'event':event,'case':case,'data':data})
add('begin',None,{'schema':1,'configuration_fully_excluded':False,'case_count':5,'sample_rate':48000,'frame_count_per_part':4800,'parts_per_case':3,'sample_format':'float32-le','pcm_format':'s16-le','pcm_positive_count':24,'pcm_negative_count':24,'pcm_amplitude':1024,'ordinary_device_calls':0,'capture_calls':0,'effect_calls':0})
add('global_ready',None,{'loopback_extension':True,'entries_present':True,'pcm_sha256':hashlib.sha256(struct.pack('<48h',*([1024]*24+[-1024]*24))).hexdigest(),'checks':checks})
for i,(name,model,ref,maximum,distance) in enumerate(CASES):
 enum=0xD002 if i<4 else 0xD004
 add('case_begin',name,{'id':name,'model':enum,'maximum':maximum,'distance':distance,'ratio':metrics[i]['expected_factor']})
 add('ready',name,{'checks':checks,'version':'1.1 ALSOFT 1.24.2','renderer':'OpenAL Soft','format':{'frequency':48000,'channels':0x1500,'type':0x1406,'hrtf':0,'limiter':0},'distance_model':enum,'source':{'reference':1.0,'maximum':float(maximum),'rolloff':1.0,'position':[0.0,0.0,-float(distance)]}})
 add('playing',name,{'state':0x1012,'checks':checks})
 for part,w in zip(PARTS,a[i]['windows']):
  add('window',name,w);add('window_checked',name,{'part':part,'state':0x1012,'checks':checks})
 add('case_metrics',name,{k:metrics[i][k] for k in ('rms','ratios')})
 add('cleanup',name,{'ok':True,'checks':checks,'failures':[]});add('case_pass',name,{'numeric_ok':True,'cleanup_ok':True})
add('success',None,{'cases':5,'render_calls':15,'frames':72000,'source_objects':5,'buffer_objects':5,'configuration_fully_excluded':False})
def encode(r):return ''.join(json.dumps(e,allow_nan=False)+'\n' for e in r)
consume(encode(rows));done=['complete_synthetic_stream']
for name,edit in [('missing_window',lambda r:r.pop(5)),('wrong_case',lambda r:r[5].update(case='linear-max')),('false_cleanup',lambda r:r[12]['data'].update(ok=False)),('forged_metrics',lambda r:r[11]['data'].update(rms=[99.0,99.0])),('trailing_event',lambda r:r.append(r[-1]))]:
 r=copy.deepcopy(rows);edit(r)
 try:consume(encode(r))
 except Invalid:done.append(name);continue
 raise AssertionError(name)
print(json.dumps({'status':'PASS','scope':'synthetic schema and arithmetic only, no native execution','checks':done}))
