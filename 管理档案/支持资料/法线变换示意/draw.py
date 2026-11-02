"""Draw the existing exact planar example; not an engine or numerical test."""
from pathlib import Path
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
from matplotlib.font_manager import FontProperties

OUT = Path(__file__).resolve().parent
plt.rcParams.update({'svg.hashsalt': 'normal-transform-planar-example',
                     'svg.fonttype': 'path', 'font.size': 13})
font = FontProperties(family='Noto Sans CJK JP')
fig, ax = plt.subplots(figsize=(9, 6.5), dpi=160)
fig.patch.set_facecolor('white')
fig.subplots_adjust(left=.08, right=.95, bottom=.17, top=.84)
ax.set_aspect('equal', adjustable='box')
ax.set_xlim(-.35, 1.4)
ax.set_ylim(-.7, 1.15)
ax.axis('off')
ax.add_patch(Circle((0,0), 1, fill=False, linestyle=(0,(2,4)),
                    edgecolor='#d4dae1', linewidth=1.2))
for end in [(1.25,0), (0,1.1)]:
    ax.add_patch(FancyArrowPatch((-.22,0) if end[0] else (0,-.62),end,
                 arrowstyle='-|>',mutation_scale=11,linewidth=1,color='#7c8794'))
ax.text(1.28,-.025,'x',color='#566170',fontsize=14)
ax.text(-.045,1.12,'y',color='#566170',fontsize=14)
ax.text(-.06,-.09,'0',color='#566170',fontsize=11)
q=math.sqrt(5)
t=(2/q,-1/q); n=(1/q,2/q); wrong=(2/q,1/q)
for v,col,style in [(t,'#1460a8','-'),(n,'#087f73','-'),(wrong,'#b84f12','--')]:
    ax.add_patch(FancyArrowPatch((0,0),v,arrowstyle='-|>',mutation_scale=18,
                                linewidth=2.8,color=col,linestyle=style,
                                shrinkA=0,shrinkB=0,zorder=3))
r=.15
ax.plot([r*t[0],r*(t[0]+n[0]),r*n[0]],
        [r*t[1],r*(t[1]+n[1]),r*n[1]],color='#087f73',linewidth=1.4)
ax.text(.33,1.01,"正确法线",fontproperties=font,color='#087f73',fontsize=14)
ax.text(.33,.92,r"$N'=(1,2)/\sqrt{5}$",color='#087f73',fontsize=14)
ax.text(.93,.51,"错误法线",fontproperties=font,color='#b84f12',fontsize=14)
ax.text(.93,.40,r"$N_{\mathrm{wrong}}=(2,1)/\sqrt{5}$",color='#b84f12',fontsize=14)
ax.text(.71,-.55,"变换后的切线",fontproperties=font,color='#1460a8',fontsize=14)
ax.text(.71,-.65,r"$T'=(2,-1)/\sqrt{5}$",color='#1460a8',fontsize=14)
fig.text(.5,.945,'单位长度相同，垂直关系不同',ha='center',fontproperties=font,fontsize=20)
fig.text(.5,.895,'原例的 xy 平面 · 等比例坐标 · 三个向量长度均为 1',
         ha='center',fontproperties=font,fontsize=12,color='#566170')
fig.text(.5,.09,r"$N'\cdot T'=0\qquad\qquad N_{\mathrm{wrong}}\cdot T'=3/5$",
         ha='center',fontsize=17)
fig.text(.5,.035,'原有代数例子的示意图；不是三维表面、渲染截图或引擎观察。',
         ha='center',fontproperties=font,fontsize=11,color='#566170')
fig.savefig(OUT/'normal-transform.svg',metadata={'Date':None,'Creator':None})
fig.savefig(OUT/'normal-transform.png',metadata={'Software':None})
plt.close(fig)
