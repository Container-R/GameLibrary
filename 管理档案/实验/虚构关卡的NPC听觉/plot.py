"""Draw an original not-to-scale plan from the fixture results."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

p=Path(__file__).parent
q=json.loads((p/"hearing.observed.json").read_text())
im=Image.new("RGB",(1120,592),"white")
d=ImageDraw.Draw(im)
font="/usr/share/fonts/opentype/noto/NotoSansCJK-"
ink="#203547"
def t(x,y,s,n=22,color=ink,b=False,anchor="lt"):
    f=font+("Bold.ttc" if b else "Regular.ttc")
    d.text((x,y),s,font=ImageFont.truetype(f,n,index=2),fill=color,anchor=anchor)
def room(box,label):
    d.rounded_rectangle(box,radius=10,fill="#edf2f6",outline="#c5d1db",width=2)
    if label.endswith(" B"):
        t(box[0]+112,box[1]+15,label,19)
    else:
        t(box[0]+12,box[3]-35,label,19)
def link(points,color,width=4):
    d.line(points,fill=color,width=width,joint="curve")
def dot(x,y,label):
    d.ellipse((x-18,y-18,x+18,y+18),fill="white",outline=ink,width=2)
    t(x,y-7,label,18,ink,True,"mt")
def dash(x1,x2,y,color):
    for x in range(x1,x2,17):
        d.line((x,y,min(x+8,x2),y),fill=color,width=3)
blue,orange,green="#205b89","#a65519","#227562"
t(35,24,"同样近的两个 NPC，收到的声音事件不同",30,b=True)
t(35,68,"虚构关卡拓扑，连线不按比例。S 到 A、B 的直线距离均为 4。",20)
room((62,160,304,380),"监听区 A")
room((400,160,710,380),"工作间")
room((815,160,1058,380),"监听区 B")
y=267
link([(180,y),(318,y),(318,141),(466,141),(466,y),(560,y)],blue)
link([(560,y),(950,y)],orange)
d.rectangle((752,y-17,772,y+17),fill="white",outline=orange,width=3)
link([(560,y),(620,y),(620,116),(896,116),(896,y),(950,y)],"#485865")
link([(560,y),(652,y),(652,348),(753,348)],green)
dash(753,849,348,green)
link([(849,348),(925,348),(925,y),(950,y)],green)
dot(180,y,"A");dot(560,y,"S");dot(950,y,"B")
t(64,402,f"左开口：代价 {q[0]['A']['path']['cost']}",19,blue)
t(330,402,f"右门开：代价 {q[1]['B']['path']['cost']}",19,orange)
t(573,402,f"关门绕长廊：代价 {q[0]['B']['path']['cost']}",19,"#485865")
t(830,402,f"加通风口：代价 {q[3]['B']['path']['cost']}",19,green)
t(62,461,"预算 10：关门仅 A 听见；开门 A、B 都听见。",22,b=True)
t(62,500,"关门时，预算 20 可经长廊送达 B；预算 16 加通风口也可送达 B。",20)
t(62,541,"虚线：只用于声传播，不是 NPC 可走的路线。",19,green)
im.save(p/"rooms.png")
