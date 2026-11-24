# Box2D：外层物理步、内部子步和一次性冲量

## 复现

采用 Box2D 的固定源码 [178495ba35695aefe9c321e569d2277f06db3b90](https://github.com/erincatto/box2d/tree/178495ba35695aefe9c321e569d2277f06db3b90)，其 CMake 自报版本 3.2.0；这是源码快照，不是对发行标签的声明。源码不随实验再发布。把 `src` 和 `include` 完整放置在环境变量 `BOX2D_SRC` 所指目录。从本目录运行：

```sh
upstream="${BOX2D_SRC:?Set BOX2D_SRC to the pinned Box2D source tree}"
runtime=$(mktemp -d)
cc -std=gnu17 -O0 -ffp-contract=off -DBOX2D_DISABLE_SIMD -DBOX2D_VALIDATE \
  -I"$upstream/include" -I"$upstream/src" native_box2d.c \
  "$upstream"/src/*.c -lm -pthread -o "$runtime/force_probe"
"$runtime/force_probe"
```

实测 Linux x86_64，GCC 14.2.0（Debian 14.2.0-19），直接编译固定快照中 43 个 C 源文件。独立构建后同一二进制各执行两次，均与 [原始标准输出](native-box2d-observed.txt) 逐字节相同。首步值使用绝对误差 1e-7 验算；一秒值为 3e-5。

## 读法

每组从静止开始，刚体质量 2 kg，不设碰撞形状，关闭重力、阻尼与睡眠影响；各组总模拟时间一秒。外层更新频率为 30、60、120 Hz，内部子步数分别对照 1 与 4。外层力是每次外层步前施加 12 N；始终使用 0.2 N·s 表示误设为“每个外层步一次固定冲量”的推动。起跳标签只模拟 4 N·s 事件调用一次与错误地调用两次，不声称验证了任何设备采样或引擎输入队列。程序还记录了只施加一步的力以及同一步叠加两次的力。

固定快照中 [外层步分配子步时长](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/physics_world.c#L945-L960)，[力写入累加器](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/body.c#L987-L1010)，[每子步积分该力](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/solver.c#L61-L83)，[收尾清掉力与扭矩](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/solver.c#L619-L629)。[即时冲量直接改速度](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/body.c#L1079-L1107)。各相同终速的对照可以有不同位移；本测试未给出接触、阻尼、速度上限附近或跨后端的结果。

## 输入队列的独立教学模型

运行 `python3 edge_probe.py` 可得到 [记录](edge-observed.txt)。预先安排了四条按下/松开事件，以 20 ms 外层步比较规则画面回调和一帧追赶三步。只有编号 1、2 分别在 `[20,40)`、`[40,60)` 被消费；用同一画面 press 标志给三步则产生三次信号。脚本的时间是事先对齐的模拟毫秒，`held_at_end` 只展示端点状态，不把它当成整个区间的持续力。这是队列模型，不读取设备、不与刚体实验集成。

[返回正文](../../../GameLibrary/玩法程序/玩法系统/时间与模拟/固定物理步中的持续推力与一次冲量.md)。
