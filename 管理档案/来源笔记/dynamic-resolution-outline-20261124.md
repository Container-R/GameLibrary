# 动态分辨率描边：来源记录

访问日期：2026-11-23。

| 主张 | 来源与定位 | 条件 |
| --- | --- | --- |
| 视口有效区可能小于已分配纹理，常规 clamp 不限制部分视口 | Unity Technologies，[Using the RTHandle system，Core RP 14.0](https://docs.unity.cn/Packages/com.unity.render-pipelines.core@14.0/manual/rthandle-system-using.html)，Using RTHandles in shaders | Unity 示例的部分视口原点是 (0,0)；本文一般式可含非零原点，偏移公式是独立推导，不暗示使用 Unity 接口创建了此偏移。 |
| TSR 后某些后处理位置的 View Property 仍给 TSR 前大小；PostProcessInput0 SceneTexture 的 Size/InvSize 给对应尺度 | Epic Games，[Temporal Upscalers，页面显示 UE 5.9](https://dev.epicgames.com/documentation/en-us/unreal-engine/temporal-upscalers-in-unreal-engine#post-process-materials-after-tsr)，Post Process Materials After TSR | 只对所述位置与颜色输入用法，不推断深度、法线、ID 的大小或坐标可直接共用。 |
| 栅格图比较固定、取整及分数半径，附覆盖和越界对照 | [Python/Pillow 试件](../实验/动态分辨率描边/README.md) | 只改变横轴分辨率，固定阶跃边与空间重采样。没有 GPU、历史、TSR、斜边或玩家可读性试验。 |
