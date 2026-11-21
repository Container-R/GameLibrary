"""Two offline GL passes, different render-target contracts; not a speed benchmark."""
import ctypes as C
import json
from ctypes import c_void_p as P, c_int as I, c_uint as U, c_float as F, c_char_p as S
egl=C.CDLL("libEGL.so.1")
gl=C.CDLL("libGL.so.1")
def bind(lib,name,ret,*arg):
    fn=getattr(lib,name)
    fn.restype,fn.argtypes=ret,arg
    return fn
D=bind(egl,"eglGetPlatformDisplay",P,U,P,P)(0x31DD,None,None)
assert D, "no Mesa surfaceless EGL display"
version=[I(),I()]
assert bind(egl,"eglInitialize",U,P,P,P)(D,*map(C.byref,version))
assert bind(egl,"eglBindAPI",U,U)(0x30A2)
arr=lambda *a:(I*len(a))(*a)
end=0x3038
config,num=P(),I()
attrs=arr(0x3033,1,0x3040,8,0x3024,8,0x3023,8,0x3022,8,end)
assert bind(egl,"eglChooseConfig",U,P,P,P,I,P)(D,attrs,C.byref(config),1,C.byref(num)) and num.value==1
surf=bind(egl,"eglCreatePbufferSurface",P,P,P,P)(D,config,arr(0x3057,8,0x3056,8,end))
ctx=bind(egl,"eglCreateContext",P,P,P,P,P)(D,config,None,arr(end))
assert surf and ctx and bind(egl,"eglMakeCurrent",U,P,P,P,P)(D,surf,surf,ctx)
def f(name,restype,*args):
    return bind(gl,"gl"+name,restype,*args)
def alloc(name):
    n=U()
    f("Gen"+name,None,I,P)(1,C.byref(n))
    assert n.value
    return n
query=alloc("Queries")
fb=alloc("Framebuffers")
tex=alloc("Textures")
f("BindFramebuffer",None,U,U)(0x8D40,fb)
f("BindTexture",None,U,U)(0x0DE1,tex)
gl_version=f("GetString",S,U)
print(json.dumps({"vendor":gl_version(0x1F00).decode(),"renderer":gl_version(0x1F01).decode(),
                  "version":gl_version(0x1F02).decode()},ensure_ascii=False))
def sample_pass(w,h):
    f("TexImage2D",None,U,I,I,I,I,I,U,U,P)(0x0DE1,0,0x8058,w,h,0,0x1908,0x1401,None)
    f("FramebufferTexture2D",None,U,U,U,U,I)(0x8D40,0x8CE0,0x0DE1,tex,0)
    assert f("CheckFramebufferStatus",U,U)(0x8D40)==0x8CD5
    f("Viewport",None,I,I,I,I)(0,0,w,h)
    f("BeginQuery",None,U,U)(0x8914,query) # GL_SAMPLES_PASSED. Single sample, no depth or stencil.
    f("Begin",None,U)(0x0005)
    for x,y in ((-1.,-1.),(1.,-1.),(-1.,1.),(1.,1.)):
        f("Vertex2f",None,F,F)(x,y)
    f("End",None)()
    f("EndQuery",None,U)(0x8914)
    samples=U()
    f("GetQueryObjectuiv",None,U,U,P)(query,0x8866,C.byref(samples))
    assert f("GetError",U)()==0
    return samples.value
for scale in (1,.7):
    main=(round(1280*scale),round(720*scale))
    output=(1280,720)
    seen=(sample_pass(*main),sample_pass(*output))
    expected=(main[0]*main[1],output[0]*output[1])
    assert seen==expected,(main,output,seen,expected)
    print(json.dumps({"scale":scale,"main":main,"output":output,
        "main_samples":seen[0],"fixed_output_samples":seen[1]}))
