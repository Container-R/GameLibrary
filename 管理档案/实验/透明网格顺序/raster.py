# CC0. Real EGL/OpenGL calls via ctypes; no CPU blend emulation.
import ctypes as C, json, os, struct, zlib
os.environ['LIBGL_ALWAYS_SOFTWARE']='1'
os.environ['EGL_PLATFORM']='surfaceless'
os.environ['MESA_SHADER_CACHE_DISABLE']='true'
e=C.CDLL('libEGL.so.1'); g=C.CDLL('libGL.so.1')
def fn(lib,name,ret,args):
 f=getattr(lib,name);f.restype=ret;f.argtypes=args;return f
P=C.c_void_p; I=C.c_int; U=C.c_uint; F=C.c_float
get=fn(e,'eglGetDisplay',P,[P]);init=fn(e,'eglInitialize',U,[P,C.POINTER(I),C.POINTER(I)]);choose=fn(e,'eglChooseConfig',U,[P,C.POINTER(I),C.POINTER(P),I,C.POINTER(I)])
d=get(None);major=I();minor=I();assert init(d,C.byref(major),C.byref(minor))
assert fn(e,'eglBindAPI',U,[U])(0x30A2) # EGL_OPENGL_API
attrs=(I*17)(0x3033,1,0x3040,8,0x3024,8,0x3023,8,0x3022,8,0x3021,8,0x3025,0,0x3038,0,0)
config=P();num=I();assert choose(d,attrs,C.byref(config),1,C.byref(num)) and num.value
surf=fn(e,'eglCreatePbufferSurface',P,[P,P,C.POINTER(I)])(d,config,(I*7)(0x3057,16,0x3056,16,0x309D,0x308A,0x3038));assert surf
ctx=fn(e,'eglCreateContext',P,[P,P,P,C.POINTER(I)])(d,config,None,(I*1)(0x3038));assert ctx
assert fn(e,'eglMakeCurrent',U,[P,P,P,P])(d,surf,surf,ctx)
disable=fn(g,'glDisable',None,[U]); enable=fn(g,'glEnable',None,[U])
for cap in [0x0B71,0x0B44,0x0BD0,0x0C11,0x809D,0x8DB9]: disable(cap) # depth,cull,dither,scissor,MSAA, framebuffer sRGB
fn(g,'glDepthMask',None,[C.c_ubyte])(0)
enable(0x0BE2)
fn(g,'glBlendEquation',None,[U])(0x8006)
fn(g,'glBlendFuncSeparate',None,[U,U,U,U])(0x0302,0x0303,1,0x0303)
fn(g,'glViewport',None,[I,I,I,I])(0,0,16,16)
clearColor=fn(g,'glClearColor',None,[F,F,F,F]);clear=fn(g,'glClear',None,[U]);read=fn(g,'glReadPixels',None,[I,I,I,I,U,U,P]);err=fn(g,'glGetError',U,[])
# Record config channels and actual framebuffer encoding; linear is GL_LINEAR=0x2601.
getattri=fn(e,'eglGetConfigAttrib',U,[P,P,I,C.POINTER(I)]); bits={}
for key,token in [('red',0x3024),('green',0x3023),('blue',0x3022),('alpha',0x3021),('samples',0x3031)]:
 v=I();assert getattri(d,config,token,C.byref(v));bits[key]=v.value
# Explicit linear RGBA8 FBO avoids platform-dependent default surface encoding.
tex=U();fbo=U()
fn(g,'glGenTextures',None,[I,C.POINTER(U)])(1,C.byref(tex))
fn(g,'glBindTexture',None,[U,U])(0x0DE1,tex.value)
fn(g,'glTexImage2D',None,[U,I,I,I,I,I,U,U,P])(0x0DE1,0,0x8058,16,16,0,0x1908,0x1401,None)
fn(g,'glGenFramebuffers',None,[I,C.POINTER(U)])(1,C.byref(fbo))
fn(g,'glBindFramebuffer',None,[U,U])(0x8D40,fbo.value)
fn(g,'glFramebufferTexture2D',None,[U,U,U,U,I])(0x8D40,0x8CE0,0x0DE1,tex.value,0)
assert fn(g,'glCheckFramebufferStatus',U,[U])(0x8D40)==0x8CD5
encoding=I();fn(g,'glGetFramebufferAttachmentParameteriv',None,[U,U,U,C.POINTER(I)])(0x8D40,0x8CE0,0x8210,C.byref(encoding));assert err()==0;assert encoding.value==0x2601
fixture=json.load(open('structure.json'))['raster_fixture'];positions=[(-1,-1,0),(3,-1,0),(-1,3,0)]
vertex_pointer=fn(g,'glVertexPointer',None,[I,U,I,P])
color_pointer=fn(g,'glColorPointer',None,[I,U,I,P])
draw_elements=fn(g,'glDrawElements',None,[U,I,U,P])
client_enable=fn(g,'glEnableClientState',None,[U])
client_enable(0x8074);client_enable(0x8076) # vertex and color arrays
# One interleaved vertex record: xyz + straight RGBA. No index expansion.
original_records=[positions[oid%3]+((1,0,0,0.5) if oid>=3 else (0,1,1,0.5)) for oid in range(6)]
def png(path,raw):
 # PNG is an untagged byte preview, NOT a colorimetric measurement.
 def chunk(tag,data):return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
 rows=b''.join(b'\0'+raw[y*64:(y+1)*64] for y in reversed(range(16)))
 open(path,'wb').write(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',16,16,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b''))
def render(indices,oldids,name):
 records=(F*(7*len(oldids)))(*(v for oid in oldids for v in original_records[oid]))
 index_data=(U*len(indices))(*indices)
 vertex_pointer(3,0x1406,28,C.cast(records,P))
 color_pointer(4,0x1406,28,P(C.addressof(records)+12))
 clearColor(0,0,0,0);clear(0x4000)
 draw_elements(4,len(indices),0x1405,C.cast(index_data,P)) # GL_TRIANGLES, GL_UNSIGNED_INT
 fn(g,'glFinish',None,[])()
 pixel=(C.c_ubyte*4)();read(8,8,1,1,0x1908,0x1401,pixel)
 full=(C.c_ubyte*(16*16*4))();read(0,0,16,16,0x1908,0x1401,full)
 assert err()==0
 raw=bytes(full);open(name+'.rgba','wb').write(raw);png(name+'.png',raw)
 return list(pixel)
base=render(fixture['input'],list(range(6)),'red_then_cyan')
swapped=render(fixture['input'][3:]+fixture['input'][:3],list(range(6)),'cyan_then_red')
fetch=render(fixture['fetch_indices'],fixture['fetch_vertex_old_ids'],'fetch_red_then_cyan')
assert base!=swapped and base==fetch
out={'draw_api':'glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, client_indices)', 'vertex_input':'interleaved xyz/RGBA compatibility client arrays, 28-byte stride', 'config_bits':bits,'framebuffer_encoding':encoding.value,'pixel_coordinate':[8,8],'red_then_cyan_rgba8':base,'cyan_then_red_rgba8':swapped,'fetch_red_then_cyan_rgba8':fetch,'all_assertions_passed':True}
print(json.dumps(out,indent=2))
fn(e,'eglMakeCurrent',U,[P,P,P,P])(d,None,None,None);fn(e,'eglDestroyContext',U,[P,P])(d,ctx);fn(e,'eglDestroySurface',U,[P,P])(d,surf);fn(e,'eglTerminate',U,[P])(d)
