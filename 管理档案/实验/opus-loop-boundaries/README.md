# Ogg Opus 循环区间复现

[返回正文](../../../GameLibrary/声音与音乐/音频制作/循环素材/Ogg%20Opus%20循环回跳不连贯，怎样查解码和混音.md)

使用 Linux、Python 3、FFmpeg 7.1.5（有 libopus 编码器）、libsndfile 1.2.2 和 Node.js。脚本在当前目录写测试素材；请在一个空目录运行。素材由脚本生成，不依赖游戏资产。未运行完整游戏、混音器或听感实验。

```sh
python3 probe.py
python3 seek_probe.py
node wrap_model.js
```

- [整包与 PCM](probe.py)、[实际输出](observed.txt)：同一 48 kHz 单声道输入用 10/20 ms 编码，分别比较包内槽位、流头裁切、尾裁及完全解码后的 PCM 帧数。
- [顺读和实际回跳](seek_probe.py)、[实际输出](seek_observed.txt)：双声道非周期素材。只平移音频页的有效 granule 计数、重算 CRC，保留原包和流头。用 FFmpeg 核对连续输出，用 libsndfile 核对直接读、显式定位 0/713/62513、向后回跳、偏移一帧的反例和末尾短读。交错 PCM 的 RMS 对两声道计算；「best lag」只在指定邻域找，移位文件另以首 24 帧搜索顺读中的候选位置，再验余下窗口。
- [块内回跳帧编号模型](wrap_model.js)、[实际输出](wrap_observed.txt)：比较固定块、变化块、刚好到终点、区间短于块，以及将回跳拖到下一块的补零反例。编号不是声音振幅。
- [来源和适用范围](../../来源笔记/opus-loop-boundaries-20261126.md)
