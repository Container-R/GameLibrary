# Adaptive Probe Volumes：位置、存值与探针取样

对应[文章](../../GameLibrary/图形渲染/场景光照/间接光照/墙挡住了光，为什么动态角色还是被隔壁照亮.md)和[有理数算例](../实验/探针隔墙漏光/README.md)。2026-11-28（北京时间）查阅 Unity 6.0（6000.0）URP 同版本手册，未运行 Unity 编辑器。

| 主张 | 读过的一手来源和定位 |
| --- | --- |
| 常规网格不沿墙划界、邻域混合可漏光 | [漏光排查](https://docs.unity.com/en-us/engine/6000.0/manual/lighting-overview/lighting/probevolumes/fixissues/troubleshoot-light-leaks)，开头、Rendering Layer Masks、Baking Set |
| 运行时位置偏置、Leak Reduction 选项、Intensity Multiplier 置零 | [Options Override](https://docs.unity.com/en-us/engine/6000.0/manual/lighting-overview/lighting/probevolumes/options-override-reference)，各字段 |
| Virtual Offset 移烘焙捕获点、Dilation 填补剩余无效探针；较远探针可能跨条件 | [有效性](https://docs.unity.com/en-us/engine/6000.0/manual/lighting-overview/lighting/probevolumes/fixissues/light-probe-validity)；[Lighting 面板](https://docs.unity.com/en-us/engine/6000.0/manual/lighting-overview/lighting/probevolumes/lighting-panel-reference)，Probe Invalidity Settings；[局部调整](https://docs.unity.com/en-us/engine/6000.0/manual/lighting-overview/lighting/probevolumes/adjustment-volume-component-reference)，Mode |
| 查看探针位置与数据、Debug Probe Sampling 权重 | [显示 APV](https://docs.unity.com/en-us/engine/6000.0/manual/lighting-overview/lighting/probevolumes/showandadjust)，Display Probes 和 Debug Probe Sampling |
| 竣工时有四个 APV 掩码预算、无匹配回退、层归属需要烘焙后核验 | [掩码机制](https://docs.unity.com/en-us/engine/6000.0/manual/lighting-overview/lighting/probevolumes/rendering-layer-masks-apv/prevent-light-leaks)，工作流与回退；[配置与验证](https://docs.unity.com/en-us/engine/6000.0/manual/lighting-overview/lighting/probevolumes/rendering-layer-masks-apv/configure-and-verify-probe-assignments)，实际分层与验证 |

正文算例故意固定一条漫反射通道，验证同一像素值不能逆推出存值和权重；后面的 Unity 步骤来自手册，是项目诊断方案，不是声称已复现 Unity 粒度、性能或回退。无样本与“接收者没有匹配 Baking Set 掩码”是不同条件。
