# HUD 与场景缩放的合成顺序：复现

[返回正文](../../../GameLibrary/图形渲染/画面呈现/动态分辨率/调低场景分辨率后，HUD%20小字为什么也变糊.md)

[解析一维试件](probe.py)及[读数](observed.txt)：16 列先按两列平均成 8，再通过像素中心映射与线性插值回到 16。目标列 6 或 7 会落入同一个低分辨率采样格。

[OpenGL 脚本](gl_hud.py)、[原始日志](gl-observed.txt)、[读回图](hud-composite.png)：Linux、Python 3 标准库、EGL/Mesa surfaceless 与桌面 OpenGL 3.3 或更新版本。实测 4.5 Core、Mesa 25.0.7 llvmpipe。运行：

```sh
MESA_SHADER_CACHE_DISABLE=true LIBGL_ALWAYS_SOFTWARE=1 python3 gl_hud.py
```

固定 96×48 RGBA8 场景，绘制不透明的简单背景，定长像素字和竖线用 scissor 限定的 clear 写入，不使用真实字体、抗锯齿或 alpha 混合。下采样、上采样都用实际 `glBlitFramebuffer(GL_LINEAR)`；中间为 48×24，禁用 sRGB 转换和抖色。输入先有完整尺寸，以便只切换 HUD 合成阶段，不模拟游戏直接低分辨率光栅化。

原始日志的 8 位红通道为 y=16 行的准星中段。图左右为目标列 62 的前/后合成，均用最近邻放大 5 倍。不同驱动的 8 位末位舍入可能不同，回归关注前合成丢掉位置差异、后合成保留位置、最终采样分布发生变化，而不是把本例的亮度数字外推到真实字体和现代时域上采样。
