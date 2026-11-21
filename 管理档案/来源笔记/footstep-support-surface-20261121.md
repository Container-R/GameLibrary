# 脚步音的支持面与标签：来源及验证

| 主张 | 原始证据 | 适用条件 |
| --- | --- | --- |
| 地形层权重不自动决定声音 | Unity 6000.0 [TerrainData.GetAlphamaps](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityengine/terraindata/getalphamaps)，数组和示例。 | API 返回的是纹理层权重；支持物优先和映射到音频标签是项目设计。 |
| 形状槽与面索引不同；Jolt 默认可能无可用面号 | Godot 4.6 [射线结果](https://docs.godotengine.org/en/4.6/classes/class_physicsdirectspacestate3d.html#class-physicsdirectspacestate3d-method-intersect-ray)、[Jolt Face Index](https://docs.godotengine.org/en/4.6/tutorials/physics/using_jolt_physics.html#ray-cast-face-index) 和 [固定实现](https://github.com/godotengine/godot/blob/4.6-stable/modules/jolt_physics/spaces/jolt_physics_direct_space_state_3d.cpp#L362-L375)。 | 开关内存代价用于 Jolt 的凹形形状，不等于所有资源。另于 4.7.2 Jolt 实际复跑同网格开关、平移和 Area。 |
| Unreal 的返回物理材质、返回面号互相独立，实际碰形由资产复杂度参与决定 | Epic [FCollisionQueryParams 5.8](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/FCollisionQueryParams?application_version=5.8) 的 bReturnFaceIndex/bReturnPhysicalMaterial 和 [Simple versus Complex Collision](https://dev.epicgames.com/documentation/unreal-engine/simple-versus-complex-collision-in-unreal-engine?lang=en-US)，资产选项表。 | [Physical Materials User Guide 5.9](https://dev.epicgames.com/documentation/unreal-engine/physical-materials-user-guide-for-unreal-engine?lang=en-US) 与 [5.7](https://dev.epicgames.com/documentation/en-us/unreal-engine/physical-materials-user-guide-for-unreal-engine?application_version=5.7) 各自的复杂碰形表和覆盖末段不一致。未运行固定 Unreal 编辑器矩阵，不给 actor override 的复杂查询结论；Physics Asset 与 Static Mesh 单独验证。 |
| 游戏的命中或物理表面可驱动音频选择 | Epic，[Shooter Game 样例音频文章](https://www.unrealengine.com/tech-blog/redesigning-audio-in-unreal-engine-s-shooter-game-sample-project)，Footsteps 部分。 | 只作交接案例，不证明逐脚接触求解、任意版本物理材质或最终听感。 |
| 同形状可含不同表面；局部图随资产保持 | [合成几何与原生射线记录](../实验/脚步音的支持面与标签/README.md)。 | 合成对照查面号/局部区；原生只查实际射线。没有采集步态碰撞力、音频文件或播放事件。 |

调阅日期：2026-11-21。
