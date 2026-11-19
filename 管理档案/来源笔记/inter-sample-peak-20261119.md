# 音频采样间峰值：来源与实测

- ITU-R BS.1770-5 (2023-11) [Recommendation](https://www.itu.int/rec/R-REC-BS.1770-5-202311-I)，Annex 2 §3 和 Attachment 1。标准示例 48 kHz 通过插值滤波估计 192 kHz 网格峰值，附件推导最不利相位下采样表头会漏峰；不能把离散过采样估计说成解析精确极值，亦未据此要求游戏满足广播交付响度。
- FFmpeg [Filters: ebur128](https://ffmpeg.org/ffmpeg-filters.html#ebur128) 的 sample/true 选项；[n7.1.5 原始实现](https://github.com/FFmpeg/FFmpeg/blob/n7.1.5/libavfilter/f_ebur128.c) 的 `config_audio_output` 和 `filter_frame` 设置 libswresample 目标 192000 Hz 并对输出求绝对值最大值。这里使用该实现作为独立于手算的可执行表头，不断言其系数等同于 ITU 示例 FIR 或符合特定计量认证。
- [实验与复现](../实验/音频采样间峰值/README.md) 使用官方 FFmpeg 7.1.5 Debian 构建。正弦解析的采样点和峰值可直接算；实际 FFmpeg 测量和转换独立执行。将显示有越界的 44.1/96 kHz f32 与对应 s16 样本逐序号比较，越界样本去向确认为带符号端值。原始 48 kHz 输入没有样本越界；1 kHz 同样样本幅度的对照组没有真峰越界。
- 观测 JSON SHA256：`7385568bacf90105423c4089abbb63b6209bd1ed591b369a142034802e247e8e`。原创图 SHA256：`da69ee928d3caa7ba836d0d74a94e7ad1adadcd504c82e2f4b0ea5effc3c2d7e`，来自稳态解析正弦，不是实际声卡波形。本实验不评估听感、实际游戏、声卡、编解码器或限幅器性能。

末尾瞬态控制：FFmpeg 7.1.5 的一秒输入仅在 47996/47997 有 .82/.85，样本峰 -1.4116；裸真峰 -66.4，已知静默补 20 ms 真峰 +0.5；同样两点移到 47900/47901 时裸真峰 +0.5。观察限定为这一构建与夹具，实际工程保存事件前后完整波形再量。
