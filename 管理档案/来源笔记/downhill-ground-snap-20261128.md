# 缓坡贴地与起跳：证据记录

[正文](../../GameLibrary/玩法程序/玩法系统/角色移动/角色沿缓坡下跑，为什么会短暂离地.md) · [实测](../实验/缓坡贴地与起跳/README.md)。2026-11-28（北京时间）。

| 主张 | 一手来源与范围 |
| --- | --- |
| Godot 自动贴地使用上一次有支撑、当前没有支撑和不朝上的门槛 | [4.7.2 固定角色源码，138、270、378–405](https://github.com/godotengine/godot/blob/ed1daf0bf001b61586d9930840f2f1394092c079/scene/2d/physics/character_body_2d.cpp)；限普通贴地路径，不扩展到特殊墙体或平台分支 |
| 手动贴地进入内部扫掠、预算至少等于 margin、命中还要有合格法线 | [同版源码 337–375](https://github.com/godotengine/godot/blob/ed1daf0bf001b61586d9930840f2f1394092c079/scene/2d/physics/character_body_2d.cpp#L337-L375) 与 [API XML](https://github.com/godotengine/godot/blob/ed1daf0bf001b61586d9930840f2f1394092c079/doc/classes/CharacterBody2D.xml) |
| 手动贴地之后两种读数对应位置和早先缓存 | [位置与缓存更新](https://github.com/godotengine/godot/blob/ed1daf0bf001b61586d9930840f2f1394092c079/scene/2d/physics/character_body_2d.cpp#L43-L105)、[两个 getter](https://github.com/godotengine/godot/blob/ed1daf0bf001b61586d9930840f2f1394092c079/scene/2d/physics/character_body_2d.cpp#L491-L497)，并由原生一物理步对照确认 |
| 跨引擎如何找观测点 | Unity 2022.3 [isGrounded](https://docs.unity3d.com/2022.3/Documentation/ScriptReference/CharacterController-isGrounded.html) 定义为最近一次移动的接触；Epic 5.5 [ComputeFloorDist](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/GameFramework/UCharacterMovementComponent/ComputeFloorDist?application_version=5.5) 的 LineDistance 参数只在 sweep 未获可走地面时使用；未运行二者 |

正文 30/60/120 Hz 的理论数来自水平一步乘 1/4，不替代试件的形状扫掠。实测没有模拟动画事件或整次跳跃；“假落地”是下游若基于不恰当阶段的地面标志产生事件的风险，不是引擎自己播放了动画。
