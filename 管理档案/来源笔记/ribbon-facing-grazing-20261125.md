# 来源核对：带状拖尾的侧向、边标签和绕序

- [OpenGL 4.6 Core Specification](https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf)，Khronos，2022-05-05。§14.6.1 从窗口坐标的面积符号、原点选项和 FrontFace 定义朝向，CullFace 根据状态控制光栅化；§15.2.2 将 `gl_FrontFacing` 与上述面积符号连接。只用作实验与诊断术语依据，不把 OpenGL 的设置视为所有引擎默认值。
- [Parallel Transport Approach to Curve Framing](https://scholarworks.iu.edu/dspace/items/39fbe931-c2c8-43a1-9c9d-a207b92d551e)，Hanson、Ma，TR425。§3 用初始正交向量与相邻切线的旋转传递框架，§3.1 讨论闭环未回到初始方向及分摊旋角，§3.2 用框架铺带状截面、指出转角内侧仍可能相交。正文把近反向视为实际项目需要另定处理的情况，不冒充论文验证了项目算法；平行输运也与简单投影不同。
- [Trail Renderer component reference](https://docs.unity.com/en-us/engine/6000.0/manual/visual-effects/lines-trails-billboards/rendering-trails/class-trail-renderer)，Unity 6.0，Alignment。含 View、TransformZ；只引用可配置朝向，不从文档反推引擎算法。
- [原创实验与复现](../实验/拖尾网格的边标签与绕序/README.md)。固定路径和镜头，唯一干预是选择侧轴符号；加法覆盖、正反脸显示和 UV 着色分开检测。对两种空间故障的合理区分来自扫角算例与此用途不同的原始证据，而非广泛引擎对照。

核读日期：2026-11-25（北京时间）。
