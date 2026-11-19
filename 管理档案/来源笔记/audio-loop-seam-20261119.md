# 音频循环接缝：来源与证据

- Audacity，[At Zero Crossings](https://manual.audacityteam.org/man/select_menu_at_zero_crossings.html)，手册说明上升零交叉且立体声两路未必同帧过零。没有把自主选择的下降零点归因于该命令。
- FMOD Studio 2.04，[Managing Assets](https://www.fmod.com/docs/2.04/studio/managing-assets.html)，Asset preview 与 Loop Points，[Troubleshooting §27.5](https://www.fmod.com/docs/2.04/studio/troubleshooting.html#music-tracks-are-getting-out-of-sync)，编码补齐、流送和声部原因。不运行 FMOD，不把更换编码或加载方式作为统一解法。
- IETF，[RFC 7845 §4.2–4.4](https://www.rfc-editor.org/rfc/rfc7845.html#section-4.2)，Ogg Opus 的起始预跳过、PCM 位置、最后一页末尾裁切。FFmpeg 7.1.5-0+deb13u1 / libopus 的一次本地往返测到 312/456 包侧信息与 49152/49152 帧；不将其等同于 FMOD 或任意定位输出。
- 相邻正式文章[如何标记和检查 PCM 音乐循环区间](../../GameLibrary/声音与音乐/音频制作/循环素材/如何标记和检查PCM音乐循环区间.md)负责交付区间、裁剪端点与帧数；本篇单独排查实际波形接缝和周期差。合成试件、读回、SVG 与运行说明见[附录](../实验/音频循环接缝/README.md)。
