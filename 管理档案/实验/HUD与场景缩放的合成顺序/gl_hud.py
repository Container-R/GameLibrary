"""Run with python3 on Linux with EGL/OpenGL and a surfaceless Mesa driver."""
import ctypes as c
import hashlib
from pathlib import Path
import struct
import zlib
import math

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

W, H = 96, 48
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

FB, READ, DRAW = 0x8D40,0x8CA8,0x8CA9
TEX = 0x0DE1
def surface(w,h):
    f,t = obj("Framebuffers"),obj("Textures")
    g("BindTexture", None,U,U)(TEX,t)
    g("TexImage2D", None,U,I,I,I,I,I,U,U,P)(TEX,0,0x8058,w,h,0,0x1908,0x1401,None)
    g("BindFramebuffer",None,U,U)(FB,f)
    g("FramebufferTexture2D",None,U,U,U,U,I)(FB,0x8CE0,TEX,t,0)
    assert g("CheckFramebufferStatus",U,U)(FB)==0x8CD5
    return f
src=surface(W,H)
low=surface(W//2,H//2)
out=surface(W,H)
g("Disable",None,U)(0x0BD0) # dither
g("Disable",None,U)(0x8DB9) # framebuffer sRGB conversion
def rect(x,y,w,h,col):
    g("Enable",None,U)(0x0C11)
    g("Scissor",None,I,I,I,I)(x,y,w,h)
    g("ClearColor",None,F,F,F,F)(*col,1.)
    g("Clear",None,U)(0x4000)
    g("Disable",None,U)(0x0C11)
def draw_scene():
    rect(0,0,W,H,(0.,0.,0.))
    rect(8,9,38,28,(.10,.14,.20))
    rect(10,10,8,24,(.12,.19,.24))
    rect(23,16,16,14,(.17,.24,.29))
    rect(7,34,40,3,(.15,.22,.31))
glyphs={
    "2":("111","001","111","100","111"),
    "7":("111","001","010","010","010"),
    "0":("111","101","101","101","111")}
def draw_hud(column):
    # Fine mark against fixed black background; separate bitmap glyph control.
    rect(column,12,1,16,(1.,1.,1.))
    rect(58,24,9,1,(1.,1.,1.))
    for j,k in enumerate("270"):
        for row, bits in enumerate(glyphs[k]):
            for x, v in enumerate(bits):
                if v=="1":
                    rect(55+4*j+x,34-row,1,1,(1.,1.,1.))
def blit(source,dest, sw,sh,dw,dh):
    g("BindFramebuffer",None,U,U)(READ,source)
    g("BindFramebuffer",None,U,U)(DRAW,dest)
    g("BlitFramebuffer",None,*([I]*8),U,U)(0,0,sw,sh,0,0,dw,dh,0x4000,0x2601)
def snapshot(which,w,h):
    g("BindFramebuffer",None,U,U)(READ,which)
    p=(c.c_ubyte*(w*h*4))()
    g("ReadPixels",None,I,I,I,I,U,U,P)(0,0,w,h,0x1908,0x1401,p)
    assert g("GetError",U)()==0
    return bytes(p)
def trial(column, early):
    g("BindFramebuffer",None,U,U)(FB,src)
    draw_scene()
    if early:
        draw_hud(column)
    blit(src,low,W,H,W//2,H//2)
    lowdata=snapshot(low,W//2,H//2)
    blit(low,out,W//2,H//2,W,H)
    if not early:
        g("BindFramebuffer",None,U,U)(FB,out)
        draw_hud(column)
    return lowdata,snapshot(out,W,H)
def row(data,y,lo,hi):
    return [(x,data[(y*W+x)*4]) for x in range(lo,hi) if data[(y*W+x)*4]!=0]
a,early=trial(62,True)
b,early2=trial(63,True)
_,late=trial(62,False)
_,late2=trial(63,False)
er,lr=row(early,16,55,71),row(late,16,55,71)
assert a==b and early==early2 and late!=late2
assert lr==[(62,255)] and row(late2,16,55,71)==[(63,255)]
assert [x for x,y in er]==[61,62,63,64] and all(abs(y-t)<=1 for (_,y),t in zip(er,(32,96,96,32)))
assert sum(early[i:i+4]!=late[i:i+4] for i in range(0,len(early),4))>0
print("output=96x48 RGBA8; intermediate=48x24 RGBA8; down/up=GL_LINEAR; GL sRGB conversion off")
for name,img,x in (("early x62",early,62),("early x63",early2,63),("late x62",late,62),("late x63",late2,63)):
    print(f"{name}: line_row={row(img,16,55,71)} frame_sha256={hashlib.sha256(img).hexdigest()}")
print("early intermediate sha256:",hashlib.sha256(a).hexdigest())

def chunk(typ,payload):
    return struct.pack(">I",len(payload))+typ+payload+struct.pack(">I",zlib.crc32(typ+payload))
def image_pair(pics):
    k,gap=5,8
    w,h=W*k*2+gap,H*k
    rows=[]
    for y in range(H-1,-1,-1):
        parts=[]
        for pic in pics:
            parts.append(b"".join(pic[4*(y*W+x):4*(y*W+x)+3]*k for x in range(W)))
        rows.extend([b"\0"+(b"\x28"*3*gap).join(parts)]*k)
    Path("hud-composite.png").write_bytes(b"\x89PNG\r\n\x1a\n"
        +chunk(b"IHDR",struct.pack(">IIBBBBB",w,h,8,2,0,0,0))
        +chunk(b"IDAT",zlib.compress(b"".join(rows)))+chunk(b"IEND",b""))
image_pair((early,late))
e("MakeCurrent", U,P,P,P,P)(d,None,None,None)
e("DestroyContext", U,P,P)(d,ctx)
e("DestroySurface", U,P,P)(d,surf)
e("Terminate", U,P)(d)
