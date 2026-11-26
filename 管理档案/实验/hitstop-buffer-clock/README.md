# 命中停顿：分开事件时间、接收时间和动作时间

[对应正文](../../../GameLibrary/玩法程序/玩法系统/战斗状态/命中停顿里按下的连招，输入缓冲该从什么时候计时.md)。

## 同一输入两种交付时刻

在本目录用 Python 3 运行 `python3 model.py`，以 [observed.txt](observed.txt) 对照六条结果。三种政策共享同一个 155 ms 的窗口检查，寿命采用半开区间 [0,55) ms。发生时间来自夹具而非设备。前五组到达时已排入可供 155 ms 检查读取的快照，第六组未到达。动作时间是现实时间减去已经经过的停顿区间，不模拟角色切换、联机或完整连招。

## Godot 主动交付路径

进入 `native/`，使用 Godot 4.7.2（版本输出含 `ed1daf0bf`）：

```sh
tmp=$(mktemp -d)
XDG_CACHE_HOME="$tmp/cache" XDG_DATA_HOME="$tmp/data" XDG_CONFIG_HOME="$tmp/config" \
  godot --headless --path . --script res://probe.gd
```

启用输入缓冲，创建两个分别带有同一人为时间元数据的合成键事件。每次均显式解析并冲刷；第二次故意等待 50 ms。回调收件时间用 `Time.get_ticks_usec()` 在 `_input` 采样；原始的 85 ms 由夹具手写，两者不是同一时基，不能直接相减。[观察结果](native/observed.txt) 给出每次冲刷前后回调数和粗粒度延时区间，不测试硬件、自动交付、规则消费或玩家操作。
