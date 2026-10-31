"""Exactly one fixed source -> compiler assembly, no shader execution."""
import ctypes as C
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
LIB=Path('/lib/x86_64-linux-gnu/libshaderc.so.1')
def need(c,m):
 if not c: raise RuntimeError(m)
need(len(sys.argv)==2 and sys.argv[1] in ('row','column'),'fixed case required')
case=sys.argv[1]
src=(ROOT/(case+'.comp')).read_bytes()
a=C.CDLL(str(LIB))
def bind(n,args,ret):
 f=getattr(a,n);f.argtypes=args;f.restype=ret;return f
ptr=C.c_void_p
init=bind('shaderc_compiler_initialize',[],ptr)
release=bind('shaderc_compiler_release',[ptr],None)
oi=bind('shaderc_compile_options_initialize',[],ptr)
or_=bind('shaderc_compile_options_release',[ptr],None)
env=bind('shaderc_compile_options_set_target_env',[ptr,C.c_int,C.c_uint32],None)
spv=bind('shaderc_compile_options_set_target_spirv',[ptr,C.c_int],None)
opt=bind('shaderc_compile_options_set_optimization_level',[ptr,C.c_int],None)
compile_=bind('shaderc_compile_into_spv_assembly',[ptr,C.c_char_p,C.c_size_t,C.c_int,C.c_char_p,C.c_char_p,ptr],ptr)
status=bind('shaderc_result_get_compilation_status',[ptr],C.c_int)
length=bind('shaderc_result_get_length',[ptr],C.c_size_t)
getbytes=bind('shaderc_result_get_bytes',[ptr],ptr)
err=bind('shaderc_result_get_error_message',[ptr],C.c_char_p)
warnings=bind('shaderc_result_get_num_warnings',[ptr],C.c_size_t)
errors=bind('shaderc_result_get_num_errors',[ptr],C.c_size_t)
rr=bind('shaderc_result_release',[ptr],None)
version=bind('shaderc_get_spv_version',[C.POINTER(C.c_uint),C.POINTER(C.c_uint)],None)
c=o=r=None
try:
 c=init();need(c,'compiler null')
 o=oi();need(o,'options null')
 env(o,0,1<<22);spv(o,0x10000);opt(o,0)
 r=compile_(c,src,len(src),2,(case+'.comp').encode(),b'main',o);need(r,'result null')
 n=length(r);need(n<=1000000,'output cap')
 b=getbytes(r);need(n==0 or b,'missing bytes')
 output=C.string_at(b,n).decode('utf-8') if n else ''
 v=C.c_uint();rev=C.c_uint();version(C.byref(v),C.byref(rev))
 record={'case':case,'library':str(LIB),'library_sha256':hashlib.sha256(LIB.read_bytes()).hexdigest(),
 'status':status(r),'errors':errors(r),'warnings':warnings(r),'diagnostics':(err(r) or b'').decode('utf-8'),
 'assembly':output,'assembly_length':n,'spv_production_version_query':v.value,'spv_revision_query':rev.value,
 'source_sha256':hashlib.sha256(src).hexdigest(),'target_env':0,'target_version':1<<22,'target_spirv':0x10000,'optimization':0,'shader_kind':2}
 print('RESULT_JSON='+json.dumps(record),flush=True)
 need(record['status']==0 and record['errors']==0,'compiler failure (receipt retained on stdout)')
finally:
 if r: rr(r)
 if o: or_(o)
 if c: release(c)
