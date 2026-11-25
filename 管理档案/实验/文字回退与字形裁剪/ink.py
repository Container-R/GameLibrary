"""Raster comparison using explicit mixed-font spans, not automatic font choice."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, features, __version__
import argparse
import hashlib

p=argparse.ArgumentParser()
p.add_argument("latin")
p.add_argument("thai")
p.add_argument("--png", default="clip-comparison.png")
o=p.parse_args()
print("Pillow",__version__,"FreeType",features.version("freetype2"),"RAQM",features.version("raqm"))
assert features.check("raqm")
for name,path in (("latin",o.latin),("thai",o.thai)):
    print(name,"font SHA-256",hashlib.sha256(Path(path).read_bytes()).hexdigest())
latin=ImageFont.truetype(o.latin,32,layout_engine=ImageFont.Layout.RAQM)
thai=ImageFont.truetype(o.thai,32,layout_engine=ImageFont.Layout.RAQM)
cut=(54,90)
def draw(mixed):
    m=Image.new("L",(184,104))
    d=ImageDraw.Draw(m)
    d.text((12,80),"Ag",font=latin,anchor="ls",fill=255)
    if mixed:
        d.text((12+round(latin.getlength("Ag ")),80),"กิ๊ กุ",font=thai,anchor="ls",fill=255)
    return m
def clip(m,lo,hi):
    c=Image.new("L",m.size)
    c.paste(m.crop((0,lo,m.width,hi)),(0,lo))
    return c
def nonzero(m):
    return sum(v!=0 for v in m.get_flattened_data())
base,full=draw(False),draw(True)
tight,wide=clip(full,*cut),clip(full,46,96)
assert nonzero(base)==nonzero(clip(base,*cut))
loss=nonzero(full)-nonzero(tight)
assert loss>0 and full.tobytes()==wide.tobytes()
print("latin bbox",base.getbbox(),"lost in [54,90)",0)
print("mixed bbox",full.getbbox(),"lost in [54,90)",loss,"lost in [46,96)",0)
# Display the same pixel buffers enlarged with nearest-neighbor.
sheet=Image.new("RGB",(1152,276),"#16202a")
d=ImageDraw.Draw(sheet)
font=ImageFont.truetype(o.latin,16,layout_engine=ImageFont.Layout.RAQM)
for col,(label,m) in enumerate((("Latin [54,90)",clip(base,*cut)),("Mixed [54,90)",tight),("Same mixed [46,96)",wide))):
    x=16+col*380
    d.text((x,12),label,font=font,fill="white")
    mask=m.resize((m.width*2,m.height*2),Image.Resampling.NEAREST)
    sheet.paste("#fdf4db",(x,40,x+mask.width,40+mask.height),mask)
    start,end=(46,96) if col==2 else cut
    for pos in (start,end):
        y=40+2*pos
        d.line((x,y,x+350,y),fill="#60afcd",width=1)
    d.text((x,252),"blue: clip bounds; shared baseline",font=font,fill="#b5c8d6")
sheet.save(o.png,optimize=True)
