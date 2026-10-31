"""Finite ICU plural probe; imports are inert. No arbitrary patterns or varargs."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import platform
import sys

class Parse(C.Structure):
    _fields_=[('line',C.c_int32),('offset',C.c_int32),('preContext',C.c_uint16*16),('postContext',C.c_uint16*16)]

def abi():
    return {'platform':platform.system(),'machine':platform.machine(),'byteorder':sys.byteorder,
            'pointer_size':C.sizeof(C.c_void_p),'int32_size':C.sizeof(C.c_int32),
            'uint16_size':C.sizeof(C.c_uint16),'double_size':C.sizeof(C.c_double),
            'UParseError':{'size':C.sizeof(Parse),'alignment':C.alignment(Parse),
                          'offsets':{n:getattr(Parse,n).offset for n,_ in Parse._fields_},'context_units_each':16}}

def hash_file(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def libraries(protocol):
    out={}
    for name,spec in protocol['libraries'].items():
        p=Path(spec['requested']); resolved=p.resolve(strict=True)
        out[name]={'requested':str(p),'resolved':str(resolved),'sha256':hash_file(resolved)}
    return out

class Failure(Exception):
    def __init__(self,category,message): self.category=category; super().__init__(message)
def require(ok,category,message):
    if not ok: raise Failure(category,message)

def main(config_id,invocation):
    import os,traceback
    protocol=json.loads(Path(__file__).with_name('protocol.json').read_text())
    configs={x['id']:x for x in protocol['configurations']}
    if config_id not in configs: raise SystemExit('unknown config')
    config=configs[config_id]
    trace=[]; loads=[]; handle=None; close=None
    report={'uuid':invocation,'config':config_id,'locale':config['locale'],'pattern':config['pattern'],
            'inputs':protocol['inputs'],'pid':os.getpid(),'python':sys.version,'category':'MALFORMED_OR_INCOMPLETE_EVIDENCE'}
    def emit(kind,value): print(json.dumps({'kind':kind,'value':value},allow_nan=False),flush=True)
    def call(name,fn,args,readback,input_value=None):
        number=1+sum(x['phase']=='attempt' for x in trace)
        a={'call':number,'name':name,'phase':'attempt'}
        if input_value is not None:a['input']=input_value
        trace.append(a);emit('trace',a)
        raw=fn(*args)
        b={'call':number,'name':name,'phase':'returned',**readback(raw)}
        if input_value is not None:b['input']=input_value
        trace.append(b);emit('trace',b)
        return raw
    try:
        require(not sys.flags.optimize,'ABI_OR_VERSION_GUARD_FAILURE','optimized child rejected')
        actual=abi();report['abi']=actual
        expected={k:protocol['abi'][k] for k in actual}
        require(actual==expected,'ABI_OR_VERSION_GUARD_FAILURE','unsupported ABI')
        before=libraries(protocol); report['libraries_before']=before
        expectedlibs={n:{k:v[k] for k in ('requested','resolved','sha256')} for n,v in protocol['libraries'].items()}
        require(before==expectedlibs,'SOURCE_OR_LIBRARY_IDENTITY_FAILURE','library pin mismatch')
        libs={}
        for name in ('icuuc','icui18n'):
            event={'name':name,'phase':'attempt'};loads.append(event);emit('load',event)
            libs[name]=C.CDLL(before[name]['resolved'])
            event={'name':name,'phase':'returned'};loads.append(event);emit('load',event)
        version=libs['icuuc'].u_getVersion_76;version.argtypes=[C.POINTER(C.c_uint8)];version.restype=None
        op=libs['icui18n'].umsg_open_76;op.argtypes=[C.POINTER(C.c_uint16),C.c_int32,C.c_char_p,C.POINTER(Parse),C.POINTER(C.c_int32)];op.restype=C.c_void_p
        fmt=libs['icui18n'].umsg_format_76;fmt.argtypes=[C.c_void_p,C.POINTER(C.c_uint16),C.c_int32,C.POINTER(C.c_int32)];fmt.restype=C.c_int32
        close=libs['icui18n'].umsg_close_76;close.argtypes=[C.c_void_p];close.restype=None
        v=(C.c_uint8*4)()
        call('version',version,[v],lambda r:{'result':r,'version':list(v)})
        require(list(v)==[76,1,0,0],'ABI_OR_VERSION_GUARD_FAILURE','unexpected runtime version')
        raw=config['pattern'].encode('utf-16-le');count=len(raw)//2
        inp=(C.c_uint16*(count+1))(*[int.from_bytes(raw[i:i+2],'little') for i in range(0,len(raw),2)],0)
        status=C.c_int32(0);parse=Parse();parse.line=-99;parse.offset=-99
        handle=call('open',op,[inp,count,config['locale'].encode('ascii'),C.byref(parse),C.byref(status)],
                    lambda r:{'handle_nonnull':bool(r),'status':status.value,'pattern_utf16_units':count,
                              'parse_line':parse.line,'parse_offset':parse.offset,'pre_context_units':list(parse.preContext),'post_context_units':list(parse.postContext)})
        require(status.value<=0 and bool(handle),'OPEN_FAILURE','open failed or null')
        outputs=[]
        for number,expected_marker in zip(protocol['inputs'],config['expected']):
            out=(C.c_uint16*64)();status=C.c_int32(0)
            def readback(length):
                valid=status.value<=0 and 0<=length<64
                return {'result':length,'status':status.value,'capacity_utf16':64,
                        'units':list(out[:length]) if valid else None,'argument_type':'c_double'}
            length=call('format',fmt,[handle,out,64,C.byref(status),C.c_double(number)],readback,number)
            require(status.value<=0 and 0<=length<64,'FORMAT_FAILURE','failed or truncated output')
            text=bytes().join(int(x).to_bytes(2,'little') for x in out[:length]).decode('utf-16-le','strict')
            outputs.append(text)
            require(text==expected_marker,'OUTPUT_MISMATCH','unexpected literal marker')
        report['outputs']=outputs
        if 'target_contract' in config:
            report['intent_acceptance']={'number':3,'intended':'FEW','actual':outputs[3],'accepted':outputs[3]=='FEW'}
        report['category']='COMPLETE_EXPECTED_OUTPUTS'
    except Failure as exc: report.update(category=exc.category,error=str(exc))
    except Exception as exc:
        report.update(category='ENVIRONMENT_OR_BINDING_FAILURE' if not trace else 'MALFORMED_OR_INCOMPLETE_EVIDENCE',error=str(exc),traceback=traceback.format_exc())
    finally:
        if handle:
            try:call('close',close,[handle],lambda r:{'result':r})
            except Exception as exc:report.update(prior_category=report['category'],category='CLEANUP_FAILURE',cleanup_error=str(exc))
        if 'libraries_before' in report:
            try:
                after=libraries(protocol);report['libraries_after']=after
                if after!=report['libraries_before']:report.update(prior_category=report['category'],category='SOURCE_OR_LIBRARY_IDENTITY_FAILURE')
            except Exception as exc:report.update(prior_category=report['category'],category='SOURCE_OR_LIBRARY_IDENTITY_FAILURE',library_after_error=str(exc))
        report['trace']=trace;report['loads']=loads
        emit('terminal',report)

if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('expected config ID and invocation UUID')
    main(sys.argv[1],sys.argv[2])
