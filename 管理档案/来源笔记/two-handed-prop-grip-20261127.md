# 双手道具接触与姿势阶段：原始依据

- Godot 4.7 [SkeletonModifier3D.modification_processed](https://docs.godotengine.org/en/4.7/classes/class_skeletonmodifier3d.html#class-skeletonmodifier3d-signal-modification-processed) 与 [Skeleton3D.skeleton_updated](https://docs.godotengine.org/en/4.7/classes/class_skeleton3d.html#class-skeleton3d-signal-skeleton-updated)：分别在 modifier 与完整骨架更新点现场读取姿势。全影响排除混合因子。[固定源码的 modifier 循环](https://github.com/godotengine/godot/blob/ed1daf0bf001b61586d9930840f2f1394092c079/scene/3d/skeleton_3d.cpp#L1177-L1210)在单个 modifier 回调后才应用 influence 插值。
- [Godot 4.7.2 固定提交的骨架更新](https://github.com/godotengine/godot/blob/ed1daf0bf001b61586d9930840f2f1394092c079/scene/3d/skeleton_3d.cpp#L314-L415)：在此通知保存基姿，运行 modifier，再发最终信号、提交蒙皮并恢复。
- Epic，[Two Bone IK](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-blueprint-two-bone-ik-in-unreal-engine)，Property Reference 的 Effector Location Space 和 Take Rotation from Effector Space：位置的参照系与末端旋转设置各自需要确认。未运行 UE。
- [可复现实验](../实验/双手道具接触与姿势阶段/README.md)分开记录刚体控制和实际 Godot 回调的输出。误差向量不必同向，表格各距离不相加；试件无蒙皮与实际求解。
