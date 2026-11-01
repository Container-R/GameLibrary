"""Original single finite CMM child. No native entry on import."""
import json,math,sys,platform
from pathlib import Path
from check import LIB,LIB_SHA,CONFIG,ABI,FORMAT,need,same,sha

def safe(value):
 if type(value) is float and not math.isfinite(value):return {'nonfinite':repr(value)}
 if isinstance(value,dict):return {k:safe(v) for k,v in value.items()}
 if isinstance(value,list):return [safe(v) for v in value]
 return value

def main():
 import ctypes as C
 data={'status':'ATTEMPTED','calls':[],'errors':[],'callback_errors':[],'operations':[],'conditions':[]}
 lib=None; callback=None; handler=False;curve=None;srgb=None;linear=None;forward=None;reverse=None;failure=None
 def emit(prefix,value):print(prefix+json.dumps(safe(value),allow_nan=False,sort_keys=True),flush=True)
 def invoke(name,args,summary,kind='void'):
  index=len(data['calls'])+1
  row={'index':index,'name':name,'arguments':summary,'status':'ATTEMPTED'};data['calls'].append(row)
  emit('CALL_JSON=',{'phase':'ENTER','index':index,'name':name,'arguments':summary})
  result=getattr(lib,name)(*args)
  reported=bool(result) if kind=='pointer' else result
  row.update(status='RETURNED',result=reported)
  emit('CALL_JSON=',{'phase':'RETURN','index':index,'name':name,'result':reported})
  return result
 def errors():need(not data['errors'] and not data['callback_errors'],'CMM/callback diagnostic')
 try:
  class xyY(C.Structure):_fields_=[('x',C.c_double),('y',C.c_double),('Y',C.c_double)]
  class Triple(C.Structure):_fields_=[('Red',xyY),('Green',xyY),('Blue',xyY)]
  data['abi']={'int':[C.sizeof(C.c_int),C.alignment(C.c_int)],'uint32':[C.sizeof(C.c_uint32),C.alignment(C.c_uint32)],'pointer':[C.sizeof(C.c_void_p),C.alignment(C.c_void_p)],'double':[C.sizeof(C.c_double),C.alignment(C.c_double)],'xyY':[C.sizeof(xyY),C.alignment(xyY),xyY.x.offset,xyY.y.offset,xyY.Y.offset],'triple':[C.sizeof(Triple),C.alignment(Triple),Triple.Red.offset,Triple.Green.offset,Triple.Blue.offset],'byteorder':sys.byteorder,'machine':platform.machine(),'platform':sys.platform}
  same(data['abi'],ABI,'preload ABI')
  data['library_before']=sha(LIB);need(data['library_before']==LIB_SHA,'library bytes')
  lib=C.CDLL(LIB)
  relevant=[line for line in Path('/proc/self/maps').read_text().splitlines() if 'lcms' in line.lower()]
  need(relevant and all(line.split()[-1]==LIB for line in relevant),'loaded library mappings');data['lcms_mappings']=relevant
  callback_type=C.CFUNCTYPE(None,C.c_void_p,C.c_uint32,C.c_char_p)
  def log_error(_context,code,text):
   try:data['errors'].append({'code':int(code),'message':(text or b'').decode('utf-8','replace')[:1024]})
   except BaseException as e:data['callback_errors'].append(type(e).__name__)
  callback=callback_type(log_error)
  bindings={
   'cmsGetEncodedCMMversion':([],C.c_int),
   'cmsSetLogErrorHandler':([callback_type],None),
   'cmsCreate_sRGBProfile':([],C.c_void_p),
   'cmsBuildGamma':([C.c_void_p,C.c_double],C.c_void_p),
   'cmsCreateRGBProfile':([C.POINTER(xyY),C.POINTER(Triple),C.POINTER(C.c_void_p)],C.c_void_p),
   'cmsFreeToneCurve':([C.c_void_p],None),
   'cmsCreateTransform':([C.c_void_p,C.c_uint32,C.c_void_p,C.c_uint32,C.c_uint32,C.c_uint32],C.c_void_p),
   'cmsDoTransform':([C.c_void_p,C.c_void_p,C.c_void_p,C.c_uint32],None),
   'cmsGetTransformInputFormat':([C.c_void_p],C.c_uint32),
   'cmsGetTransformOutputFormat':([C.c_void_p],C.c_uint32),
   'cmsDeleteTransform':([C.c_void_p],None),
   'cmsCloseProfile':([C.c_void_p],C.c_int)}
  for name,(args,result) in bindings.items():getattr(lib,name).argtypes=args;getattr(lib,name).restype=result
  data['version']=invoke('cmsGetEncodedCMMversion',[],[],'int');need(data['version']==2190,'version self-report')
  invoke('cmsSetLogErrorHandler',[callback],['install']);handler=True;errors()
  srgb=invoke('cmsCreate_sRGBProfile',[],[],'pointer');need(srgb is not None,'sRGB null');errors()
  curve=invoke('cmsBuildGamma',[None,1.0],[None,1.0],'pointer');need(curve is not None,'gamma null');errors()
  white=xyY(.3127,.3290,1.0);primaries=Triple(xyY(.64,.33,1.0),xyY(.30,.60,1.0),xyY(.15,.06,1.0));curves=(C.c_void_p*3)(curve,curve,curve)
  data['configuration']={'white':[white.x,white.y,white.Y],'primaries':[[x.x,x.y,x.Y] for x in (primaries.Red,primaries.Green,primaries.Blue)],'gamma':1.0,'format':FORMAT,'intent':1,'flags':320,'source_rgb':[128,64,192],'alphas':[128/255,1.0]};same(data['configuration'],CONFIG,'readback configuration')
  linear=invoke('cmsCreateRGBProfile',[C.byref(white),C.byref(primaries),curves],['D65','Rec709','shared-gamma-1'],'pointer');need(linear is not None,'linear null');errors()
  invoke('cmsFreeToneCurve',[curve],['gamma']);curve=None;errors()
  forward=invoke('cmsCreateTransform',[srgb,FORMAT,linear,FORMAT,1,320],['srgb',FORMAT,'linear',FORMAT,1,320],'pointer');need(forward is not None,'forward null');errors()
  reverse=invoke('cmsCreateTransform',[linear,FORMAT,srgb,FORMAT,1,320],['linear',FORMAT,'srgb',FORMAT,1,320],'pointer');need(reverse is not None,'reverse null');errors()
  for handle,label in ((forward,'forward'),(reverse,'reverse')):
   for name in ('cmsGetTransformInputFormat','cmsGetTransformOutputFormat'):
    value=invoke(name,[handle],[label],'int');need(value==FORMAT,'format readback');errors()
  def convert(handle,label,name,values):
   need(type(values) is list and len(values)==3 and all(type(x) is float and math.isfinite(x) for x in values),'finite input')
   src=(C.c_double*3)(*values);dst=(C.c_double*3)(math.nan,math.nan,math.nan)
   need(C.sizeof(src)==24 and C.addressof(src)!=C.addressof(dst),'buffer separation/size')
   actual=list(src);same(actual,values,'actual array input')
   invoke('cmsDoTransform',[handle,src,dst,1],[label,name,1,24]);output=list(dst)
   data['operations'].append({'name':name,'input':actual,'output':safe(output)})
   errors();need(all(math.isfinite(x) and 0<=x<=1 for x in output),'finite/range native output')
   return output
  data['source_encoded']=[128/255,64/255,192/255]
  decoded=convert(forward,'forward','decode',data['source_encoded']);data['decoded']=decoded
  # Reject decoded disagreement before issuing reverse work.
  from check import near,load
  reference=load((Path(__file__).parent/'protocol-reference.json').read_text())
  near(decoded,[float(x) for x in reference['source_linear']],'native decode')
  for i,(name,alpha) in enumerate((('main',128/255),('opaque',1.0))):
   working=[x*alpha for x in decoded];output=convert(reverse,'reverse',name,working)
   data['conditions'].append({'name':name,'alpha':alpha,'working':working,'output':output,'encoded_direct':[x*alpha for x in data['source_encoded']],'output_alpha':1.0})
   near(output,[float(x) for x in reference['rows'][i]['encoded_from_linear']],'native encode')
 except BaseException as e:failure=type(e).__name__+': '+str(e)
 finally:
  # Continue all applicable cleanup even if a particular Python cleanup call raises.
  cleanup=[]
  if curve is not None:cleanup.append(('cmsFreeToneCurve',[curve],['gamma'],'void'))
  for handle,label in ((forward,'forward'),(reverse,'reverse')):
   if handle is not None:cleanup.append(('cmsDeleteTransform',[handle],[label],'void'))
  for handle,label in ((srgb,'srgb'),(linear,'linear')):
   if handle is not None:cleanup.append(('cmsCloseProfile',[handle],[label],'int'))
  for name,args,summary,kind in cleanup:
   try:
    ret=invoke(name,args,summary,kind)
    if name=='cmsCloseProfile':need(ret==1,'profile close failed')
   except BaseException as e:failure=(failure+'; ' if failure else '')+'cleanup '+type(e).__name__+': '+str(e)
  if handler:
   try:invoke('cmsSetLogErrorHandler',[callback_type()],['restore-null'])
   except BaseException as e:failure=(failure+'; ' if failure else '')+'handler cleanup '+str(e)
  try:
   errors();data['library_after']=sha(LIB);need(data['library_after']==LIB_SHA,'library after');data['cleanup_complete']=failure is None
  except BaseException as e:failure=(failure+'; ' if failure else '')+'final '+str(e)
 if failure:
  data.update(status='FAIL',failure=failure);emit('FAILURE_JSON=',data);return 1
 try:
  data['status']='PASS'
  from check import check_payload,load
  check_payload(data,load((Path(__file__).parent/'protocol-reference.json').read_text()))
 except BaseException as e:
  data.update(status='FAIL',failure=type(e).__name__+': '+str(e));emit('FAILURE_JSON=',data);return 1
 emit('RESULT_JSON=',data);return 0
if __name__=='__main__':raise SystemExit(main())
