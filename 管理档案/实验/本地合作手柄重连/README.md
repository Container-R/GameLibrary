# 本地合作手柄重连：复现实验

[返回正文](../../../GameLibrary/玩法程序/玩法系统/输入接入/本地合作手柄断开后，怎样恢复原来的玩家席位.md)

- `check_sdl2_virtual_events.py`：Linux x86-64、Python 3 ctypes、SDL2 2.32.4，要求独立进程且看不到物理手柄。用两个同配置虚拟设备捕获实际 SDL_PollEvent，再移动枚举位置、增删设备。输出刻意按种类与值排序；只观察字段和两类通知的存在，不主张回调发生顺序。
- `check_seat_resume.py`：合成输入的游戏层示例。旧连接、无效的默认零、认领键一直按住、杆未回中及 P2 不应被重置分别由断言区分。不运行 SDL。
- `check_seat_contention.py`：合成同一输入更新中两席争一连接、两连接争一席、二次掉线与没有冲突时同时绑定。选择冲突全拒绝是例子而非平台规范。不运行 SDL。

在此目录执行：

```sh
set -e
python3 -B check_sdl2_virtual_events.py > /tmp/gl-sdl2-events.json
cmp /tmp/gl-sdl2-events.json sdl2-events-observed.json
python3 -B check_seat_resume.py > /tmp/gl-seat-resume.json
cmp /tmp/gl-seat-resume.json seat-observed.json
python3 -B check_seat_contention.py > /tmp/gl-seat-contention.json
cmp /tmp/gl-seat-contention.json seat-contention-observed.json
```

SDL2 实测只支持该版本和虚拟路径的观察，不是 USB、蓝牙、硬件能力报告或特定游戏的试验。合成两例分别演示输入隔离与争用规则，不是一份完整设备路由实现。
