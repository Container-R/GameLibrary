# 分轨共同播放位置：OpenAL Soft 回环复现

在本实验目录，用 Python 3 标准库和已安装的 OpenAL Soft（需提供
`ALC_SOFT_loopback`）运行。已执行版本为 OpenAL 1.1 /
OpenAL Soft 1.24.2。

```sh
ALSOFT_DRIVERS=null python3 native_loopback.py > actual.txt
cmp native-observed.txt actual.txt
```

[测试脚本](native_loopback.py) · [原始输出](native-observed.txt)

## 输入、操作、判断

生成两份预先驻留的 48 kHz 立体声 PCM16 缓冲；参考轨只在左声道有脉冲，
待加入轨只在右声道有脉冲，便于从同一双声道混音读回并分轨测量。
每个脉冲长 32 采样帧；120 BPM 对应每 24000 帧一拍。每一种对照单独
创建回环设备及上下文，渲染 100000 帧双声道浮点混音。先渲染 36000 帧，
读出待加入轨的 `AL_SAMPLE_OFFSET`，再提交增益、开始播放或设置偏移的操作，
然后渲染余下部分。区间判断是样本绝对值第一次超过 0.04；断言开放前的待加入轨
低于 1e−7。共同游标增益门控发生在空档，离下一参考脉冲 12000 帧，本实验不
测量增益变化的具体斜坡或边界恰落在非零信号处的行为。

- `late_zero`：只播放参考，待加入轨到 36000 帧直接从文件头播放。
- `running_muted`：用 `alSourcePlayv` 一次启动两轨，待加入轨初始增益为零；
  到 36000 帧已推进同量，此刻只改增益。
- `late_aligned`：先只播放参考，到 36000 帧给待加入轨设同样的媒体帧
  偏移，再启动。两素材、设备都使用 48 kHz，且不循环，无需换算。
- `shifted_asset`：沿用共同游标方案，但把待加入轨的源脉冲整体延迟
  2400 帧，模拟分轨导出起点不一致。时钟对齐无法消除素材内的偏差。

回环输出是混音器生成的数值，不是扬声器回采。只验证指定版本、已加载缓冲、
解码后同采样率、手工离线推进条件下的定位；未验证文件解码、流式加载、
虚拟化、环绕、重采样、设备延迟、感知或实时线程调度。

接口定义见 [ALC_SOFT_loopback](https://github.com/openalext/openalext/blob/master/ALC_SOFT_loopback.txt)
（应用读回渲染样本）和 [OpenAL 1.1 规范](https://www.openal.org/documentation/openal-1.1-specification.pdf)
（`AL_SAMPLE_OFFSET`、`alSourcePlayv`）。

[返回正文](../../../GameLibrary/声音与音乐/交互音乐/音乐切换/分层配乐加入鼓组时，怎样对齐正在播放的拍点.md)。
