"""EGL/OpenGL software raster, per-buffer pre-exposure contract."""
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

import math
vert='''#version 330 core
void main(){
 const vec2 v[3]=vec2[3](vec2(-1,-1),vec2(3,-1),vec2(-1,3));
 gl_Position=vec4(v[gl_VertexID],0,1);
}
'''
write_color='''#version 330 core
uniform float pre;
out vec4 color;
void main(){
 float linearLight = gl_FragCoord.x < 1.0 ? 2.88 : 28.8;
 color=vec4(vec3(linearLight*pre),1.0);
}
'''
read_color='''#version 330 core
uniform sampler2D rendered;
uniform float multiplier;
out vec4 color;
void main(){
 vec3 stored = texelFetch(rendered,ivec2(gl_FragCoord.xy),0).rgb;
 color = vec4(stored*multiplier,1.0);
}
'''
gen=gl('glGenVertexArrays',None,[i,C.POINTER(u)])
vao=u();gen(1,C.byref(vao))
gl('glBindVertexArray',None,[u])(vao)
for flag in (0x0BD0,0x0BE2,0x8DB9,0x0B71,0x0B44,0x0C11):
 gl('glDisable',None,[u])(flag)
gl('glViewport',None,[i,i,i,i])(0,0,2,1)

def fbo(fmt):
 tex=u(); fb=u()
 gl('glGenTextures',None,[i,C.POINTER(u)])(1,C.byref(tex))
 gl('glBindTexture',None,[u,u])(0x0DE1,tex)
 gl('glTexImage2D',None,[u,i,i,i,i,i,u,u,p])(0x0DE1,0,fmt,2,1,0,0x1908,0x1406,None)
 for mode in (0x2800,0x2801):
  gl('glTexParameteri',None,[u,u,i])(0x0DE1,mode,0x2600)
 gl('glGenFramebuffers',None,[i,C.POINTER(u)])(1,C.byref(fb))
 gl('glBindFramebuffer',None,[u,u])(0x8D40,fb)
 gl('glFramebufferTexture2D',None,[u,u,u,u,i])(0x8D40,0x8CE0,0x0DE1,tex,0)
 assert gl('glCheckFramebufferStatus',u,[u])(0x8D40)==0x8CD5
 return tex,fb

src,src_fb=fbo(0x881A) # RGBA16F: finite positive test values; no clamping test
_,out_fb=fbo(0x8814) # RGBA32F: read linear values >1, no tone curve
encode=program(vert,write_color)
decode=program(vert,read_color)
def bind(prog,fb):
 gl('glBindFramebuffer',None,[u,u])(0x8D40,fb)
 gl('glUseProgram',None,[u])(prog)
def set_f(prog,name,value):
 l=gl('glGetUniformLocation',i,[u,C.c_char_p])(prog,name.encode())
 assert l>=0
 gl('glUniform1f',None,[i,f])(l,value)
def pixels():
 values=(f*8)()
 gl('glReadPixels',None,[i,i,i,i,u,u,p])(0,0,2,1,0x1908,0x1406,values)
 assert all(values[k]==values[k+1]==values[k+2] and values[k+3]==1.0 for k in [0,4])
 return [values[0],values[4]]
def render():
 gl('glDrawArrays',None,[u,i,i])(0x0004,0,3)
results={}
for name,pre in [('old_pre',8.),('new_pre',1/16)]:
 gl('glBindTexture',None,[u,u])(0x0DE1,0)
 bind(encode,src_fb)
 set_f(encode,'pre',pre)
 render()
 enc=pixels()
 row={}
 for mode,m in [('correct', (1/16)/pre),('mistaken_direct_gain',1/16)]:
  bind(decode,out_fb)
  gl('glBindTexture',None,[u,u])(0x0DE1,src)
  set_f(decode,'multiplier',m)
  render()
  row[mode]=pixels()
 results[name]={'pre':pre,'stored_linear':enc,**row}
assert results['old_pre']['correct']==results['new_pre']['correct']
for got,expect in zip(results['old_pre']['correct'],[.18,1.8],strict=True):
 assert math.isclose(got,expect,rel_tol=.001),(got,expect)
assert all(wrong/good==8. for wrong,good in zip(results['old_pre']['mistaken_direct_gain'],results['old_pre']['correct'],strict=True))
assert all(wrong/good==1/16 for wrong,good in zip(results['new_pre']['mistaken_direct_gain'],results['new_pre']['correct'],strict=True))
error=gl('glGetError',u,[])()
assert error==0,hex(error)
egl('eglMakeCurrent',u,[p,p,p,p])(D,None,None,None)
egl('eglDestroyContext',u,[p,p])(D,ctx)
egl('eglDestroySurface',u,[p,p])(D,surface)
egl('eglTerminate',u,[p])(D)
print(json.dumps({'backend':info,'source':'RGBA16F','output':'RGBA32F','results':results,'gl_error':error},indent=2))
