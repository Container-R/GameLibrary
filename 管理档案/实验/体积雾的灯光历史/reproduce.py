"""Fixed orthographic camera, software single-scattering surrogate (not engine)."""
from math import exp, sqrt
from random import Random
from pathlib import Path
from PIL import Image, ImageDraw

W,Z,Y=64,32,32
SIGMA=.045
WEIGHTS=[exp(-SIGMA*z)*(1-exp(-SIGMA)) for z in range(Z)]
def sources(shift):
    # A localized beam footprint in horizontal x / depth z cells.
    return [1.0 if 4<=z<25 and abs(x-(12+.30*z+shift))<=3 else 0.0
            for z in range(Z) for x in range(W)]
def rays(cells):
    return [sum(WEIGHTS[z]*cells[z*W+x] for z in range(Z)) for x in range(W)]
def update(history,current,alpha,mask=None):
    return [c if mask is not None and mask[i] else alpha*h+(1-alpha)*c
            for i,(h,c) in enumerate(zip(history,current))]
old,new=sources(0),sources(27)
changed=[p!=q for p,q in zip(old,new)]
frame_sets=[]
weights=(0.,.9,.7,.9)
for alpha,mask in zip(weights,(None,None,None,changed)):
    h=old
    frames=[]
    for frame in range(1,30):
        h=update(h,new,alpha,mask if frame==1 else None)
        if frame in (1,5,15,29): frames.append(rays(h))
    frame_sets.append(frames)
x_old,x_new=17,44
ref=rays(old)[x_old]
assert ref>0 and rays(new)[x_old]==0.0 and abs(rays(new)[x_new]-ref)<1e-12
print("Clean light relocation (old beam column / old steady linear value):")
for label,frames in zip(("no history",".90 history",".70 history",".90 + changed-cell reject"), frame_sets):
    vals=[v[x_old]/ref for v in frames]
    print(label, "frames 1/5/15/29:", " ".join(f"{x:.6f}" for x in vals))
assert abs(frame_sets[1][1][x_old]/ref-.9**5)<1e-12
assert frame_sets[3][0][x_old]==0 and abs(frame_sets[3][0][x_new]/ref-1)<1e-12

# Known stationary light, same seeded noisy samples applied to each policy.
# Benchmark a single representative ray; noise is injected as per-frame jitter surrogate.
random=Random(1204)
noise=[random.uniform(-.3,.3) for _ in range(4096)]
print("Stationary beam, temporal RMS relative to clean value (warmup 100, 3996 samples):")
for label,alpha in zip(("no history",".90 history",".70 history",".90 + changed-cell reject"),weights):
    h=1.
    delta=[]
    for t,e in enumerate(noise):
        h=alpha*h+(1-alpha)*(1+e)
        if t>=100: delta.append(h-1)
    print(label, f"{sqrt(sum(x*x for x in delta)/len(delta)):.6f}")
print("Rejection uses oracle: exact old/new lit-support XOR, no disocclusion test.")

# Visual rows show same fixed scale and display curve, no per-panel normalization.
out=Image.new("RGB",(1000,590),"#111823")
d=ImageDraw.Draw(out)
d.text((24,18),"Fixed camera: a beam moves from left to right",fill="#edf5ff",font_scale=2)
d.text((24,49),"Color shows integrated light; green guides mark the old and new beam columns.",fill="#bdcddd",font_scale=1.4)
def band(data):
    img=Image.new("RGB",(W,Y))
    den=max(rays(old))
    for yy in range(Y):
        v=exp(-.5*((yy-(Y-1)/2)/8)**2)
        for x,light in enumerate(data):
            c=sqrt(max(0, min(1,light*v/den)))
            img.putpixel((x,yy),(int(13+231*c),int(23+153*c),int(38+49*c)))
    return img.resize((176,95),Image.Resampling.NEAREST)
xs=(220,410,600,790)
for x,s in zip(xs,("Frame 1","Frame 5","Frame 15","Frame 29")):
    d.text((x+58,85),s,fill="#dfe8f4",font_scale=1.4)
for j,(label,frames) in enumerate(zip(("Current only","90% history","70% history","90% + reject*"),frame_sets)):
    y=116+j*111
    d.text((26,y+37),label,fill="#edf5ff",font_scale=1.6)
    for x,data in zip(xs,frames):
        out.paste(band(data),(x,y))
        for xv in (x_old,x_new):
            xx=x+int((xv+.5)*176/W)
            d.line((xx,y+84,xx,y+95),fill="#87e5ba",width=2)
d.text((24,565),"*Reject only cells whose illuminated membership changed; known from the fixture, not inferred.",fill="#bdcddd",font_scale=1.4)
out.save(Path(__file__).with_name("comparison.png"))
