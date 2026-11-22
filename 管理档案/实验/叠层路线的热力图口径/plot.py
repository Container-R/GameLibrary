"""Original synthetic plot; reads the recorded Node output, no external data."""
import json
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw

folder = Path(__file__).parent
data = json.loads((folder / "exposure.observed.json").read_text())
rows = data["byRegion"]
collapsed = data["collapsedWithoutConnectorsOrUnknown"]
base = "white"
canvas = Image.new("RGB", (1080, 540), base)
d = ImageDraw.Draw(canvas)
fonts = "/usr/share/fonts/opentype/noto/NotoSansCJK-"
def lab(x, y, s, size=23, color="#192a37", bold=False):
    f = ImageFont.truetype(fonts + ("Bold.ttc" if bold else "Regular.ttc"), size, index=2)
    d.text((x,y), s, font=f, fill=color, anchor="lt")
blue, amber, tint = "#174d77", "#a44614", "#edf2f6"
lab(34,24,"同一格，两层路：先看热力图是怎样算的",32,bold=True)
lab(34,72,"固定关卡版本，合成记录。比例只用有明确成功或危险失败的合格尝试计算。",21)
for x, nx in [(34,350),(372,702),(724,1045)]:
    d.rounded_rectangle((x,127,nx,446),radius=13,fill=tint)
lab(53,150,"① 只按平面叠放",25,bold=True)
d.rectangle((108,214,277,317), fill="#d8e6ee", outline="#3b4c5b", width=2)
d.line((110,269,275,269),fill=blue,width=9)
for x in range(110,271,20):
    d.line((x,269,min(x+10,275),269),fill=amber,width=9)
lab(117,228,"上、下层投影",18)
lab(117,288,"落在同一位置",18)
lab(69,358,f"同一格：{collapsed['failed']} / {collapsed['exposure']}",24,bold=True)
lab(69,397,f"两层合并 {collapsed['risk']:.2%}",20)
def section(x, title, key, limit):
    lab(x,150,title,25,bold=True)
    for k, y, clr, label in [("lower",215,blue,"下层"),("upper",322,amber,"上层")]:
        r=rows[k]
        lab(x,y,label,22,clr,True)
        d.rounded_rectangle((x,y+33,x+194,y+56),radius=4,fill="#d4dde3")
        width=round(194 * r[key]/limit)
        d.rounded_rectangle((x,y+33,x+width,y+56),radius=4,fill=clr)
        val = f'{r["failed"]} 次' if key=="failed" else f'{r["risk"]:.0%}'
        lab(x+207,y+31,val,22,clr,True)
        suffix = f"有成功或危险失败：{r['exposure']} 次" if key=="failed" else f"{r['failed']} / {r['exposure']} 次"
        lab(x,y+63,suffix,18)
section(391,"② 按失败数量","failed",max(rows[k]["failed"] for k in ("upper","lower")))
section(743,"③ 按穿越失败比例","risk",1)
lab(36,463,f"上层另有 {data['openByRegion']['upper']} 次未见结局、{data['otherEndingByRegion']['upper']} 次已知折返；未计入比例。",19)
lab(36,497,"未归类与连接区不并入双楼层对照；少量样本只提供排查线索。",19)
canvas.save(folder / "overlay.png")
