# 来源核对：角色变形的帧调试

- RenderDoc v1.44，[Quick Start](https://github.com/baldurk/renderdoc/blob/v1.44/docs/getting_started/quick_start.rst)，Event Browser、Pipeline State、Mesh Viewer。当前事件决定检查的图形状态；事件列表的编号和顺序属于该捕获；可查看绑定资源、着色器、缓冲及几何数据。本文用应用侧身份对齐跨捕获 draw，是调试建议，不是 RenderDoc 自动关联功能。
- RenderDoc v1.44，[Mesh Viewer](https://github.com/baldurk/renderdoc/blob/v1.44/docs/window/mesh_viewer.rst)，开头及投影设置。文档列出输入/输出阶段、实例控制、细分情况下的阶段区别；光栅器前输出的三维预览依赖投影估计，该估计有近远平面、视场和正交限制。数值诊断采用实际着色器的空间约定。
- RenderDoc v1.44，[Resource Inspector](https://github.com/baldurk/renderdoc/blob/v1.44/docs/window/resource_inspector.rst)，Usage in Frame。可用记录列出部分缓冲/纹理在捕获中的使用类型及 EID 范围。无可见写入不排除此前帧或 CPU 生产；不是 CPU 动画图的跟踪器。
- Unity 6.0，[PlayerSettings.meshDeformation](https://docs.unity3d.com/cn/6000.0/ScriptReference/PlayerSettings-meshDeformation.html)，Description。CPU 与 compute（单独或批量）的实现实例。并非本文实验使用的引擎，不能据此推断任意项目的缓冲布局或每一步事件。
- RenderDoc v1.44，[In-application API](https://github.com/baldurk/renderdoc/blob/v1.44/docs/in_application_api.rst#L413-L418)，`TriggerMultiFrameCapture`。下一批呈现帧独立捕获、分别保存；这里没有断言应用内手动捕获 API 也只能跨一次呈现。
- Khronos Group，[glTF 2.0 §3.11 Animations](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#animations)。采样器、通道、键值和插值不会规定播放时机和循环等应用行为。这个例子用于区分资产与运行时逻辑，不把它推广给所有格式。
- [原始对照](../实验/单帧姿势与动画轨迹/README.md)：Mesa OpenGL，单关节在 VS 旋转线段，变换反馈读取顶点并逐像素比颜色。相等帧不向着色器传入上帧或角速度；原始脚本与输出核对了非空画面、浮点坐标及中心/相邻帧的差异。不能用此实验认证某个 RenderDoc UI 操作、引擎或物理 GPU。

核读：2026-11-25（北京时间）。
