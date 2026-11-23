# 对白起音与音乐压低：证据

- [FFmpeg 7.1 sidechaincompress 源码](https://ffmpeg.org/doxygen/7.1/af__sidechaincompress_8c_source.html)，compressor_config_output、output_gain 和 compressor：全湿、单位增益、峰值、硬拐点的上限式和攻击释放。 [滤镜文档](https://ffmpeg.org/ffmpeg-filters.html#sidechaincompress) 对应入口。
- [FMOD Studio 2.04](https://www.fmod.com/docs/2.04/studio/mixing.html#snapshots-and-the-tracks-view) 和 [Godot 4.6](https://docs.godotengine.org/en/4.6/tutorials/audio/audio_effects.html#compressor) 说明可配置的快照/侧链概念，不是游戏运行时的实测。
- [复现](../实验/对白起音与音乐压低/README.md)分别保存合成等能检测、固定合成语音和原创乐段的混音、线性 dB 斜坡预算、实例所有权。FFmpeg 原生 7.1.5-0+deb13u1，Node 24.22.3。无听审、正式演员、真实游戏接入或可懂度结论。

调阅日期：2026-11-23（北京时间）。
