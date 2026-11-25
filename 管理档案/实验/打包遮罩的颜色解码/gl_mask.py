"""OpenGL offscreen packed-data sampling control. Linux + EGL + Mesa."""
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

W, H = 8, 1
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
out vec4 value;
void main() {
    value = texelFetch(source_texture, ivec2(int(gl_FragCoord.x),0), 0);
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

# Each input texel repeats one byte in R, G, B and A. Change only internal
# format between sampling runs, including all pixel transfer parameters.
scale = (0, 32, 64, 128, 192, 224, 255)
sentinel = (32, 128, 224, 64)
n = len(scale) + 1
TEX, FB, RGBA, GL_FLOAT = 0x0DE1, 0x8D40, 0x1908, 0x1406
pixels = (c.c_ubyte * (4 * n))(*[b for b in scale for _ in range(4)], *sentinel)
def texture(fmt, ty, buf):
    t = obj("Textures")
    g("BindTexture", None, U, U)(TEX, t)
    g("TexImage2D", None, U, I, I, I, I, I, U, U, P)(TEX, 0, fmt, n, 1, 0, RGBA, ty, buf)
    for key, val in ((0x2801,0x2600),(0x2800,0x2600),(0x813D,0)):
        g("TexParameteri", None, U, U, I)(TEX, key, val)
    return t

dest = texture(0x8814, GL_FLOAT, None) # GL_RGBA32F
f = obj("Framebuffers")
g("BindFramebuffer", None, U, U)(FB, f)
g("FramebufferTexture2D", None, U, U, U, U, I)(FB, 0x8CE0, TEX, dest, 0)
assert g("CheckFramebufferStatus", U, U)(FB) == 0x8CD5
g("Viewport", None, I, I, I, I)(0,0,n,1)
for enable in (0x0BD0,0x8DB9,0x0BE2): # dither, framebuffer sRGB, blending
    g("Disable", None, U)(enable)

def run(fmt):
    source = texture(fmt, 0x1401, pixels) # GL_UNSIGNED_BYTE
    g("DrawArrays", None, U, I, I)(4, 0, 3)
    out = (F * (4 * n))()
    g("ReadPixels", None, I, I, I, I, U, U, P)(0, 0, n, 1, RGBA, GL_FLOAT, out)
    assert g("GetError", U)() == 0 and source.value
    g("DeleteTextures", None, I, P)(1, c.byref(source))
    return [tuple(out[i:i+4]) for i in range(0,len(out),4)]

def decode(x):
    return x/12.92 if x <= 0.04045 else ((x+0.055)/1.055)**2.4

linear, srgb = run(0x8058), run(0x8C43) # GL_RGBA8, GL_SRGB8_ALPHA8
print("inputs: same bytes in RGBA; sampler: texelFetch level 0; destination: RGBA32F")
print("byte linear_R    linear_G    linear_B    linear_A    sRGB_R      sRGB_G      sRGB_B      sRGB_A")
for b, L, C in zip(scale, linear, srgb):
    x = b/255
    print(f"{b:3d}  " + "    ".join(f"{v:.6f}" for v in (*L,*C)))
    assert all(abs(v-x) < 1e-6 for v in L)
    assert all(abs(v-decode(x)) < .003 for v in C[:3])
    assert abs(C[3]-x) < 1e-6
assert linear[3][1] >= .4 > srgb[3][1]
assert linear[0] == srgb[0] and linear[-2] == srgb[-2]
assert all(abs(v-b/255) < 1e-6 for v,b in zip(linear[-1],sentinel))
assert all(abs(v-decode(b/255)) < .003 for v,b in zip(srgb[-1][:3],sentinel[:3]))
assert abs(linear[-1][3]-srgb[-1][3]) < 1e-6
print("distinct channel sentinel (32,128,224,64):")
for label, values in (("linear",linear[-1]),("sRGB  ",srgb[-1])):
    print(label+"  "+"  ".join(f"{v:.6f}" for v in values))
print("threshold G>=0.4 at byte 128: linear=True sRGB=False; endpoints equal and alpha unchanged")
e("MakeCurrent", U,P,P,P,P)(d,None,None,None)
e("DestroyContext", U,P,P)(d,ctx)
e("DestroySurface", U,P,P)(d,surf)
e("Terminate", U,P)(d)
