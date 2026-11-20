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


# 8x8 reference texture: four black/white stripe pairs across each repeat.
# 1024 only enters conceptual texel-density calculation, not this texture.
gl("Enable",None,U)(0x0DE1)
pix=(c.c_ubyte*64)(*(255 if (x+y)%2 else 0 for y in range(8) for x in range(8)))
texture=(U*1)()
gl("GenTextures",None,I,P)(1,texture)
gl("BindTexture",None,U,U)(0x0DE1,texture[0])
for k,val in [(0x2800,0x2600),(0x2801,0x2600),(0x2802,0x2901),(0x2803,0x2901)]:
 gl("TexParameteri",None,U,U,I)(0x0DE1,k,val)
gl("TexImage2D",None,U,I,I,I,I,I,U,U,P)(0x0DE1,0,0x8040,8,8,0,0x1909,0x1401,pix)
gl("MatrixMode",None,U)(0x1701)
gl("LoadIdentity",None)()
gl("Ortho",None,D,D,D,D,D,D)(0,4,0,2,-1,1)
frames={}
def sample(policy, offset):
    # Camera is moved with the module so pixels compare the same surface points.
    uv={"raw":(1,1,0),"anchored":(2,1,0),"world":(2,1,offset/2)}[policy]
    u,v,phase=uv
    gl("ClearColor",None,F,F,F,F)(1,0,1,1)
    gl("Clear",None,U)(0x4000)
    gl("Color3f",None,F,F,F)(1,1,1)
    begin,end,vertex,texcoord=gl("Begin",None,U),gl("End",None),gl("Vertex2d",None,D,D),gl("TexCoord2d",None,D,D)
    begin(4)
    for x,y in [(0,0),(4,0),(4,2),(0,0),(4,2),(0,2)]:
        texcoord(x*u/4+phase,y*v/2)
        vertex(x,y)
    end()
    rgba=(c.c_ubyte*(W*H*4))()
    gl("ReadPixels",None,I,I,I,I,U,U,P)(0,0,W,H,0x1908,0x1401,rgba)
    b=bytes(rgba); frames[policy,offset]=b; red=b[::4]
    assert set(red)=={0,255}; assert red==b[1::4]==b[2::4]
    assert gl("GetError",U)()==0
    def steps(values):return sum(a!=b for a,b in zip(values,values[1:]))
    return {"horizontal_transitions":steps(red[:W]),"vertical_transitions":steps(red[::W]),"first_level":red[0],"sha256":hashlib.sha256(b).hexdigest()}
res={}
for p in ("raw","anchored","world"):
 res[p]={"base":sample(p,0),"shifted":sample(p,0.25)}
assert [res[p]["base"]["horizontal_transitions"] for p in res]==[7,15,15]
assert [res[p]["base"]["vertical_transitions"] for p in res]==[7,7,7]
assert res["anchored"]["base"]==res["world"]["base"]==res["anchored"]["shifted"]
assert res["raw"]["base"]==res["raw"]["shifted"]
assert res["world"]["shifted"]["first_level"]!=res["world"]["base"]["first_level"]
if "--png-base64" in sys.argv:
    import base64,io
    from PIL import Image,ImageDraw
    img=Image.new("RGB",(480,192),"#222b36")
    draw=ImageDraw.Draw(img)
    for i,p in enumerate(res):
        draw.text((160*i+8,6),p,fill="white")
        for j,o in enumerate((0,0.25)):
            patch=Image.frombytes("RGBA",(W,H),frames[p,o]).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            img.paste(patch.resize((128,64),Image.Resampling.NEAREST),(160*i+8,22+80*j))
            draw.text((160*i+8,88+80*j),f"translation {o:g} m",fill="white")
    out=io.BytesIO();img.save(out,format="PNG")
    print(base64.b64encode(out.getvalue()).decode("ascii"))
else:
    print(json.dumps({"backend":backend,"target":[W,H],"translation_m":0.25,"cases":res},indent=2))
check(current(display,None,None,None))
check(egl("DestroyContext",U,P,P)(display,ctx))
check(egl("DestroySurface",U,P,P)(display,surface))
check(egl("Terminate",U,P)(display))
