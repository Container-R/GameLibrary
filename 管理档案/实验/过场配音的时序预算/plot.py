"""Original scale timeline, generated from the Node fixture."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root=Path(__file__).parent
v=json.loads((root/"model.observed.json").read_text())
im=Image.new("RGB",(1120,530),"white")
d=ImageDraw.Draw(im)
font="/usr/share/fonts/opentype/noto/NotoSansCJK-"
ink="#182b3c"
def txt(x,y,s,sz=21,bold=False,fill=ink,anchor="lt"):
    family=font+("Bold.ttc" if bold else "Regular.ttc")
    d.text((x,y),s,font=ImageFont.truetype(family,sz,index=2),fill=fill,anchor=anchor)
def m(ms): return round(160+ms*0.132)
def segment(ms0,ms1,y,fill):
    d.rectangle((m(ms0),y,m(ms1)-1,y+23),fill=fill)
def box(y0, y1):
    d.rounded_rectangle((34,y0,1085,y1),radius=12,fill="#eff3f6")
def line(x,y0,y1,c,w=1): d.line((x,y0,x,y1),fill=c,width=w)
txt(35,24,"配音变长，固定事件仍在 6.50 秒",30,True)
txt(35,69,"同一场景时钟。蓝绿为音频片段占用，反应和等待只在标注允许处收缩。",20)
for y in (157,252,347): box(y-14,y+65)
for tick in range(0,7000,1000):
    line(m(tick),117,396,"#c2ccd4")
    txt(m(tick),104,f"{tick//1000}s",18,anchor="mt")
hard=m(v["reference"]["hardCue"])
line(hard,122,413,"#903437",3)
txt(hard,417,"固定事件",19,True,"#903437","mt")
for y,key,title in [(157,"reference","原配音"),(252,"stretch","可容纳"),(347,"impossible","放不下")]:
    txt(52,y,title,23,True)
    row=v[key]
    if not row["ok"]:
        plan=row["minimumPlan"]
        segment(plan["aStart"],plan["aEnd"],y,"#205c90")
        segment(plan["aEnd"],plan["bStart"],y,"#aa7026")
        segment(plan["bStart"],plan["bEnd"],y,"#187369")
        segment(plan["bEnd"],row["hardCue"],y,"#aa7026")
        segment(row["hardCue"],plan["finish"],y,"#903437")
        txt(m(600),y+35,f"反应与等待已到下限，仍溢出 {row['overflow']} ms",19,fill="#903437")
        continue
    a,b=row["dialogueA"],row["dialogueB"]
    segment(a["start"],a["sectionEnd"],y,"#205c90")
    segment(a["sectionEnd"],b["start"],y,"#aa7026")
    segment(b["start"],b["sectionEnd"],y,"#187369")
    segment(b["sectionEnd"],b["sectionEnd"]+row["afterB"],y,"#aa7026")
    if row["neutralHold"]:
        segment(b["sectionEnd"]+row["afterB"],row["hardCue"],y,"#738394")
    txt(m(600),y+35,f"反应 {row['reaction']} ms　｜　B 后等待 {row['afterB']} ms　｜　末尾机动 {row['neutralHold']} ms",18)
for i,(label,color) in enumerate([("台词 A","#205c90"),("台词 B","#187369"),("受限停顿","#aa7026"),("末尾机动","#738394")]):
    x=165+i*185
    d.rectangle((x,481,x+25,497),fill=color)
    txt(x+34,477,label,18)
im.save(root/"timeline.png")
