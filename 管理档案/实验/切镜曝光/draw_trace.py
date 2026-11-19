"""Draw chart from archived numeric trace, no rendering claim."""
from pathlib import Path
from math import log2
import json
from PIL import Image, ImageDraw, ImageFont

root=Path(__file__).resolve().parent
o=json.loads((root/"observed.json").read_text())
img=Image.new("RGB",(1040,610),"#101725")
d=ImageDraw.Draw(img)
def font(size,bold=False):
    return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",size)
def label(x,y,s,sz=18,c="#dce7f5",bold=False):
    d.text((x,y),s,font=font(sz,bold),fill=c)

label(63,35,"Exposure after a hard cut",31,bold=True)
label(63,82,"Fixed scene patch, before tone mapping; no display-code values",18)
left,top,right,bottom = 107,162,959,454
px=lambda x: int(left+30+x*(right-left-60)/5)
py=lambda s: int(bottom-s*(bottom-top)/7)
label(28,120,"Stops relative to target patch",16)
for y in range(8):
    d.line((left,py(y),right,py(y)),fill="#323e51",width=1)
    label(69,py(y)-11,f"{y:+}",17)
for i in range(6):
    label(px(i)-6,bottom+19,str(i),18)
label(431,501,"Frame after the cut",18)
# Current-view samples arrive only from frame 2 onwards.
x=px(2)
d.line((x,top-12,x,bottom),fill="#97a5ba",width=1)
label(x+10,top-31,"First current-shot meter result",16)

styles=[
    ("retained_old_history_guard_meter","#f7af51","circle","Keep old gain; reject old meter"),
    ("seeded_new_shot_guard_meter","#70dfb2","square","Seed new gain; reject old meter"),
    ("seeded_new_shot_unfiltered_old_meter","#8bb6ff","triangle","Seed new gain; accept old meter"),
]
for n,(key,c,kind,name) in enumerate(styles):
    points=[(px(v["frame"]),py(log2(v["exposed_linear"]/.18))) for v in o[key]]
    d.line(points,fill=c,width=3)
    for x,y in points:
        if kind=="circle":d.ellipse((x-4,y-4,x+4,y+4),fill=c)
        if kind=="square":d.rectangle((x-4,y-4,x+4,y+4),fill=c)
        if kind=="triangle":d.polygon([(x,y-6),(x-6,y+5),(x+6,y+5)],fill=c)
    label(63+n*321,550,name,16,c,bold=True)
img.save(root/"trace.png")
