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

W, H = 96, 40
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

def shader(kind, source):
    sh = g("CreateShader", U, U)(kind)
    block = (c.c_char_p * 1)(source)
    g("ShaderSource", None, U, I, P, P)(sh, 1, block, None)
    g("CompileShader", None, U)(sh)
    check(sh, "Shader", 0x8B81)
    return sh
def check(h, kind, flag):
    ok = I()
    g("Get"+kind+"iv", None, U, U, P)(h, flag, c.byref(ok))
    if not ok.value:
        log = c.create_string_buffer(2048)
        g("Get"+kind+"InfoLog", None, U, I, P, P)(h, len(log), None, log)
        raise RuntimeError(log.value.decode())

# OpenGL comparison: orthographic XY, signed facing, additive samples.
prog = g("CreateProgram", U)()
vs = b"""#version 330 core
layout(location=0) in vec2 pixel;
layout(location=1) in float widthUV;
out float across;
void main() {
    across = widthUV;
    gl_Position = vec4(pixel / vec2(48.0,20.0) - 1.0,0.0,1.0);
}
"""
fs = b"""#version 330 core
in float across;
uniform int diagnostic;
out vec4 color;
void main() {
    if (diagnostic == 0) {
        // Exact intent: one +0.25 red contribution per triangle coverage.
        color = vec4(0.25, 0.0, 0.0, 0.0);
    } else if (diagnostic == 1) {
        color = gl_FrontFacing ? vec4(0.15,0.65,0.45,1) : vec4(0.95,0.57,0.18,1);
    } else {
        color = across >= 0.5 ? vec4(0.2,0.75,1,1) : vec4(0.85,0.23,0.6,1);
    }
}
"""
for kind, src in ((0x8B31, vs), (0x8B30, fs)):
    g("AttachShader", None, U, U)(prog, shader(kind, src))
g("LinkProgram", None, U)(prog)
check(prog, "Program", 0x8B82)
g("UseProgram", None, U)(prog)
diag = g("GetUniformLocation", I,U,c.c_char_p)(prog,b"diagnostic")
assert diag >= 0
vao, vbo, ibo = obj("VertexArrays"), obj("Buffers"), obj("Buffers")
g("BindVertexArray", None,U)(vao)
g("BindBuffer", None,U,U)(0x8892, vbo)
g("BindBuffer", None,U,U)(0x8893, ibo)
indices = (U*6)(0,1,2,2,1,3)
g("BufferData", None,U,S,P,U)(0x8893,c.sizeof(indices),indices,0x88E4)
for loc, count, offset in ((0,2,0),(1,1,8)):
    g("EnableVertexAttribArray", None,U)(loc)
    g("VertexAttribPointer", None,U,I,U,c.c_ubyte,I,P)(loc,count,0x1406,0,12,offset)
g("FrontFace", None,U)(0x0901) # GL_CCW
g("CullFace", None,U)(0x0405) # GL_BACK
g("Viewport", None,I,I,I,I)(0,0,W,H)
for capability in (0x0BD0,0x0B71,0x809D): # dither, depth test, multisample
    g("Disable", None,U)(capability)
g("BlendFunc", None,U,U)(1,1) # GL_ONE + GL_ONE
g("ClearColor", None,F,F,F,F)(0,0,0,0)

def points(eps, mode):
    all_verts=[]
    prev=None
    for s in (-1, 0.5):
        dx,dy = -eps,-2*s # normalize(V × P'), V=+Z; same 2D direction
        norm = math.hypot(dx,dy)
        side = dx/norm, dy/norm
        if prev is None and mode == "reverse":
            side = -side[0],-side[1]
        if prev is not None and mode != "raw" and sum(a*b for a,b in zip(prev,side))<0:
            side = -side[0],-side[1]
        cx,cy = 16+84*(1-s*s),20+84*eps*s
        for sign in (1,-1):
            all_verts.append((cx+12*sign*side[0],cy+12*sign*side[1],(sign+1)/2))
        prev=side
    return all_verts

def area(a,b,c_):
    return (b[0]-a[0])*(c_[1]-a[1])-(b[1]-a[1])*(c_[0]-a[0])

def draw(pts, cull, diagnostic):
    vertices = (F*12)(*(x for p in pts for x in p))
    g("BufferData", None,U,S,P,U)(0x8892,c.sizeof(vertices),vertices,0x88E4)
    g("Enable" if cull else "Disable", None,U)(0x0B44)
    g("Enable" if diagnostic==0 else "Disable", None,U)(0x0BE2)
    g("Uniform1i", None,I,I)(diag,diagnostic)
    g("Clear", None,U)(0x4000)
    g("DrawElements", None,U,I,U,P)(4,6,0x1405,None)
    pixels=(c.c_ubyte*(W*H*4))()
    g("ReadPixels", None,I,I,I,I,U,U,P)(0,0,W,H,0x1908,0x1401,pixels)
    assert g("GetError", U)()==0
    return bytes(pixels)

def coverage(raw):
    red = raw[::4]
    assert set(red) <= {0,64,128}, set(red)
    return len(red)-red.count(0),red.count(128)
def rgb_at(p,x,y):
    i=4*(x+y*W)
    return tuple(p[i:i+3])
def png(path,w,h,data):
    def chunk(typ, payload):
        return struct.pack(">I",len(payload))+typ+payload+struct.pack(">I",zlib.crc32(typ+payload))
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",w,h,8,2,0,0,0))
           +chunk(b"IDAT",zlib.compress(b"".join(b"\0"+row for row in data)))+chunk(b"IEND",b""))
def sheet(panels):
    # Rows: width UV (no cull), front/back (no cull), width UV (CCW only).
    # Columns: raw, sequential sign selection, opposite seed.
    scale, gap = 3, 4
    panel_w,panel_h = W*scale,H*scale
    w,h = 3*panel_w+2*gap,3*panel_h+2*gap
    dark=b"\x12\x12\x12"
    rows=[bytearray(dark*w) for _ in range(h)]
    for j,row in enumerate(panels):
        for i,pix in enumerate(row):
            for y in range(panel_h):
                out=b"".join(bytes(rgb_at(pix,x,H-1-y//scale))*scale for x in range(W))
                start=(panel_w+gap)*i*3
                rows[j*(panel_h+gap)+y][start:start+len(out)]=out
    png("ribbon-gl.png",w,h,rows)

panels=[[],[],[]]
for mode in ("raw","consistent","reverse"):
    pts=points(.01,mode)
    xyArea=(area(*pts[:3]),area(pts[2],pts[1],pts[3]))
    unculled=draw(pts, False, 0)
    visible=draw(pts, True, 0)
    plain, dup=coverage(unculled)
    culled, culled_dup=coverage(visible)
    print(f"{mode}: doubled_area=({xyArea[0]:+.2f},{xyArea[1]:+.2f}) "
          f"union={plain} overlap={dup} CCW_only={culled} "
          f"coverage_sha256={hashlib.sha256(unculled).hexdigest()}")
    uv=draw(pts,False,2)
    faces=draw(pts,False,1)
    uv_cull=draw(pts,True,2)
    for row,img in zip(panels,(uv,faces,uv_cull)):
        row.append(img)
    assert culled_dup==0
    if mode=="raw":
        assert xyArea[0]>0>xyArea[1] and dup>0 and 0<culled<plain
        raw_area=plain
    elif mode=="consistent":
        assert min(xyArea)>0 and dup==0 and culled==plain>raw_area
        repaired=plain
        repaired_mask=tuple(r!=0 for r in unculled[::4])
        repaired_uv=uv
    else:
        assert max(xyArea)<0 and dup==0 and culled==0 and plain==repaired
        # For exactly non-grid edges these two orientations coincide in this fixture.
        assert tuple(r!=0 for r in unculled[::4])==repaired_mask
        # Same x/y points away from the UV transition, opposite positive side.
        for x,y in ((50,26),(50,14)):
            assert rgb_at(repaired_uv,x,y)!=rgb_at(uv,x,y)
            assert rgb_at(repaired_uv,x,y)!=(0,0,0)!=rgb_at(uv,x,y)
        print("UV at x=50 y=26,14 (seed A vs seed B):",
              [(rgb_at(repaired_uv,50,y),rgb_at(uv,50,y)) for y in (26,14)])
print(f"minimum normalized cross magnitude along curve: {.01/math.sqrt(1+.01**2):.7f}")
sheet(panels)
e("MakeCurrent", U,P,P,P,P)(d,None,None,None)
e("DestroyContext", U,P,P)(d,ctx)
e("DestroySurface", U,P,P)(d,surf)
e("Terminate", U,P)(d)
