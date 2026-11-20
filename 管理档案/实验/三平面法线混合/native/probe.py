"""Software EGL/OpenGL flat triplanar-normal regression on an exact tilted plane."""
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

# One exact tilted plane, rasterized as two triangles. Orthographic view.
import math
from pathlib import Path
vs='''#version 330 core
out vec3 base;
void main(){
 const vec2 v[6]=vec2[6](vec2(-1,-1),vec2(1,-1),vec2(1,1),vec2(-1,-1),vec2(1,1),vec2(-1,1));
 float a=radians(25.0);
 vec2 q=v[gl_VertexID]*0.8;
 vec3 position=vec3(q,-tan(a)*q.x);
 base=vec3(sin(a),0,cos(a));
 gl_Position=vec4(position,1);
}'''
fs='''#version 330 core
in vec3 base;
uniform sampler2D flatmap;
uniform int mode;
uniform float exponent;
out vec4 result;
void main(){
 vec3 n=normalize(base);
 vec3 w=pow(abs(n),vec3(exponent)); w/=dot(w,vec3(1));
 // Texture stores decoded tangent normal, avoiding quantization/import ambiguity.
 vec3 t=texelFetch(flatmap,ivec2(0),0).xyz;
 vec3 sx=vec3(sign(n.x),0,0), sy=vec3(0,sign(n.y),0), sz=vec3(0,0,sign(n.z));
 vec3 direct=normalize(w.x*(vec3(0,t.x,t.y)+sx*t.z)
                      +w.y*(vec3(t.x,0,t.y)+sy*t.z)
                      +w.z*(vec3(t.x,t.y,0)+sz*t.z));
 vec2 slope=-t.xy/t.z;
 // X: U=y,V=z; Y: U=x,V=z; Z: U=x,V=y. Unit UV scale.
 vec3 body=w.x*vec3(0,slope.x,slope.y)+w.y*vec3(slope.x,0,slope.y)+w.z*vec3(slope.x,slope.y,0);
 vec3 surface=body-n*dot(n,body);
 vec3 gradient=normalize(n-surface);
 vec3 chosen=mode==0?n:(mode==1?direct:gradient);
 vec3 light=normalize(vec3(0.8,0.3,0.5));
 float intensity=0.1+0.6*max(dot(chosen,light),0.0)+0.3*pow(max(dot(chosen,normalize(light+vec3(0,0,1))),0.0),32.0);
 result=vec4(chosen,intensity);
}'''
prog=program(vs,fs)
vao=u();gl('glGenVertexArrays',None,[i,C.POINTER(u)])(1,C.byref(vao));gl('glBindVertexArray',None,[u])(vao)
tex=u();gl('glGenTextures',None,[i,C.POINTER(u)])(1,C.byref(tex));gl('glBindTexture',None,[u,u])(0x0DE1,tex)
flat=(f*4)(0,0,1,1)
gl('glTexImage2D',None,[u,i,i,i,i,i,u,u,p])(0x0DE1,0,0x8814,1,1,0,0x1908,0x1406,flat)
for mode in (0x2800,0x2801):gl('glTexParameteri',None,[u,u,i])(0x0DE1,mode,0x2600)
flattex=tex.value
outtex=u();gl('glGenTextures',None,[i,C.POINTER(u)])(1,C.byref(outtex));gl('glBindTexture',None,[u,u])(0x0DE1,outtex)
S=96
gl('glTexImage2D',None,[u,i,i,i,i,i,u,u,p])(0x0DE1,0,0x8814,S,S,0,0x1908,0x1406,None)
fb=u();gl('glGenFramebuffers',None,[i,C.POINTER(u)])(1,C.byref(fb));gl('glBindFramebuffer',None,[u,u])(0x8D40,fb)
gl('glFramebufferTexture2D',None,[u,u,u,u,i])(0x8D40,0x8CE0,0x0DE1,outtex,0)
assert gl('glCheckFramebufferStatus',u,[u])(0x8D40)==0x8CD5
for flag in (0x0BD0,0x0BE2,0x8DB9,0x0B71,0x0B44):gl('glDisable',None,[u])(flag)
gl('glViewport',None,[i,i,i,i])(0,0,S,S)
gl('glUseProgram',None,[u])(prog)
gl('glBindTexture',None,[u,u])(0x0DE1,flattex)
loc=gl('glGetUniformLocation',i,[u,C.c_char_p])
frames={}; values={}
for exponent in [1,4]:
 for mode,name in enumerate(['baseline','axis_blend','surface_gradient']):
  gl('glUniform1i',None,[i,i])(loc(prog,b'mode'),mode)
  gl('glUniform1f',None,[i,f])(loc(prog,b'exponent'),exponent)
  gl('glClearColor',None,[f,f,f,f])(0,0,0,0);gl('glClear',None,[u])(0x4000)
  gl('glDrawArrays',None,[u,i,i])(0x0004,0,6)
  pixels=(f*(S*S*4))();gl('glReadPixels',None,[i,i,i,i,u,u,p])(0,0,S,S,0x1908,0x1406,pixels)
  sample=list(pixels[(48*S+48)*4:(48*S+48)*4+4])
  angle=math.degrees(math.atan2(sample[0],sample[2]))
  key=f'p{exponent}_{name}'
  values[key]={'normal':sample[:3],'linear_lighting':sample[3],'tilt_degrees':angle,'error_degrees':abs(angle-25)}
  frames[key]=list(pixels)
assert values['p4_axis_blend']['error_degrees']>22
assert all(values[f'p{p}_{m}']['error_degrees']<0.0001 for p in [1,4] for m in ['baseline','surface_gradient'])
assert values['p1_axis_blend']['error_degrees']<0.0001
flat_error=max(abs(a-b) for a,b in zip(frames['p4_baseline'],frames['p4_surface_gradient']))
assert flat_error<1e-6
assert frames['p4_baseline']!=frames['p4_axis_blend']
error=gl('glGetError',u,[])();assert error==0
# Optional contact sheet from ACTUAL readback, no synthetic repaint of geometry.
import sys
if len(sys.argv)==2:
 from PIL import Image,ImageDraw
 sheet=Image.new('RGB',(600,270),'#101820');d=ImageDraw.Draw(sheet)
 for col,name in enumerate(['baseline','axis_blend','surface_gradient']):
  d.text((col*200+8,6),name,fill='white')
  data=frames['p4_'+name]
  for row in [0,1]:
   rgb=[]
   for k in range(0,len(data),4):
    n=data[k:k+4]
    if n[3]==0:rgb.append((16,24,32))
    elif row==0:rgb.append(tuple(round((v*0.5+0.5)*255) for v in n[:3]))
    else:rgb.append((round(max(0,min(1,n[3]))*255),)*3)
   im=Image.new('RGB',(S,S));im.putdata(rgb);im=im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
   sheet.paste(im,(col*200+40,35+row*112))
 d.text((8,250),'p=4; top: normal RGB; bottom: linear lighting (no tonemap)',fill='white')
 sheet.save(sys.argv[1])
print(json.dumps({'backend':info,'geometry':'plane z=-tan(25deg)*x; 2 triangles; orthographic; 96x96 float RGBA','texture':'1x1 RGBA32F decoded tangent normal (0,0,1)','cases':values,'flat_gradient_max_rgba_difference':flat_error,'gl_error':error},indent=2,sort_keys=True))
egl('eglMakeCurrent',u,[p,p,p,p])(D,None,None,None)
egl('eglDestroyContext',u,[p,p])(D,ctx);egl('eglDestroySurface',u,[p,p])(D,surface);egl('eglTerminate',u,[p])(D)
