# 移动墙组的投影锚点复现

[返回正文](../../../GameLibrary/技术美术/环境管线/纹理与材质/两块墙一起搬动，污渍怎样跟着走又不断缝.md)

Linux、Python 3.12.14、Pillow、Mesa EGL surfaceless（实际 Mesa 25.0.7 llvmpipe、桌面 OpenGL 4.5 core）。不需游戏资产。脚本在当前目录生成调试 PNG。

```sh
python3 model.py
LIBGL_ALWAYS_SOFTWARE=1 MESA_SHADER_CACHE_DISABLE=true python3 gl_anchor.py
```

- [精确分数模型](model.py) · [实际输出](observed.txt)：拼缝数学位置、平移/旋转、共同搬移世界原点及倍宽坐标，区分固定相位和保持米数。完整逆仿射只处理共享的可逆组变换，不自动逆掉各模块独立缩放。
- [原生调试着色器](gl_anchor.py) · [实际浮点读回](gl_observed.txt) · [调试色图](anchor_readback.png)：两个独立 draw 使用相同输出布局，着色器内对投影位置变换。比较同一表面位置的相位、拼缝近邻、原点重定位。橄榄绿与紫蓝是人为编码，不是纹理资产的真实色彩。
- [来源记录](../../来源笔记/material-anchor-moving-modules-20261126.md)。试验没有执行三平面法线混合、实际 Godot 材质、非均匀缩放渲染或性能基准。缩放取舍由精确模型和几何推导说明。
