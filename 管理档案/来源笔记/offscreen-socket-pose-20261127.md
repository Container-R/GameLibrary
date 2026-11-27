# 离屏挂点姿态：来源与证据

- [正式正文](../../GameLibrary/角色动画/动画运行时/姿态更新/角色离开镜头后，道具挂点为什么还在用旧姿势.md)；[单轴试件与数据](../实验/离屏挂点的姿态时序/README.md)。
- [UE 5.5 GetSocketTransform](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/Components/USkinnedMeshComponent/GetSocketTransform?application_version=5.5)：入参可为 Socket 或骨名，世界坐标查询无匹配可退回组件世界变换。仅把这一行为应用于本文的世界空间查询。
- [UE 5.5 动画 Tick 选项](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/Components/EVisibilityBasedAnimTickOption?application_version=5.5)：`AlwaysTickPose` 在未渲染时不刷新骨骼变换，而 `AlwaysTickPoseAndRefreshBones` 在两种可见状况都刷新。文章不用它推断暂停、LOD、其他预算机制或线程条件下的行为。
- [UE 5.5 骨骼组件](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/Components/USkeletalMeshComponent?application_version=5.5) 查 `FinalizeBoneTransform`、`RegisterOnBoneTransformsFinalizedDelegate`；最终化是观测点，不代替记录新旧姿态来源。[Socket Details](https://dev.epicgames.com/documentation/en-us/unreal-engine/skeletal-mesh-sockets-in-unreal-engine?application_version=5.5) 的 Force Always Animated 针对 LOD 父链，没有提供离屏每帧刷新的保证。
- Unity 2022.3 的 [CullUpdateTransforms](https://docs.unity3d.com/2022.3/Documentation/ScriptReference/AnimatorCullingMode.CullUpdateTransforms.html)、[AlwaysAnimate](https://docs.unity3d.com/2022.3/Documentation/ScriptReference/AnimatorCullingMode.AlwaysAnimate.html) 和 [Renderer.isVisible](https://docs.unity3d.com/2022.3/Documentation/ScriptReference/Renderer-isVisible.html)：区分写回、更新策略和用于排查的可见状态；编辑器 Scene 视图和阴影是可见结果的干扰项。未以文档断言每类回调或 Animator 状态进度。
- 五组数字都来自一维合成，未使用 Unreal、Unity、真实动画线程或性能采样。生产者/消费者编号是本文的诊断办法，不是引擎字段。
