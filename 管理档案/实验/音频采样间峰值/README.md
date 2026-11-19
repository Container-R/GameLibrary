# 音频采样间峰值：同一 PCM 的浮点与整数输出

[返回正文](../../../GameLibrary/声音与音乐/音频制作/混音/样本峰值没到%200%20dBFS，为什么游戏音频转采样后还是削顶.md)。

```sh
python3 -B probe.py | cmp - observed.json
MPLCONFIGDIR=/tmp/gamelibrary-mpl-peak python3 -B figure.py
```

[probe.py](probe.py) 用 Python 3 标准库调用 FFmpeg 7.1.5；需要小端主机、FFmpeg 构建包含 libswresample。不同构建的版本串和重采样幅度可能不同，断言检查本试件的实质差异，`cmp` 检查相同版本配置记录的字节。原始数据见 [observed.json](observed.json)。脚本生成的试件与检测一路保留 f32，再另跑相同目标采样率的 s16 试件，比较越界浮点位置与整数端值，而非只数贴边样本。两个输出不改增益或启用抖动选项。

[figure.py](figure.py) 使用 matplotlib、numpy 和可用的中文字体重绘 [peak.png](peak.png)。图是理想正弦的采样位置示意，不是工具输出波形。无需播放高频测试音；试件没有模拟声卡、耳机、播放器音量或有损编码。
