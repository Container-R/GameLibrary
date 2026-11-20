"""Software EGL: explicit CPU draw admission vs real OpenGL clipping and raster."""
import ctypes as c
import hashlib
import json
import os
import sys

os.environ.update(EGL_PLATFORM="surfaceless", LIBGL_ALWAYS_SOFTWARE="true",
                  MESA_SHADER_CACHE_DISABLE="true")
E = c.CDLL("libEGL.so.1")
G = c.CDLL("libGL.so.1")
P, I, U, F, D = c.c_void_p, c.c_int, c.c_uint, c.c_float, c.c_double
W, H = 64, 32
ACTUAL = (-3, 1)

def api(lib, name, result, *args):
    fn = getattr(lib, name)
    fn.restype, fn.argtypes = result, args
    return fn

def egl(name, result, *args):
    return api(E, "egl" + name, result, *args)

def gl(name, result, *args):
    return api(G, "gl" + name, result, *args)

def check(v):
    if not v:
        raise RuntimeError(f"EGL error {egl('GetError', I)():#x}")
    return v

display = check(egl("GetDisplay", P, P)(None))
check(egl("Initialize", U, P, P, P)(display, None, None))
check(egl("BindAPI", U, U)(0x30A2))  # Desktop OpenGL.
attr = (I*13)(0x3033, 1, 0x3040, 8, 0x3024, 8, 0x3023, 8, 0x3022, 8, 0x3038)
config, n = P(), I()
check(egl("ChooseConfig", U, P, P, P, I, P)(display, attr, c.byref(config), 1, c.byref(n)))
assert n.value == 1
surface = check(egl("CreatePbufferSurface", P, P, P, P)(
    display, config, (I*5)(0x3057, W, 0x3056, H, 0x3038)))
# Compatibility context; immediate-mode triangles keep the fixture dependency-free.
ctx = check(egl("CreateContext", P, P, P, P, P)(display, config, None, (I*1)(0x3038)))
current = egl("MakeCurrent", U, P, P, P, P)
check(current(display, surface, surface, ctx))
s = gl("GetString", c.c_char_p, U)
backend = {k: s(v).decode() for k, v in
           [("vendor", 0x1F00), ("renderer", 0x1F01), ("version", 0x1F02)]}
assert "llvmpipe" in backend["renderer"], backend
for flag in (0x0BD0, 0x0BE2, 0x8DB9, 0x0B71, 0x0B44, 0x0C11, 0x809D):
    gl("Disable", None, U)(flag)
gl("Viewport", None, I,I,I,I)(0,0,W,H)

def run(camera, bound, override=False):
    # Only this interval test uses the culling box. GL sees the actual triangles.
    admit = max(camera[0], bound[0]) <= min(camera[1], bound[1])
    submit = admit or override
    gl("ClearColor", None, F,F,F,F)(0,0,0,1)
    gl("Clear", None, U)(0x4000)
    if submit:
        gl("MatrixMode", None, U)(0x1701)
        gl("LoadIdentity", None)()
        gl("Ortho", None, D,D,D,D,D,D)(*camera, -1, 1, -1, 1)
        gl("Color3f", None, F,F,F)(1,0,0)
        begin, end, vertex = gl("Begin", None, U), gl("End", None), gl("Vertex2d", None,D,D)
        begin(4)
        l,r = ACTUAL
        for v in [(l,-.5),(r,-.5),(r,.5),(l,-.5),(r,.5),(l,.5)]:
            vertex(*v)
        end()
    pixels = (c.c_ubyte*(W*H*4))()
    gl("ReadPixels", None, I,I,I,I,U,U,P)(0,0,W,H,0x1908,0x1401,pixels)
    rgba = bytes(pixels)
    assert set(rgba[1::4]) == set(rgba[2::4]) == {0} and set(rgba[3::4]) == {255}
    red = rgba[0::4]; assert set(red) <= {0,255}
    hits = [(q%W,q//W) for q,value in enumerate(red) if value]
    return dict(camera_x=camera, cpu_bound_x=bound,
                cpu_admitted=admit, cpu_override=override, gl_draws=int(submit),
                red_pixels=len(hits), touched_xy_inclusive=[
                    min(x for x,y in hits),min(y for x,y in hits),
                    max(x for x,y in hits),max(y for x,y in hits)] if hits else None,
                rgba_sha256=hashlib.sha256(rgba).hexdigest()),rgba

small=(-2.25,-1.75); main=(0,4); second=(-5,-4); loose=(-5,1)
cases = {
    "main_small_culled":run(main,small),
    "main_small_forced_draw":run(main,small,True),
    "main_exact_admitted":run(main,ACTUAL),
    "second_exact_culled":run(second,ACTUAL),
    "second_loose_admitted":run(second,loose),
}
rows = {name:row for name,(row,_) in cases.items()}
assert [(r["gl_draws"],r["red_pixels"]) for r in rows.values()] == [
    (0,0),(1,256),(1,256),(0,0),(1,0)]
expected = bytes(255 if x<16 and 8<=y<24 else 0 for y in range(H) for x in range(W))
assert cases["main_small_forced_draw"][1][0::4] == expected
assert cases["main_small_forced_draw"][1] == cases["main_exact_admitted"][1]
assert cases["second_exact_culled"][1] == cases["second_loose_admitted"][1]
error = gl("GetError", U)(); assert error == 0, hex(error)
if len(sys.argv)==2:
    from PIL import Image,ImageDraw
    sheet=Image.new("RGB",(820,166),"#162031")
    label=ImageDraw.Draw(sheet)
    titles=["Main: small","Main: forced","Main: exact","Second: exact","Second: loose"]
    for j,((row,rgba),title) in enumerate(zip(cases.values(),titles,strict=True)):
        x=10+j*164
        label.text((x,8),title,fill="white")
        im=Image.frombytes("RGBA",(W,H),rgba).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        sheet.paste(im.resize((128,64),Image.Resampling.NEAREST),(x,40))
        label.text((x,115),f"draws {row['gl_draws']}, red {row['red_pixels']}",fill="white")
    label.text((10,145),"Actual RGBA8 readback: red = rasterized output; black = cleared background.",fill="white")
    sheet.save(sys.argv[1])
print(json.dumps(dict(backend=backend, size=[W,H], actual_quad_x=ACTUAL, cases=rows,
    scope="Own CPU interval culling; real OpenGL orthographic clipping and raster",
    gl_error=error),indent=2))
check(current(display,None,None,None))
check(egl("DestroyContext",U,P,P)(display,ctx))
check(egl("DestroySurface",U,P,P)(display,surface))
check(egl("Terminate",U,P)(display))
