# 来源核读记录

核读日：2026-11-18 UTC。研究目录名沿委派的 20261119 标识，不以目录名覆盖实际访问日期。

## 1. Epic Audio Stream Caching Overview

URL：https://dev.epicgames.com/documentation/unreal-engine/an-overview-of-audio-stream-caching-in-unreal-engine

访问页面显示 UE 5.9，滚动文档，无本地固定引擎源码。实际读取导言、缓存容量例、Priming、Keeping Sounds In Memory、Trim、cache pressure。

支持：对象加载与压缩数据可播状态不同；预热、保留与资源竞争是不同条件。没有证据认定“首字缺失”或某个延迟数字。

冲突：该页 Prime 与 Retain 两处全局设置都写 2。未采用其数值配方，也未采用“zero latency under any circumstance”作为设备保证。API enum 的版本化资料作为选项语义依据，但不推断所有版本实现相同。文章不抄缓存默认容量，原页相关单位陈述也需要实现核对。

## 2. Epic UE 5.1 Python API: SoundWaveLoadingBehavior

URL：https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/SoundWaveLoadingBehavior?application_version=5.1

实际读取全文。定位：导言的覆盖顺序；LOAD_ON_DEMAND、PRIME_ON_LOAD、RETAIN_ON_LOAD、FORCE_INLINE 各条。

支持：Prime 首块可淘汰；Retain 到对象销毁或 ReleaseCompressedAudioData；Force Inline 是不同非流式解码路径；该页枚举 Prime=2、Retain=1。适用范围是启用 stream caching 的该版本接口资料，不是已执行 5.1 引擎，也不把 Python 当正式游戏线程。

## 3. Epic UE 5.1 Python API: AudioMixerLibrary

URL：https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AudioMixerLibrary?application_version=5.1

实际读取并定位 prime_sound_for_playback 与 prime_sound_cue_for_playback。前者列 on_load_completion 参数，后者没有；概览也解释 Cue 不发完成 delegate。只据此建议单 SoundWave 排查，不推断回调线程、成功语义或时限。

## 4. Epic UE 4.27 Audio Stream Caching Overview

URL：https://dev.epicgames.com/documentation/en-us/unreal-engine/audio-stream-caching-overview?application_version=4.27

实际读取 Monitoring the Stream Cache。支持 stat audiostreaming 的缓存块观察、加载时间和解码器使用字段。该页将功能标为 Beta；未挪用平台名单、默认容量或命令存在性到所有新版本。

## 方法和观测来源

四组实验设计、时钟边界、控制变量和判别流程为作者建议，尚未在引擎中执行。合成 PCM 的位置关系来自本目录脚本实际写盘、回读及断言；完整延迟和前缀删除由脚本主动构造，不是发现的游戏故障。

未播放音频或评价听感；样本级结论无需感知推断。正文未声称案例中的人声可懂、改善听感或满足体验门槛。

## 执行边界

在本轮可用环境检查中未找到可运行的 Unreal 编辑器或工程；检查范围有限，不声称证明所有机器上均不存在。没有安装引擎。只执行标准库合成 PCM 写盘、回读与断言；没有引擎、输出设备或真人感知实验。

复算生成器、结果与重建说明见[实验材料](../实验/对白起播的内容与时间/README.md)。作者稿的正式位置见[正文](../../GameLibrary/声音与音乐/游戏音效/播放管理/对白第一次播放迟到：预热完成以后，首块音频还在吗.md)。
