"""Software OpenGL triangulated vertex-mask draw and float readback."""
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
W = H = 101

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


# Single-sampled RGBA32F FBO: R interpolated input, G applied hard classifier.
tex=(U*1)(); fb=(U*1)()
gl("GenTextures",None,I,P)(1,tex); gl("BindTexture",None,U,U)(0x0DE1,tex[0])
for key in (0x2800,0x2801): gl("TexParameteri",None,U,U,I)(0x0DE1,key,0x2600)
gl("TexImage2D",None,U,I,I,I,I,I,U,U,P)(0x0DE1,0,0x8814,W,H,0,0x1908,0x1406,None)
gl("GenFramebuffers",None,I,P)(1,fb)
gl("BindFramebuffer",None,U,U)(0x8D40,fb[0])
gl("FramebufferTexture2D",None,U,U,U,U,I)(0x8D40,0x8CE0,0x0DE1,tex[0],0)
assert gl("CheckFramebufferStatus",U,U)(0x8D40)==0x8CD5
gl("ReadBuffer",None,U)(0x8CE0)
shader=b"""#version 120
void main() {
 float p=gl_Color.r;
 gl_FragColor=vec4(p, p>=0.503 ? 1.0 : 0.0, 0.0, 1.0);
}
"""
sh=gl("CreateShader",U,U)(0x8B30)
sp=c.c_char_p(shader)
gl("ShaderSource",None,U,I,P,P)(sh,1,c.byref(sp),None)
gl("CompileShader",None,U)(sh)
def valid(obj,name):
    status=I()
    gl("Get"+name+"iv",None,U,U,P)(obj,0x8B81 if name=="Shader" else 0x8B82,c.byref(status))
    if not status.value:
        log=c.create_string_buffer(4096)
        gl("Get"+name+"InfoLog",None,U,I,P,P)(obj,4096,None,log)
        raise RuntimeError(log.value.decode("utf-8","replace"))
valid(sh,"Shader")
program=gl("CreateProgram",U)()
gl("AttachShader",None,U,U)(program,sh)
gl("LinkProgram",None,U)(program)
valid(program,"Program")
gl("UseProgram",None,U)(program)
gl("MatrixMode",None,U)(0x1701)
gl("LoadIdentity",None)()
gl("Ortho",None,D,D,D,D,D,D)(0,1,0,1,-1,1)
gl("ShadeModel",None,U)(0x1D01)
points=[(0,0,1),(1,0,0),(1,1,1),(0,1,0)]
tris={"white":[0,1,2,0,2,3],"black":[0,1,3,1,2,3]}
def capture(n,name):
    gl("Viewport",None,I,I,I,I)(0,0,n,n)
    gl("ClearColor",None,F,F,F,F)(0,0,1,0)
    gl("Clear",None,U)(0x4000)
    begin,end=gl("Begin",None,U),gl("End",None)
    vertex,color=gl("Vertex2d",None,D,D),gl("Color3f",None,F,F,F)
    begin(4)
    for i in tris[name]:
        x,y,v=points[i]
        color(v,0,0);vertex(x,y)
    end()
    pixels=(F*(n*n*4))()
    gl("ReadPixels",None,I,I,I,I,U,U,P)(0,0,n,n,0x1908,0x1406,pixels)
    assert set(pixels[2::4])=={0} and set(pixels[3::4])=={1}
    assert set(pixels[1::4])=={0,1}
    assert gl("GetError",U)()==0
    return pixels[0::4],pixels[1::4],hashlib.sha256(bytes(pixels)).hexdigest()
white,mw,hw=capture(100,"white")
black,mb,hb=capture(100,"black")
center=[capture(101,i)[0][50*101+50] for i in ("white","black")]
changes=[int(a!=b) for a,b in zip(mw,mb)]
def exact(n,x,y):
    return (2*n-abs(2*x-2*y),abs(2*x+2*y+2-2*n))
errors=[0,0]
for y in range(100):
    for x in range(100):
        for i,ref in enumerate(exact(100,x,y)):
            index=y*100+x
            errors[i]=max(errors[i],abs((white,black)[i][index]-ref/200))
            assert (mw,mb)[i][index]==(ref*1000>=503*200)
assert max(errors)<1e-5 and all(abs(a-b)<1e-5 for a,b in zip(center,[1,0]))
assert [sum(mw),sum(mb),sum(changes)]==[7450,2450,5000]
res={"scope":"synthetic square, software OpenGL float readback, no mesh simplifier/game assets",
     "backend":backend,"size":[100,100],"center_size":[101,101],"center_raw_red":center,
     "classified_green_sum":[int(sum(mw)),int(sum(mb))],"class_mismatch":sum(changes),
     "raw_red_mae":sum(abs(a-b) for a,b in zip(white,black))/10000,
     "raw_red_max_abs_vs_exact":errors,"rgba32f_sha256":[hw,hb]}
print(json.dumps(res))
if "--png" in sys.argv:
    import base64,io
    from PIL import Image,ImageDraw
    img=Image.new("RGB",(500,335),"#172333"); draw=ImageDraw.Draw(img)
    for i,(title,raw,mask) in enumerate([("White diagonal",white,mw),("Black diagonal",black,mb),
                                         ("Mismatch",None,changes)]):
        left=12+164*i
        draw.text((left,12),title,fill="white")
        if raw is not None:
            patch=Image.new("L",(100,100));patch.putdata([round(255*max(0,min(1,a))) for a in raw])
            img.paste(patch.transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((145,145),Image.Resampling.NEAREST),(left,32))
        patch=Image.new("RGB",(100,100))
        patch.putdata([((251,153,72) if i==2 else (110,198,247)) if a else (22,91,76) for a in mask])
        img.paste(patch.transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((145,145),Image.Resampling.NEAREST),(left,186))
    f=io.BytesIO();img.save(f,format="PNG")
    data=f.getvalue()
    print("PNG_SHA256:"+hashlib.sha256(data).hexdigest())
    print("PNG:"+base64.b64encode(data).decode("ascii"))
check(current(display,None,None,None))
check(egl("DestroyContext",U,P,P)(display,ctx))
check(egl("DestroySurface",U,P,P)(display,surface))
check(egl("Terminate",U,P)(display))
