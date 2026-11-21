"""Draw the measured four-case cross section. Only Python standard library."""
from pathlib import Path
from dataclasses import dataclass
from html import escape
import math

@dataclass(frozen=True)
class Surface:
    key: str
    a: tuple
    b: tuple
    dot: float
    layer: int
    color: str

SURFACES = [
    Surface("floor", (-.62,0), (.19,0), 1, 1, "#ffe576"),
    Surface("prop", (-.38,.12), (-.06,.12), 1, 2, "#ffe576"),
    Surface("rear", (-.38,-.40), (.36,-.40), 1, 2, "#ffe576"),
    Surface("bevel", (.19,0), (.34,.26), .15/math.hypot(.15,.26), 1, "#ffe576"),
    Surface("wall", (.34,.26), (.34,.53), 0, 1, "#ffe576"),
]
CASES = [("A  Wide box",.50,0,3),("B  Thin box",.18,0,3),
         ("C  Thin + normal",.18,.55,3),("D  + receiver bit",.18,.55,1)]

def clip(s, depth, dot, mask):
    if s.dot < dot or not s.layer & mask:
        return
    lo,hi=0.,1.
    for a,b,half in zip(s.a,s.b,(.5,depth)):
        d=b-a
        if d:
            u,v=sorted(((-half-a)/d,(half-a)/d))
            lo,hi=max(lo,u),min(hi,v)
        elif abs(a)>half:
            return
    if lo<hi:
        return tuple(tuple(a+t*(b-a) for a,b in zip(s.a,s.b)) for t in (lo,hi))

assert [[s.key for s in SURFACES if clip(s,h,n,m)] for _,h,n,m in CASES] == [
    ["floor","prop","rear","bevel","wall"], ["floor","prop","bevel"],
    ["floor","prop"], ["floor"],
]
bevel=SURFACES[3]
hit=clip(bevel,.18,0,3)
assert math.isclose(hit[1][1],.18) and math.isclose(hit[1][0], .19+.15*.18/.26)
assert math.isclose(1/bevel.dot,2.001110802640484,abs_tol=1e-10)

svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1010" height="724" viewBox="0 0 1010 724">',
     '<title>Decal receiver debugging: four cross sections</title>',
     '<desc>The wide box marks all five surfaces. A thinner box clips the rear shell and wall and still touches the lower bevel. A normal filter removes that bevel. A receiver bit excludes the parallel prop.</desc>',
     '<rect width="1010" height="724" fill="#0e1626"/>']
def label(x,y,s,size=17,fill="#edf6ff"):
    svg.append(f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-family="DejaVu Sans,sans-serif">{escape(s)}</text>')
def line(x1,y1,x2,y2,c,w):
    svg.append(f'<path d="M{x1:.2f} {y1:.2f} L{x2:.2f} {y2:.2f}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"/>')
label(24,42,"One projector, three different filters",27)
label(24,68,"Cross section in projector-local coordinates. Yellow = receives decal.",17,"#b9cbe4")
for i,(name,depth,dot,mask) in enumerate(CASES):
    ox=23+(i%2)*492
    oy=85+(i//2)*307
    svg.append(f'<rect x="{ox}" y="{oy}" rx="12" width="472" height="290" fill="#18253a"/>')
    label(ox+18,oy+31,name,21)
    label(ox+18,oy+55,f"Half depth {depth:.2f}   |   min dot {dot:.2f}   |   mask {mask:02b}",15,"#b9cbe4")
    def local(p):
        x,y=p
        return ox+238+178*x,oy+170-168*y
    left,top=local((-.5,depth))
    svg.append(f'<rect x="{left}" y="{top}" width="178" height="{336*depth}" fill="#274766" stroke="#6aadd5" stroke-dasharray="7 5" stroke-width="1.6"/>')
    for s in SURFACES:
        line(*local(s.a),*local(s.b),"#a9bcd0" if s.layer==1 else "#9a8db8",6)
        if (t:=clip(s,depth,dot,mask)):
            line(*local(t[0]),*local(t[1]),s.color,4)
    label(ox+21,oy+147,"Prop",15,"#d4bdf3")
    label(ox+39,oy+191,"Floor",15)
    label(ox+20,oy+243,"Rear shell",15,"#d4bdf3")
    label(ox+329,oy+143,"Wall",15)
    label(ox+324,oy+174,"Bevel",15)
    line(ox+383,oy+185,ox+383,oy+219,"#7fbdf4",2)
    line(ox+377,oy+212,ox+383,oy+219,"#7fbdf4",2)
    line(ox+389,oy+212,ox+383,oy+219,"#7fbdf4",2)
    label(ox+397,oy+211,"-Y",15,"#9ccfff")
label(24,711,"Box = geometric bounds. The hard normal threshold here is a teaching model, not an engine fade curve.",16,"#b9cbe4")
svg.append("</svg>")
out=Path(__file__).with_name("cross-section.svg")
out.write_text("\n".join(svg)+"\n",encoding="utf-8")
for case,h,n,m in CASES:
    print(case,[(s.key,[[round(v,6) for v in p] for p in t]) for s in SURFACES if (t:=clip(s,h,n,m))])
