---
id: SOL-MUSIC-001
title: 音乐循环素材交接：用 PCM 帧区间表达主体，不混淆文件尾部与循环终点
type: solution
status: source-backed
primary_discipline: MUSIC
related_disciplines: [SFX, PROG, TA, QA]
related_roles: [composer, interactive-audio-designer, audio-programmer, qa-engineer]
related_topics: [music-loops, sample-frames, pcm, tempo, audio-asset-handoff]
engines: []
versions: ["FMOD 2.04 documentation only", "FFmpeg 7.1.5-0+deb13u1 local runtime", "Python 3.12.14"]
platforms: [offline-pcm-processing]
updated_at: 2026-10-31
verification_method: 官方端点文档核对；原创 PCM WAV 的两次实际 FFmpeg 裁剪、完整 PCM 字节验证与独立复跑；不含 FMOD 或设备播放
sources:
  - https://www.fmod.com/docs/2.04/api/core-api-sound.html#setlooppoints
  - https://www.fmod.com/docs/2.04/api/core-api-common.html#fmod_timeunit
  - https://www.fmod.com/docs/2.04/studio/glossary.html#tempo-marker
  - https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/doc/filters.texi#L3773-L3822
---

# 音乐循环素材交接：用 PCM 帧区间表达主体，不混淆文件尾部与循环终点

## 问题：同一个结束数字，不一定指同一段声音

作曲交付一份带前置留量和尾部的音频，音乐主体是一小节。音频程序拿到“循环到第 94138 个采样点”，却不知道这个数字是最后一个保留位置，还是第一个排除位置。素材能加载、时长看起来正确，仍可能少一帧，或把尾部的第一帧混进循环。

交接应先统一成**带明确单位的半开区间 `[begin, end)`**，再根据目标工具转换，而不是在各处复用同一个终点整数。本条实际验证了离线提取中的一帧差异；没有证明这会形成可听见的 click，也没有运行 FMOD 循环。

本文补充作曲到音频实现的素材边界合同。[交互音乐状态交接](../audio/music-state-transition-contract.md)负责玩法意图、音乐量化与实例生命周期；那些机制不能替代这里的素材帧数验收。反过来，帧数完全正确也不能证明实际转场自然、尾音处理正确或请求按时出声。

## 1. 先定义帧，再谈拍与字节

本例采用 48,000 Hz、双声道、每声道有符号 16-bit PCM。一帧是同一时间点上的一组 L/R 分量：

```text
1 sample frame = 2 channel samples = 4 PCM bytes
duration_seconds = frame_count / 48000
```

声道数影响字节数，不会让同样的帧数在双声道中播放两倍时长。FMOD 文档中的 PCM 时间单位与采样率相关，PCMBYTES 还要乘声道数和每分量字节数；不要混用，也不要把 WAV header 算成 PCM 音频数据。[FMOD TIMEUNIT](https://www.fmod.com/docs/2.04/api/core-api-common.html#fmod_timeunit)

### 分数拍长需要明确的项目政策

假设 BPM 明确以四分音符为一拍，123 BPM、4/4、一小节：

```text
ideal_frames = 48000 × 60 × 4 / 123
             = 3840000 / 41
             ≈ 93658.536585
```

整数 PCM 文件不能容纳分数个完整帧。本实验采用“最近整数，恰好半帧时向上”的明确政策，选择 **93,659 帧**。这是原创素材合同，不是声称 FMOD、某 DAW 或所有工作室采用此取整规则。

与理想数学周期相比，这份整数主体多 `19/41` 帧，约 9.65 微秒。固定整数周期重复时，这个差额在纯算术模型中会累加；但实际中间件可能使用其他调度、变速或重采样机制，本文没有测试，不能直接宣称真实系统必然以该数值漂移。若长期同步是产品要求，应另行约定素材周期、音乐网格与运行时同步机制，而不是在交付单上隐去取整。

FMOD Tempo Marker 定义用于拍、小节量化的 BPM 与拍号；它并不为这份素材提供自动核对帧长的证据。[FMOD Tempo Marker](https://www.fmod.com/docs/2.04/studio/glossary.html#tempo-marker) 变拍号、变速曲线、附点节拍单位和不同采样率转换不属于本次固定例子。

## 2. 文件范围、音乐主体与尾部必须分开

本次原创素材是一组数值色标式音频帧，不是第三方音乐或真实录音：前置为 `(-111, 111)`，主体普通帧为 `(100, -100)`，主体首末帧分别为 `(1234, -2345)`、`(3456, -4567)`，尾部为 `(222, -222)`。这些值用于定位，不用于试听。

| 部分 | 半开帧区间 | 帧数 | PCM 字节数 |
|---|---|---:|---:|
| 前置留量 | `[0, 480)` | 480 | 1,920 |
| 音乐主体 | `[480, 94139)` | 93,659 | 374,636 |
| 尾部留量 | `[94139, 96539)` | 2,400 | 9,600 |
| 全部 PCM | `[0, 96539)` | 96,539 | 386,156 |

因此“文件共有 96,539 帧”和“循环主体长 93,659 帧”同时成立。尾部是否在转场时继续播放、如何与下一段重叠，仍属于音频工程的创作与运行规则；本例的尾部 marker 不是混响尾音，不证明某种尾音混合方案。

源 WAV 实际长 386,200 字节，其中 PCM 为 386,156 字节。外部工具输出 WAV 可以带不同的描述信息，所以不能用两个 WAV 整文件是否相同来替代 PCM 内容比较。

## 3. 在工具边界转换端点，而不是复制数字

| 接口或交付格式 | 开始值 | 结束值 | 此处结束值的意义 |
|---|---:|---:|---|
| 本文统一合同 | 480 | 94139 | 第一个不属于主体的帧 |
| FFmpeg `atrim` 的 `_sample` 参数 | 480 | 94139 | 第一个丢弃的 sample frame |
| FMOD Core PCM loop points 的来源映射 | 480 | 94138 | 最后一个包含在循环中的位置 |

固定 FFmpeg 文档将 `end_sample` 定义为首个丢弃位置；`_sample` 选项通过样本计数工作，不等价于依赖输入时间戳的时间选项。`atrim` 本身不重置时间戳，本例另接 `asetpts=PTS-STARTPTS`。[FFmpeg 固定源码文档](https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/doc/filters.texi#L3773-L3822)

FMOD 2.04 的 `Sound::setLoopPoints` 文档则明确两端 inclusive，并规定端点范围、结束值必须大于开始值、loop mode 等条件；已缓冲的 stream 修改循环点另有限制。[FMOD Sound::setLoopPoints](https://www.fmod.com/docs/2.04/api/core-api-sound.html#setlooppoints) 这里仅推导出对应参数，不声称用实际 FMOD 实例播放成功；更不能把 Core API 的端点约定直接套到 Studio 时间线区域。

在本例，半开转闭区间是 `last = end - 1`。这个换算还要求区间非空、范围有效，且目标接口支持该长度；它不是对任意音频 API 的通用规则。

## 4. 实际离线证据：少一帧是数据事实，不是听感结论

[实验目录](../../research/experiments/music-loop-frame-contract/README.md)保存实现前冻结的区间、完整命令、输出与独立期望值。两条实际 FFmpeg 过滤路径为：

```text
correct:   atrim=start_sample=480:end_sample=94139,asetpts=PTS-STARTPTS
offbyone:  atrim=start_sample=480:end_sample=94138,asetpts=PTS-STARTPTS
```

| 实际输出 | 帧数 | PCM 字节数 | 末帧 L/R |
|---|---:|---:|---|
| 正确半开区间 | 93,659 | 374,636 | `(3456, -4567)` |
| 错用 inclusive 终点 | 93,658 | 374,632 | `(100, -100)` |

两者均可被工具正常处理；错误路径不是解码失败，而是交付意图错误。作者验证所有解码 PCM 字节与独立字面主体一致，并用实际 ffprobe 核对声道、位深、采样率、`time_base` 与 `duration_ts`。独立审查复制运行并重新检查 PCM、marker 和归档字节，结论一致。

另有三项有限 runner 新鲜度检查：优化模式拒绝、缺失工具路径、工具非零退出；失败不留下本次可误用的旧 PASS summary。它们是执行证据卫生，不是音频行为测试或通用故障注入证明。

环境为 Python 3.12.14，以及自报 `7.1.5-0+deb13u1` 的 `/usr/bin/ffmpeg` 与 `/usr/bin/ffprobe`。工具文件 SHA 与完整版本输出已记录。官方 `n7.1.5` 标签解析到 `3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587`，提交日期 2026-06-19；这是文档来源身份，不是认证本地 Debian 二进制与上游源代码完全对应。

原始 WAV 只在本地作为二进制保留；发布证据用 gzip 加 base64 无损归档，每份 657–669 字节。解码后应核对原始整文件 SHA，再解析 PCM；小归档来自重复人工 marker，不代表真实音乐具有相同压缩率。

## 5. 可直接用于交接的最小字段

下表是原创工程建议，不是厂商强制格式。

| 字段 | 必须说明的内容 | 验收责任 |
|---|---|---|
| 素材身份 | 文件 SHA、内容 revision、stem/段落名称 | 作曲与音频设计确认交付版本 |
| 音频数据格式 | sample rate、channels、每分量位宽、PCM/编码格式；frame 与 bytes 的单位 | 音频程序读取实际文件核对 |
| 音乐定义 | BPM 的拍单位、拍号、主体小节数、是否有变速；音乐入口相位 | 作曲说明，不能只写“123 BPM” |
| 主体区间 | `begin_frame`、`end_frame_exclusive`、长度；前置与尾部另列 | 音频设计与导入脚本核对 |
| 取整政策 | 理想分数帧长、选定整数帧长、差额和允许条件 | 作曲/音频程序共同批准 |
| 目标映射 | 具体版本/接口/单位、inclusive 或 exclusive、资源模式 | 集成人员验证，禁止复制裸整数 |
| 已完成验证 | 实际 PCM 提取、边界 marker/波形、目标工程播放与听感分别标状态 | QA 不把离线成功升级成整链通过 |

若一个 stem 与另一个 stem 的起点、主体帧数或音乐相位不同，不要只用文件时长近似相等批准同步交付。离线能检查区间一致性，实际相位/音乐意图仍需音频人员确认；本文没有运行多 stem 混合测试。

## 6. 不应从本实验推出什么

- 一帧差异存在，不等于必然可听见，更没有测量 click 感知阈值。
- 全部 PCM 相同，不等于设备输出延迟、实际音频时钟或中间件调度相同。
- PCM WAV 裁剪正确，不证明 MP3/AAC 等编码的 padding、预滚或 gapless 行为。
- 素材主体对齐，不证明尾音自然、转调合理或玩法意图及时响应。
- 固定 123 BPM 例子不验证动态变速、采样率转换或无限循环的网格同步。

若需求是“战斗切换听起来正确”，仍要回到[音乐状态交接验收](../audio/music-state-transition-contract.md)：用真实目标版本、音乐工程、观察日志和听音结果补齐。本文能交付的是清楚、可复核的素材边界，不是未经播放验证的声音体验保证。

## 来源与访问记录

FMOD 2.04 `Sound::setLoopPoints`、`FMOD_TIMEUNIT`、Tempo Marker，以及上述固定 FFmpeg 文档均于 2026-10-31 核对。FFmpeg 网站整页抓取超时后使用其官方 GitHub 固定文本；未将不可访问的 Wwise 页面计为证据。公式、素材合同和验收表为原创分析；原始数值素材不包含第三方音频资产。
