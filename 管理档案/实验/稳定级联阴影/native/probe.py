"""Directional-shadow grid experiment using real OpenGL depth and mask passes."""
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
def shader(kind,src):
 sh=gl('glCreateShader',u,[u])(kind);s=C.c_char_p(src.encode());gl('glShaderSource',None,[u,i,C.POINTER(C.c_char_p),C.POINTER(i)])(sh,1,C.byref(s),None);gl('glCompileShader',None,[u])(sh)
 status=i();gl('glGetShaderiv',None,[u,u,C.POINTER(i)])(sh,0x8B81,C.byref(status))
 if not status.value:
  log=C.create_string_buffer(4096);gl('glGetShaderInfoLog',None,[u,i,C.POINTER(i),p])(sh,4096,None,log);raise RuntimeError(log.value.decode())
 return sh
def program(vs, fs):
 obj=gl('glCreateProgram',u,[])()
 for sh in [shader(0x8B31,vs),shader(0x8B30,fs)]:
  gl('glAttachShader',None,[u,u])(obj,sh)
 gl('glLinkProgram',None,[u])(obj)
 status=i()
 gl('glGetProgramiv',None,[u,u,C.POINTER(i)])(obj,0x8B82,C.byref(status))
 if not status.value:
  log=C.create_string_buffer(4096)
  gl('glGetProgramInfoLog',None,[u,i,C.POINTER(i),p])(obj,4096,None,log)
  raise RuntimeError(log.value.decode())
 return obj

projection='''#version 330 core
uniform vec2 origin;
uniform float pitch;
void main() {
 const vec2 v[6]=vec2[6](
   vec2(-1.625,-2.625), vec2(1.2,-2.625), vec2(1.2,1.05),
   vec2(-1.625,-2.625), vec2(1.2,1.05), vec2(-1.625,0.108333333));
 gl_Position=vec4(2.0*(v[gl_VertexID]-origin)/(16.0*pitch)-1.0,-0.5,1.0);
}'''
depthonly='''#version 330 core
void main() {}
'''
fullscreen='''#version 330 core
void main() {
 const vec2 v[3]=vec2[3](vec2(-1,-1),vec2(3,-1),vec2(-1,3));
 gl_Position=vec4(v[gl_VertexID],0,1);
}'''
look='''#version 330 core
uniform vec2 origin;
uniform float pitch;
uniform sampler2D shadowbuf;
out vec4 color;
void main() {
 vec2 receiver = (gl_FragCoord.xy - 0.5)/64.0 - vec2(3);
 ivec2 cell = ivec2(floor((receiver - origin)/pitch));
 if (any(lessThan(cell, ivec2(0))) || any(greaterThanEqual(cell, ivec2(16)))) {
   color=vec4(1,0,0,1);
 } else {
   float d = texelFetch(shadowbuf,cell,0).r;
   float lit = d<0.75 ? 0.0 : 1.0;
   color=vec4(lit,lit,lit,1);
 }
}
'''
shadowprogram=program(projection,depthonly)
maskprogram=program(fullscreen,look)
vao=u()
gl('glGenVertexArrays',None,[i,C.POINTER(u)])(1,C.byref(vao))
gl('glBindVertexArray',None,[u])(vao)

def buffer(size, internal, fmt, dtype, attach, draw, read):
 tex=u(); obj=u()
 gl('glGenTextures',None,[i,C.POINTER(u)])(1,C.byref(tex))
 gl('glBindTexture',None,[u,u])(0x0DE1,tex)
 gl('glTexImage2D',None,[u,i,i,i,i,i,u,u,p])(0x0DE1,0,internal,size,size,0,fmt,dtype,None)
 for mode in (0x2800,0x2801):
  gl('glTexParameteri',None,[u,u,i])(0x0DE1,mode,0x2600)
 gl('glGenFramebuffers',None,[i,C.POINTER(u)])(1,C.byref(obj))
 gl('glBindFramebuffer',None,[u,u])(0x8D40,obj)
 gl('glFramebufferTexture2D',None,[u,u,u,u,i])(0x8D40,attach,0x0DE1,tex,0)
 gl('glDrawBuffer',None,[u])(draw)
 gl('glReadBuffer',None,[u])(read)
 assert gl('glCheckFramebufferStatus',u,[u])(0x8D40)==0x8CD5
 return tex,obj

depth,shadowfbo=buffer(16,0x8CAC,0x1902,0x1406,0x8D00,0,0)
color,maskfbo=buffer(384,0x8058,0x1908,0x1401,0x8CE0,0x8CE0,0x8CE0)
for flag in [0x0BD0,0x0BE2,0x8DB9,0x0B44]:
 gl('glDisable',None,[u])(flag)

def uniforms(prog,x,y,pitch):
 gl('glUseProgram',None,[u])(prog)
 loc=gl('glGetUniformLocation',i,[u,C.c_char_p])
 gl('glUniform2f',None,[i,f,f])(loc(prog,b'origin'),x,y)
 gl('glUniform1f',None,[i,f])(loc(prog,b'pitch'),pitch)

def draw(origin,pitch):
 gl('glBindTexture',None,[u,u])(0x0DE1,0)
 gl('glBindFramebuffer',None,[u,u])(0x8D40,shadowfbo)
 gl('glViewport',None,[i,i,i,i])(0,0,16,16)
 gl('glEnable',None,[u])(0x0B71)
 gl('glClear',None,[u])(0x0100)
 uniforms(shadowprogram,*origin,pitch)
 gl('glDrawArrays',None,[u,i,i])(0x0004,0,6)
 depths=(f*(16*16))()
 gl('glReadPixels',None,[i,i,i,i,u,u,p])(0,0,16,16,0x1902,0x1406,depths)
 assert all(z==0.25 or z==1 for z in depths) and 0.25 in depths
 gl('glBindFramebuffer',None,[u,u])(0x8D40,maskfbo)
 gl('glViewport',None,[i,i,i,i])(0,0,384,384)
 gl('glDisable',None,[u])(0x0B71)
 gl('glBindTexture',None,[u,u])(0x0DE1,depth)
 uniforms(maskprogram,*origin,pitch)
 gl('glDrawArrays',None,[u,i,i])(0x0004,0,3)
 pixels=(C.c_ubyte*(384*384*4))()
 gl('glReadPixels',None,[i,i,i,i,u,u,p])(0,0,384,384,0x1908,0x1401,pixels)
 raw=bytes(pixels)
 mask=raw[::4]
 assert mask==raw[1::4]==raw[2::4] and set(mask)=={0,255}
 return sum(z==0.25 for z in depths), mask

from fractions import Fraction as F
from math import floor
centers=[(F(0),F(0)),(F(3,10),F(1,8)),(F(11,20),F(-3,4))]
groups={
 'moving_fixed_extent_no_snap':(centers,[F(16)]*3,False),
 'moving_fixed_extent_snap':(centers,[F(16)]*3,True),
 'changing_extent_despite_snap':(centers[:1]*3,[F(16),F(17),F(112,5)],True),
}
output={}
for name,(xyz,ws,snap) in groups.items():
 rows=[]
 for (x,y),w in zip(xyz,ws,strict=True):
  pitch=w/16
  if snap:
   x,y=[floor(v/pitch+F(1,2))*pitch for v in [x,y]]
  origin=(x-w/2,y-w/2)
  count,m=draw(tuple(map(float,origin)),float(pitch))
  if not rows: baseline=m
  rows.append({'origin':list(map(str,origin)),'pitch':str(pitch),
               'written_depth_texels':count,'shadow_count':m.count(0),
               'mask_changed_points':sum(a!=b for a,b in zip(baseline,m,strict=True))})
 output[name]=rows
assert [r['mask_changed_points'] for r in output['moving_fixed_extent_snap']]==[0,0,0]
assert all(row['mask_changed_points']>0 for n,rows in output.items() if n!='moving_fixed_extent_snap' for row in rows[1:])
error=gl('glGetError',u,[])()
assert error==0, hex(error)
egl('eglMakeCurrent',u,[p,p,p,p])(D,None,None,None)
egl('eglDestroyContext',u,[p,p])(D,ctx)
egl('eglDestroySurface',u,[p,p])(D,surface)
egl('eglTerminate',u,[p])(D)
print(json.dumps({'backend':info,'depth_texture_size':[16,16],'receiver_points':[384,384],
                  'cases':output,'gl_error':error},indent=2))
