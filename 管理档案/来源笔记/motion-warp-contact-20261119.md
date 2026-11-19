# 越障接触约束：来源与试件

- Epic Games，[Motion Warping](https://dev.epicgames.com/documentation/en-us/unreal-engine/motion-warping-in-unreal-engine)，页面当次标注 UE 5.9，Animation Montage / Details / Blueprint：窗口起止、攀越手接触提示、Skew Warp 末端对齐、平移与旋转开关及 Static/Bone 提供方式。未查私有引擎源码；没有从文档推导每个配置的实际求值顺序。
- Epic Games，[Root Motion](https://dev.epicgames.com/documentation/en-us/unreal-engine/root-motion-in-unreal-engine)，UE 5.9 Overview、启用节：提取的根运动可以驱动角色；骨架与胶囊分开。
- Epic Games，[UMovementComponent](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/UMovementComponent?application_version=5.8)，UE 5.8 API，说明 swept movement 按 UpdatedComponent 的碰撞处理。作为接口例，不据此断言任意控制器都用同一函数。
- Epic Games，[FMotionWarpingTarget](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Plugins/MotionWarping/FMotionWarpingTarget)，该次读取标注 UE 5.8，Variables: bFollowComponent / Component / BoneName：组件或骨骼目标可在扭曲期间更新。不是支撑全程手掌锁定。
- 已出版 [FFXV 后续片段组织](../../GameLibrary/角色动画/动画运行时/动作选择/FFXV如何组织越障动画的后续片段.md) 只用于划分上游片段与本篇对齐职责；不据此补写 FFXV 的求解细节。

两个原创小试件、运行命令和逐字输出见 [越障接触约束](../实验/越障接触约束/README.md)。第一组展示相同的正确末端不足以断言较早的接触点正确；第二组展示冻结世界点/只跟平移不能跟随整个位姿。未运行引擎或真实动画，不做 Unreal 按帧行为、接触画质、性能或碰撞安全承诺。
