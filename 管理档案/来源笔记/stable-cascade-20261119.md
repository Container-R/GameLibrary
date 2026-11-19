# 方向光的级联阴影：来源、推导与试件

问题：相机移动时，方向光阴影边缘为什么在静态接收面上跳。只讨论采样格的世界基底、尺度与相位，以及怎样和边界、滤波和投射者裁剪相区分。

| 直接来源 | 阅读结果 | 本文用途和限制 |
|---|---|---|
| [Microsoft，Cascaded Shadow Maps](https://learn.microsoft.com/en-us/windows/win32/dxtecharts/cascaded-shadow-maps)，Partitioning the Frustum、Computing a View Frustum Bound、Rendering the Scene、Blend Between Cascades | 按视锥深度拆分，投影适配在资源使用与稳定性间取舍，交界处过渡需两级联的结果。 | 不是本文实际运行的 CSM；模型只有一个正交深度图。 |
| [Microsoft，Common Techniques to Improve Shadow Depth Maps](https://learn.microsoft.com/en-us/windows/win32/dxtecharts/common-techniques-to-improve-shadow-depth-maps)，Calculating a Tight Projection、Calculating the Near Plane and Far Plane、Moving the Light in Texel-Sized Increments | 同一分辨率下紧贴投影的世界纹素更密；范围变化会妨碍稳定化。示例把最小/最大边界以世界单位每纹素向下对齐。仅按视锥 Z 的选择可能漏投射物。 | 取最近对齐与其示例不是同一舍入规则。接收者 XY 余量不能替代潜在投射者的 Z 范围。 |
| [Valient / Guerrilla，GDC 2009，第 36 页](https://www.guerrilla-games.com/media/News/Files/GDC09_Valient_Rendering_Technology_Of_Killzone_2.pdf#page=36)及[扩展讲者笔记](https://www.guerrilla-games.com/media/News/Files/GDC09_Valient_Rendering_Technology_Of_Killzone_2_Extended_Presenter_Notes.pdf)，Sunlight – shadow map rendering | 实际查看第 36 页，图为两种视锥朝向，外框不随相机方向旋转；正文说明球覆盖、整纹素位移和利用率代价。扩展笔记对比此前随镜头选择 UV 方向的方案。相邻页注明演讲示例修改了步长及过滤。 | 不复用其图像，不将演讲演示或正文实验当商业项目效果或同条件性能数据。 |
| [Matt Pettineo，A Sampling of Shadow Techniques](https://therealmjp.github.io/posts/shadow-maps/)，Cascade Optimization | 解释固定投影大小与纹素吸附的分工，并将稳定级联和自动收紧分段列为样例不同选项。 | FOV／长宽比／深度分段变化需再次核对；给出正交投影测试步骤，不声称已跑该样例。 |

原创推导：对正交 XY 每轴，固定世界采样中心是 a+(i+0.5)W/N；同基底、同 W/N 且 a 变整数倍纹素时，两个投影的共同内部覆盖同一世界采样格。半径 R 的接收区在最近对齐后把每轴最大中心误差 δ/2 与过滤足迹 gδ 加到覆盖约束，得 W≥2RN/(N−2g−1)；N>2g+1。这里的 g 为选定的连续每轴足迹，不等于 taps 数量；浮点、边界、轴向尺度及图集隔离须分别处理。

原创实测：[稳定级联阴影试件](../实验/稳定级联阴影/README.md)。Fraction 检查单点采样和覆盖式；另有一套 16×16 光空间矩形纹素和 384×384 固定接收探针的二维 CPU 模型（正文图来自该模型）；最后使用无窗口 Mesa llvmpipe OpenGL 实际栅格化两个三角形到浮点深度纹理，然后着色并读回固定世界探针的两类遮罩。两者观察到相同的面积变化计数，不等于对照了所有像素数据来源或测定引擎真实效果。场景没有相机重投影、真实阴影过滤、其他级联、动态投射物或硬件测量。

外部材料查阅日期：2026-11-19 UTC。
