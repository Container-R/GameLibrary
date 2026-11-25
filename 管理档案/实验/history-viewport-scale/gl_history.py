"""OpenGL offscreen history viewport and sampler control. Linux + EGL + Mesa."""
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

W, H = 5, 1
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

vs = shader(0x8B31, """#version 330 core
void main() {
    const vec2 p[3] = vec2[3](vec2(-1,-1), vec2(3,-1), vec2(-1,3));
    gl_Position = vec4(p[gl_VertexID],0,1);
}""")
fs = shader(0x8B30, """#version 330 core
uniform sampler2D source_texture;
uniform float prev_origin, prev_width, current_width;
out vec4 value;
void main() {
    const float u[5] = float[5](0.75, 0.75, 255.0/256.0, 255.0/256.0, 1.01);
    int mode = int(gl_FragCoord.x);
    float h = u[mode];
    float x = prev_origin + h * ((mode == 1) ? current_width : prev_width);
    if (mode >= 3) {
        if (h < 0.0 || h >= 1.0) {
            value = vec4(0,0,0,0); // rejected, not an edge sample
            return;
        }
        x = clamp(x, prev_origin + 0.5, prev_origin + prev_width - 0.5);
    }
    value = texture(source_texture, vec2(x / 128.0, 0.5));
}""")
pr = g("CreateProgram", U)()
for sh in (vs, fs):
    g("AttachShader", None, U, U)(pr, sh)
g("LinkProgram", None, U)(pr)
ok = I()
g("GetProgramiv", None, U, U, P)(pr, 0x8B82, c.byref(ok))
assert ok.value, "shader link"
g("UseProgram", None, U)(pr)
loc = g("GetUniformLocation", I, U, c.c_char_p)(pr, b"source_texture")
assert loc >= 0
g("Uniform1i", None, I, I)(loc, 0)
vao = obj("VertexArrays")
g("BindVertexArray", None, U)(vao)

TEX, FB, RGBA, GL_FLOAT = 0x0DE1, 0x8D40, 0x1908, 0x1406
def texture(width, height, fmt, ty):
    t = obj("Textures")
    g("BindTexture", None, U, U)(TEX, t)
    g("TexImage2D", None, U, I, I, I, I, I, U, U, P)(
        TEX, 0, fmt, width, height, 0, RGBA, ty, None)
    for key, val in ((0x2801,0x2601), (0x2800,0x2601),
                     (0x2802,0x812F), (0x2803,0x812F), (0x813D,0)):
        g("TexParameteri", None, U, U, I)(TEX, key, val)
    return t

def attach(t):
    f = obj("Framebuffers")
    g("BindFramebuffer", None, U, U)(FB, f)
    g("FramebufferTexture2D", None, U, U, U, U, I)(FB, 0x8CE0, TEX, t, 0)
    assert g("CheckFramebufferStatus", U, U)(FB) == 0x8CD5
    return f

dest = texture(W, H, 0x8814, GL_FLOAT) # GL_RGBA32F
dest_fb = attach(dest)
history = texture(128, 4, 0x8058, 0x1401) # GL_RGBA8
history_fb = attach(history)
for state in (0x0BD0, 0x8DB9, 0x0BE2): # dither, sRGB framebuffer, blend
    g("Disable", None, U)(state)

def clear(rgba):
    g("ClearColor", None, F, F, F, F)(*rgba)
    g("Clear", None, U)(0x4000)

def scissor(x, width):
    g("Scissor", None, I, I, I, I)(x, 0, width, 4)

def case(origin, previous, current):
    g("BindFramebuffer", None, U, U)(FB, history_fb)
    g("Disable", None, U)(0x0C11)
    clear((1,0,1,1)) # invalid-history sentinel
    g("Enable", None, U)(0x0C11)
    scissor(origin, previous)
    clear((0,1,0,1))
    scissor(origin + 3 * previous // 4, 1)
    clear((0,0,1,1))
    g("Disable", None, U)(0x0C11)

    g("BindFramebuffer", None, U, U)(FB, dest_fb)
    g("BindTexture", None, U, U)(TEX, history)
    g("Viewport", None, I, I, I, I)(0, 0, W, H)
    for name, val in ((b'prev_origin', origin), (b'prev_width', previous),
                      (b'current_width', current)):
        loc = g("GetUniformLocation", I, U, c.c_char_p)(pr, name)
        assert loc >= 0
        g("Uniform1f", None, I, F)(loc, val)
    g("DrawArrays", None, U, I, I)(4, 0, 3)
    vals = (F * (4 * W))()
    g("ReadPixels", None, I, I, I, I, U, U, P)(0,0,W,H,RGBA,GL_FLOAT,vals)
    assert g("GetError", U)() == 0
    out = [tuple(vals[i:i+4]) for i in range(0, len(vals), 4)]
    print(f"allocation=128x4, previous origin={origin}, width={previous}, current width={current}")
    for name, value in zip(("correct .75", "wrong .75", "raw inside edge",
                            "bounded inside edge", "rejected outside"), out):
        print(f"  {name:21s} " + " ".join(f"{v:.6f}" for v in value))
    return out

g("BindFramebuffer", None, U, U)(FB, dest_fb)
a = case(0, 64, 128)
b = case(0, 128, 64)
d = case(12, 64, 100)
for values in (a,b,d):
    for actual, expected in zip((values[0],values[3],values[4]),
                                ((0,.5,.5,1),(0,1,0,1),(0,0,0,0))):
        assert all(abs(x-y) <= .005 for x,y in zip(actual,expected))
for values,want in ((a,(1,0,1,1)),(b,(0,1,0,1)),(d,(1,0,1,1))):
    assert values[1] == want
assert abs(a[2][0]-.25) <= .005 and abs(d[2][0]-.25) <= .005
assert b[2] == (0,1,0,1)
print("PASS: scale, subrectangle, full-texture control and rejection")
