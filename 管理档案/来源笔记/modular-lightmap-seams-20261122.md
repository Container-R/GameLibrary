# 模块墙烘焙光照接缝：来源与边界

| 主张 | 原始材料 | 边界 |
| --- | --- | --- |
| 图集中的邻岛会进入过滤取样，过小间距会串色 | Unity 6000.0 [Fix light bleeding in lightmaps](https://docs.unity3d.com/6000.0/Documentation/Manual/ProgressiveLightmapper-UVOverlap.html)，过滤、UV overlap diagnostic、边距策略。 | 数值是合成一维试件；没有给跨渲染器的硬阈值，基础 mip 与派生 mip 要分辨。 |
| 缝合针对同一对象可识别的特定图表边 | Unity 6000.0 [Smooth hard edges in lightmaps](https://docs.unity.com/en-us/engine/6000.0/manual/lighting-overview/direct-and-indirect-lighting/lightmapping/baking-before-runtime/troubleshooting/seam-stitching)，范围限制；[2020.2 对照](https://docs.unity3d.com/ru/2020.2/Manual/Lightmapping-SeamStitching.html) 未在该页说明轴对齐，不推断版本引入日期。 | Unity 仅引用文档，不把说明插图当跨物体或全场景验证。 |
| Epic 诊断视图分别提供密度与照明信息 | Epic [Understanding Lightmapping](https://dev.epicgames.com/documentation/en-us/unreal-engine/understanding-lightmapping-in-unreal-engine)，Contiguous UVs and Padding、Lightmap Density、Lighting Only。 | 不能用只看照明断定纯间接。固定四纹素来自 DXT 块语境；未实际跑 Unreal。图表重排的资产流程由旧文单独覆盖。 |
| 在固定试件中，对象切与不切可以得到同样的贴图 | Blender Foundation [4.3 Render Baking](https://docs.blender.org/manual/en/4.3/render/cycles/baking.html) 的 Influence、Margin；[复现材料](../实验/模块墙烘焙光照接缝/README.md)。 | Blender 4.3.2 Cycles CPU 直接/间接分测，只能说明指定场景，不测 Unity/Godot、运行时取样或画面可见性。 |

原始页面于 2026-11-21 调阅。
