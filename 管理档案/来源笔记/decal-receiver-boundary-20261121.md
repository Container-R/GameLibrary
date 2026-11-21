# 投影贴花的接收边界：来源与证据

本记录区分引擎文档、固定实现、官方演示画面和独立几何示意。没有运行 Godot、Unity 或 Unreal 的对照场景。

| 结论及正文位置 | 一手来源与定位 | 适用范围 |
| --- | --- | --- |
| 盒限定候选表面；减薄 Y 可去掉越界接收面（“投影盒”） | Godot Engine，[Decal](https://docs.godotengine.org/en/4.7/classes/class_decal.html)，4.7，`size`、`upper_fade`、`lower_fade`。Godot 说明投影在局部尺寸定义的盒内，减小 Y 可降低误投风险。 | 淡出与盒边界应分开；薄盒仍可含多个平行接收面。 |
| 朝向、盒深与投影可见性不等价（前三节） | Godot Engine，[Forward+，固定提交 ed1daf0bf](https://github.com/godotengine/godot/blob/ed1daf0bf/servers/rendering/renderer_rd/shaders/forward_clustered/scene_forward_clustered.glsl#L1462-L1474)，接收层位交集、盒内测试、深度权重和法线淡出。正的 `normal_fade` 走平滑乘数，而不是角度硬裁。 | 该分支不从投影器沿路径找首个接收面。不能推出其他投影实现也无可见性测试。教学剖面用硬阈值只为把三项变量分开。 |
| 越平行于投射方向，映射越拉伸（“倒角处理朝向”） | Epic Games，[1.4 - Projection on Multiple Surfaces](https://dev.epicgames.com/documentation/en-us/unreal-engine/1.4---projection-on-multiple-surfaces?application_version=4.27)，Unreal Engine 4.27，示例页文字。 | 此页作为官方现象说明，不对 Epic 图片作独立观察主张。正文的 2 和约 3.86 来源于正交投影剖面推导，不是引擎测量。 |
| 平行道具可通过不同接收层排除（“倒角处理朝向”） | Godot Engine，[Decal](https://docs.godotengine.org/en/4.7/classes/class_decal.html)，4.7，`cull_mask` 与类说明（Forward+、Mobile、Mobile 每 mesh resource 的可见数量及 AABB 条件）。Unity Technologies，[Rendering Layers](https://docs.unity3d.com/kr/Packages/com.unity.render-pipelines.universal@15.0/manual/features/rendering-layers.html)，15.0.4，Enable Rendering Layers for Decals、How to use Rendering Layers with Decals。 | Unity 对照图经实际查看：只移除桶的接收位后，桶盖、桶身的橙色消失，墙和地面标记保留。并非实时运行验证、性能测试或其他版本承诺。 |
| 剖面中，薄盒之后剩下的倒角可由朝向区分，平行箱盖仍须接收位（“逐项排查”） | [原创剖面脚本、图与坐标](../实验/投影贴花的接收边界/README.md)。 | 脚本用线段、盒、独立单位法线和位标识，没有真实渲染管线、混合或逐像素验证。 |

文档调阅日期：2026-11-21。没有转载官方示例图。
