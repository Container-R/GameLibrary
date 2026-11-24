"""Run with python3 on Linux with EGL/OpenGL and a surfaceless Mesa driver."""
import ctypes as c
import hashlib
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

W = H = 128
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

prog = g("CreateProgram", U)()
vs = b"""#version 330 core
layout(location=0) in vec2 localPos;
uniform mat2 joint;
out vec2 posed;
void main() { posed = joint * localPos; gl_Position = vec4(posed / 2.5, 0.0, 1.0); }
"""
fs = b"""#version 330 core
out vec4 color;
void main() { color = vec4(1.0); }
"""
for kind, source in ((0x8B31, vs), (0x8B30, fs)):
    g("AttachShader", None, U, U)(prog, shader(kind, source))
g("TransformFeedbackVaryings", None, U, I, P, U)(
    prog, 1, (c.c_char_p*1)(b"posed"), 0x8C8C)
g("LinkProgram", None, U)(prog)
check(prog, "Program", 0x8B82)
g("UseProgram", None, U)(prog)
loc = g("GetUniformLocation", I, U, c.c_char_p)(prog, b"joint")
assert loc >= 0
vao, vbo, tfb = obj("VertexArrays"), obj("Buffers"), obj("Buffers")
g("BindVertexArray", None, U)(vao)
g("BindBuffer", None, U, U)(0x8892, vbo)
verts = (F*4)(0, 0, 2, 0)
g("BufferData", None, U, S, P, U)(0x8892, c.sizeof(verts), verts, 0x88E4)
g("VertexAttribPointer", None, U,I,U,c.c_ubyte,I,P)(0,2,0x1406,0,0,None)
g("EnableVertexAttribArray", None, U)(0)
g("BindBuffer", None, U, U)(0x8C8E, tfb)
g("BufferData", None, U, S, P, U)(0x8C8E, c.sizeof(verts), None, 0x88E9)
g("BindBufferBase", None, U, U, U)(0x8C8E, 0, tfb)
g("Viewport", None, I,I,I,I)(0,0,W,H)
g("Disable", None, U)(0x0BD0) # dither
g("ClearColor", None, F,F,F,F)(0,0,0,1)
def render(deg):
    a = math.radians(deg)
    p, q = math.cos(a), math.sin(a)
    g("UniformMatrix2fv", None, I,I,c.c_ubyte,P)(loc,1,0,(F*4)(p,q,-q,p))
    g("Clear", None, U)(0x4000)
    g("BeginTransformFeedback", None, U)(1) # GL_LINES
    g("DrawArrays", None, U,I,I)(1,0,2)
    g("EndTransformFeedback", None)()
    coords, pix = (F*4)(), (c.c_ubyte*(W*H*4))()
    g("GetBufferSubData", None, U,S,S,P)(0x8C8E,0,c.sizeof(coords),coords)
    g("ReadPixels", None, I,I,I,I,U,U,P)(0,0,W,H,0x1908,0x1401,pix)
    assert g("GetError", U)() == 0
    raw = bytes(pix)
    assert raw[0::4].count(255) > 20, "blank comparison is meaningless"
    for actual, expected in zip(coords, [0,0,2*p,2*q]):
        assert math.isclose(actual, expected, abs_tol=1e-6)
    return tuple(coords), raw

for index in (9, 10, 11):
    t = index/20
    a, b = 30+(t-.5)*120, 30-(t-.5)*60
    m, n = render(a), render(b)
    count = sum(u != v for u,v in zip(m[1][0::4], n[1][0::4]))
    print(f"t={t:.2f} A={a:.1f} B={b:.1f}  "
          f"A_tip={m[0][2]:.6f},{m[0][3]:.6f}  B_tip={n[0][2]:.6f},{n[0][3]:.6f}  "
          f"changed_pixels={count}  A_sha256={hashlib.sha256(m[1]).hexdigest()}  "
          f"B_sha256={hashlib.sha256(n[1]).hexdigest()}")
    assert (m[0] == n[0]) == (m[1] == n[1]) == (index == 10)
e("MakeCurrent", U, P,P,P,P)(d,None,None,None)
e("DestroyContext", U, P,P)(d,ctx)
e("DestroySurface", U, P,P)(d,surf)
e("Terminate", U, P)(d)
