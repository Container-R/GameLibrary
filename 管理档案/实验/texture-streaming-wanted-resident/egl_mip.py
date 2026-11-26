"""Read labeled mip samples on software OpenGL; does not stream data."""
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
W,H = 32,8
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
layout(binding=0) uniform sampler2D src;
uniform int mode;
out vec4 color;
void main() {
    vec2 uv=vec2(gl_FragCoord.x / 64.0, 0.5);
    if (mode==0) color=texture(src, uv);
    else if (mode==1) color=textureLod(src, uv, 0.0);
    else {
        int w=textureSize(src,0).x;
        color=vec4(w & 255, w >> 8, textureQueryLevels(src),255)/255.0;
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
target = 0x0DE1  # TEXTURE_2D
tex, view, neutral, clamped = u(),u(),u(),u()
for obj in (tex,view): g("GenTextures",None,i,p)(1,C.byref(obj))
g("BindTexture",None,u,u)(target,tex)
g("TexStorage2D",None,u,i,u,i,i)(target,9,0x8058,256,256) # RGBA8
colors=[(0,0,255,255),(0,255,0,255),(255,0,0,255)]
colors.extend((40+18*l,80+10*l,130-7*l,255) for l in range(3,9))
for level,rgba in enumerate(colors):
    size=256>>level
    buf=C.create_string_buffer(bytes(rgba)*size*size)
    g("TexSubImage2D",None,u,i,i,i,i,i,u,u,p)(target,level,0,0,size,size,0x1908,0x1401,buf)
g("TextureView",None,u,u,u,u,u,u,u,u)(view,target,tex,0x8058,2,7,0,1)
for obj in (neutral,clamped):
    g("GenSamplers",None,i,p)(1,C.byref(obj))
    for par,val in [(0x2801,0x2700),(0x2800,0x2600),(0x2802,0x812F),(0x2803,0x812F)]:
        g("SamplerParameteri",None,u,u,i)(obj,par,val)
g("SamplerParameterf",None,u,u,C.c_float)(clamped,0x813A,2.0) # TEXTURE_MIN_LOD
error=g("GetError",u)
assert error()==0
def read(texture,sampler,test_mode):
    g("BindTexture",None,u,u)(target,texture)
    g("BindSampler",None,u,u)(0,sampler)
    g("Uniform1i",None,i,i)(mode,test_mode)
    g("DrawArrays",None,u,i,i)(4,0,3)
    out=(C.c_ubyte*4)()
    g("ReadPixels",None,i,i,i,i,u,u,p)(W//2,H//2,1,1,0x1908,0x1401,out)
    assert error()==0
    return tuple(out)

for name,obj,sampler,expected in [
    ("full with sampler minLOD=2",tex,clamped,(2,2,0,256,9)),
    ("view of asset mip 2..8",view,neutral,(2,2,2,64,7)),
    ("full with gradient choosing mip 2",tex,neutral,(2,0,0,256,9)),
]:
    results=[colors.index(read(obj,sampler,0)),colors.index(read(obj,sampler,1)),
             colors.index(read(obj,neutral,1))]
    lo,hi,count,_=read(obj,sampler,2)
    got=(*results,lo+256*hi,count)
    print(f"{name}: implicit/explicit0/neutral0={results}; level0_width={got[-2]}; levels={count}")
    assert got==expected, (got,expected)
