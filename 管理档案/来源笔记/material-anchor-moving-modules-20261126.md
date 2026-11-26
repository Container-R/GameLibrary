# 投影锚点的主要来源与证据

- Godot Engine 4.5，[Standard Material 3D and ORM Material 3D / World Triplanar](https://docs.godotengine.org/en/4.5/tutorials/3d/standard_material_3d.html#world-triplanar)。官方文档的 UV1/UV2 两个小节分别给出三轴采样与按法线混合，以及默认对象局部、开关切到世界空间。正文的共享锚不是此开关的附加功能，也没有运行 Godot 断言其输出。
- [独立着色器与原始读回](../实验/material-anchor-moving-modules/README.md)：真实 Mesa 软件 OpenGL 对两个独立 draw 运行的无光照调试色与相位验证；不是三平面取样权重和实际法线纹理的实验。组变换公式是本篇产生对应点的几何推导，固定方向中的非均匀缩放用精确模型核对。
- 文档查阅：2026-11-26（北京时间）。
