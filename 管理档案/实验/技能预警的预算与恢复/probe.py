"""MESA software GL fixture. Each view is pixel-read from an EGL pbuffer."""
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import sys
from PIL import Image, ImageDraw

os.environ["LIBGL_ALWAYS_SOFTWARE"]="true"
os.environ["MESA_SHADER_CACHE_DISABLE"]="true"
egl=C.CDLL("libEGL.so.1")
gl=C.CDLL("libGL.so.1")
p,i,u,f=C.c_void_p,C.c_int,C.c_uint,C.c_float

def bind(lib,name,ret,*args):
    fun=getattr(lib,name); fun.restype=ret; fun.argtypes=args
    return fun

get_display=bind(egl,"eglGetPlatformDisplay",p,u,p,p)
initialize=bind(egl,"eglInitialize",u,p,p,p)
choose=bind(egl,"eglChooseConfig",u,p,p,p,i,p)
api=bind(egl,"eglBindAPI",u,u)
surface=bind(egl,"eglCreatePbufferSurface",p,p,p,p)
context=bind(egl,"eglCreateContext",p,p,p,p,p)
current=bind(egl,"eglMakeCurrent",u,p,p,p,p)
version=bind(gl,"glGetString",C.c_char_p,u)
clearcolor=bind(gl,"glClearColor",None,f,f,f,f)
clear=bind(gl,"glClear",None,u)
viewport=bind(gl,"glViewport",None,i,i,i,i)
begin=bind(gl,"glBegin",None,u)
end=bind(gl,"glEnd",None)
color=bind(gl,"glColor3ub",None,*([C.c_ubyte]*3))
vertex=bind(gl,"glVertex2f",None,f,f)
disable=bind(gl,"glDisable",None,u)
get_int=bind(gl,"glGetIntegerv",None,u,p)
read=bind(gl,"glReadPixels",None,i,i,i,i,u,u,p)
error=bind(gl,"glGetError",u)

d=get_display(0x31DD,None,None) # EGL_PLATFORM_SURFACELESS_MESA
assert d and initialize(d,None,None)
assert api(0x30A2) # EGL_OPENGL_API
attrs=(i*15)(0x3033,1,0x3040,8,0x3024,8,0x3023,8,0x3022,8,0x3021,8,0x3032,0,0x3038)
cfg=p(); n=i()
assert choose(d,attrs,C.byref(cfg),1,C.byref(n)) and n.value==1
ctx=context(d,cfg,None,(i*3)(0x3098,2,0x3038))
assert ctx
W,H=144,80
out=Path(sys.argv[1]); out.mkdir(parents=True,exist_ok=True)
textures={}
def draw(w,h,rects):
    if (w,h) not in textures:
        textures[w,h]=surface(d,cfg,(i*5)(0x3057,w,0x3056,h,0x3038))
    s=textures[w,h]
    assert s and current(d,s,s,ctx)
    viewport(0,0,w,h)
    for flag in (0x0BD0,0x809D,0x0BE2,0x0B71): disable(flag) # dither/MSAA/blend/depth
    clearcolor(20/255,27/255,38/255,1); clear(0x4000)
    for (x0,y0,x1,y1),rgb in rects:
        color(*rgb); begin(7)
        for x,y in ((x0,y0),(x1,y0),(x1,y1),(x0,y1)):
            vertex(x/W*2-1,1-y/H*2)
        end()
    a=(C.c_ubyte*(w*h*4))()
    read(0,0,w,h,0x1908,0x1401,a)
    assert not error()
    return Image.frombytes("RGBA",(w,h),bytes(a)).transpose(Image.Transpose.FLIP_TOP_BOTTOM).convert("RGB")

# A and B share a true y footprint. Partition glyph marks into upper/lower
# bands on this same rectangle so overlapping schedules do not overwrite.
DATA={"A":(-6,4,-6,100,110,114), "B":(3,7,3,103,116,120), "C":(2,5,2,99,112,121)}
PAL={"A":{"warning":(255,186,73),"active":(255,115,62)},
     "B":{"warning":(104,212,243),"active":(95,160,255)},
     "C":{"warning":(232,110,219),"active":(245,71,167)}}
def phase(t, a, b, e):
    return "warning" if a<=t<b else "active" if b<=t<e else None

def frame(t,cam,policy="correct"):
    base=[((x,0,x+2,H),(36,46,61)) for x in range(0,W,18)]
    base += [((0,y,W,y+2),(36,46,61)) for y in range(0,H,16)]
    slots={}
    for name,(low,high,origin,warn,start,end_t) in DATA.items():
        ph=phase(t,warn,start,end_t)
        if not ph or (name=="C" and policy!="leak") or (policy=="origin" and not cam<=origin<cam+8): continue
        lo,hi=max(low,cam),min(high,cam+8)
        if lo>=hi: continue
        x0,x1=(lo-cam)*18,(hi-cam)*18
        slots[name]={"x":[lo,hi],"phase":ph,"ticks_to_impact":start-t if ph=="warning" else None}
        y0,y1={"A":(18,38),"B":(42,62),"C":(32,48)}[name]
        rgb=PAL[name][ph]
        if ph=="active":
            base.append(((x0,y0,x1,y1),rgb))
        else:
            # Dashes, not merely a hue change. An edge-aligned dash starts 1px into each cell.
            for x in range(x0+1,x1-2,6):
                base += [((x,y0,min(x+4,x1),y0+4),rgb),((x,y1-4,min(x+4,x1),y1),rgb)]
    return base,slots

scales=[1,.5]
timeline=[(105,8),(106,0),(110,0),(114,0),(116,0),(120,0)]
samples={"tick105_outside":(105,8,"correct"),"tick106_return":(106,0,"correct"),
         "tick110_A_active":(110,0,"correct"),"tick114_A_expired":(114,0,"correct"),
         "tick116_B_active":(116,0,"correct"),"tick120_both_expired":(120,0,"correct"),
         "tick106_wrong_origin_cull":(106,0,"origin"),"tick106_wrong_disclose_C":(106,0,"leak")}
report={"frames":{},"outline":{}}
shots={}
def render_scale(rects,scale):
    return draw(round(W*scale),round(H*scale),rects)
def count(im,rgb):
    return sum(px==rgb for px in im.get_flattened_data())
def snap(im): return im.resize((W,H),Image.Resampling.NEAREST)
for name,(t,cam,p) in samples.items():
    rects,slots=frame(t,cam,p)
    report["frames"][name]={"view":[cam,cam+8],"hazards":slots,"internal_readback":{}}
    for sc in scales:
        raw=render_scale(rects,sc); shots[name,sc]=snap(raw)
        report["frames"][name]["internal_readback"][str(sc)]={"size":list(raw.size),
        "glyph_pixels":{k:sum(count(raw,v) for v in PAL[k].values()) for k in DATA}}
assert not report["frames"]["tick105_outside"]["hazards"]
assert report["frames"]["tick106_return"]["hazards"]=={"A":{"x":[0,4],"phase":"warning","ticks_to_impact":4},"B":{"x":[3,7],"phase":"warning","ticks_to_impact":10}}
for s in map(str,scales):
    def row(k): return report["frames"][k]["internal_readback"][s]["glyph_pixels"]
    assert row("tick106_return")["A"]>0 and row("tick106_return")["B"]>0 and row("tick106_return")["C"]==0
    assert row("tick106_wrong_origin_cull")["A"]==0 and row("tick106_wrong_disclose_C")["C"]>0
    for key,expected in [("tick110_A_active",{"A":"active","B":"warning"}),("tick116_B_active",{"B":"active"})]:
        assert {k:v["phase"] for k,v in report["frames"][key]["hazards"].items()}==expected
        for k,ph in expected.items():
            assert count(shots[key,float(s)],PAL[k][ph])>0
    assert row("tick114_A_expired")["A"]==0 and row("tick114_A_expired")["B"]>0
    assert not any(row("tick120_both_expired").values())

rgb=(246,242,222)
for label,center,width in [("thin_centered",72,1.2),("thin_shifted",72.5,1.2),("wider_centered",72,2.4)]:
    rects=[((center-width/2,14,center+width/2,66),rgb)]
    report["outline"][label]={}
    for sc in scales:
        im=render_scale(rects,sc); shots[label,sc]=snap(im)
        cols=[x for x in range(im.width) if im.getpixel((x,im.height//2))==rgb]
        report["outline"][label][str(sc)]={"internal_columns":cols,"pixels":count(im,rgb)}
assert [report["outline"]["thin_centered"][str(s)]["pixels"] for s in scales]==[104,0]
assert report["outline"]["thin_shifted"]["0.5"]["pixels"]==26
assert report["outline"]["wider_centered"]["0.5"]["pixels"]==52
msaa=i();get_int(0x80A9,C.byref(msaa))
report["backend"]={"vendor":version(0x1F00).decode(),"renderer":version(0x1F01).decode(),
                   "version":version(0x1F02).decode(),"samples":msaa.value}
assert "llvmpipe" in report["backend"]["renderer"].lower() and msaa.value==0

def contact(name,rows,notes):
    panel=Image.new("RGB",(len(rows[0])*156+14,len(rows)*115+55),(12,17,25))
    pen=ImageDraw.Draw(panel)
    pen.text((12,9),notes,fill="white")
    for iy,row in enumerate(rows):
        for ix,(key,s,title) in enumerate(row):
            x,y=12+156*ix,27+iy*115
            pen.text((x,y),title,fill=(219,228,241))
            panel.paste(shots[key,s],(x,y+18))
    fp=out/name;panel.save(fp)
    report.setdefault("figures",{})[name]=hashlib.sha256(fp.read_bytes()).hexdigest()

main_keys=list(samples)[1:5]
titles=["106: return   A+4 / B+10","110: A active / B+6","114: A gone / B+2","116: B active"]
contact("timeline.png",[[(key,sc,f"{sc:g}x {title}") for key,title in zip(main_keys,titles)] for sc in scales],
        "A orange (upper), B blue (lower). Dashed: warning. Solid: active. Bands separate timers, not ground depth.")
ct=["tick105_outside","tick106_wrong_origin_cull","tick106_wrong_disclose_C","tick120_both_expired"]
contact("controls.png",[[(key,sc,f"{sc:g}x {title}") for key,title in zip(ct,["105 outside","106 wrong origin","106 wrong reveal","120 expired"])] for sc in scales],
        "Negative controls. Purple C is deliberately wrong; a correct return must never reveal it.")
ot=list(report["outline"])
contact("outline.png",[[(key,sc,f"{sc:g}x {title}") for key,title in zip(ot,["1.2 px centered","1.2 px shifted .5","2.4 px centered"])] for sc in scales],
        "Same display size; half-scale raster is presented with nearest replication.")
print(json.dumps(report,indent=2))
