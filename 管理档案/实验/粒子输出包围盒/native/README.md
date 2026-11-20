# 粒子绘制范围：CPU 剔除与 OpenGL 读回

在本目录运行。需要 Python、系统 EGL 与 Mesa llvmpipe；仅生成对照图需要 Pillow。

```sh
set -e
timeout 30 python3 -B probe.py /tmp/particle-bounds-contact.png > /tmp/particle-bounds-observed.json
cmp /tmp/particle-bounds-observed.json observed.json
cmp /tmp/particle-bounds-contact.png contact.png
```

实际运行：无窗口 EGL、Mesa 25.0.7 / llvmpipe / OpenGL 4.5 Compatibility。脚本用自己的 CPU 区间相交判定决定是否调用 OpenGL 绘制；边界值不是 OpenGL 的输入。提交时 OpenGL 实际剪裁并栅格化两个三角形，构成 X=[−3,1]、Y=[−0.5,0.5] 的不透明红色四边形。Y 方向相机为 [−1,1]。结果从 64×32 目标读回 RGBA8，不由 CPU 填写可见像素。

| 相机 X | CPU 边界 X | 判定／对照 | 提交 | 红像素 |
|---|---|---|---:|---:|
| [0,4] | [−2.25,−1.75] | 剔除 | 0 | 0 |
| [0,4] | [−2.25,−1.75] | 剔除后人为强制提交 | 1 | 256 |
| [0,4] | [−3,1] | 贴合实际输出，准入 | 1 | 256 |
| [−5,−4] | [−3,1] | 剔除 | 0 | 0 |
| [−5,−4] | [−5,1] | 宽松边界，准入 | 1 | 0 |

主相机两个可见样本的完整像素读回一致，红色覆盖为 X=0–15、Y=8–23（16×16）。副相机两份读回全黑且一致，但宽松边界确实提交了两个三角形的一次绘制。绘制计数是脚本的实际 API 调用时序，不是驱动或硬件统计。图为实际读回，放大仅为显示。此处两次独立运行的 JSON 与 PNG 分别逐字节一致。

仅复现“给定绘制体，剔除时使用哪个边界”的后果。未运行 Unity、Unreal、Godot 或其粒子生命周期；没有模拟随时间更新、真实输出扩展、透明贴图、遮挡剔除、其他轴边界、性能或硬件 GPU 验证。宽松边界导致额外一次提交，不等于测到帧率损失。
