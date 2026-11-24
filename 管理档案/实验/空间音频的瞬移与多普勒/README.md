# OpenAL Soft 多普勒音高：固定位置输入对照

Linux 上需 Python 3、提供 ALC_SOFT_loopback 的 OpenAL Soft 共享库；公开听音副本还需有 libopus 编码器的 FFmpeg。实验使用 OpenAL Soft 1.24.2，通过 loopback 直接读回 48 kHz、单声道的 PCM16，不出声卡。参阅[扩展说明](https://openal-soft.org/openal-extensions/SOFT_loopback.txt)。

```sh
ALSOFT_DRIVERS=null ALSOFT_CONF=/dev/null python3 native_loopback.py
ffmpeg -hide_banner -loglevel error -y -fflags +bitexact -i comparison.wav -c:a libopus -b:a 48k -flags:a +bitexact comparison.opus
```

听音副本 [comparison.opus](comparison.opus) 由四段片段组成，依次是 5 m/s 接近、5 m/s 远离、误报 120 m/s 接近和速度归零。每段取稳态 0.35 s，另加 5 ms 淡入淡出、0.15 s 间隔。淡化和时间剪辑只服务试听；[具体频率测量](loopback-observed.txt)使用的是编码前 PCM 中间 0.4 s 的上升过零间隔。

每段新建声源；位置固定为 (0,0,−10)，监听器固定在原点且速度为零。多普勒因子设为 1，声速 343，距离衰减关闭，四段共用零外加移调的单声道 440 Hz 正弦源。以相同空间状态隔离显式速度参数的影响；位置不实际移动。第三段将 2 米除以 1/60 秒所得的速度作为恒定输入，并不是重放真实瞬移。实际混音块何时消费状态、一次提交的误速度会保留多久、速度更新是否平滑，以及监听器跳切或坐标重置如何实现均未实测。不能将稳态幅度、频率和持续时间外推到其他空间音频实现。

原始 WAV 用脚本在本地重建，不随听音副本发布。声音是试件生成的正弦波，不含第三方音频。

[返回正文](../../../GameLibrary/声音与音乐/游戏音效/空间音频/空间音频的瞬移与多普勒速度.md)
