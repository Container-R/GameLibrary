#!/usr/bin/env python3
"""Finite Linux x86_64 ICU76 experiment, not a general MessageFormat wrapper."""
import ctypes as C, hashlib,json,pathlib,platform,sys
if not __debug__: raise SystemExit('Refusing -O')
BASE='{0, plural, one {One key} other {Many keys}}'
MAP=str.maketrans('aeiouAEIOU','áéíóúÁÉÍÓÚ')
PATTERNS={'baseline':BASE,'naive':BASE.translate(MAP),'literal_only':'{0, plural, one {Óné kéy} other {Mány kéys}}','swapped':'{0, plural, one {Many keys} other {One key}}'}
def require(ok,msg):
    if not ok: raise RuntimeError(msg)
require(len(sys.argv)==2 and sys.argv[1] in PATTERNS,'case whitelist')
case=sys.argv[1]; pattern=PATTERNS[case]
require(platform.system()=='Linux' and platform.machine()=='x86_64','unsupported ABI')
require(C.sizeof(C.c_int)==4 and C.sizeof(C.c_uint16)==2,'ABI type size')
class Parse(C.Structure):
    _fields_=[('line',C.c_int32),('offset',C.c_int32),('pre',C.c_uint16*16),('post',C.c_uint16*16)]
require(C.sizeof(Parse)==72 and [getattr(Parse,x).offset for x in ['line','offset','pre','post']]==[0,4,8,40],'parse ABI layout')
files={n:pathlib.Path('/lib/x86_64-linux-gnu/lib'+n+'.so.76').resolve() for n in ['icuuc','icui18n','icudata']}
uc=C.CDLL(str(files['icuuc'])); lib=C.CDLL(str(files['icui18n']))
version=uc.u_getVersion_76;version.argtypes=[C.POINTER(C.c_uint8)];version.restype=None
v=(C.c_uint8*4)();version(v);require(list(v)==[76,1,0,0],'runtime version')
err=uc.u_errorName_76;err.argtypes=[C.c_int];err.restype=C.c_char_p
op=lib.umsg_open_76;op.argtypes=[C.POINTER(C.c_uint16),C.c_int32,C.c_char_p,C.POINTER(Parse),C.POINTER(C.c_int)];op.restype=C.c_void_p
fmt=lib.umsg_format_76;fmt.argtypes=[C.c_void_p,C.POINTER(C.c_uint16),C.c_int32,C.POINTER(C.c_int)];fmt.restype=C.c_int32
close=lib.umsg_close_76;close.argtypes=[C.c_void_p];close.restype=None
encoding='utf-16-le' if sys.byteorder=='little' else 'utf-16-be'
raw=pattern.encode(encoding); units=len(raw)//2
inp=(C.c_uint16*(units+1))();C.memmove(inp,raw,len(raw))
status=C.c_int(0); pe=Parse();pe.line=-99;pe.offset=-99
def context(arr):
    vals=list(arr); vals=vals[:vals.index(0)] if 0 in vals else vals
    return b''.join(x.to_bytes(2,sys.byteorder) for x in vals).decode(encoding)
def state(s):return {'code':s.value,'name':err(s.value).decode('ascii'),'success':s.value<=0}
result={'case':case,'pattern':pattern,'locale':'en','pattern_utf16_units':units,'version':list(v),'platform':platform.platform(),'python':platform.python_version(),'byteorder':sys.byteorder,'libraries':{n:{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for n,p in files.items()},'format_calls':[]}
handle=op(inp,units,b'en',C.byref(pe),C.byref(status))
result['open']={**state(status),'handle_nonnull':bool(handle),'parse_line':pe.line,'parse_offset':pe.offset,'pre_context':context(pe.pre),'post_context':context(pe.post)}
try:
    if status.value<=0:
        require(bool(handle),'success without handle')
        require(case!='naive','naive unexpectedly parsed; do not call format with mutated syntax')
        for number in [1.0,2.0]:
            out=(C.c_uint16*256)();status=C.c_int(0)
            length=fmt(handle,out,256,C.byref(status),C.c_double(number))
            row={'number':number,'c_argument_type':'double','capacity_utf16':256,'returned_length':length,'status':state(status)}
            if status.value<=0 and 0<=length<256:
                row['output']=C.string_at(C.addressof(out),length*2).decode(encoding)
            result['format_calls'].append(row)
            require(status.value<=0 and 0<=length<256,'format failed or truncated')
finally:
    if handle: close(handle)
print('RESULT_JSON='+json.dumps(result,ensure_ascii=False))
