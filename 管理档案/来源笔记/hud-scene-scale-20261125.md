# 来源核对：HUD 合成与场景缩放

- [Unreal Engine 5.9 Scalability Reference](https://dev.epicgames.com/documentation/en-us/unreal-engine/scalability-reference-for-unreal-engine)，Resolution Scale。文档区分通常不受该场景比例处理的 2D UI 与被缩放的场景。文章不将范围写成任意 3D widget、材质或自定义组合都免受缩放。
- [Screen Percentage with Temporal Upscale](https://dev.epicgames.com/documentation/en-us/unreal-engine/screen-percentage-with-temporal-upscale-in-unreal-engine)，Primary 说明先进行场景比例缩放再绘制 UI；Secondary 指能独立配置另一个空间放大阶段。这里据此要求核实后续实际呈现链，不推断每种视口插件顺序。
- [Godot 4.7 Multiple resolutions](https://docs.godotengine.org/en/4.7/tutorials/rendering/multiple_resolutions.html)，3D resolution scaling 与 Stretch settings。根 Viewport 模式先在基础尺寸绘制再拉伸；Canvas Items 模式直接在目标尺寸渲染，但逻辑单位到像素仍可不一一对应；分开的 3D scale 可不降低 2D。本文未运行这些引擎路径。
- [OpenGL 4.6 Core Specification](https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf)，§18.3.1，`BlitFramebuffer` 不同尺寸的颜色矩形与线性过滤。精确列值和相位同一性来自实际 OpenGL 读回，不是所有过滤器的通用保证。
- [可复现实验](../实验/HUD与场景缩放的合成顺序/README.md)。解析一维与 OpenGL 二维证据分别核对；后者固定输出、源背景、施加的缩放与 HUD 逻辑位置，只改变 HUD 写入时机。图与日志不代表文字排版、色彩空间变换、物理屏幕或某一游戏的生产实现。

核读日期：2026-11-25（北京时间）。
