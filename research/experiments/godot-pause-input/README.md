# Godot 4.6.3 暂停与应用输入队列边界

## 可证伪问题

场景暂停时，显式设为 `PROCESS_MODE_ALWAYS` 的输入适配器仍收到事件，而 `PROCESS_MODE_PAUSABLE` 的玩法消费者停止。如果适配器只入队、不隔离暂停代次，恢复后的第一次玩法固定步是否会执行暂停前未消费及暂停期间的旧攻击？在同一次真实引擎运行中，对比朴素队列与暂停/恢复两边界清队列并递增epoch的产品策略。

这不是设备输入实验：通过实际 `Input.parse_input_event(InputEventAction)` 合成动作，进入引擎 `_input` 分发；没有键盘、手柄、OS事件或键位映射。`InputEventAction` 本来就是手工动作事件，不是硬件发出的具体输入类型。

## 运行与可追踪性

```sh
python run.py
```

运行器使用已安装Godot，无下载或额外依赖；禁止 `python -O`，拒绝记录在 `results/optimized-rejection.txt`。HOME及三个XDG目录隔离到 `/tmp/gamelibrary-godot-pause-*`。每次正常运行先移除旧summary，核对实际 `--help` 支持所需参数，并验证每个主回调delta≈1/指定fps。真实进程超时、非零返回、stderr、ERROR、缺失结果或独立判据不匹配均失败。记录命令、环境、配置、源SHA256、二进制SHA256及逐事件/回调原始日志。

实测2026-10-31：`4.6.3.stable.official.7d41c59c4`，Linux x86_64，Python3.12.14。二进制SHA256：`f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`。配置60Hz固定步、jitter_fix=0、单线程场景；主控ALWAYS，玩法子节点显式PAUSABLE，不能错误继承主控的ALWAYS。

## 受控交错，不依赖猜测毫秒数

1. 观察到玩法真实固定回调至少一次；主控在其后的一次 `_process` 注入 `pre_pause` 按下/释放对。立即调用暂停边界，使它还未被玩法消费就暂停。
2. 暂停状态下注入 `during_pause` 按下/释放对。每次注入调用真实 `parse_input_event`，并显式 `flush_buffered_events`；日志必须证实预期 `_input` 接收，不能仅假设调用成功。
3. 等ALWAYS控制器在暂停期间实际获得至少2次固定回调心跳，逐次断言玩法tick没有增加；这避免144fps下仅等一个主帧尚未到固定调度时机的空洞通过。随后在主回调观察：朴素队列有2个攻击，受保护队列尚有1个暂停期间命令。执行恢复边界（递增epoch并清受保护队列）。
4. 等到观察到玩法tick真正推进，记录“新输入前已执行攻击”，再注入 `fresh` 对。
5. 等到玩法tick再次推进，独立Python判据核对完整事件和模式观察。200主回调只是故障看门狗，不是时间/帧率结论。

双队列消费由同一个玩法回调完成，使用完全相同的输入流。朴素失败是刻意保留的对照，不能为了“全绿”删除。每次注入都成对释放，日志检查全局action未保持按下；这不等于研究了跨暂停的持续按键。

## 实际结果

| 人工主帧配置 | 主控 `_process` | 玩法 `_physics_process` | 朴素最终攻击 | 受保护最终攻击 |
|---|---:|---:|---|---|
| `--fixed-fps 30` | 4 | 6 | pre_pause, during_pause, fresh | fresh |
| `--fixed-fps 60` | 5 | 3 | pre_pause, during_pause, fresh | fresh |
| `--fixed-fps 144` | 13 | 3 | pre_pause, during_pause, fresh | fresh |

三进程均退出0，全部判据通过。每组新输入前，朴素已消费`[pre_pause,during_pause]`，受保护为空。ALWAYS适配器收到6个按下/释放事件，PAUSABLE玩法节点只收到暂停外的4个；暂停观察区间玩法tick不变；每组均记录2次ALWAYS固定心跳，从而有实际固定调度机会作为非空证据。

这些计数是该交错的观测，不是所有机器/引擎构建的固定回调预算。`--fixed-fps` 是人工游戏时间安排，关闭实时同步，不代表显示器刷新率、GPU渲染或真实持续暂停时长。本单元不测5秒暂停是否补时，也不推出引擎欠账规则。

## 工程解释与边界

**暂停消费者不会自动清掉另一个常驻节点维护的应用队列。** 若产品规则要求菜单期间不缓存战斗攻击，应让唯一的暂停入口同步完成：切换输入上下文、递增游戏输入epoch、清空待消费攻击，再切换场景暂停状态；恢复同样隔离旧代次。不同输入类别可以有不同规则，不能把移动持有态、文本输入和菜单确认一律当攻击边沿清理。

本夹具测试的是“清队列+epoch过滤”组合，正常路径中的旧命令已被清掉，**没有单独证明epoch过滤可拦截异步延迟投递**。如果旧设备事件直到恢复后才到达，并被适配器标成当前epoch，这个方案并不能识别其年龄。生产实现须另测接收时间/源事件时间戳、输入上下文切换、释放重武装和延迟回调。不得把此夹具写成“任何暂停输入均不泄漏”。

同样未覆盖：键盘ghosting、手柄掉线、键位映射、按住跨暂停、UI处理/未处理输入优先级、信号直接修改玩法、线程、回滚、账号/场景切换、渲染与物理求解、Unity或跨平台行为。官方还提醒暂停节点仍可接收信号；仅停回调不是全局业务写保护。

## 官方来源（访问2026-10-31，版本4.6）

- [Pausing games and process mode](https://docs.godotengine.org/en/4.6/tutorials/scripting/pausing_games.html)，*Process Modes*：ALWAYS/PAUSABLE区别，暂停节点的回调及信号边界。
- [Input](https://docs.godotengine.org/en/4.6/classes/class_input.html)，`parse_input_event`、`flush_buffered_events`、`action_press`：前者合成事件并产生 `_input`；flush显式分发缓冲，action_press不产生 `_input`，因此不能用它替代本实验的分发检查。
- [InputEventAction](https://docs.godotengine.org/en/4.6/classes/class_inputeventaction.html)，*Description*：手工虚拟动作与物理输入事件区别。
- [CLI reference](https://docs.godotengine.org/en/4.6/tutorials/editor/command_line_tutorial.html)，`--fixed-fps` / `--headless`：人工时间与无头模式；相关语义已在前一固定步夹具核对。

代码为原创最小夹具，不含第三方实现复制。文档为4.6系列，实际二进制和哈希单独记录。

## 独立复核

独立复核在相同机器/二进制、另一目录重跑3个引擎进程，五份源文件哈希完全相同，得到相同判据结果。额外日志审查要求暂停心跳严格位于暂停/恢复边界之间；见[审计记录](review/audit.md)。归档结果可用 `python review/verify_pause_trace.py` 复核，不会启动引擎。作者3次与复核3次是相同3配置的重复验证，不是6种场景，也不是跨平台证据。
