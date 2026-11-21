# 动态分辨率与帧时间：来源、推导和观测

| 主张 | 一手证据或实验定位 | 边界 |
| --- | --- | --- |
| 动态分辨率能改变实际渲染范围但不必重分配 | [Unity 6000.3 Introduction to Dynamic Resolution](https://docs.unity.com/en-us/engine/6000.3/manual/cameras/resolution-scale/dynamic-resolution/introduction)，Impact on render targets。 | 该文档列满尺寸分配和子范围使用。并非所有管线、相机和渲染步骤都跟比例。本文的 OpenGL 对照实际改变附件和视口，本意不是复现 Unity 的分配策略。 |
| 一步随内部比例减少覆盖量，另一步保持固定输出 | [原始脚本和输出](../实验/动态分辨率与帧时间/README.md)，OpenGL 两次执行。Khronos [OpenGL 4.5 Core Specification](https://registry.khronos.org/OpenGL/specs/gl/glspec45.core.pdf) §17.3.5（印刷页 485），Occlusion Queries。 | 量的是通过的样本数；单采样，无深度/模板遮挡。不是像素着色器调用统计、全帧开销或硬件性能。 |
| CPU 时间、GPU 时间、帧提交/显示不是单一数字 | [Unity 6000.0 Frame Timing Manager](https://docs.unity.com/en-us/engine/6000.0/manual/analysis/graphics-performance-profiling/profile-rendering/frame-timing-manager/manager)，计时可用性、TBDR 示意与 Timing results；[Microsoft PIX 新 Timing Captures](https://devblogs.microsoft.com/pix/timing-captures-new/) 和 [GPU Captures](https://devblogs.microsoft.com/pix/gpu-captures/)，Timing。 | GPU Capture 重放不能表征现场跨队列重叠。合成并集只用于说明重复相加，不能代替等待和依赖识别。 |
| 比例要配计时所属帧 | [Unity 6000.0 FrameTiming](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/FrameTiming.html)，frameStartTimestamp/widthScale/heightScale；[Frame Timing Manager](https://docs.unity.com/en-us/engine/6000.0/manual/analysis/graphics-performance-profiling/profile-rendering/frame-timing-manager/manager)，Result delay。 | 文档所述四帧结果延迟不保证结果有效。Node 脚本只建模固定延迟与错配，不是引擎实现。 |
| 固定比例达标与动态控制响应是不同问题 | [Epic Unreal 5.9 Dynamic Resolution](https://dev.epicgames.com/documentation/unreal-engine/dynamic-resolution-in-unreal-engine?lang=en-US)，历史、预算、快速下调及异步；[5.9 Console Variables Reference](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-console-variables-reference)，DynamicRes。 | 共享带宽只是特殊条件；CPU-bound 目标比例和预算策略须看构建实际配置。正文不为读者预设单一阈值。 |

文档调阅日期：2026-11-21。三种帧间隔的数值来自理想稳定流水线 `max(CPU, GPU)` 和给定线性像素项，不是上述文档报告的性能。
