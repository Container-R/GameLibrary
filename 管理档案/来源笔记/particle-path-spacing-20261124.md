# 粒子距离发射的路径采样：来源记录

访问日期：2026-11-23。

- Unity Technologies，[Emission module reference（Unity 6.3）](https://docs.unity.com/en-us/engine/6000.3/manual/visual-effects/particle-systems/particle-system-modules/part-sys-emission-module)，Rate over Distance 一行说明每移动单位发出的数量。不能据此推出中间采样点或粒子出生坐标、出生年龄的实现。
- Epic Games，[Emitter Update Group（Unreal Engine 5.9）](https://dev.epicgames.com/documentation/en-us/unreal-engine/emitter-update-group-reference-for-niagara-effects-in-unreal-engine#spawning-modules)，Spawning Modules 中 Spawn Per Unit 区别于 Spawn Per Frame 和 Spawn Rate，同样只用于支撑按距离发射的接口语义。
- [Pillow 几何试件](../实验/粒子距离发射与路径采样/README.md)是本文的独立实现与位置观察，不外推引擎的内置模块或特效结果。
