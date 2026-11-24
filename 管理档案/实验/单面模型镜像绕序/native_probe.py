"""Draw mirrored instances and depth-tested wall pairs on surfaceless OpenGL."""
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
attrs = (i*17)(0x3033,1,0x3040,8,0x3024,8,0x3023,8,0x3022,8,0x3021,8,0x3032,0,0x3025,24,0x3038)
assert e("ChooseConfig",u,p,p,p,i,p)(display,attrs,C.byref(cfg),1,C.byref(n)) and n.value == 1
W,H = 96,64
surface = e("CreatePbufferSurface",p,p,p,p)(display,cfg,(i*5)(0x3057,W,0x3056,H,0x3038))
context = e("CreateContext",p,p,p,p,p)(display,cfg,None,(i*7)(0x3098,3,0x30FB,3,0x30FD,1,0x3038))
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

vertex = shader(0x8B31, '''#version 330 core
uniform vec3 scale[3];
uniform float xCenter[3];
uniform int wallMode, slotBase, slotStride, reverseWallOrder;
flat out int id;
void main(){
    const vec2 corners[4]=vec2[4](vec2(-.5,-.5),vec2(.5,-.5),vec2(.5,.5),vec2(-.5,.5));
    const int order[12]=int[12](0,1,2,0,2,3,0,2,1,0,3,2);
    const vec2 tri[3]=vec2[3](vec2(-.20,-.25),vec2(.20,-.25),vec2(-.20,.25));
    int slot=slotBase+gl_InstanceID*slotStride;
    if(wallMode==0){
        id=0;
        vec2 xy=tri[gl_VertexID]*scale[slot].xy+vec2(xCenter[slot],0);
        gl_Position=vec4(xy,0,1);
    }else{
        int vId=(gl_VertexID+6*reverseWallOrder)%12;
        id=vId/6;
        vec3 v=vec3(corners[order[vId]],id==0 ? .5 : -.5)*scale[slot];
        gl_Position=vec4(v.xy,-v.z,1); // +Z camera; smaller window depth is nearer
    }
}
''')
frag = shader(0x8B30, '''#version 330 core
flat in int id;
out vec4 color;
void main(){
    if(id==0){ color=vec4(1, gl_FrontFacing ? .375 : .625, 0, 1); }
    else { color=vec4(0, gl_FrontFacing ? .625 : .375, 1, 1); }
}
''')
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
def loc(name):
    result=g("GetUniformLocation",i,u,C.c_char_p)(program,name.encode())
    assert result >= 0, name
    return result
def uint(name,value):
    g("Uniform1i",None,i,i)(loc(name),value)
def vecarray(name,components,values):
    data=(C.c_float*len(values))(*values)
    g(f"Uniform{components}fv",None,i,i,p)(loc(name),len(values)//components,data)
def draws(vertices,first_slot,count,stride=1):
    uint("slotBase",first_slot)
    uint("slotStride",stride)
    g("DrawArraysInstanced",None,u,i,i,i)(4,0,vertices,count)

CULL, DEPTH, CCW, CW = 0x0B44, 0x0B71, 0x0901, 0x0900
g("CullFace",None,u)(0x0405) # GL_BACK
g("DepthFunc",None,u)(0x0201) # GL_LESS
g("ClearColor",None,*([C.c_float]*4))(0,0,0,1)
depth_bits=i()
assert e("GetConfigAttrib",u,p,p,i,p)(display,cfg,0x3025,C.byref(depth_bits))
assert depth_bits.value >= 24
print(f"viewport={W}x{H}, depth_bits={depth_bits.value}")
def raster(cull,front):
    g("Enable" if cull else "Disable",None,u)(CULL)
    g("FrontFace",None,u)(front)
def clear():
    g("Clear",None,u)(0x4000 | 0x0100)
def read():
    buf=(C.c_ubyte*(W*H*4))()
    g("ReadPixels",None,i,i,i,i,u,u,p)(0,0,W,H,0x1908,0x1401,buf)
    assert g("GetError",u)()==0
    return Image.frombytes("RGBA",(W,H),bytes(buf)).convert("RGB").transpose(Image.Transpose.FLIP_TOP_BOTTOM)

panels=[]
from collections import Counter
BG=(0,0,0)
colors={(255,96,0):"A/front",(255,159,0):"A/back",(0,159,255):"B/front",(0,96,255):"B/back"}
def pixels(tile):
    # Avoid deprecated Image.getdata while retaining compatibility with older Pillow.
    payload=tile.tobytes()
    return zip(payload[::3],payload[1::3],payload[2::3])
def tally(tile):
    return Counter({colors[pixel]:count for pixel,count in Counter(pixels(tile)).items() if pixel!=BG})
uint("wallMode",0)
vecarray("scale",3,[1,1,1, -1,1,1, -1,-1,1])
vecarray("xCenter",1,[-2/3,0,2/3])
for label,cull,front,split,expected in [
    ("Cards: CCW + back cull",True,CCW,False,["A/front",None,"A/front"]),
    ("Cards: CW + back cull",True,CW,False,[None,"A/front",None]),
    ("Cards: CCW, no cull",False,CCW,False,["A/front","A/back","A/front"]),
    ("Cards: split by parity",True,CCW,True,["A/front","A/front","A/front"])]:
    clear()
    raster(cull,front)
    if split:
        draws(3,0,2,stride=2) # slots 0 and 2 share positive parity
        raster(True,CW)
        draws(3,1,1)
    else:
        draws(3,0,3)
    tile=read()
    counts=[tally(tile.crop((j*32,0,(j+1)*32,H))) for j in range(3)]
    assert [next(iter(c),None) for c in counts] == expected and all(len(c)<=1 for c in counts), counts
    print(label,counts)
    panels.append((label,tile))

uint("wallMode",1)
g("Enable",None,u)(DEPTH)
expected_mask=None
for label,scale,cull,front,expected in [
    ("Walls: original, CCW",(1,1,1),True,CCW,"A/front"),
    ("Walls: X mirror, CCW",(-1,1,1),True,CCW,"B/front"),
    ("Walls: X mirror, CW",(-1,1,1),True,CW,"A/front"),
    ("Walls: Z mirror, CCW",(1,1,-1),True,CCW,"A/front"),
    ("Walls: Z mirror, CW",(1,1,-1),True,CW,"B/front"),
    ("Walls: Z mirror, no cull",(1,1,-1),False,CCW,"B/back"),
    ("Walls: X+Z mirror, CCW",(-1,1,-1),True,CCW,"B/front"),
    ("Walls: Z mirror, CW no cull",(1,1,-1),False,CW,"B/front")]:
    clear()
    raster(cull,front)
    vecarray("scale",3,list(scale))
    # In stale uncull mode, submit the near B wall first and far A last.
    # The readback must still show B, proving the depth test matters.
    uint("reverseWallOrder",int(label=="Walls: Z mirror, no cull"))
    draws(12,0,1)
    tile=read()
    count=tally(tile)
    assert count == {expected:1536}, count
    mask=bytes(pixel!=BG for pixel in pixels(tile))
    if expected_mask is None:
        expected_mask=mask
    assert mask==expected_mask, "wall silhouette changed"
    near="A" if scale[2]>0 else "B"
    depth=C.c_float()
    g("ReadPixels",None,i,i,i,i,u,u,p)(W//2,H//2,1,1,0x1902,0x1406,C.byref(depth))
    assert g("GetError",u)()==0
    expected_depth=.25 if expected[0]==near else .75
    assert abs(depth.value-expected_depth)<1e-6, depth.value
    print(f"{label}: {dict(count)}; near={near}; center depth={depth.value:.2f}; same silhouette")
    panels.append((label,tile))

canvas=Image.new("RGB",(724,501),"#192431")
draw=ImageDraw.Draw(canvas)
draw.text((14,10),"Native OpenGL framebuffer | A = orange, B = blue | no lighting",fill="white")
for k,(label,tile) in enumerate(panels):
    x,y=14+(k%4)*178,31+(k//4)*149
    draw.text((x,y),label,fill="white")
    canvas.paste(tile.resize((144,96),Image.Resampling.NEAREST),(x,y+19))
    if k<4:
        draw.text((x,y+119),"+       X       X+Y",fill="white")
    else:
        id_face=next(iter(tally(tile)))
        draw.text((x,y+119),id_face+"; 1536 px",fill="white")
draw.text((14,480),"Cards: left ordinary, middle X mirror, right X+Y mirror. Walls: view from +Z.",fill="white")
canvas.save(Path(__file__).with_name("native-comparison.png"))
