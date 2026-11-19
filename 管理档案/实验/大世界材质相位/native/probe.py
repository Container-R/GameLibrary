"""Native desktop GL float arithmetic via EGL/Mesa; no engine or raster claim.
Run: python probe.py > observed.json
Standard library only; uses already-installed libEGL/libGL. No persistent GL state.
"""
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
shader_source='''#version 330 core
layout(location=0) in vec4 input_values; // world, origin, host-relative, origin phase
uniform float period;
out vec4 measured;
void main() {
 float relative = input_values.z;
 measured = vec4(input_values.x-input_values.y, relative,
                 mod(relative,period),mod(relative+input_values.w,period));
 gl_Position=vec4(0.0,0.0,0.0,1.0);
}
'''
shader=gl('glCreateShader',u,[u])(0x8B31)
src=C.c_char_p(shader_source.encode());gl('glShaderSource',None,[u,i,C.POINTER(C.c_char_p),C.POINTER(i)])(shader,1,C.byref(src),None)
gl('glCompileShader',None,[u])(shader)
status=i();gl('glGetShaderiv',None,[u,u,C.POINTER(i)])(shader,0x8B81,C.byref(status))
if not status.value:
 log=C.create_string_buffer(8192);gl('glGetShaderInfoLog',None,[u,i,C.POINTER(i),p])(shader,8192,None,log);raise RuntimeError(log.value.decode())
program=gl('glCreateProgram',u,[])();gl('glAttachShader',None,[u,u])(program,shader)
varyings=(C.c_char_p*1)(b'measured');gl('glTransformFeedbackVaryings',None,[u,i,C.POINTER(C.c_char_p),u])(program,1,varyings,0x8C8C)
gl('glLinkProgram',None,[u])(program);gl('glGetProgramiv',None,[u,u,C.POINTER(i)])(program,0x8B82,C.byref(status))
if not status.value:
 log=C.create_string_buffer(8192);gl('glGetProgramInfoLog',None,[u,i,C.POINTER(i),p])(program,8192,None,log);raise RuntimeError(log.value.decode())
gl('glUseProgram',None,[u])(program);location=gl('glGetUniformLocation',i,[u,C.c_char_p])(program,b'period');assert location>=0
gl('glUniform1f',None,[i,f])(location,0.75)
origins=[10000000.,10000000.125];points=[10000000.125,10000000.375]
inputs=[(x,c,x-c,c%0.75) for c in origins for x in points]
flat=(f*16)(*(v for row in inputs for v in row))
vao=u();gl('glGenVertexArrays',None,[i,C.POINTER(u)])(1,C.byref(vao));gl('glBindVertexArray',None,[u])(vao)
buffers=(u*2)();gl('glGenBuffers',None,[i,C.POINTER(u)])(2,buffers)
bind=gl('glBindBuffer',None,[u,u]);data=gl('glBufferData',None,[u,C.c_ssize_t,p,u])
bind(0x8892,buffers[0]);data(0x8892,C.sizeof(flat),flat,0x88E4)
gl('glEnableVertexAttribArray',None,[u])(0);gl('glVertexAttribPointer',None,[u,i,u,C.c_ubyte,i,p])(0,4,0x1406,0,16,None)
bind(0x8C8E,buffers[1]);data(0x8C8E,64,None,0x88E1)
gl('glBindBufferBase',None,[u,u,u])(0x8C8E,0,buffers[1])
gl('glEnable',None,[u])(0x8C89);gl('glBeginTransformFeedback',None,[u])(0x0000)
gl('glDrawArrays',None,[u,i,i])(0x0000,0,4);gl('glEndTransformFeedback',None,[])();gl('glFinish',None,[])()
output=(f*16)();gl('glGetBufferSubData',None,[u,C.c_ssize_t,C.c_ssize_t,p])(0x8C8E,0,64,output)
error=gl('glGetError',u,[])();assert error==0,hex(error)
rows=[]
for j,(world,origin,relative,phase) in enumerate(inputs):
 result=list(output[j*4:j*4+4]);expected=[0.,relative,relative%0.75,world%0.75];assert result==expected,(j,result,expected)
 rows.append({'world_host_double':world,'origin_host_double':origin,'uploaded_float32':list(flat[j*4:j*4+4]),'readback_world_subtract_relative_relative_phase_anchored_phase':result})
result={'scope':'actual desktop OpenGL vertex shader transform feedback; software driver; not engine, GPU hardware, rasterization or image quality','egl_version':[major.value,minor.value],**info,'period':0.75,'rows':rows,'all_exact_assertions_passed':True,'gl_error':error}
# Resources released by context destruction; no files made except caller stdout redirection.
egl('eglMakeCurrent',u,[p,p,p,p])(D,None,None,None)
egl('eglDestroyContext',u,[p,p])(D,ctx);egl('eglDestroySurface',u,[p,p])(D,surface);egl('eglTerminate',u,[p])(D)
print(json.dumps(result,indent=2))
