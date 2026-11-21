# 粒子跳变的来源与验证记录

核对日期：2026-11-21。固定版本资料用于 API 契约；不以模型预测特定引擎的粒子数量或画面。

| 主张 | 一手出处与准确定位 | 范围 |
| --- | --- | --- |
| 传送时可以在目标变换设置之后重置节点的物理插值历史 | [Godot 4.7：Using physics interpolation](https://docs.godotengine.org/en/4.7/tutorials/physics/interpolation/using_physics_interpolation.html#call-reset-physics-interpolation-when-teleporting-objects)，传送章节与设位置后调用的代码示例 | 节点插值，不涉及距离发射器或拖尾段 |
| 粒子可按发射器移动距离发射 | [Unity 6.0：Emission module](https://docs.unity3d.com/en-us/engine/6000.0/manual/visual-effects/particle-systems/particle-system-modules/part-sys-emission-module)，Rate over Distance | 只用于区分采样机制，未实测 Unity 传送时的采样策略 |
| 拖尾顶点可以独立于粒子模拟空间保存为世界坐标 | [Unity 6.0：TrailModule.worldSpace](https://docs.unity3d.com/en-us/engine/6000.0/script-reference/unityengine/particlesystem/trailmodule/worldspace)，Description | 坐标空间与是否连接不同；分段是文章的实现建议 |
| 局部坐标随节点，`finished` 仅在一次性发射下触发 | Godot 4.7.2 [CPUParticles2D](https://github.com/godotengine/godot/blob/ed1daf0bf/doc/classes/CPUParticles2D.xml)、[GPUParticles2D](https://github.com/godotengine/godot/blob/ed1daf0bf/doc/classes/GPUParticles2D.xml)，`local_coords`、`finished` | 不据此承诺其他粒子模块的信号或可见状态 |

[复现实验](../实验/粒子传送与历史重置/README.md)验证固定规则下位置、发射点、拖尾边和发射余量的计算。Godot 4.7.2 的无显示 API 冒烟执行到实例的属性与停止、移动、重启操作，未获取原生粒子位置或像素，不作正文结论的依据。
