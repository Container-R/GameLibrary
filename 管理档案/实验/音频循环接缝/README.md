# 音频循环接缝

[返回正文](../../../GameLibrary/声音与音乐/音频制作/循环素材/环境音找到零交叉，为什么循环点还能听出接缝.md)

本次在 Linux 用 Python 标准库、Inkscape 和 FFmpeg 7.1.5-0+deb13u1（libopus）执行。建议先把本目录复制到独立工作目录，以免覆盖检出的 JSON 或 SVG：

```bash
set -o pipefail
python3 -B check_loop_seam.py --wav-directory generated | diff -u observed.json -
python3 -B readback_wav.py | diff -u wav-readback.json -
python3 -B check_repeat_timing.py | diff -u repeat-observed.json -
python3 -B draw_seam.py
```

第一步生成两个原创 48 kHz 16 位双声道 WAV，文件中的第一次内部接缝无整体首尾淡化影响；原始 WAV 不随仓库提交，直接用脚本生成。第二步读取真正写入文件的样本。第三步需要 FFmpeg、ffprobe 和 libopus：本例比较 Ogg Opus 解码后的 PCM 帧数，不证明波形未改或能无缝重入；不同编码器构建可能产生不同包侧信息。150 周期的偏差只是一组假定帧数的整数计算。最后生成用于正文的原创 SVG，不生成真实节目或游戏截图。不测人耳、FMOD 现场、播放设备或任何商业游戏。
