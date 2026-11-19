import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from math import pi
import numpy as np
for family in ("Noto Sans CJK SC","Noto Sans CJK JP","WenQuanYi Zen Hei"):
    if any(f.name==family for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = family
        break
else:
    raise RuntimeError("CJK font required")
plt.rcParams["axes.unicode_minus"]=False
t=np.linspace(0,7,1500)
u=np.arange(0,8)
v=np.arange(0,7.01,.5)
f=lambda n:.8*np.sqrt(2)*np.sin(pi*n/2+pi/4)
fig,ax=plt.subplots(figsize=(8.6,3.7))
ax.plot(t,f(t),label="理想重建：12 kHz 正弦",color="#0a628a",lw=2.1)
ax.scatter(v[1::2],f(v[1::2]),marker="x",color="#ab4c22",s=42,label="96 kHz 新增采样时刻",zorder=4)
ax.scatter(u,f(u),color="#0b385b",edgecolor="white",s=53,label="48 kHz 原始采样",zorder=5)
ax.axhline(1,color="#9d431e",ls="--",lw=1,label="标称满量程 ±1")
ax.axhline(-1,color="#9d431e",ls="--",lw=1)
ax.set(xlim=(-.07,7.07),ylim=(-1.23,1.26),xlabel="时间（以 48 kHz 的采样间隔为单位）",ylabel="归一化幅度")
ax.legend(bbox_to_anchor=(.5,1.02),loc="lower center",ncol=2,frameon=False,fontsize=9)
fig.tight_layout()
fig.savefig("peak.png",dpi=145)
