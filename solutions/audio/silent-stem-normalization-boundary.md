---
id: SOL-SFX-002
title: 离线 stem 混音：零值输入结束，为何可能改变另一轨增益
type: solution
status: source-backed
primary_discipline: SFX
related_disciplines: [MUSIC, TA, ENGINE, QA]
related_roles: [interactive-audio-designer, composer, audio-programmer, tools-programmer]
related_topics: [offline-mixing, stem-lifetime, normalization, asset-handoff]
engines: [engine-agnostic-offline-tool]
platforms: [Linux-observed-only]
versions: ["FFmpeg comparison source 3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587", "installed FFmpeg 7.1.5-0+deb13u1 self-report; selected executable/library hashes, not authenticated release provenance"]
updated_at: 2026-11-01
verification_method: 固定官方源码核对；原创有限离线混音及独立复跑的完整字节对照；不含中间件、播放设备或听感验证
sources:
  - https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/doc/filters.texi
  - https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/libavfilter/af_amix.c
  - https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/libavfilter/avfilter.c
  - https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/libavfilter/af_asetnsamples.c
---

# 离线 stem 混音：零值输入结束，为何可能改变另一轨增益

## 工程问题：没有贡献样本值，不等于没有参与增益计算

为游戏音乐制作分轨预览或离线导出时，团队可能只交付每条 stem 的样本与权重，默认某条轨道的尾部全为零，因此“保留零值尾部”与“提前结束该输入”完全等价。这一假设忽略了混音器是否根据**仍参与混音的输入集合**调整增益。

本文只讨论 FFmpeg `amix` 的一个有限离线配置。它不是 FMOD/Wwise 总线行为、实时动态音乐调度或真实制作事故复盘。这里的 normalize 是输入缩放策略，不是测量 LUFS、自动匹配主观响度或证明听起来更好。

## 原理：内容、存活范围与归一化是不同输入

固定比较源码的 `calculate_scales` 根据活跃输入和权重设置缩放；全零样本不会自行取消输入的活跃标志。等权两输入与等权单输入的分母不同。`activate` 又将 EOF 与内部 FIFO 清空分开处理：读到结束状态，不等于还缓存在队列中的样本已经被混完。[S1][S2]

因此，比较输入是否相同，至少要分别检查：数值内容、输入长度/结束方式、权重、是否归一化、退出时的过渡策略。把两条轨道音量旋钮都设为 1，不能单独确定最终波形。本文的 `dropout_transition=0` 是为了隔离变化原因的诊断设置，不是推荐生产混音都瞬间跳变。

## 原创有限实验设计

没有使用商业音乐、用户素材或录音。输入是 48 kHz、单声道、无头小端 float32 数值数组：A 有 4096 帧，每帧 +0.5；B 全部为 +0，分别取 4096 或 2048 帧。这里 PCM 帧是一组声道样本，与 FFmpeg 的 AVFrame 数据块不是一个概念。

两输入都显式使用 `asetnsamples=n=256:p=0`，避免把默认解复用包大小当成已知边界。长度均整除 256；权重为 `1 1`，结束策略为 `longest`，退出过渡为 0。冻结前读取固定块、链接 EOF 与混音 FIFO 的源码，提出完整字节判据，而不是看结果再挪动分界或排除附近样本。

实际作者与独立复跑均得到下表。每行是同一冻结配置在两个新目录各运行一次；没有按实际输出调整帧边界或容差。

| 配置 | B 长度 / normalize | 输出 `[0,2048)` | 输出 `[2048,4096)` |
|---|---|---|---|
| full-normalized | 4096 / 1 | 每帧 +0.25 | 每帧 +0.25 |
| short-normalized | 2048 / 1 | 每帧 +0.25 | 每帧 +0.5 |
| short-unscaled | 2048 / 0 | 每帧 +0.5 | 每帧 +0.5 |

每个输出恰好 4096 帧、16384 字节，全部样本有限且与预先冻结的完整字节序列一致。合计 **6 个混音进程与 2 个版本查询**，重复同样三种配置，不是六种测试场景；全部正常退出。独立检查器不导入作者波形判据，依据先于代码冻结的字面分段与摘要验收作者和复跑档案。

安装程序自报 `7.1.5-0+deb13u1`；历史记录称所选可执行文件与 libavfilter 文件的摘要在执行前后分别保持相同。本公开衍生正文省略这两个安装指纹值；该历史核对没有在本轮重新执行或认证。原始输入/输出以可逆十六进制逐字节保存，而非只保留峰值或均值。该结果是固定工具的离线数值事实，不说明声音被播放过。

执行前审查修正两项取证缺口：失败路径需要保存可用的后置摘要与部分输出；消费者还需拒绝不满足 UTC 契约的时间字段。初始纯合成反例、修正与复核保留，不记为 FFmpeg 失败。最终纯 Python 七方法套件分别由作者与审查者普通/优化各跑一次；另外的独立检查器合成控制及八项拒绝探针也不算混音场景。

## 交付时怎样避免“同素材、不同预览”

以下是根据机制提出的工作流程，不是已经验证有效的工作室规范：

1. **记录混音拓扑与时间范围。** 除素材身份和 PCM 坐标系，还要写明哪些输入参与、何时结束、是否有补零/截断。零值尾部是否保留应是明确选择。
2. **记录增益政策。** 权重、归一化、退出过渡、输出格式和版本共同进入预览/导出记录；不要仅交付“各轨音量为 1”。
3. **区分两种验收。** 一种是给定输入/参数的数值一致性，另一种是音乐设计、响度和听感是否合适。前者通过不能替后者签收。
4. **变更后重验相关组合。** 若某 stem 被裁短，至少重新生成受影响的预览并检查其他轨是否被连带缩放；没有必要把所有参数排列穷举成同一种测试。

| 选择 | 可以解决的问题 | 必须另行考虑的代价 |
|---|---|---|
| 保持一致的输入参与范围 | 避免预览之间无意切换活跃输入集合 | 是否仍符合实际素材/导出政策；本实验不测文件大小与制作效率 |
| 明确使用归一化及退出过渡 | 把自动缩放作为有意设计 | 退出输入可能改变其他轨增益；过渡的音乐效果需要听音/设计验收 |
| 诊断时关闭归一化 | 将输入集合与自动缩放的影响分离 | 求和后的余量、限幅、溢出和输出格式必须另外评估，不能当通用修复 |

## 证据边界与维护

该有限数值数组不证明音乐无爆音、无削波、响度合适、不同平台逐位一致或实时播放采样级同步。没有测试负权重、变权重、非零退出过渡、异采样率、重采样、多声道、其他浮点实现、任意 EOF 排列或并行实时输入。

固定源码与安装程序身份分列；文件摘要不是完整动态依赖来源认证。源码中的零退出过渡通过浮点表达式参与计算，并非独立整数规则，所以协议预先规定任意非有限值或不同字节都失败，不以放宽容差修正结果。发生工具、参数或输入寿命变更时，应在新的独立目录运行明确修订的协议，不能覆盖旧取证。

## 关联与来源

- [音乐状态交接](music-state-transition-contract.md)研究玩法意图、提交和观察，已有假端口模型不验证真实混音。本条也不替它补出中间件调度结论。
- [PCM 循环与编码帧数](../music/pcm-loop-frame-contract.md)处理区间与呈现长度，不说明多输入增益政策；帧数相同仍可能是不同波形。
- [交互音频岗位](../../管理档案/历史正文/roles/audio/interactive-audio-designer.md)需要将数值/集成验收与创作判断分别交付。
- [实验归档](../../research/experiments/ffmpeg-silent-stem/README.md)和[来源定位](../../research/source-notes/silent-stem-normalization.md)记录精确版本、协议、原始字节、复核与未测范围。

**S1** 固定 `doc/filters.texi` 的 amix/asetnsamples 小节。**S2** 固定 `af_amix.c` 的缩放/输出/激活函数；队列与固定块行为分别回查 `avfilter.c` 和 `af_asetnsamples.c`。访问日期 2026-11-01；未复制第三方完整源码或执行第三方素材。
