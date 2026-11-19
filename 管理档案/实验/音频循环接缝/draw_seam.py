from pathlib import Path
from xml.sax.saxutils import escape
import json

data=json.loads(Path('wav-readback.json').read_text())
s=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 990 367" width="990" height="367" role="img" aria-label="Sample frames before and after two stereo loop joins">','<rect width="990" height="367" fill="#111c2a"/>']
def text(x,y,t,z=15,c="#e8f2ff"):
    s.append(f'<text x="{x}" y="{y}" fill="{c}" font-family="DejaVu Sans, sans-serif" font-size="{z}">{escape(t)}</text>')
def line(x0,y0,x1,y1,c,w=1):
    s.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{c}" stroke-width="{w}"/>')
text(21,34,"A zero marker can hide a change in the join",25)
for i,(title,key,channel,limit,col) in enumerate((
    ("A. Matched phase, left","phase_matched_full_cycles","left",900,"#8be4cb"),
    ("B. Opposite slopes, left","left_zero_opposite_slopes","left",900,"#ffc994"),
    ("C. Same B join, right","left_zero_opposite_slopes","right",13000,"#ff9b90"),
)):
    x=20+318*i
    s.append(f'<rect x="{x}" y="57" width="304" height="258" rx="10" fill="#19283a" stroke="#455c71"/>')
    text(x+13,84,title,17)
    line(x+33,179,x+276,179,"#62798d")
    text(x+11,184,"0",12)
    trip=data[key]["first_internal_seam_triplets"][channel]
    points=[(x+63+k*90,179-72*v/limit) for k,v in enumerate(trip)]
    for a,b in zip(points,points[1:]):line(*a,*b,col,3)
    for (px,py),v,l in zip(points,trip,("last kept","first kept","next")):
        s.append(f'<circle cx="{px}" cy="{py}" r="4.5" fill="{col}"/>')
        text(px-(17 if abs(v)<1000 else 26), py-12, str(v), 12, col)
        text(px-28,269,l,12)
    text(x+12,296, "Vertical scale: ±"+str(limit)+" PCM",12,"#bdcede")
text(21,345,"Only kept samples are shown. The end marker is excluded in this example.",14,"#d0deed")
s.append("</svg>")
Path("loop-seam.svg").write_text("\n".join(s)+"\n")
