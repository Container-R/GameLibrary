# 根运动淡化的位移：来源与验证

- Godot 4.6 官方 [AnimationMixer 文档](https://docs.godotengine.org/en/4.6/classes/class_animationmixer.html)：一个接口返回运动位置增量，另一个返回位置轨道的混合值；尊重初始键值属于有意义的特定用途。位置差分的局部坐标与旋转行为需按实际引擎契约，本文不验证旋转。
- [Godot 4.6.3 源码](https://github.com/godotengine/godot/blob/4.6.3-stable/scene/animation/animation_mixer.cpp#L1329-L1376) 的位置根轨、非 local 分支按前后采样差乘当前混合权重累入 `root_motion_cache.loc`；另一路把当前插值相对初值的贡献累入 `t->loc`；[约 1874 行](https://github.com/godotengine/godot/blob/4.6.3-stable/scene/animation/animation_mixer.cpp#L1865-L1880) 把该值给 accumulator。实际试件单轴且无旋转、回绕、时间 seek。
- Epic Games [Root Motion in Unreal Engine](https://dev.epicgames.com/documentation/en-us/unreal-engine/root-motion-in-unreal-engine) 的 Root Motion from Everything 一行：参与的启用根运动资产各自提取，再按源资产姿势权重混合。只引用流程区分，并无 Unreal 运行结果。
- [试件](../实验/根运动淡化的位移/README.md) 实际用 Godot 4.6.3 官方稳定版、AnimationTree 手动推进 0.1 秒、同步 Blend2，三种轨道起点/速度；+8 起始偏移且同速时差分 2.1 对提取 0.1，起点相同速度不同则 0.175 对 0.125，同速同起点均 0.1。实际日志 SHA256：`01596eb7b7e6fd2109383cbdf00e1fc2f9463cc9d365c6cc1676417212c43c11`。不验证角色碰撞、根空间旋转、非同步图、步态接触、网络或极端坐标量化。
