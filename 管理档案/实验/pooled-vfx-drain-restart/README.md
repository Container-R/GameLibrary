# 粒子特效重播和迟到回调的复现

对应正文：[粒子特效回池后重播，怎样避免被上一轮关掉](../../../GameLibrary/视觉特效/特效制作/粒子模拟与发射/粒子特效回池后重播，怎样避免被上一轮关掉.md)。

这里有两个独立层次。探针运行真实 Godot 节点和定时器，读取状态与信号。Python 则是用预约死亡时间模拟旧、新粒子并存的最小模型，不代表引擎的粒子数量。

## Godot 探针

在本目录使用 Godot 4.7.2（版本输出含 `ed1daf0bf`）：

```sh
tmp=$(mktemp -d)
XDG_CACHE_HOME="$tmp/cache" XDG_DATA_HOME="$tmp/data" XDG_CONFIG_HOME="$tmp/config" \
  godot --headless --fixed-fps 60 --path . --script res://probe.gd
```

脚本在 `process_frame` 建立检查点。四个 CPUParticles2D 实例均为 8 个粒子槽，寿命配置为 0.3 秒，固定种子 123；对照自然一次性、显式停止一次性、显式停止连续模式、尚未收完就重播。检查点编号是观测顺序，不是其他版本的时序承诺。独立运行的结果一致；见 [实测输出](observed.txt)。无窗口没有取渲染像素，不验证尾迹或 GPU 粒子。延迟回调由实验刻意创建，代表旧业务工作，不由粒子完成信号触发。

## Python 策略模型

```sh
python3 model.py
```

预期见 [模型输出](model-observed.txt)。它只比较不清理、清理及旧编号校验，不实现完整多组件回收器或渲染。
