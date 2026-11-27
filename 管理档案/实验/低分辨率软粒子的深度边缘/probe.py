"""Two-pass software OpenGL depth/opacity probe."""
import ctypes as C
import os

os.environ["LIBGL_ALWAYS_SOFTWARE"] = "true"
os.environ["MESA_SHADER_CACHE_DISABLE"] = "true"
egl, gl = C.CDLL("libEGL.so.1"), C.CDLL("libGL.so.1")
p, i, u = C.c_void_p, C.c_int, C.c_uint

def bind(lib, name, ret, *args):
    fn = getattr(lib, name)
    fn.restype, fn.argtypes = ret, args
    return fn

def e(name, ret, *args):
    return bind(egl, "egl" + name, ret, *args)

def g(name, ret, *args):
    return bind(gl, "gl" + name, ret, *args)

display = e("GetPlatformDisplay",p,u,p,p)(0x31DD,None,None)
assert display and e("Initialize",u,p,p,p)(display,None,None)
assert e("BindAPI",u,u)(0x30A2)
cfg, n = p(), i()
attrs = (i*15)(0x3033,1,0x3040,8,0x3024,8,0x3023,8,0x3022,8,0x3021,8,0x3032,0,0x3038)
assert e("ChooseConfig",u,p,p,p,i,p)(display,attrs,C.byref(cfg),1,C.byref(n)) and n.value == 1
W,H = 4,2
surface = e("CreatePbufferSurface",p,p,p,p)(display,cfg,(i*5)(0x3057,W,0x3056,H,0x3038))
context = e("CreateContext",p,p,p,p,p)(display,cfg,None,(i*7)(0x3098,4,0x30FB,5,0x30FD,1,0x3038))
assert surface and context and e("MakeCurrent",u,p,p,p,p)(display,surface,surface,context)
getstr = g("GetString",C.c_char_p,u)
print(getstr(0x1F01).decode())
print(getstr(0x1F02).decode())

g("Viewport",None,i,i,i,i)(0,0,W,H)
for flag in (0x0BD0, 0x809D, 0x0BE2, 0x0B71, 0x8DB9):
    g("Disable",None,u)(flag) # dither, MSAA, blend, depth, framebuffer sRGB
vao=u()
g("GenVertexArrays",None,i,p)(1,C.byref(vao))
g("BindVertexArray",None,u)(vao)

def shader(stage,source):
    ident=g("CreateShader",u,u)(stage)
    src=(C.c_char_p*1)(source.encode())
    g("ShaderSource",None,u,i,p,p)(ident,1,src,None)
    g("CompileShader",None,u)(ident)
    ok=i()
    g("GetShaderiv",None,u,u,p)(ident,0x8B81,C.byref(ok))
    if not ok.value:
        buf=C.create_string_buffer(8192)
        g("GetShaderInfoLog",None,u,i,p,p)(ident,len(buf),None,buf)
        raise RuntimeError(buf.value.decode())
    return ident

vertex = shader(0x8B31, """#version 450 core
void main() {
    const vec2 v[3] = vec2[3](vec2(-1,-1), vec2(3,-1), vec2(-1,3));
    gl_Position = vec4(v[gl_VertexID], 0, 1);
}
""")
fragment = shader(0x8B30, """#version 450 core
layout(binding=0) uniform sampler2D fullDepth;
layout(binding=1) uniform sampler2D coarseData;
uniform int mode;
out vec4 color;
float fade(float z) { return clamp((z-4.0)/2.0, 0.0, 1.0); }
void main(){
  ivec2 xy=ivec2(gl_FragCoord.xy);
  if(mode <= 2){
    ivec2 o=xy*2;
    vec4 v=vec4(texelFetch(fullDepth,o,0).r,texelFetch(fullDepth,o+ivec2(1,0),0).r,
                texelFetch(fullDepth,o+ivec2(0,1),0).r,texelFetch(fullDepth,o+ivec2(1,1),0).r);
    float z=(mode==0)?min(min(v.x,v.y),min(v.z,v.w)):
            ((mode==1)?max(max(v.x,v.y),max(v.z,v.w)):dot(v,vec4(0.25)));
    color=vec4(z,fade(z),0,1);
  }else{
    float z=texelFetch(fullDepth,xy,0).r;
    float a=fade(z);
    if(mode==4) a=texture(coarseData,vec2(gl_FragCoord.x/4.0,0.5)).g;
    if(mode==5 || mode==6){
      vec2 l=texelFetch(coarseData,ivec2(0,0),0).rg;
      vec2 r=texelFetch(coarseData,ivec2(1,0),0).rg;
      vec2 best=abs(l.x-z)<=abs(r.x-z)?l:r;
      a=(mode==6 && abs(best.x-z)>0.01)?fade(z):best.y;
    }
    color=vec4(a,0,0,1);
  }
}
""")
program=g("CreateProgram",u)()
for sh in (vertex,fragment): g("AttachShader",None,u,u)(program,sh)
g("LinkProgram",None,u)(program)
success=i()
g("GetProgramiv",None,u,u,p)(program,0x8B82,C.byref(success))
assert success.value
g("UseProgram",None,u)(program)
mode=g("GetUniformLocation",i,u,C.c_char_p)(program,b"mode")
assert mode >= 0
TEX = 0x0DE1
depth,coarse,fbo=u(),u(),u()
for unit,obj,fmt,w,h in [(0,depth,0x822E,4,2),(1,coarse,0x8230,2,1)]:
    g("GenTextures",None,i,p)(1,C.byref(obj))
    g("ActiveTexture",None,u)(0x84C0+unit)
    g("BindTexture",None,u,u)(TEX,obj)
    g("TexStorage2D",None,u,i,u,i,i)(TEX,1,fmt,w,h) # R32F / RG32F
    for par,val in [(0x2801,0x2601),(0x2800,0x2601),(0x2802,0x812F),(0x2803,0x812F)]:
        g("TexParameteri",None,u,u,i)(TEX,par,val)
g("GenFramebuffers",None,i,p)(1,C.byref(fbo))
FB=0x8D40
g("BindFramebuffer",None,u,u)(FB,fbo)
g("FramebufferTexture2D",None,u,u,u,u,i)(FB,0x8CE0,TEX,coarse,0)
assert g("CheckFramebufferStatus",u,u)(FB)==0x8CD5

def draw(target, w,h,step):
    g("BindFramebuffer",None,u,u)(FB,target)
    g("Viewport",None,i,i,i,i)(0,0,w,h)
    g("Uniform1i",None,i,i)(mode,step)
    g("DrawArrays",None,u,i,i)(4,0,3)

def pixels(step):
    draw(0,4,2,step)
    arr=(C.c_ubyte*32)()
    g("ReadPixels",None,i,i,i,i,u,u,p)(0,0,4,2,0x1908,0x1401,arr)
    assert arr[0:16]==arr[16:32]
    return list(arr[0:16:4])

def setup(row):
    g("ActiveTexture",None,u)(0x84C0)
    g("TexSubImage2D",None,u,i,i,i,i,i,u,u,p)(TEX,0,0,0,4,2,0x1903,0x1406,(C.c_float*8)(*(row*2)))

def build(mode):
    # The coarse sampler is never accessed by the reduction shader branch.
    # Explicitly unbind its texture from the sampling unit during this draw.
    g("ActiveTexture",None,u)(0x84C1)
    g("BindTexture",None,u,u)(TEX,0)
    draw(fbo,2,1,mode)
    g("BindTexture",None,u,u)(TEX,coarse)

setup([10,2,10,10])
cases={'full': pixels(3)}
build(0)
cases['nearest+bilinear']=pixels(4)
cases['nearest+depth pick']=pixels(5)
build(1)
cases['farthest+bilinear']=pixels(4)
build(2)
cases['mean+bilinear']=pixels(4)
setup([10,2,10,2])
cases['alternating full']=pixels(3)
build(0)
cases['alternating depth pick']=pixels(5)
cases['alternating full fallback']=pixels(6)
expected=[[255,0,255,255],[0,64,191,255],[255,0,255,255],
          [255,255,255,255],[255,255,255,255],[255,0,255,0],
          [0,0,0,0],[255,0,255,0]]
assert list(cases.values())==expected, cases
assert g("GetError",u)()==0
for name, row in cases.items(): print(name, row)
