# 来源笔记：预制体变体与 Radius 覆写

对应正文：[改了基础敌人的碰撞体，为什么有些预制体变体没更新](../../GameLibrary/引擎与工具/资产工具/预制体继承与覆写/改了基础敌人的碰撞体，为什么有些预制体变体没更新.md)。

| 主张与位置 | 查读的 Unity Technologies 原始资料（6000.0） | 边界 |
| --- | --- | --- |
| 变体根在 Prefab Mode 代表父 Prefab 的实例，可以看到并撤销覆写；在 Project 检查变体的来源 | [Create variations of prefabs](https://docs.unity.com/en-us/engine/6000.0/manual/working-with-gameobjects/prefabs/prefab-variants)，Prefab variant hierarchies、Edit a prefab variant | 用直接变体和同一个继承组件，不推断替换组件后身份 |
| 场景或变体上的有效覆写优先，单条操作可 Revert 或向指定层 Apply | [Override prefab instances](https://docs.unity.com/en-us/engine/6000.0/manual/working-with-gameobjects/prefabs/override/prefab-instance-overrides)，Behavior of overrides、Apply individual overrides with the context menu；[Prefab instance Inspector reference](https://docs.unity3d.com/cn/6000.0/Manual/prefab-instance-inspector-reference.html)，Overrides、Select、Open | 多目标取决于上下文；不宣称跨层 Apply 会怎样合并未举例的中间记录 |
| Radius 是局部参数，世界轮廓还受缩放；可用 Edit Collider 看几何 | [Capsule collider component reference](https://docs.unity.com/en-us/engine/6000.0/manual/physics-section/physics-overview/collision-section/collider-shapes/primitive-colliders/class-capsule-collider)，Edit Collider、Radius、Center、Height、Direction；[CapsuleCollider.radius](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityengine/capsulecollider/radius)，Description | 不推导非均匀缩放下的世界胶囊或接触距离 |
| 文本序列化中实例来源和属性修改有对应记录，可按对象引用及属性路径辅助定位 | [YAML serialization of prefabs](https://docs.unity.com/en-us/engine/6000.0/manual/working-with-scenes/text-scene-format/yaml-prefab-serialization)，Prefab instance、Property overrides | 只用于比对，不以单个命中判有效覆写，不假设固定半径序列化名称 |
| 三层测试值和撤销后由哪层决定 | 依据上述规则推导；[对照材料](../实验/预制体半径覆写/README.md) | 已执行 Python 3.12.14 标量模型，未运行 Unity 编辑器 |
