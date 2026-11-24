# 拖尾网格的边标签与绕序

[返回正文](../../../GameLibrary/视觉特效/特效制作/拖尾网格/拖尾中心线没断，网格为什么会翻面.md)

- [解析扫角脚本](probe.py)及[原始输出](observed.txt)：使用 `T×D`，与正文 `D×T` 的方向符号相反，零点与换边结论相同。
- [OpenGL 对照](gl_ribbon.py)、[原始输出](gl-observed.txt)、[颜色图](ribbon-gl.png)：Linux、Python 3、Mesa surfaceless EGL 和桌面 OpenGL 3.3 或更新版本；实测 Mesa 25.0.7 llvmpipe、OpenGL 4.5 Core。运行：
  ```sh
  MESA_SHADER_CACHE_DISABLE=true LIBGL_ALWAYS_SOFTWARE=1 python3 gl_ribbon.py
  ```

固定视向 +Z，曲线 `P(s)=(1−s²,εs,s)`，ε=0.01，s 取 −1、0.5。从 `P′=(-2s,ε,1)` 得到单位切线，叉积模为 `sqrt(4s²+ε²)/sqrt(4s²+ε²+1)`，在 s=0 取最小值。正交投到 `(16+84P.x,20+84P.y)` 后，沿归一化叉积两侧各挤出 12 像素。这里故意只接两个截面，各用真实曲线导数；并未渲染完整曲线、不跑 Unity 内置组件。

每个三角形以 0.25 的红通道值作加法覆盖，实测 8 位缓冲对应 64、128；关闭深度、多重采样和抖色。图中颜色诊断则关闭混合，重叠处后画的三角形会盖住先画者，所以覆盖统计取自单独一遍。图由三种宽度轴列组和三个调试模式行组构成，与正文顺序相同。PNG 由读回色值按最近邻 3 倍放大。两轮日志与 PNG 逐字节一致；不把确切像素数外推到不同驱动或尺寸。
