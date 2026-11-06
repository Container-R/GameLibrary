"""Original 2D teaching schematic. No renderer, material, engine, or user test."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
from matplotlib.font_manager import FontProperties
p=Path(__file__).resolve().parent
font=FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams['svg.fonttype']='none'
fig=plt.figure(figsize=(14,9),facecolor='#f5f4ef')
labels=[('A  粗略明暗关系',None,False),('B  增加高对比重复纹样','#4a5057',False),('C  只降低重复线条的对比','#9da3aa',False),('D  加入玩法对象后，重新讨论门内背景','#9da3aa',True)]
def scene(ax,seam=None,actor=False,bright=False):
 ax.set_xlim(0,600);ax.set_ylim(0,320);ax.set_aspect('equal');ax.axis('off')
 ax.add_patch(Rectangle((0,0),600,320,color='#727b85'))
 ax.add_patch(Rectangle((40,35),520,245,color='#bcc2ca'))
 if seam:
  # Fixed drawing-coordinate thickness makes inset views true scaled copies.
  thickness=4.8
  for y in [70,110,150,190,230,270]:
   ax.add_patch(Rectangle((40,y-thickness/2),520,thickness,color=seam,zorder=1.5))
  for j,(y0,y1) in enumerate([(35,70),(70,110),(110,150),(150,190),(190,230),(230,270),(270,280)]):
   for x in range(75+35*(j%2),560,70):
    ax.add_patch(Rectangle((x-thickness/2,y0),thickness,y1-y0,color=seam,zorder=1.5))
 ax.add_patch(Rectangle((210,30),180,230,color='#8b929b',zorder=2))
 ax.add_patch(Rectangle((235,30),130,205,color='#29323d' if not bright else '#7f8b97',zorder=3))
 ax.add_patch(Rectangle((40,25),520,10,color='#969fa8',zorder=4))
 # A persistent gameplay ledge. Its strong edge must not be removed with decorative lines.
 ax.add_patch(Rectangle((438,115),100,11,color='#384753',zorder=4))
 ax.add_patch(Rectangle((438,123),100,3,color='#dcdfc8',zorder=4))
 if actor:
  ax.add_patch(Circle((298,170),11,color='#343c46',zorder=5))
  ax.add_patch(Polygon([[285,158],[311,158],[319,119],[311,108],[310,55],[300,55],[297,103],[293,55],[282,55],[285,108],[276,119]],closed=True,color='#343c46',zorder=5))
 # All outlines are filled shapes; avoid fixed point-width patch strokes.
 for patch in ax.patches:patch.set_linewidth(0)
for i,(title,seam,act) in enumerate(labels):
 x=.055+.48*(i%2);y=.53 if i<2 else .075
 if i != 3:
  ax=fig.add_axes([x,y+.085,.41,.285]);scene(ax,seam,act,act)
 else:
  for j,bright in enumerate([False,True]):
   ax=fig.add_axes([x+j*.215,y+.115,.195,.205]);scene(ax,seam,True,bright)
   fig.text(x+j*.215+.03,y+.085,'深色门内背景' if not bright else '较浅门内背景候选',fontproperties=font,fontsize=11,color='#43515b')
 fig.text(x,y+.385,title,fontproperties=font,fontsize=14,color='#17232e')
 if i!=3:
  small=fig.add_axes([x,y,.145,.078]);scene(small,seam)
  fig.text(x+.155,y+.02,'同一二维图缩小显示\n不是更远镜头的实测',fontproperties=font,fontsize=10,color='#43515b')
 else:
  fig.text(x,y+.02,'D内两图为同尺度、同剪影，只改门内底色。\n它们表示候选冲突，不给出玩家辨识结论。',fontproperties=font,fontsize=10,color='#43515b')
fig.text(.055,.965,'原创二维制作对照：固定门洞和墙面，分别改变纹样与局部背景',fontproperties=font,fontsize=19,color='#17232e')
fig.text(.055,.025,'所有面板均为平面色块。线条不代表已建模砖缝，底色不代表材质或真实照明；不评价玩家辨识效果。',fontproperties=font,fontsize=10,color='#43515b')
fig.savefig(p/'value-group-comparison.svg',facecolor=fig.get_facecolor())
fig.savefig(p/'value-group-comparison.png',dpi=130,facecolor=fig.get_facecolor())
print('Wrote original SVG and PNG; no 3D render or perception measurement.')
