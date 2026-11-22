"""Mesa EGL surfaceless shader fixture. Real quad derivatives, synthetic surface."""
import ctypes as C
import json, math, os
from pathlib import Path

os.environ.setdefault("EGL_PLATFORM", "surfaceless")
os.environ.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")
os.environ.setdefault("MESA_SHADER_CACHE_DISABLE", "1")
I,U,P,F,S=C.c_int,C.c_uint,C.c_void_p,C.c_float,C.c_char_p
egl=C.CDLL("libEGL.so.1")
def bind(lib, name, ret, *args):
    f=getattr(lib,name); f.restype=ret; f.argtypes=args; return f
eg=lambda name,ret,*a: bind(egl,"egl"+name,ret,*a)
d=eg("GetDisplay",P,P)(None)
assert eg("Initialize",U,P,P,P)(d,None,None), "EGL initialize failed"
assert eg("BindAPI",U,U)(0x30A2), "OpenGL API not supported"
attrs=(I*5)(0x3040,8,0x3033,1,0x3038)
cfg=P(); n=I()
assert eg("ChooseConfig",U,P,P,P,I,P)(d,attrs,C.byref(cfg),1,C.byref(n)) and n.value
ctx=eg("CreateContext",P,P,P,P,P)(d,cfg,None,(I*5)(0x3098,3,0x30FB,3,0x3038))
assert ctx and eg("MakeCurrent",U,P,P,P,P)(d,None,None,ctx)
get=eg("GetProcAddress",P,S)
def gl(name,ret,*args):
    addr=get(("gl"+name).encode())
    assert addr, name
    return C.CFUNCTYPE(ret,*args)(addr)

def shader(kind,txt):
    sh=gl("CreateShader",U,U)(kind)
    gl("ShaderSource",None,U,I,P,P)(sh,1,C.byref(S(txt.encode())),None)
    gl("CompileShader",None,U)(sh)
    ok=I()
    gl("GetShaderiv",None,U,U,P)(sh,0x8B81,C.byref(ok))
    if not ok.value:
        msg=C.create_string_buffer(4096)
        gl("GetShaderInfoLog",None,U,I,P,P)(sh,4096,None,msg)
        raise RuntimeError(msg.value.decode())
    return sh

vs=shader(0x8B31,"""#version 330
void main(){
  vec2 p=vec2(gl_VertexID==1?3.:-1.,gl_VertexID==2?3.:-1.);
  gl_Position=vec4(p,0,1);
}""")
fs=shader(0x8B30,Path("contrast.frag").read_text())
program=gl("CreateProgram",U)()
for sh in [vs,fs]: gl("AttachShader",None,U,U)(program,sh)
gl("LinkProgram",None,U)(program)
ok=I()
gl("GetProgramiv",None,U,U,P)(program,0x8B82,C.byref(ok)); assert ok.value
gl("UseProgram",None,U)(program)
vao=U()
gl("GenVertexArrays",None,I,P)(1,C.byref(vao))
gl("BindVertexArray",None,U)(vao)
w=h=64
tex=U(); fbo=U()
gl("GenTextures",None,I,P)(1,C.byref(tex))
gl("BindTexture",None,U,U)(0x0DE1,tex)
gl("TexImage2D",None,U,I,I,I,I,I,U,U,P)(0x0DE1,0,0x8814,w,h,0,0x1908,0x1406,None)
gl("GenFramebuffers",None,I,P)(1,C.byref(fbo))
gl("BindFramebuffer",None,U,U)(0x8D40,fbo)
gl("FramebufferTexture2D",None,U,U,U,U,I)(0x8D40,0x8CE0,0x0DE1,tex,0)
assert gl("CheckFramebufferStatus",U,U)(0x8D40)==0x8CD5
gl("Viewport",None,I,I,I,I)(0,0,w,h)
loc=gl("GetUniformLocation",I,U,S)
phase=loc(program,b"phase"); flat=loc(program,b"flat_control")
pixels=(F*(w*h*4))()
def draw(x,is_flat):
    gl("Uniform1f",None,I,F)(phase,x)
    gl("Uniform1i",None,I,I)(flat,is_flat)
    gl("DrawArrays",None,U,I,I)(4,0,3)
    gl("ReadPixels",None,I,I,I,I,U,U,P)(0,0,w,h,0x1908,0x1406,pixels)
    return list(pixels)

def pixel(values,x,y): return values[4*(y*w+x):4*(y*w+x)+4]
def summarize(rows):
    return {"ranges":[[min(r[c] for r in rows),max(r[c] for r in rows)] for c in range(4)],
            "rmse_to_reference":[math.sqrt(sum((r[c]-r[2])**2 for r in rows)/len(rows)) for c in (0,1)]}

def panels(frames, file):
    from PIL import Image, ImageDraw
    result=Image.new('RGB',(5*w*2,3*(h*2+14)+16),(24,24,24))
    label=ImageDraw.Draw(result)
    for i in range(5):
        label.text((i*w*2+3,0),f"phase {(-.02+i*.01):+.2f}",fill=(245,245,245))
    for mode,title in enumerate(["Point sample","Derivative filter","32x32 pixel reference"]):
        sy=16+mode*(h*2+14)
        label.text((3,sy),title,fill=(245,245,245))
        for i,frame in enumerate(frames):
            # Same display transform in all columns and rows.
            image=Image.new('L',(w,h))
            image.putdata([round(255*math.sqrt(max(0,min(1,pixel(frame,x,y)[mode]/1000))))
                           for y in reversed(range(h)) for x in range(w)])
            result.paste(image.crop((24,24,40,40)).resize((w*2,h*2),Image.Resampling.NEAREST),(i*w*2,sy+14))
    result.save(file)

phases=[-.02+i*.001 for i in range(41)]
sphere=[]; plane=[]; rim=[]; exports=[]
for i,x in enumerate(phases):
    data=draw(x,0)
    sphere.append(pixel(data,32,32))
    rim.append(pixel(data,57,32))
    plane.append(pixel(draw(x,1),32,32))
    if i%10==0: exports.append(data)
assert all(r[0]==r[1] for r in plane)
assert any(r[0]!=r[1] for r in sphere)
assert min(r[3] for r in rim)==0 and max(r[3] for r in rim)==1
panels(exports,"phase-panels.png")
gs=gl("GetString",S,U)
print(json.dumps({"renderer":gs(0x1F01).decode(),"version":gs(0x1F02).decode(),
  "grid":[w,h],"pixel_pitch":.04,"alpha":.015,"phases":phases,
  "channels":["D_center","D_trace_approx","D_box_reference_32x32","coverage_center"],
  "sphere_center_32_32":summarize(sphere),"plane_center_32_32":summarize(plane),
  "sphere_boundary_57_32":summarize(rim),
  "sphere_center_samples":sphere,"sphere_boundary_samples":rim},indent=2))
