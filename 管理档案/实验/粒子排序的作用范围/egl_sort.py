"""Offscreen linear RGBA16F readback; no Niagara or hardware GPU."""
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
uniform vec4 rectDepth; // x left/right, view depths at left/right
void main() {
    const vec2 corner[6] = vec2[6](vec2(0,0),vec2(1,0),vec2(0,1),
                                  vec2(0,1),vec2(1,0),vec2(1,1));
    vec2 uv = corner[gl_VertexID];
    float x = mix(rectDepth.x, rectDepth.y, uv.x);
    float depth = mix(rectDepth.z, rectDepth.w, uv.x);
    gl_Position = vec4(x, 2.0 * uv.y - 1.0, depth * 0.4 - 1.0, 1.0);
}
""")
fragment = shader(0x8B30, """#version 450 core
uniform vec3 tint;
out vec4 color;
void main(){color=vec4(tint,0.5);}
""")
program = g("CreateProgram",u)()
for sh in (vertex,fragment): g("AttachShader",None,u,u)(program,sh)
g("LinkProgram",None,u)(program)
success=i()
g("GetProgramiv",None,u,u,p)(program,0x8B82,C.byref(success))
assert success.value
g("UseProgram",None,u)(program)
uniform = g("GetUniformLocation",i,u,C.c_char_p)
rect, tint = uniform(program,b"rectDepth"), uniform(program,b"tint")
assert rect >= 0 and tint >= 0
f = C.c_float
tex, fb, depth = u(),u(),u()
g("GenTextures",None,i,p)(1,C.byref(tex))
g("BindTexture",None,u,u)(0x0DE1,tex)
g("TexStorage2D",None,u,i,u,i,i)(0x0DE1,1,0x881A,W,H) # RGBA16F
g("GenFramebuffers",None,i,p)(1,C.byref(fb))
g("BindFramebuffer",None,u,u)(0x8D40,fb)
g("FramebufferTexture2D",None,u,u,u,u,i)(0x8D40,0x8CE0,0x0DE1,tex,0)
g("GenRenderbuffers",None,i,p)(1,C.byref(depth))
g("BindRenderbuffer",None,u,u)(0x8D41,depth)
g("RenderbufferStorage",None,u,u,i,i)(0x8D41,0x81A6,W,H)
g("FramebufferRenderbuffer",None,u,u,u,u)(0x8D40,0x8D00,0x8D41,depth)
assert g("CheckFramebufferStatus",u,u)(0x8D40)==0x8CD5
g("Enable",None,u)(0x0B71) # depth test
g("DepthFunc",None,u)(0x0201) # LESS
g("Enable",None,u)(0x0BE2) # blend
g("BlendFuncSeparate",None,u,u,u,u)(0x0302,0x0303,1,0x0303)
g("ClearColor",None,f,f,f,f)(0,0,0,1)
g("ClearDepth",None,C.c_double)(1)
mask = g("DepthMask",None,C.c_ubyte)
draw_arrays = g("DrawArrays",None,u,i,i)
uniform4 = g("Uniform4f",None,i,f,f,f,f)
uniform3 = g("Uniform3f",None,i,f,f,f)
read = g("ReadPixels",None,i,i,i,i,u,u,p)
red,blue=(1,0,0),(0,0,1)
al=(-1,0,4,4,red); ar=(0,1,1,1,red)
bl=(-1,0,2,2,blue); br=(0,1,3,3,blue)
card_a=(-1,1,4,1,red); card_b=(-1,1,2,3,blue)
want_l, want_r=(.25,0,.5),(.5,0,.25)

def scenario(label, order, write_depth, expected):
    mask(1)
    g("Clear",None,u)(0x00004000|0x00000100)
    mask(write_depth)
    for x0,x1,z0,z1,rgb in order:
        uniform4(rect,x0,x1,z0,z1)
        uniform3(tint,*rgb)
        draw_arrays(4,0,6) # TRIANGLES
    samples=[]
    for x in (W//4,3*W//4):
        data=(f*4)()
        read(x,H//2,1,1,0x1908,0x1406,C.byref(data))
        samples.append(tuple(data[:3]))
    assert g("GetError",u)()==0
    assert tuple(samples)==expected,(label,samples,expected)
    print(label, "left", samples[0], "right", samples[1])

scenario("sprites_group_A_B",[al,ar,br,bl],False,(want_l,want_l))
scenario("sprites_group_B_A",[br,bl,al,ar],False,(want_r,want_r))
scenario("sprites_interleave",[al,br,bl,ar],False,(want_l,want_r))
scenario("intersecting_cards_A_B",[card_a,card_b],False,(want_l,want_l))
scenario("intersecting_cards_B_A",[card_b,card_a],False,(want_r,want_r))
scenario("sprites_depth_write",[al,ar,br,bl],True,(want_l,(.5,0,0)))
