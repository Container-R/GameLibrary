"""Five frozen static loopback cases. Never opens an ordinary playback device."""
import base64
import ctypes as C
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import struct
import sys

HERE=Path(__file__).absolute().parent

def local_module(name,file):
    spec=importlib.util.spec_from_file_location(name,HERE/file)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module
K=local_module('driver_contract','contract.py')
N=local_module('driver_numeric_consumer','consumer.py')

class Stop(Exception): pass

def partial_value(value):
    # Failure-only representation: never substitute zero for a nonfinite getter.
    if type(value) is float and not math.isfinite(value):
        return {'nonfinite_float': 'nan' if math.isnan(value) else ('positive_infinity' if value>0 else 'negative_infinity')}
    if type(value) is dict: return {k:partial_value(v) for k,v in value.items()}
    if type(value) is list: return [partial_value(v) for v in value]
    return value
SEQ=0

def emit(event,case,data):
    global SEQ
    print(json.dumps({'seq':SEQ,'event':event,'case':case,'data':data},sort_keys=True,allow_nan=False),flush=True)
    SEQ+=1

def require(ok,reason):
    if not ok: raise Stop(reason)

class API:
    def __init__(self):
        self.lib=C.CDLL('libopenal.so.1')
        self.checks=[]; self.dev=None; self.actual={}; self.failure_values={}
        signatures={
            'alcGetError':(C.c_int,[C.c_void_p]),
            'alcIsExtensionPresent':(C.c_byte,[C.c_void_p,C.c_char_p]),
            'alcGetProcAddress':(C.c_void_p,[C.c_void_p,C.c_char_p]),
            'alcCreateContext':(C.c_void_p,[C.c_void_p,C.POINTER(C.c_int)]),
            'alcMakeContextCurrent':(C.c_byte,[C.c_void_p]),
            'alcDestroyContext':(None,[C.c_void_p]),
            'alcCloseDevice':(C.c_byte,[C.c_void_p]),
            'alcGetIntegerv':(None,[C.c_void_p,C.c_int,C.c_int,C.POINTER(C.c_int)]),
            'alGetError':(C.c_int,[]),'alGetString':(C.c_char_p,[C.c_int]),
            'alGenBuffers':(None,[C.c_int,C.POINTER(C.c_uint)]),
            'alDeleteBuffers':(None,[C.c_int,C.POINTER(C.c_uint)]),
            'alBufferData':(None,[C.c_uint,C.c_int,C.c_void_p,C.c_int,C.c_int]),
            'alGetBufferi':(None,[C.c_uint,C.c_int,C.POINTER(C.c_int)]),
            'alGenSources':(None,[C.c_int,C.POINTER(C.c_uint)]),
            'alDeleteSources':(None,[C.c_int,C.POINTER(C.c_uint)]),
            'alSourcei':(None,[C.c_uint,C.c_int,C.c_int]),
            'alSourcef':(None,[C.c_uint,C.c_int,C.c_float]),
            'alSourcefv':(None,[C.c_uint,C.c_int,C.POINTER(C.c_float)]),
            'alGetSourcei':(None,[C.c_uint,C.c_int,C.POINTER(C.c_int)]),
            'alGetSourcef':(None,[C.c_uint,C.c_int,C.POINTER(C.c_float)]),
            'alGetSourcefv':(None,[C.c_uint,C.c_int,C.POINTER(C.c_float)]),
            'alListenerf':(None,[C.c_int,C.c_float]),
            'alListenerfv':(None,[C.c_int,C.POINTER(C.c_float)]),
            'alGetListenerf':(None,[C.c_int,C.POINTER(C.c_float)]),
            'alGetListenerfv':(None,[C.c_int,C.POINTER(C.c_float)]),
            'alDistanceModel':(None,[C.c_int]),'alGetInteger':(C.c_int,[C.c_int]),
            'alSourcePlay':(None,[C.c_uint]),'alSourceStop':(None,[C.c_uint]),
        }
        for name,(result,args) in signatures.items():
            f=getattr(self.lib,name); f.restype=result; f.argtypes=args; setattr(self,name,f)
        self.ac('initial_alc',None)
        ok=bool(self.alcIsExtensionPresent(None,b'ALC_SOFT_loopback')); self.ac('loopback_extension',None)
        require(ok,'loopback_unavailable')
        specs=[('open','alcLoopbackOpenDeviceSOFT',C.c_void_p,[C.c_char_p]),
               ('format','alcIsRenderFormatSupportedSOFT',C.c_byte,[C.c_void_p,C.c_int,C.c_int,C.c_int]),
               ('render','alcRenderSamplesSOFT',None,[C.c_void_p,C.c_void_p,C.c_int])]
        for short,name,result,args in specs:
            address=self.alcGetProcAddress(None,name.encode('ascii')); self.ac('resolve_'+short,None)
            require(bool(address),'missing_loopback_entry')
            setattr(self,short,C.CFUNCTYPE(result,*args)(address))
    def ac(self,label,device):
        code=int(self.alcGetError(device)); self.checks.append({'stage':label,'error':code})
        if code != 0: emit('api_failure',None,{'stage':label,'api':'ALC','error':code})
        require(code==0,'alc_error_'+label)
    def al(self,label):
        code=int(self.alGetError()); self.checks.append({'stage':label,'error':code})
        if code != 0: emit('api_failure',None,{'stage':label,'api':'AL','error':code})
        require(code==0,'al_error_'+label)
    def source_int(self,source,token,label):
        value=C.c_int(-1); self.alGetSourcei(source,token,C.byref(value)); self.al(label)
        return value.value
    def cleanup(self,ctx,source,buffer):
        self.checks=[]; failures=[]
        def attempt(label,fn):
            try: fn()
            except BaseException: failures.append(label)
        if source.value:
            def stop(): self.alSourceStop(source.value); self.al('stop')
            attempt('stop',stop)
            def stopped():
                value=self.source_int(source.value,0x1010,'get_stopped')
                self.failure_values['cleanup_source_state']=value
                require(value==0x1014,'not_stopped')
            attempt('stopped',stopped)
            def detach(): self.alSourcei(source.value,0x1009,0); self.al('detach_buffer')
            attempt('detach_buffer',detach)
            def detached_buffer():
                value=self.source_int(source.value,0x1009,'get_detached_buffer')
                self.failure_values['cleanup_buffer_binding']=value
                require(value==0,'still_bound')
            attempt('detached_buffer',detached_buffer)
            def delete_source(): self.alDeleteSources(1,C.byref(source)); self.al('delete_source')
            attempt('delete_source',delete_source)
        if buffer.value:
            def delete_buffer(): self.alDeleteBuffers(1,C.byref(buffer)); self.al('delete_buffer')
            attempt('delete_buffer',delete_buffer)
        if ctx:
            def detach_context():
                ok=bool(self.alcMakeContextCurrent(None)); self.failure_values['cleanup_detach_context']=ok
                self.ac('detach_context',self.dev)
                require(ok,'detach_false')
            attempt('detach_context',detach_context)
            def destroy_context(): self.alcDestroyContext(ctx); self.ac('destroy_context',self.dev)
            attempt('destroy_context',destroy_context)
        if self.dev:
            def close():
                ok=bool(self.alcCloseDevice(self.dev)); self.failure_values['cleanup_close_loopback']=ok
                self.checks.append({'stage':'close_loopback','ok':ok})
                require(ok,'close_false')
            attempt('close_loopback',close)
        result={'ok':not failures,'checks':self.checks,'failures':failures}
        if failures: result['failure_values']=partial_value(self.failure_values)
        return result

def run_case(api,case,pcm,baseline):
    cid=case['id']; emit('case_begin',cid,case)
    ctx=None; source=C.c_uint(0); buffer=C.c_uint(0); first=None; metric=None
    api.dev=None; api.checks=[]; api.actual={}; api.failure_values={}
    try:
        api.dev=api.open(None); api.failure_values['loopback_open_nonnull']=bool(api.dev)
        api.ac('loopback_open',api.dev); require(bool(api.dev),'loopback_open_null')
        for key,name in [('hrtf_extension',b'ALC_SOFT_HRTF'),('limiter_extension',b'ALC_SOFT_output_limiter')]:
            ok=bool(api.alcIsExtensionPresent(api.dev,name)); api.failure_values[key]=ok
            api.ac(key,api.dev); require(ok,key+'_unavailable')
        ok=bool(api.format(api.dev,48000,0x1500,0x1406)); api.failure_values['format_supported']=ok
        api.ac('format_supported',api.dev); require(ok,'format_unavailable')
        attrs=(C.c_int*11)(0x1007,48000,0x1990,0x1500,0x1991,0x1406,0x1992,0,0x199A,0,0)
        ctx=api.alcCreateContext(api.dev,attrs); api.failure_values['context_nonnull']=bool(ctx)
        api.ac('create_context',api.dev); require(bool(ctx),'context_null')
        ok=bool(api.alcMakeContextCurrent(ctx)); api.failure_values['make_current']=ok
        api.ac('make_current',api.dev); require(ok,'make_current_false')
        api.al('initial_al')
        for key,token,expected in [('version',0xB002,K.VERSION),('renderer',0xB003,'OpenAL Soft')]:
            raw=api.alGetString(token); api.al('get_'+key)
            require(raw==expected.encode('ascii'),'source_version_review_required')
            api.actual[key]=expected  # only publish the exact approved technical values
        api.actual['format']={}
        for key,token in [('frequency',0x1007),('channels',0x1990),('type',0x1991),('hrtf',0x1992),('limiter',0x199A)]:
            v=C.c_int(-1); api.alcGetIntegerv(api.dev,token,1,C.byref(v)); api.ac('get_format_'+key,api.dev)
            api.actual['format'][key]=v.value; require(v.value==K.FORMAT[key],'format_readback')
        v=C.c_int(-1); api.alcGetIntegerv(api.dev,0x1993,1,C.byref(v)); api.ac('get_hrtf_status',api.dev)
        api.actual['hrtf_status']=v.value
        api.alGenBuffers(1,C.byref(buffer)); api.al('gen_buffer')
        api.failure_values['generated_buffer_id']=buffer.value; require(buffer.value!=0,'buffer_zero')
        pcm_array=(C.c_short*48)(*([1024]*24+[-1024]*24))
        require(C.string_at(C.addressof(pcm_array),96)==pcm,'pcm_bytes')
        api.alBufferData(buffer.value,0x1101,C.cast(pcm_array,C.c_void_p),96,48000); api.al('buffer_data')
        api.actual['buffer']={}
        for key,token in [('frequency',0x2001),('bits',0x2002),('channels',0x2003),('size',0x2004)]:
            v=C.c_int(-1); api.alGetBufferi(buffer.value,token,C.byref(v)); api.al('get_buffer_'+key)
            api.actual['buffer'][key]=v.value; require(v.value==K.BUFFER[key],'buffer_readback')
        api.alGenSources(1,C.byref(source)); api.al('gen_source')
        api.failure_values['generated_source_id']=source.value; require(source.value!=0,'source_zero')
        api.alSourcei(source.value,0x1009,buffer.value); api.al('set_source_buffer')
        binding=api.source_int(source.value,0x1009,'get_source_buffer')
        api.failure_values['source_buffer_binding']=binding; require(binding==buffer.value,'buffer_binding')
        api.actual['listener']={}
        listener_tokens={'gain':0x100A,'position':0x1004,'velocity':0x1006,'orientation':0x100F}
        for key,expected in K.LISTENER.items():
            token=listener_tokens[key]
            if type(expected) is float:
                api.alListenerf(token,expected); api.al('set_listener_'+key)
                v=C.c_float(); api.alGetListenerf(token,C.byref(v)); api.al('get_listener_'+key); actual=v.value
            else:
                v=(C.c_float*len(expected))(*expected); api.alListenerfv(token,v); api.al('set_listener_'+key)
                out=(C.c_float*len(expected))(); api.alGetListenerfv(token,out); api.al('get_listener_'+key); actual=list(out)
            api.actual['listener'][key]=actual; require(N.exact(actual,expected),'listener_readback')
        api.actual['source']={}
        for key,token,expected in [*K.SOURCE_FLOATS,('maximum',0x1023,float(case['maximum']))]:
            api.alSourcef(source.value,token,expected); api.al('set_source_'+key)
            v=C.c_float(); api.alGetSourcef(source.value,token,C.byref(v)); api.al('get_source_'+key)
            api.actual['source'][key]=v.value; require(v.value==expected,'source_float_readback')
        for key,token,expected in K.SOURCE_INTS:
            api.alSourcei(source.value,token,expected); api.al('set_source_'+key)
            v=api.source_int(source.value,token,'get_source_'+key)
            api.actual['source'][key]=v; require(v==expected,'source_int_readback')
        for key,token,expected in [*K.SOURCE_VECTORS,('position',0x1004,[0.0,0.0,-float(case['distance'])])]:
            v=(C.c_float*3)(*expected); api.alSourcefv(source.value,token,v); api.al('set_source_'+key)
            out=(C.c_float*3)(); api.alGetSourcefv(source.value,token,out); api.al('get_source_'+key)
            actual=list(out); api.actual['source'][key]=actual; require(N.exact(actual,expected),'source_vector_readback')
        api.alDistanceModel(case['model']); api.al('set_distance_model')
        model=int(api.alGetInteger(0xD000)); api.al('get_distance_model'); api.actual['distance_model']=model
        require(model==case['model'],'distance_model_readback')
        for key,token,expected in [('type',0x1027,0x1028),('state',0x1010,0x1011),('sample_offset',0x1025,0)]:
            v=api.source_int(source.value,token,'get_source_'+key); api.actual['source'][key]=v
            require(v==expected,'source_initial_readback')
        emit('ready',cid,{**api.actual,'checks':api.checks})
        api.checks=[]; api.alSourcePlay(source.value); api.al('play')
        state=api.source_int(source.value,0x1010,'get_playing'); api.failure_values['after_play_state']=state
        require(state==0x1012,'not_playing')
        emit('playing',cid,{'state':state,'checks':api.checks})
        windows=[]
        for part in K.PARTS:
            api.checks=[]
            output=(C.c_float*4800)()
            api.render(api.dev,C.cast(output,C.c_void_p),4800)
            raw=C.string_at(C.addressof(output),19200)
            emit('window',cid,{'part':part,'frame_count':4800,'byte_count':len(raw),
                 'sha256':hashlib.sha256(raw).hexdigest(),'base64':base64.b64encode(raw).decode('ascii')})
            api.ac('render_alc',api.dev); api.al('render_al'); N.samples(raw)
            state=api.source_int(source.value,0x1010,'get_playing'); api.failure_values[part+'_state']=state
            require(state==0x1012,'not_playing')
            emit('window_checked',cid,{'part':part,'state':state,'checks':api.checks})
            if part!='warmup': windows.append(raw)
        metric=N.metrics(windows,baseline); N.check_metrics(metric,case)
        emit('case_metrics',cid,metric)
    except BaseException as exc:
        first=exc.args[0] if isinstance(exc,(Stop,N.Reject)) else 'unexpected_exception'
        emit('case_failure',cid,{'reason':first,'checks':api.checks,
             'partial_actual':partial_value(api.actual),'failure_values':partial_value(api.failure_values)})
    finally:
        cleanup=api.cleanup(ctx,source,buffer)
        emit('cleanup',cid,cleanup)
        if not cleanup['ok'] and first is None: first='cleanup_failed'
    if first is not None: raise Stop(first)
    emit('case_pass',cid,{'numeric_ok':True,'cleanup_ok':True})
    return metric['rms']

def main():
    emit('begin',None,K.BEGIN)
    try:
        require(sys.byteorder=='little' and C.sizeof(C.c_short)==2 and C.sizeof(C.c_int)==4 and C.sizeof(C.c_float)==4,'abi')
        require(C.string_at(C.byref(C.c_float(1.0)),4)==b'\x00\x00\x80\x3f','binary32')
        pcm=struct.pack('<48h',*([1024]*24+[-1024]*24))
        api=API()
        emit('global_ready',None,{'loopback_extension':True,'entries_present':True,'checks':api.checks,
                                 'pcm_sha256':hashlib.sha256(pcm).hexdigest()})
        baseline=None
        for case in K.CASES:
            result=run_case(api,case,pcm,baseline)
            if baseline is None: baseline=result
        emit('success',None,{'cases':5,'render_calls':15,'frames':72000,'source_objects':5,'buffer_objects':5,
                            'configuration_fully_excluded':False})
        return 0
    except BaseException as exc:
        reason=exc.args[0] if isinstance(exc,(Stop,N.Reject)) else 'unexpected_exception'
        emit('failure',None,{'reason':reason})
        return 1

if __name__=='__main__': sys.exit(main())
