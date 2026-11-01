"""Finite portable archive checks. No ctypes/Pillow imports or native calls."""
from pathlib import Path,PurePosixPath
import hashlib,json,math,datetime,uuid
LIB='/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages/pillow.libs/liblcms2-88eaba2f.so.2.0.19'
LIB_SHA='4cf9f69016c7804bcb4fa56f5bbc55640cb1b7196ac7b93ba29ed9df9bd9ff4d'
PROTOCOL='31792686b01bbe1a71d03fc66e7852e1771eb02dabf7431db43aa8f1d5fd69e6'
HELPER='bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970'
REF_SHA='ef18c62716121f7c1d52d39c226b5fe89d555942e73556807de96dc30f479412'
SOURCES=('PROTOCOL.md','protocol-reference.py','protocol-reference.json','isolation.py','child.py','run.py','check.py','test_pure.py')
BASE={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'}
FORMAT=0x440018
CONFIG={'white':[.3127,.3290,1.0],'primaries':[[.64,.33,1.0],[.30,.60,1.0],[.15,.06,1.0]],'gamma':1.0,'format':FORMAT,'intent':1,'flags':0x140,'source_rgb':[128,64,192],'alphas':[128/255,1.0]}
ABI={'int':[4,4],'uint32':[4,4],'pointer':[8,8],'double':[8,8],'xyY':[24,8,0,8,16],'triple':[72,8,0,24,48],'byteorder':'little','machine':'x86_64','platform':'linux'}
CALLS=['cmsGetEncodedCMMversion','cmsSetLogErrorHandler','cmsCreate_sRGBProfile','cmsBuildGamma','cmsCreateRGBProfile','cmsFreeToneCurve','cmsCreateTransform','cmsCreateTransform','cmsGetTransformInputFormat','cmsGetTransformOutputFormat','cmsGetTransformInputFormat','cmsGetTransformOutputFormat','cmsDoTransform','cmsDoTransform','cmsDoTransform','cmsDeleteTransform','cmsDeleteTransform','cmsCloseProfile','cmsCloseProfile','cmsSetLogErrorHandler']
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pairs(xs):
 out={}
 for k,v in xs:
  need(k not in out,'duplicate JSON key');out[k]=v
 return out
def finite(v):
 if type(v) is float:need(math.isfinite(v),'nonfinite JSON')
 elif isinstance(v,dict):
  for x in v.values():finite(x)
 elif isinstance(v,list):
  for x in v:finite(x)
 return v
def load(s):
 def bad(x):raise ValueError('nonfinite constant '+x)
 return finite(json.loads(s,object_pairs_hook=pairs,parse_constant=bad))
def same(a,b,msg):
 need(type(a) is type(b),msg+' type')
 if isinstance(b,dict):
  need(set(a)==set(b),msg+' keys')
  for k in b:same(a[k],b[k],msg+'.'+k)
 elif isinstance(b,list):
  need(len(a)==len(b),msg+' length')
  for i,(x,y) in enumerate(zip(a,b)):same(x,y,msg+str(i))
 else:need(a==b,msg+' value')
def triple(v,label):
 need(type(v) is list and len(v)==3,label+' shape')
 for x in v:need(type(x) is float and math.isfinite(x) and 0<=x<=1,label+' finite/range/type')
def near(a,b,label):
 triple(a,label)
 for x,y in zip(a,b):need(abs(x-y)<=.0001,label+' tolerance')
def expected_calls():
 args=[[],['install'],[],[None,1.0],['D65','Rec709','shared-gamma-1'],['gamma'],['srgb',FORMAT,'linear',FORMAT,1,320],['linear',FORMAT,'srgb',FORMAT,1,320],['forward'],['forward'],['reverse'],['reverse'],['forward','decode',1,24],['reverse','main',1,24],['reverse','opaque',1,24],['forward'],['reverse'],['srgb'],['linear'],['restore-null']]
 results=[2190,None,True,True,True,None,True,True,FORMAT,FORMAT,FORMAT,FORMAT,None,None,None,None,None,1,1,None]
 return [dict(index=i+1,name=n,arguments=a,result=r,status='RETURNED') for i,(n,a,r) in enumerate(zip(CALLS,args,results))]
def check_payload(data,ref):
 need(type(data['conditions']) is list and len(data['conditions'])==2,'condition count')
 same(data['status'],'PASS','status');same(data['configuration'],CONFIG,'configuration');same(data['abi'],ABI,'ABI')
 same(data['library_before'],LIB_SHA,'library before');same(data['library_after'],LIB_SHA,'library after')
 same(data['version'],2190,'version');same(data['calls'],expected_calls(),'API calls');same(data['errors'],[],'CMM errors');same(data['callback_errors'],[],'callback errors')
 same(data['cleanup_complete'],True,'cleanup')
 maps=data['lcms_mappings'];need(type(maps) is list and len(maps)>0,'mappings')
 for line in maps:
  need(type(line) is str and len(line.split())>=6 and line.split()[-1]==LIB,'mapped library')
 same(data['source_encoded'],[128/255,64/255,192/255],'source')
 ops=data['operations'];need(type(ops) is list and len(ops)==3,'operations')
 same([x['name'] for x in ops],['decode','main','opaque'],'operation names')
 same(ops[0]['input'],data['source_encoded'],'actual decode input')
 decoded=ops[0]['output'];near(decoded,[float(x) for x in ref['source_linear']],'decode')
 same(data['decoded'],decoded,'decoded association')
 for i,(alpha,name) in enumerate(((128/255,'main'),(1.0,'opaque'))):
  row=data['conditions'][i];same(row['name'],name,'condition name');same(row['alpha'],alpha,'alpha')
  working=[x*alpha for x in decoded];same(row['working'],working,'actual host arithmetic');same(ops[i+1]['input'],working,'reverse actual input')
  output=ops[i+1]['output'];near(output,[float(x) for x in ref['rows'][i]['encoded_from_linear']],'reverse '+name)
  same(row['output'],output,'condition output');same(row['output_alpha'],1.0,'opaque output alpha')
  direct=[x*alpha for x in data['source_encoded']];same(row['encoded_direct'],direct,'direct arithmetic')
  if i==0:
   for x,y in zip(output,direct):need(abs(x-y)>.0485,'main separation')
  else:near(output,data['source_encoded'],'opaque control')
 return {'status':'PASS','conditions':2,'conversion_calls':3,'c_api_calls':20,'scope':'finite normalized values; no exact byte/visual/GPU claim'}
def parse_stdout(raw):
 lines=raw.decode('utf-8').splitlines();events=[];result=None
 for line in lines:
  if line.startswith('CALL_JSON='):
   need(result is None,'call after result');events.append(load(line[10:]))
  elif line.startswith('RESULT_JSON='):
   need(result is None,'duplicate result');result=load(line[12:])
  else:raise ValueError('unexpected stdout')
 need(result is not None,'missing result')
 expected=[]
 for call in result['calls']:
  expected.append({'phase':'ENTER','index':call['index'],'name':call['name'],'arguments':call['arguments']})
  expected.append({'phase':'RETURN','index':call['index'],'name':call['name'],'result':call['result']})
 same(events,expected,'raw calls');return result

def consume(source,evidence):
 root=Path(source);out=Path(evidence);r=load((out/'receipt.json').read_text());same(r['status'],'PASS','receipt')
 rid=r['uuid'];need(type(rid) is str and str(uuid.UUID(rid))==rid and out.name==rid,'UUID')
 original=PurePosixPath(r['original_source']);inv=PurePosixPath(r['original_invocation'])
 need(original.is_absolute() and '..' not in original.parts and inv==original/'evidence'/rid,'original paths')
 sources={n:sha(root/n) for n in SOURCES};need(sources['PROTOCOL.md']==PROTOCOL and sources['isolation.py']==HELPER and sources['protocol-reference.json']==REF_SHA,'fixed source pins')
 same(r['source_before'],sources,'before sources');same(r['source_after'],sources,'after sources')
 same(r['library_before'],LIB_SHA,'parent library before');same(r['library_after'],LIB_SHA,'parent library after')
 same(r['base_environment'],BASE,'base environment');same(r['selected_environment'],{k:str(inv/'environment'/k) for k in ('HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR')},'environment')
 p=r['process'];same(p['status'],'RETURNED','process status');same(p['exit_code'],0,'exit');need(type(p['pid']) is int and p['pid']>0,'pid')
 need(type(r['python_path']) is str and PurePosixPath(r['python_path']).is_absolute(),'python path')
 same(p['argv'],[r['python_path'],str(original/'child.py')],'argv');same(p['cwd'],str(original),'cwd')
 need(r['python_before']==r['python_after'] and type(r['python_before']) is str and len(r['python_before'])==64,'Python identity')
 for name in ('attempted_utc','returned_utc'):need(datetime.datetime.fromisoformat(p[name]).utcoffset()==datetime.timedelta(0),'UTC timestamp')
 need(p['returned_utc']>=p['attempted_utc'],'timestamp order')
 same(r['outputs'],{n:sha(out/n) for n in ('stdout.txt','stderr.txt','result.json')},'outputs')
 need((out/'stderr.txt').read_bytes()==b'','stderr');data=parse_stdout((out/'stdout.txt').read_bytes());same(data,load((out/'result.json').read_text()),'raw parsed')
 return check_payload(data,load((root/'protocol-reference.json').read_text()))
if __name__=='__main__':
 import sys
 need(len(sys.argv)==3,'usage check.py SOURCE_ROOT EVIDENCE_UUID')
 print(json.dumps(consume(sys.argv[1],sys.argv[2]),sort_keys=True))
