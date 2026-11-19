from pathlib import Path
from xml.sax.saxutils import escape

W,H = 900,460
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Shoulder swap: physical path and target visibility are different checks">','<rect width="900" height="460" fill="#111c2a"/>']
L=(-1,-3); R=(1,-3); V=(0,-2); T=(0,5)
def text(x,y,t,clr="#edf3ff",size=16):
    s.append(f'<text x="{x}" y="{y}" fill="{clr}" font-family="DejaVu Sans, sans-serif" font-size="{size}">{escape(t)}</text>')
def seg(a,b,c,color,dash=""):
    x,y=pos(a,c); x1,y1=pos(b,c)
    arg=f' stroke-dasharray="{dash}"' if dash else ""
    s.append(f'<line x1="{x}" y1="{y}" x2="{x1}" y2="{y1}" stroke="{color}" stroke-width="3"{arg}/>')
def dot(p,c,color,r=4,outline=None):
    x,y=pos(p,c)
    s.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" stroke="{outline or color}" stroke-width="1.5"/>')
# The route panel is zoomed in; each panel is isotropic.
def pos(p,c):
    if c == 248:
        return c+p[0]*83, 228-(p[1]+3)*83
    return c+p[0]*34, 282-p[1]*34

text(29,34,"A shoulder swap has two separate checks",size=25)
s += ['<rect x="25" y="57" width="432" height="366" rx="12" fill="#172637" stroke="#435369"/>',
      '<rect x="473" y="57" width="402" height="366" rx="12" fill="#172637" stroke="#435369"/>']
text(45,88,"A. Can the camera move across?")
text(493,88,"B. Is the focus still visible?")
c=248
seg(L,R,c,"#ff8c81","5 5");seg(L,V,c,"#8be4cb");seg(V,R,c,"#8be4cb")
dot((0,-3),c,"#994e4e",83*.35,"#ffadad")
for p,t,xo,yo in [(L,"Left",-40,56),(R,"Right",10,56),(V,"Via",23,-5)]:
    dot(p,c,"#c7fff4",16.6,"#8be4cb");dot(p,c,"#102a2f",4);x,y=pos(p,c);text(x+xo,y+yo,t)
text(49,348,"Red: blocked direct move","#ffb4ab")
text(49,378,"Green: both detour segments clear","#bcffe7")
c=675
seg(L,T,c,"#8be4cb");seg(R,T,c,"#8be4cb");seg(V,T,c,"#ff8c81","5 5")
for p,t,xo,yo in [(L,"Left",-35,-9),(R,"Right",10,-9),(V,"Via",8,-7),(T,"Focus",12,10)]:
    dot(p,c,"#e4fcf4");x,y=pos(p,c);text(x+xo,y+yo,t)
dot((0,1),c,"#ff8c81",6.8,"#ffbdb5")
text(700,255,"Prop blocks", "#ffb4ab",14);text(700,275,"only the via ray", "#ffb4ab",14)
text(46,447,"Illustration: sphere proxy and a single point of focus; not a rendered gameplay view.", "#c6d5e7",14)
s.append("</svg>")
Path("shoulder-path.svg").write_text("\n".join(s)+"\n")
