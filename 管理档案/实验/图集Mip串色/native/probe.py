"""Actual EGL/OpenGL raster + generated mip readback; run from any cwd."""
import ctypes as C
import os
import json
os.environ['LIBGL_ALWAYS_SOFTWARE']='true'
os.environ['EGL_PLATFORM']='surfaceless'
os.environ['MESA_SHADER_CACHE_DISABLE']='true'
E=C.CDLL('libEGL.so.1'); G=C.CDLL('libGL.so.1')
i=C.c_int; u=C.c_uint; f=C.c_float; p=C.c_void_p

def egl(name,result,args):
 fn=getattr(E,name);fn.restype=result;fn.argtypes=args;return fn
geterror=egl('eglGetError',i,[])
def ok(value,label):
 if not value:raise RuntimeError(f'{label}: EGL error {geterror():#x}')
 return value
D=egl('eglGetDisplay',p,[p])(None);ok(D,'get display')
major=i();minor=i();ok(egl('eglInitialize',u,[p,C.POINTER(i),C.POINTER(i)])(D,C.byref(major),C.byref(minor)),'initialize')
ok(egl('eglBindAPI',u,[u])(0x30A2),'bind desktop OpenGL')
a=(i*13)(0x3033,1,0x3040,8,0x3024,8,0x3023,8,0x3022,8,0x3021,8,0x3038)
config=p();n=i();ok(egl('eglChooseConfig',u,[p,C.POINTER(i),C.POINTER(p),i,C.POINTER(i)])(D,a,C.byref(config),1,C.byref(n)),'choose config');assert n.value==1
attrs=(i*5)(0x3057,1,0x3056,1,0x3038)
surface=egl('eglCreatePbufferSurface',p,[p,p,C.POINTER(i)])(D,config,attrs);ok(surface,'pbuffer')
attrs=(i*7)(0x3098,3,0x30FB,3,0x30FD,1,0x3038)
ctx=egl('eglCreateContext',p,[p,p,p,C.POINTER(i)])(D,config,None,attrs);ok(ctx,'3.3 core context')
ok(egl('eglMakeCurrent',u,[p,p,p,p])(D,surface,surface,ctx),'make current')
getproc=egl('eglGetProcAddress',p,[C.c_char_p])
def gl(name,result,args):
 address=getproc(name.encode())
 if not address:raise RuntimeError('GL entry missing: '+name)
 return C.CFUNCTYPE(result,*args)(address)
string=gl('glGetString',C.c_char_p,[u]);info={k:string(v).decode() for k,v in [('vendor',0x1F00),('renderer',0x1F01),('version',0x1F02),('glsl',0x8B8C)]}
from pathlib import Path
import hashlib
root=Path(__file__).resolve().parent
T=0x0DE1; RGBA=0x1908; BYTE=0x1401
bindtex=gl('glBindTexture',None,[u,u]);param=gl('glTexParameteri',None,[u,u,i]);upload=gl('glTexImage2D',None,[u,i,i,i,i,i,u,u,p])
gettex=gl('glGetTexImage',None,[u,i,u,u,p])
def texture(width,height,raw=None):
 t=u();gl('glGenTextures',None,[i,C.POINTER(u)])(1,C.byref(t));bindtex(T,t)
 for key,val in [(0x2801,0x2701),(0x2800,0x2601),(0x2802,0x812F),(0x2803,0x812F)]:param(T,key,val)
 arr=(C.c_ubyte*len(raw))(*raw) if raw else None
 upload(T,0,0x8058,width,height,0,RGBA,BYTE,arr)
 return t.value
textures={};mips={}
for name,boundary in [('unaligned_boundary_x3',3),('aligned_boundary_x4',4),('red_gutter_to_x6',6)]:
 raw=[v for y in range(4) for x in range(8) for v in ([255,0,0,255] if x<boundary else [0,0,255,255])]
 t=texture(8,4,raw);gl('glGenerateMipmap',None,[u])(T);textures[name]=t
 levels=[]
 for level,w,h in [(0,8,4),(1,4,2),(2,2,1),(3,1,1)]:
  arr=(C.c_ubyte*(w*h*4))();gettex(T,level,RGBA,BYTE,arr)
  levels.append({'level':level,'width':w,'height':h,'rgba_rows':[[list(arr[(y*w+x)*4:(y*w+x+1)*4]) for x in range(w)] for y in range(h)]})
 mips[name]=levels
# RGBA8 output framebuffer. No MSAA, sRGB conversion, blending or dithering.
outtex=texture(128,32);param(T,0x2801,0x2600)
fbo=u();gl('glGenFramebuffers',None,[i,C.POINTER(u)])(1,C.byref(fbo));gl('glBindFramebuffer',None,[u,u])(0x8D40,fbo)
gl('glFramebufferTexture2D',None,[u,u,u,u,i])(0x8D40,0x8CE0,T,outtex,0)
assert gl('glCheckFramebufferStatus',u,[u])(0x8D40)==0x8CD5
for flag in [0x0BD0,0x0BE2,0x8DB9,0x0B71]:gl('glDisable',None,[u])(flag)
def compile_shader(kind,source):
 sh=gl('glCreateShader',u,[u])(kind);src=C.c_char_p(source.encode());gl('glShaderSource',None,[u,i,C.POINTER(C.c_char_p),C.POINTER(i)])(sh,1,C.byref(src),None);gl('glCompileShader',None,[u])(sh)
 status=i();gl('glGetShaderiv',None,[u,u,C.POINTER(i)])(sh,0x8B81,C.byref(status))
 if not status.value:
  log=C.create_string_buffer(4096);gl('glGetShaderInfoLog',None,[u,i,C.POINTER(i),p])(sh,4096,None,log);raise RuntimeError(log.value.decode())
 return sh
vs='''#version 330 core
void main(){ vec2 v=vec2((gl_VertexID<<1)&2,gl_VertexID&2); gl_Position=vec4(v*2.0-1.0,0.0,1.0); }
'''
fs='''#version 330 core
uniform sampler2D atlas;
uniform int fetch_mode;
out vec4 color;
void main(){
 if(fetch_mode==1) color=texelFetch(atlas,ivec2(1,0),1);
 else color=textureLod(atlas,vec2(0.46875,0.5),1.0);
}
'''
program=gl('glCreateProgram',u,[])()
for sh in [compile_shader(0x8B31,vs),compile_shader(0x8B30,fs)]:gl('glAttachShader',None,[u,u])(program,sh)
gl('glLinkProgram',None,[u])(program);status=i();gl('glGetProgramiv',None,[u,u,C.POINTER(i)])(program,0x8B82,C.byref(status));assert status.value
gl('glUseProgram',None,[u])(program)
loc=gl('glGetUniformLocation',i,[u,C.c_char_p]);uniform=gl('glUniform1i',None,[i,i]);uniform(loc(program,b'atlas'),0)
vao=u();gl('glGenVertexArrays',None,[i,C.POINTER(u)])(1,C.byref(vao));gl('glBindVertexArray',None,[u])(vao)
cases=[('baked_contamination_texelFetch','unaligned_boundary_x3',1),('pure_mip_texelFetch','aligned_boundary_x4',1),('pure_mip_bilinear_mix','aligned_boundary_x4',0),('gutter_bilinear_control','red_gutter_to_x6',0)]
for j,(label,name,mode) in enumerate(cases):
 bindtex(T,textures[name]);uniform(loc(program,b'fetch_mode'),mode)
 gl('glViewport',None,[i,i,i,i])(j*32,0,32,32);gl('glDrawArrays',None,[u,i,i])(0x0004,0,3)
pixels=(C.c_ubyte*(128*32*4))();gl('glReadPixels',None,[i,i,i,i,u,u,p])(0,0,128,32,RGBA,BYTE,pixels)
error=gl('glGetError',u,[])();assert error==0,hex(error)
results=[]
for j,(label,name,mode) in enumerate(cases):
 vals={tuple(pixels[(y*128+x)*4:(y*128+x+1)*4]) for y in range(32) for x in range(j*32,(j+1)*32)}
 assert len(vals)==1;results.append({'case':label,'atlas':name,'rgba':list(vals.pop())})
assert mips['aligned_boundary_x4'][1]['rgba_rows'][0]==[[255,0,0,255]]*2+[[0,0,255,255]]*2
assert results[0]['rgba']==[128,0,128,255]
assert results[1]['rgba']==[255,0,0,255]
assert results[2]['rgba']==[159,0,96,255]
assert results[3]['rgba']==[255,0,0,255]
# Deliberate limitation: gutter no longer prevents contamination at level 2.
assert mips['red_gutter_to_x6'][2]['rgba_rows'][0][1]==[128,0,128,255]
rgb=bytes(pixels[k] for y in reversed(range(32)) for x in range(128) for k in range((y*128+x)*4,(y*128+x)*4+3))
ppm=b'P6\n128 32\n255\n'+rgb;(root/'readback.ppm').write_bytes(ppm)
result={'scope':'actual software desktop GL mip generation and raster readback, no engine or hardware GPU benchmark',**info,'format':'linear RGBA8, opaque, no sRGB/blending/dither/MSAA','filter':'GL_LINEAR_MIPMAP_NEAREST min; GL_LINEAR mag; clamp-to-edge whole atlas','sample_uv':[0.46875,0.5],'sample_lod':1.0,'fetch_ij_lod':[1,0,1],'mips':mips,'raster_swatches_left_to_right':results,'ppm_sha256':hashlib.sha256(ppm).hexdigest(),'gl_error':error}
egl('eglMakeCurrent',u,[p,p,p,p])(D,None,None,None);egl('eglDestroyContext',u,[p,p])(D,ctx);egl('eglDestroySurface',u,[p,p])(D,surface);egl('eglTerminate',u,[p])(D)
print(json.dumps(result,indent=2))
