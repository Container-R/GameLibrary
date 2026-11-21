# 导航跨越的落地交接：来源与范围

| 正文主张 | 一手来源及定位 | 证据范围 |
| --- | --- | --- |
| 有近点不代表有正确楼层或无障碍回接 | [Unity 6000.0 NavMesh.SamplePosition](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityengine/ai/navmesh/sampleposition#remarks)，Remarks；[Godot 4.6 NavigationServer3D](https://docs.godotengine.org/en/4.6/classes/class_navigationserver3d.html#class-navigationserver3d-method-map-get-closest-point-owner)，返回最近点的区域。 | Unity 先沿网格所用垂直轴投影，再考虑邻近查询；文档明确不查阻隔。Godot 区域 RID 不暗含楼层、有效步行路线或物理支撑。两项均不能替代接回步骤。 |
| 关闭自动跨越后的完成及取消边界 | [Unity 6000.0 CompleteOffMeshLink](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityengine/ai/navmeshagent/completeoffmeshlink#remarks)，Remarks 与 Examples；[ResetPath](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityengine/ai/navmeshagent/resetpath#remarks)，Remarks。 | Complete 仅在当前链接生效，移动至另一端最近有效的导航位置；ResetPath 如正在链接上会立即完成。两者不检测角色本体着地。草案关于同连接、方向和对齐的查验是工程建议，不是 API 参数。 |
| 导航与物理位置可能不同 | [Unity 6000.0 nextPosition](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityengine/ai/navmeshagent/nextposition#remarks)，Remarks。 | 重新开启 updatePosition 会立即同步 Transform 到 nextPosition；不同物理控制器的实际整合未执行。 |
| Godot 链接入口与着地不是同一信号 | [Godot 4.6 使用导航链接](https://docs.godotengine.org/en/4.6/tutorials/navigation/navigation_using_navigationlinks.html)、[NavigationAgent3D](https://docs.godotengine.org/en/4.6/classes/class_navigationagent3d.html)，类说明及 link_reached；[CharacterBody3D](https://docs.godotengine.org/en/4.6/classes/class_characterbody3d.html#class-characterbody3d-method-is-on-floor)，is_on_floor。 | 路径关系与实际移动分开；入口/出口来自配置的元数据与正确 owner，不是完成通知。接地状态来自上一次 move_and_slide，与 up_direction、floor_max_angle 有关，不提供支撑身份。 |
| 分开验证物理支撑与接回候选能识别两类误判 | [合成模型与复现](../实验/导航跨越的落地交接/README.md)。 | 脚点/支撑身份及候选点均由试件指定，没有真实运动、烘焙或寻路引擎。沿途可走是正文另要求的条件，不是该点模型的输出。 |

文档调阅日期：2026-11-21。
