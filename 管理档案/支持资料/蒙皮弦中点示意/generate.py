#!/usr/bin/env python3
"""Original geometry illustration, standard library only; no skinning runtime."""
from pathlib import Path
import math
import json

ROOT=Path(__file__).resolve().parent
p0=(1.0,0.0); p1=(-0.5,math.sqrt(3)/2)
lbs=tuple((a+b)/2 for a,b in zip(p0,p1))
rotation=(0.5,math.sqrt(3)/2)
assert math.isclose(math.hypot(*lbs),0.5)
assert math.isclose(math.hypot(*rotation),1.0)
assert math.isclose(math.atan2(rotation[1],rotation[0]),math.pi/3)
CX,CY,S=380,450,260  # same scale for X and Y, invert only screen Y

def screen(p):return (CX+S*p[0],CY-S*p[1])
def xy(p):return ','.join(f'{v:.6f}' for v in screen(p))
def line(a,b,style):return f'<line x1="{screen(a)[0]:.6f}" y1="{screen(a)[1]:.6f}" x2="{screen(b)[0]:.6f}" y2="{screen(b)[1]:.6f}" {style}/>'
def dot(p,color):return f'<circle cx="{screen(p)[0]:.6f}" cy="{screen(p)[1]:.6f}" r="7" fill="{color}" stroke="white" stroke-width="2"/>'
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="800" viewBox="0 0 1120 800" role="img" aria-labelledby="title desc">
<title id="title">平均位置不在旋转圆上</title>
<desc id="desc">沿Z轴看XY平面，X与Y等比例。单位圆上0度与120度两个端点的等权LBS结果是弦中点，距原点二分之一；本例归一化旋转混合的60度结果位于圆上，距原点一。只是一个顶点，不代表体积保持。</desc>
<rect width="1120" height="800" fill="#ffffff"/>
<g font-family="Noto Sans CJK SC, Noto Sans CJK JP, sans-serif" fill="#172b3a">
<text x="50" y="54" font-size="30" font-weight="bold">同样两个旋转：平均位置与混合旋转并不相同</text>
<text x="50" y="91" font-size="18">沿 Z 轴看 XY 平面 · 两项各占 1/2 · 无平移、缩放或剪切 · 等比例坐标</text>
<circle cx="380" cy="450" r="260" fill="#f8fafc" stroke="#a8b5c3" stroke-width="2"/>
{line((-1.16,0),(1.2,0),'stroke="#a8b5c3" stroke-width="1.5"')}
{line((0,-1.12),(0,1.13),'stroke="#a8b5c3" stroke-width="1.5"')}
<text x="696" y="457" font-size="19">X</text><text x="391" y="151" font-size="19">Y</text>
<text x="352" y="479" font-size="19">O</text>
<path d="M {xy(p0)} A 260,260 0 0 0 {xy(p1)}" fill="none" stroke="#16816b" stroke-width="5"/>
{line(p0,p1,'stroke="#c16b13" stroke-width="4"')}
{line((0,0),rotation,'stroke="#16816b" stroke-width="2" stroke-dasharray="6 6"')}
{line((0,0),lbs,'stroke="#c16b13" stroke-width="5"')}
{dot(p0,'#253c5a')}{dot(p1,'#253c5a')}{dot(rotation,'#16816b')}{dot(lbs,'#c16b13')}
<text x="650" y="478" font-size="18">p₀ = (1, 0)</text>
<text x="91" y="197" font-size="18">p₁ = (−1/2, √3/2)</text>
<text x="472" y="194" font-size="18" fill="#126452">旋转混合：60°</text>
<text x="460" y="345" font-size="18" fill="#96500b">LBS：弦中点</text>
<text x="280" y="748" font-size="17" fill="#536577">单位圆：到 Z 轴的距离为 1</text>
<g transform="translate(775,190)">
<text x="0" y="0" font-size="22" font-weight="bold">比较同一个顶点</text>
<circle cx="8" cy="45" r="7" fill="#253c5a"/>
<text x="29" y="51" font-size="19">两个输入终点</text>
<text x="29" y="83" font-size="18">分别为 0° 与 120°</text>
<text x="29" y="113" font-size="18">到轴距离均为 1</text>
<circle cx="8" cy="167" r="7" fill="#c16b13"/>
<text x="29" y="173" font-size="19" fill="#96500b">先旋转，再平均位置</text>
<text x="29" y="205" font-size="18">(1/4, √3/4)</text>
<text x="29" y="235" font-size="18">到轴距离 = 1/2</text>
<circle cx="8" cy="289" r="7" fill="#16816b"/>
<text x="29" y="295" font-size="19" fill="#126452">本例先混合旋转</text>
<text x="29" y="327" font-size="18">(1/2, √3/2)</text>
<text x="29" y="357" font-size="18">到轴距离 = 1</text>
<text x="0" y="420" font-size="17">圆弧表示本例的旋转位置，</text>
<text x="0" y="448" font-size="17">不是动画采样或执行轨迹。</text>
</g>
<text x="50" y="784" font-size="16" fill="#536577">原创理想几何示意；只比较一个顶点，不证明网格体积保持，也不是角色、着色器或性能实测。</text>
</g></svg>'''
(ROOT/'skinning-chord.svg').write_text(svg)
(ROOT/'geometry.json').write_text(json.dumps({'space':'XY viewed along Z; all z=0','weights':[0.5,0.5],'input_endpoints':[p0,p1],'lbs':lbs,'normalized_rotation_result':rotation,'distance_to_axis':{'lbs':math.hypot(*lbs),'rotation':math.hypot(*rotation)},'drawing_pixels_per_unit':{'x':S,'y':S},'scope':'original ideal single-vertex geometry; not a skinning runtime'},indent=2)+'\n')
