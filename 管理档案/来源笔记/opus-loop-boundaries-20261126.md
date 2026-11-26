# Ogg Opus 循环排查：来源与证据

1. IETF，[RFC 7845](https://www.rfc-editor.org/rfc/rfc7845.html)。§4.2/5.1 规定解码流头 pre-skip，§4.3 区分 granule 及播过一帧后的 PCM 边界；§4.4–4.5 管尾裁及非零起点；§4.6 要求考虑 seek pre-roll 和靠近流头的处理。文中的三个坐标例子使用单条 48 kHz 时钟；不推广到多条链式流或重采样结果。页计数变体依 [RFC 3533 §6](https://www.rfc-editor.org/rfc/rfc3533.html#section-6) 更新页 CRC。
2. Xiph.Org，[libopusfile 0.12 定位接口](https://opus-codec.org/docs/opusfile_api-0.12/group__stream__seeking.html#op_pcm_seek) 说明定位以 PCM 样本偏移计，并提醒不保证与顺读值完全一致。仅核接口说明，未运行 libopusfile。
3. libsndfile，[1.2.2 源码](https://github.com/libsndfile/libsndfile/blob/1.2.2/src/ogg_opus.c)。查 `ogg_opus_analyze_file` 的 `gp_start` 与元数据总帧数，`ogg_opus_read_refill` 的 `pkt_pos` 比较，`ogg_opus_seek` 向目标加起点与 pre-skip。这解释该测试为什么可能初次顺读有偏移、而显式回跳正确。未检验其他库版本，不建议给调用参数加减固定的 312。
4. [实验及输出](../实验/opus-loop-boundaries/README.md)。FFmpeg 的相同逐字节输出指共享音频包、仅时间起点不同的双声道两文件；不指 10/20 ms 两次编码的 PCM 值相同。固定 1.2.2、输入、窗口的结论详见输出。仅运行 PCM 取样和块编号模型，未听测或测运行时性能。

资料复核：2026-11-26（北京时间）。
