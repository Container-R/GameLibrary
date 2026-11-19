# 硬切曝光：来源及适用范围

问题：切镜后 first-frame 亮度来自历史初始化、过期测光还是 scene-color 比例。区分当前目标与实际增益；区分缓冲写入比例与本帧显示所需乘数。主体不描述完整光度模型、摄像机色彩风格或亮度风险阈值。

| 一手来源 | 已核对的内容 | 本文采用与限制 |
|---|---|---|
| [Epic Auto Exposure](https://dev.epicgames.com/documentation/unreal-engine/auto-exposure-in-unreal-engine)，Unreal 5.9，Exposure Change Speed and Movement、Pre-Exposure、HDR (Eye Adaptation) | 目标与当前曝光可从调试面板分开；适应速度用每秒档数，含分段线性与指数；其预曝光使用前帧场景曝光写入以缩小数值范围。 | 不把试件的固定步迟到队列或线性速度说成 Unreal 行为；不从 Camera Cut API 名称推定任何产品版本如何重置全部历史。 |
| Unity HDRP 17.0.4，[Exposure override reference](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.0/manual/reference-override-exposure.html)、[Debug exposure](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.0/manual/test-debug-exposure.html)，Automatic／Histogram View | 自动曝光支持 Progressive 与 Instant（适应模式名为 Fixed），调试图能够区分直方图包含的像素范围、目标/当前曝光和最后显示直方图。 | 仅观察说明，不假设 Unity 摄像机重置策略、速度单位或 E/P 实现与 Epic 相同。 |
| [Google Filament](https://google.github.io/filament/main/filament.html)，§5.2.6 Pre-exposed lights、§8.1.3 Exposure | 半精度的动态范围是预曝光动机之一。文档区分在着色后乘比例和在照明运算前预缩放光。相机显示增益由曝光参数导出，不等于 EV100 本身。 | 本文 e=log₂(最终增益)，不采用摄影符号约定；不冒称实际两个引擎的所有色缓冲都能随意更换编码比例。 |

原创推导：对某环节若约定 C=P·L，欲得 E·L 就用 C·E/P；欲与新比例的另一场景缓冲比较可换成 C·P_new/P_old。只在已知比例及仍可恢复的线性区成立。剪切后的适应策略、标记世代和来源帧的做法是工程约定，不是源文档指令。

[实测材料](../实验/切镜曝光/README.md)：Python 人为安排新旧测光到达，并生成原创轨迹，实际查看 PNG。Mesa 软件 OpenGL 原生两遍独立验证：两种 pre-scale 写入真实 RGBA16F，再读取并写入 RGBA32F；正确的结果一致，漏除 pre-scale 后分别多 3 档、少 4 档。固定线性输入，无 histogram 或相机动画、色调映射或设备感知。查阅时间 2026-11-19 UTC。
