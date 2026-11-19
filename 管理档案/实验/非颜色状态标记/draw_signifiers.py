from pathlib import Path
from xml.sax.saxutils import escape

s=['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="455" viewBox="0 0 960 455" role="img" aria-label="Map door availability cues independent of current selection">','<rect width="960" height="455" fill="#121b29"/>']
def label(x,y,val,size=16,c="#edf5ff"):
    s.append(f'<text x="{x}" y="{y}" fill="{c}" font-family="DejaVu Sans, sans-serif" font-size="{size}">{escape(val)}</text>')
def rect(x,y,w,h,c,stroke=None,width=1):
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{c}"'+(f' stroke="{stroke}" stroke-width="{width}"' if stroke else '')+'/>')
def badge(x,y,c,variant,focus):
    rect(x-30,y-30,60,60,"#000000")
    if focus:
        rect(x-30,y-30,60,60,"none","#f0f5ff",3)
    if variant=="plain":
        rect(x-13,y-15,26,30,c)
    else:
        d = f'M {x-13},{y+15} V {y-14} H {x+13} V {y+15}'
        s.append(f'<path d="{d}" stroke="{c}" stroke-width="5" fill="none" stroke-linejoin="round"/>')
        if variant=="locked":
            s.append(f'<path d="M {x-13},{y} H {x+13}" stroke="{c}" stroke-width="5"/>')

label(24,38,"A bright icon can still hide its meaning",26)
for i,(x,ttl,desc,gray,extra) in enumerate([
    (25,"Color only","Same silhouette for both states",False,False),
    (253,"Remove hue","Both map to gray 127",True,False),
    (481,"Shape and color","Crossbar means blocked",False,True),
    (709,"Shape without hue","Availability is still encoded",True,True),
]):
    rect(x,55,220,348,"#192838","#42566c")
    label(x+12,84,ttl,17);label(x+12,108,desc,12,"#ccdcee")
    for j,op in enumerate(("ready","blocked")):
        y=192+133*j;label(x+13,y-41,op.capitalize(),14)
        for k,selected in enumerate((False,True)):
            c="#7f7f7f" if gray else ("#009400" if op=="ready" else "#ff0000")
            variant=("open" if op=="ready" else "locked") if extra else "plain"
            cx=x+61+k*104
            badge(cx,y,c,variant,selected)
            label(cx-24,y+52,"Focus" if selected else "Idle",12,"#dce9f7")
label(26,438,"White outer border = current focus. Silhouette and focus are separate visual layers.",15,"#d7e9fa")
s.append("</svg>")
Path("state-focus-matrix.svg").write_text("\n".join(s)+"\n")
