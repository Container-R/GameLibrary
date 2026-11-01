"""Independent finite archive oracle; stdlib only, no author imports/native calls."""
import json,hashlib,math,sys
from pathlib import Path
from decimal import Decimal,localcontext

def require(ok,message):
 if not ok:raise ValueError(message)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def strict(s):
 def pairs(items):
  d={}
  for k,v in items:
   require(k not in d,'duplicate key');d[k]=v
  return d
 def bad(s):raise ValueError(s)
 return json.loads(s,object_pairs_hook=pairs,parse_constant=bad)
def equal(x,y):return json.dumps(x,sort_keys=True,allow_nan=False)==json.dumps(y,sort_keys=True,allow_nan=False)
def main(source,archive):
 s=Path(source);a=Path(archive);r=strict((a/'receipt.json').read_text())
 require(r['status']=='PASS' and r['uuid']==a.name,'receipt identity')
 require(r['process']['status']=='RETURNED' and type(r['process']['exit_code']) is int and r['process']['exit_code']==0,'exit')
 require('timeout' not in r['process'] and 'drain_incomplete' not in r['process'],'timeout')
 require((a/'stderr.txt').read_bytes()==b'','stderr')
 require(r['source_before']==r['source_after']=={n:digest(s/n) for n in r['source_before']},'sources')
 require(r['library_before']==r['library_after']=='4cf9f69016c7804bcb4fa56f5bbc55640cb1b7196ac7b93ba29ed9df9bd9ff4d','library')
 require(r['outputs']=={n:digest(a/n) for n in ['stdout.txt','stderr.txt','result.json']},'output hashes')
 raw=(a/'stdout.txt').read_text().splitlines();require(len(raw)==41,'40 call events and final')
 require(all(x.startswith('CALL_JSON=') for x in raw[:40]) and raw[40].startswith('RESULT_JSON='),'raw envelope')
 d=strict(raw[40][12:]);require(equal(d,strict((a/'result.json').read_text())),'raw/result binding')
 names=['cmsGetEncodedCMMversion','cmsSetLogErrorHandler','cmsCreate_sRGBProfile','cmsBuildGamma','cmsCreateRGBProfile','cmsFreeToneCurve','cmsCreateTransform','cmsCreateTransform','cmsGetTransformInputFormat','cmsGetTransformOutputFormat','cmsGetTransformInputFormat','cmsGetTransformOutputFormat','cmsDoTransform','cmsDoTransform','cmsDoTransform','cmsDeleteTransform','cmsDeleteTransform','cmsCloseProfile','cmsCloseProfile','cmsSetLogErrorHandler']
 results=[2190,None,True,True,True,None,True,True,4456472,4456472,4456472,4456472,None,None,None,None,None,1,1,None]
 require(len(d['calls'])==20,'call count')
 for i,(n,v,c) in enumerate(zip(names,results,d['calls'])):
  require(c['name']==n and c['index']==i+1 and c['status']=='RETURNED' and equal(c['result'],v),'literal lifecycle')
  enter=strict(raw[2*i][10:]);ret=strict(raw[2*i+1][10:])
  require(equal(enter,{'phase':'ENTER','index':i+1,'name':n,'arguments':c['arguments']}),'raw entry')
  require(equal(ret,{'phase':'RETURN','index':i+1,'name':n,'result':v}),'raw return')
 require(d['status']=='PASS' and d['cleanup_complete'] is True and d['errors']==[] and d['callback_errors']==[],'cleanup/errors')
 require(d['calls'][-1]['arguments']==['restore-null'],'handler restoration last')
 require(d['calls'][12]['arguments']==['forward','decode',1,24] and d['calls'][13]['arguments']==['reverse','main',1,24] and d['calls'][14]['arguments']==['reverse','opaque',1,24],'conversion count/shape')
 require(d['configuration']['format']==4456472 and d['configuration']['intent']==1 and d['configuration']['flags']==320,'format/config')
 with localcontext() as ctx:
  ctx.prec=70;D=Decimal;encoded=[D(x)/255 for x in [128,64,192]]
  decoded=[((x+D('.055'))/D('1.055'))**D('2.4') for x in encoded]
  expected=[[float(D('1.055')*(x*alpha)**(D(5)/12)-D('.055')) for x in decoded] for alpha in [D(128)/255,D(1)]]
 def near(values,expected):
  require(len(values)==3,'triple')
  require(all(type(x) is float and math.isfinite(x) and 0<=x<=1 and abs(x-y)<=1e-4 for x,y in zip(values,expected)),'finite/reference')
 ops=d['operations'];require([x['name'] for x in ops]==['decode','main','opaque'],'operation order')
 require(equal(ops[0]['input'],[128/255,64/255,192/255]),'actual source array')
 near(ops[0]['output'],list(map(float,decoded)));require(equal(d['decoded'],ops[0]['output']),'decoded link')
 for i,alpha in enumerate([128/255,1.0]):
  row=d['conditions'][i];working=[x*alpha for x in ops[0]['output']]
  require(equal(row['alpha'],alpha) and equal(row['working'],working) and equal(ops[i+1]['input'],working),'actual host/input link')
  near(ops[i+1]['output'],expected[i]);require(equal(row['output'],ops[i+1]['output']),'output link')
  direct=[x*alpha for x in [128/255,64/255,192/255]];require(equal(row['encoded_direct'],direct),'direct branch')
  if i==0:require(all(abs(x-y)>.0485 for x,y in zip(row['output'],direct)),'domain separation')
 return {'uuid':r['uuid'],'status':'ACCEPTED_FINITE_OBSERVATION','c_api_calls':20,'conversions':3,'conditions':2,'decoded':d['decoded'],'main':ops[1]['output'],'opaque':ops[2]['output'],'scope':'independent raw lifecycle/numerical/source consistency; complementary author full ABI/environment/schema checks, not authenticated execution'}
if __name__=='__main__':print(json.dumps(main(*sys.argv[1:]),indent=2))
