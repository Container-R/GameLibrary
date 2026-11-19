"""Actual EGL/OpenGL displacement raster readback with authored CPU AABB test."""
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
# Explicit APPLICATION test, not driver's native culling. Identity view/projection.
source_bounds=[2.5,-0.5,3.5,0.5]
envelope=[-3.0,0.0,0.0,0.0] # [min_dx,min_dy,max_dx,max_dy]
expanded=[source_bounds[0]+envelope[0],source_bounds[1]+envelope[1],source_bounds[2]+envelope[2],source_bounds[3]+envelope[3]]
def intersects(b):return b[0]<=1 and b[2]>=-1 and b[1]<=1 and b[3]>=-1

def shader(kind,src):
 sh=gl('glCreateShader',u,[u])(kind);s=C.c_char_p(src.encode());gl('glShaderSource',None,[u,i,C.POINTER(C.c_char_p),C.POINTER(i)])(sh,1,C.byref(s),None);gl('glCompileShader',None,[u])(sh)
 status=i();gl('glGetShaderiv',None,[u,u,C.POINTER(i)])(sh,0x8B81,C.byref(status))
 if not status.value:
  log=C.create_string_buffer(4096);gl('glGetShaderInfoLog',None,[u,i,C.POINTER(i),p])(sh,4096,None,log);raise RuntimeError(log.value.decode())
 return sh
vs='''#version 330 core
uniform float displacement;
void main(){
 const vec2 v[6]=vec2[6](vec2(2.5,-0.5),vec2(3.5,-0.5),vec2(3.5,0.5),vec2(2.5,-0.5),vec2(3.5,0.5),vec2(2.5,0.5));
 gl_Position=vec4(v[gl_VertexID]+vec2(displacement,0.0),0.0,1.0);
}'''
fs='''#version 330 core
out vec4 color;
void main(){color=vec4(1.0,0.0,0.0,1.0);}'''
program=gl('glCreateProgram',u,[])()
for sh in [shader(0x8B31,vs),shader(0x8B30,fs)]:gl('glAttachShader',None,[u,u])(program,sh)
gl('glLinkProgram',None,[u])(program);status=i();gl('glGetProgramiv',None,[u,u,C.POINTER(i)])(program,0x8B82,C.byref(status));assert status.value
vao=u();gl('glGenVertexArrays',None,[i,C.POINTER(u)])(1,C.byref(vao));gl('glBindVertexArray',None,[u])(vao)
tex=u();gl('glGenTextures',None,[i,C.POINTER(u)])(1,C.byref(tex));gl('glBindTexture',None,[u,u])(0x0DE1,tex)
gl('glTexImage2D',None,[u,i,i,i,i,i,u,u,p])(0x0DE1,0,0x8058,64,64,0,0x1908,0x1401,None)
fbo=u();gl('glGenFramebuffers',None,[i,C.POINTER(u)])(1,C.byref(fbo));gl('glBindFramebuffer',None,[u,u])(0x8D40,fbo)
gl('glFramebufferTexture2D',None,[u,u,u,u,i])(0x8D40,0x8CE0,0x0DE1,tex,0);assert gl('glCheckFramebufferStatus',u,[u])(0x8D40)==0x8CD5
for flag in [0x0BD0,0x0BE2,0x8DB9,0x0B71,0x0B44]:gl('glDisable',None,[u])(flag)
gl('glViewport',None,[i,i,i,i])(0,0,64,64);gl('glUseProgram',None,[u])(program)
loc=gl('glGetUniformLocation',i,[u,C.c_char_p])(program,b'displacement');assert loc>=0
cases=[('disable_app_cull_visible',-3.0,True),('source_aabb_app_cull_visible',-3.0,intersects(source_bounds)),('envelope_app_cull_visible',-3.0,intersects(expanded)),('envelope_false_positive_offscreen',0.0,intersects(expanded)),('disable_app_cull_offscreen',0.0,True)]
rows=[];images=[]
for name,dx,submit in cases:
 gl('glClearColor',None,[f,f,f,f])(0,0,0,1);gl('glClear',None,[u])(0x4000)
 gl('glUniform1f',None,[i,f])(loc,dx)
 if submit:gl('glDrawArrays',None,[u,i,i])(0x0004,0,6)
 raw=(C.c_ubyte*(64*64*4))();gl('glReadPixels',None,[i,i,i,i,u,u,p])(0,0,64,64,0x1908,0x1401,raw)
 colors=[list(raw[k:k+4]) for k in range(0,len(raw),4)];assert all(v in [[0,0,0,255],[255,0,0,255]] for v in colors)
 count=sum(v==[255,0,0,255] for v in colors)
 expected=1024 if submit and dx==-3 else 0;assert count==expected,(name,count)
 rows.append({'case':name,'shader_dx':dx,'app_submitted_draw':submit,'red_pixels':count,'center_rgba':colors[32*64+32]})
 images.append(bytes(raw))
error=gl('glGetError',u,[])();assert error==0,hex(error)
# Actual framebuffer panels, left to right as case list; vertically flipped to PPM.
pixels=bytes(v for y in reversed(range(64)) for img in images for x in range(64) for v in img[(y*64+x)*4:(y*64+x)*4+3])
ppm=b'P6\n320 64\n255\n'+pixels;(root/'readback.ppm').write_bytes(ppm)
result={'scope':'CPU-authored AABB draw admission plus actual software GL vertex displacement and raster readback; no native engine culling or performance claim',**info,'source_xy_aabb':source_bounds,'declared_displacement_envelope':envelope,'expanded_xy_aabb':expanded,'clip_xy':[-1,-1,1,1],'framebuffer':[64,64],'cases':rows,'ppm_sha256':hashlib.sha256(ppm).hexdigest(),'gl_error':error}
egl('eglMakeCurrent',u,[p,p,p,p])(D,None,None,None);egl('eglDestroyContext',u,[p,p])(D,ctx);egl('eglDestroySurface',u,[p,p])(D,surface);egl('eglTerminate',u,[p])(D)
print(json.dumps(result,indent=2))
