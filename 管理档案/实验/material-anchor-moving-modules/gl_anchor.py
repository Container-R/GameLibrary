"""OpenGL offscreen projection anchors on two module draws. Linux + EGL + Mesa."""
import ctypes as c

P, I, U, F, S = c.c_void_p, c.c_int, c.c_uint, c.c_float, c.c_ssize_t
egl, gl = c.CDLL("libEGL.so.1"), c.CDLL("libGL.so.1")
def sig(lib, name, result, *types):
    fn = getattr(lib, name)
    fn.restype, fn.argtypes = result, types
    return fn
def e(name, result, *types):
    return sig(egl, "egl" + name, result, *types)
def g(name, result, *types):
    return sig(gl, "gl" + name, result, *types)
def ints(*x):
    return (I * len(x))(*x)
def obj(name):
    h = U()
    g("Gen" + name, None, I, c.POINTER(U))(1, c.byref(h))
    return h

W, H = 128, 32
d = e("GetPlatformDisplay", P, U, P, P)(0x31DD, None, None) # Mesa surfaceless
major, minor = I(), I()
assert d and e("Initialize", U, P, P, P)(d, c.byref(major), c.byref(minor))
assert e("BindAPI", U, U)(0x30A2) # desktop OpenGL
cfg, count = P(), I()
assert e("ChooseConfig", U, P, P, P, I, P)(
    d, ints(0x3033, 1, 0x3040, 8, 0x3024, 8, 0x3023, 8, 0x3022, 8, 0x3021, 8, 0x3038),
    c.byref(cfg), 1, c.byref(count)) and count.value == 1
surf = e("CreatePbufferSurface", P, P, P, P)(d, cfg, ints(0x3057, W, 0x3056, H, 0x3038))
ctx = e("CreateContext", P, P, P, P, P)(d, cfg, None, ints(0x3098, 3, 0x30FB, 3, 0x3038))
assert ctx and surf and e("MakeCurrent", U, P, P, P, P)(d, surf, surf, ctx)
print(g("GetString", c.c_char_p, U)(0x1F02).decode())
print(g("GetString", c.c_char_p, U)(0x1F01).decode())

def shader(kind, code):
    sh = g("CreateShader", U, U)(kind)
    src = (c.c_char_p * 1)(code.encode())
    g("ShaderSource", None, U, I, c.POINTER(c.c_char_p), P)(sh, 1, src, None)
    g("CompileShader", None, U)(sh)
    ok = I()
    g("GetShaderiv", None, U, U, P)(sh, 0x8B81, c.byref(ok))
    if not ok.value:
        msg = c.create_string_buffer(2000)
        g("GetShaderInfoLog", None, U, I, P, P)(sh, len(msg), None, msg)
        raise RuntimeError(msg.value.decode())
    return sh

vs=shader(0x8B31,"""#version 330 core
out vec2 localPos;
void main(){
    const vec2 v[3]=vec2[3](vec2(0,0),vec2(2,0),vec2(0,2));
    vec2 q=v[gl_VertexID];
    localPos=q*vec2(2,1);
    gl_Position=vec4(q*2.-1.,0,1);
}
""")
fs=shader(0x8B30,"""#version 330 core
in vec2 localPos;
out vec4 outValue;
uniform float pieceX;
uniform vec2 anchor;
uniform int turn;
uniform int mode; // 0 local; 1 world; 2 shared
void main(){
    mat2 rot=(turn==0) ? mat2(1) : mat2(0,1,-1,0);
    vec2 assembled=localPos+vec2(pieceX,0);
    vec2 world=rot*assembled+anchor;
    vec2 pos=(mode==0) ? localPos : ((mode==1) ? world : transpose(rot)*(world-anchor));
    float phase=fract(pos.x/3.);
    outValue=vec4(phase,vec2(phase<.35 ? .2 : .8,phase<.35 ? .77 : .25),1);
}
""")
pr=g("CreateProgram",U)()
for sh in (vs,fs):
    g("AttachShader",None,U,U)(pr,sh)
g("LinkProgram",None,U)(pr)
ok=I()
g("GetProgramiv",None,U,U,P)(pr,0x8B82,c.byref(ok))
assert ok.value
g("UseProgram",None,U)(pr)
g("BindVertexArray",None,U)(obj("VertexArrays"))
TEX, FB, RGBA = 0x0DE1, 0x8D40, 0x1908
out=obj("Textures")
g("BindTexture",None,U,U)(TEX,out)
g("TexImage2D",None,U,I,I,I,I,I,U,U,P)(TEX,0,0x8814,W,H,0,RGBA,0x1406,None)
fb=obj("Framebuffers")
g("BindFramebuffer",None,U,U)(FB,fb)
g("FramebufferTexture2D",None,U,U,U,U,I)(FB,0x8CE0,TEX,out,0)
assert g("CheckFramebufferStatus",U,U)(FB)==0x8CD5
for state in (0x0BD0,0x8DB9,0x0BE2):
    g("Disable",None,U)(state)

def loc(name):
    x=g("GetUniformLocation",I,U,c.c_char_p)(pr,name.encode())
    assert x>=0
    return x

def render(mode,turn,t):
    g("Uniform1i",None,I,I)(loc("turn"),turn)
    g("Uniform1i",None,I,I)(loc("mode"),mode)
    g("Uniform2f",None,I,F,F)(loc("anchor"),*t)
    for i in (0,1): # two independent draws, same shader and group parameters
        g("Viewport",None,I,I,I,I)(i*W//2,0,W//2,H)
        g("Uniform1f",None,I,F)(loc("pieceX"),2*i)
        g("DrawArrays",None,U,I,I)(4,0,3)
    rgba=(F*(W*H*4))()
    g("ReadPixels",None,I,I,I,I,U,U,P)(0,0,W,H,RGBA,0x1406,rgba)
    assert g("GetError",U)()==0
    return list(rgba)

def probe(v,x,y=H//2):
    return v[4*(y*W+x)]

def eq(a,b,tol=1e-5):
    return all(abs(x-y)<=tol for x,y in zip(a,b))

data={}
for name,mode in (("per-piece",0),("fixed world",1),("shared moving",2)):
    a=render(mode,0,(0,0))
    b=render(mode,1,(5,7))
    data[name]=(a,b)
    print(f"{name:14s} seam-neighbor phases {probe(a,63):.6f} {probe(a,64):.6f}; "
          f"one moved probe {probe(a,64):.6f} -> {probe(b,64):.6f}; "
          f"full before/after match={eq(a,b)}")
    assert (abs(probe(a,63)-probe(a,64)) < .02)==(mode!=0)
    assert eq(a,b)==(mode!=1)

wb,wa=render(1,0,(2000,4000)),render(1,0,(1000,2000))
gb,ga=render(2,0,(2000,4000)),render(2,0,(1000,2000))
print(f"same point after origin shift: raw world {probe(wb,64):.6f} -> {probe(wa,64):.6f}; "
      f"shared {probe(gb,64):.6f} -> {probe(ga,64):.6f}")
assert not eq(wb,wa,1e-4) and eq(gb,ga,1e-4)
# Compact scientific image from measured debug pixel output, no lighting.
from PIL import Image,ImageDraw
canvas=Image.new('RGB',(530,250),'#17202c')
draw=ImageDraw.Draw(canvas)
for x,label in ((9,"INDEPENDENT LOCAL"),(185,"WORLD"),(361,"SHARED ANCHOR")):
    draw.text((x,8),label,fill="white")
    draw.text((x,33),"BEFORE",fill="white")
    draw.text((x,132),"AFTER",fill="white")
for j,(name,(before,after)) in enumerate(data.items()):
    left=9+j*176
    for p,top in ((before,48),(after,147)):
        tile=Image.new('RGB',(W,H))
        tile.putdata([tuple(round(255*c) for c in p[i:i+3]) for i in range(0,len(p),4)])
        tile=tile.transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((160,72),Image.Resampling.NEAREST)
        canvas.paste(tile,(left,top))
        draw.line((left+80,top-3,left+80,top-1),fill="white")
        draw.line((left+80,top+72,left+80,top+74),fill="white")
draw.text((9,230),"White ticks mark the join. Debug RGB, not a lit material.",fill="white")
canvas.save("anchor_readback.png")
