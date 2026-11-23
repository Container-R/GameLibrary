"""Draw and read two independent GLSL experiments on surfaceless OpenGL."""
import ctypes as C
import os
from pathlib import Path
from PIL import Image, ImageDraw

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
context = e("CreateContext",p,p,p,p,p)(display,cfg,None,(i*3)(0x3098,3,0x3038))
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

vertex=shader(0x8B31,'''#version 330 core
void main(){
    const vec2 vertices[3]=vec2[3](vec2(-1,-1),vec2(3,-1),vec2(-1,3));
    gl_Position=vec4(vertices[gl_VertexID],0,1);
}
''')

def draw(tex, body):
    frag=shader(0x8B30, '#version 330 core\nuniform sampler2D src;\nout vec4 color;\nvoid main(){\n'+body+'\n}')
    program=g("CreateProgram",u)()
    for s in (vertex,frag): g("AttachShader",None,u,u)(program,s)
    g("LinkProgram",None,u)(program)
    ok=i()
    g("GetProgramiv",None,u,u,p)(program,0x8B82,C.byref(ok))
    if not ok.value:
        buf=C.create_string_buffer(8192)
        g("GetProgramInfoLog",None,u,i,p,p)(program,len(buf),None,buf)
        raise RuntimeError(buf.value.decode())
    g("UseProgram",None,u)(program)
    g("BindTexture",None,u,u)(0x0DE1,tex)
    g("DrawArrays",None,u,i,i)(4,0,3)
    buf=(C.c_ubyte*(W*H*4))()
    g("ReadPixels",None,i,i,i,i,u,u,p)(0,0,W,H,0x1908,0x1401,buf)
    assert g("GetError",u)()==0
    return Image.frombytes("RGBA",(W,H),bytes(buf)).convert("RGB")

def texture(levels, minfilter, magfilter, repeat=False):
    tex=u()
    g("GenTextures",None,i,p)(1,C.byref(tex))
    g("BindTexture",None,u,u)(0x0DE1,tex)
    for param,val in [(0x2801,minfilter),(0x2800,magfilter),(0x2802,0x2901 if repeat else 0x812F),
                      (0x2803,0x812F),(0x813D,len(levels)-1)]:
        g("TexParameteri",None,u,u,i)(0x0DE1,param,val)
    for lod,(w,h,data) in enumerate(levels):
        payload=C.create_string_buffer(bytes(data))
        g("TexImage2D",None,u,i,i,i,i,i,u,u,p)(0x0DE1,lod,0x8058,w,h,0,0x1908,0x1401,payload)
    return tex

# Constant authored values label every level independently: no filter contamination.
def coded(width):
    return [(max(1,width>>l),max(1,32>>l),[32+36*l,52,255-36*l,255]*(max(1,width>>l)*max(1,32>>l))) for l in range(6)]
atlas=texture(coded(64),0x2700,0x2600) # NEAREST_MIPMAP_NEAREST, NEAREST
repeat=texture(coded(32),0x2700,0x2600,True)
common='vec2 q=vec2((gl_FragCoord.x+15.0)/32.0, .5); vec2 scale=vec2(.5,1.);'
mapped='vec2 uv=vec2(.25,0.) + fract(q)*scale; uv.y=.5;'
mips=[
    ("Atlas implicit after fract",draw(atlas,common+mapped+'color=texture(src,uv);')),
    ("Atlas explicit continuous gradient",draw(atlas,common+mapped+'color=textureGrad(src,uv,dFdx(q)*scale,dFdy(q)*scale);')),
    ("Standalone GL_REPEAT",draw(repeat,common+'color=texture(src,q);')),
]
for name,im in mips:
    labels=[round((im.getpixel((x,H//2))[0]-32)/36) for x in range(W)]
    print(f"{name}: LOD by x={labels}")
    assert labels == ([0]*16+[5]*2+[0]*14 if name.startswith("Atlas implicit") else [0]*32)

# Explicit LOD 0 and bilinear filtering isolate boundary taps. Tile RGBA8 red bytes 64/192.
red0,red1,blue=(64,0,0,255),(192,0,0,255),(0,0,255,255)
def row(items):
    return [(len(items),1,[c for texel in items for c in texel])]
tiles=[
    ("Atlas foreign neighbor", [blue,blue,red0,red1,blue,blue,blue,blue], (32,0,128)),
    ("Atlas duplicate own edge", [blue,red0,red0,red1,red1,blue,blue,blue], (64,0,0)),
    ("Atlas copy opposite edge", [blue,red1,red0,red1,red0,blue,blue,blue], (128,0,0)),
    ("Standalone GL_REPEAT", [red0,red1], (128,0,0)),
]
gutter=[]
for j,(name,texels,expected) in enumerate(tiles):
    standalone=j==3
    tex=texture(row(texels),0x2601,0x2601,standalone)
    uv='q' if standalone else '.25 + .25 * fract(q)'
    im=draw(tex,f'float q=floor(gl_FragCoord.x)/32.; color=textureLod(src,vec2({uv},.5),0.);')
    read=lambda x: im.getpixel((x,H//2))
    print(f"{name}: x=0 left edge {read(0)}, x=8 first center {read(8)}, x=24 last center {read(24)}, x=31 right approach {read(31)}")
    assert all(abs(a-b)<=1 for a,b in zip(read(0),expected))
    assert read(8)==red0[:3] and read(24)==red1[:3]
    gutter.append((name,im))
assert gutter[2][1].tobytes()==gutter[3][1].tobytes()

# Compose readbacks without resampling except nearest enlargement; labels are separate.
frames=[("A. Mip labels; nearest level and texel",mips),
        ("B. Fixed mip 0; bilinear seam color",gutter)]
sheet=Image.new("RGB",(720,310),(239,244,247))
d=ImageDraw.Draw(sheet)
y=12
for title,rows in frames:
    d.text((12,y),title,fill=(16,36,48)); y+=22
    for name,img in rows:
        d.text((14,y+5),name,fill=(30,45,59))
        sheet.paste(img.resize((416,23),Image.Resampling.NEAREST),(284,y))
        y+=30
    y+=11
sheet.save(Path(__file__).with_name("comparison.png"))
