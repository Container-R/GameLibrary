# 来源笔记：Unity 6.0 蒙皮范围与动画可见性

对应正文：[蒙皮角色在镜头边缘消失，先查姿态还是包围盒](../../GameLibrary/角色动画/角色变形/蒙皮/蒙皮角色在镜头边缘消失，先查姿态还是包围盒.md)。

| 主张 | 已读的 Unity 6000.0 原始资料 | 适用条件 |
| --- | --- | --- |
| 蒙皮部件用预计算范围判是否离屏；根骨关联范围；Update When Offscreen 更新离屏蒙皮且逐帧重算 | [Skinned Mesh Renderer component reference](https://docs.unity.com/en-us/engine/6000.0/manual/assets-and-media/asset-types/mesh/components-reference/class-skinned-mesh-renderer)，Properties：Bounds、Update When Offscreen、Root bone | 只用于 Skinned Mesh Renderer，不把 MeshRenderer 和 Animator 的行为混入 |
| 自定义 localBounds 的空间、运行时赋值、不随场景 Prefab 保存及 ResetLocalBounds | [Renderer.localBounds](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityengine/renderer/localbounds)，Description | 针对脚本自定义覆盖；不由此推论 Inspector 导入配置的序列化 |
| Animator 的三种可见策略不是同一个开关 | [AnimatorCullingMode](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityengine/animatorcullingmode)，Properties | 不推断所有回调、播放时钟和动画层级的可见判定拓扑 |
| Renderer.isVisible 并不等同目标相机色彩通道的提交 | [Renderer.isVisible](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Renderer-isVisible.html)，Description | Scene 相机和阴影也可能影响该值；检查同一个目标视图 |
| BakeMesh 可计算离屏 CPU 快照，顶点相对 Renderer Transform、受缩放选项影响 | [SkinnedMeshRenderer.BakeMesh](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityengine/skinnedmeshrenderer/bakemesh)，Description 与 useScale | 使用当前骨姿；避免把 CPU 蒙皮等同着色器顶点变形。复杂层级复核实际坐标 |
| 停用旧盒或换骨姿的两个独立对照，角度采样之间的极值 | [单骨几何试件](../实验/蒙皮角色的剔除包围盒/README.md)，Python 3.12.14 | 只验证几何相交与姿态输入的因果区别；不验证 Unity 运行时 |
