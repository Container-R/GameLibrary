---
id: SOL-PROG-001
title: 用固定 Tick 划清战斗模拟与引擎表现边界
type: solution
status: source-backed
primary_discipline: PROG
related_roles: [gameplay-programmer, animation-programmer, engine-programmer, network-programmer]
related_topics: [fixed-timestep, input-buffering, deterministic-simulation, presentation-adapter]
engines: [engine-agnostic, Unity]
versions: ["Unity 6000.0 文档", "Input System 1.11.2 文档"]
updated_at: 2026-10-31
verification_method: 原始文档核对；设计与测试矩阵为原创推导，未运行 Unity 或跨平台确定性测试
sources:
  - https://gafferongames.com/post/fix_your_timestep/
  - https://gafferongames.com/post/deterministic_lockstep/
  - https://docs.unity3d.com/Packages/com.unity.inputsystem@1.11/manual/Settings.html
  - https://docs.unity.com/en-us/engine/6000.0/manual/scripting/managing-time-and-frame-rate/time-handling-variations
---

# 用固定 Tick 划清战斗模拟与引擎表现边界

## 问题与适用范围

攻击窗口、冷却和输入消费若随渲染帧推进，更换帧率或动画系统时可能改变玩法。本文提出可移植的离散战斗规则核心，适合以数值、状态机和离散命中规则为主的原型。**不承诺迁移引擎物理、Root Motion 或自动获得联机确定性。** 具体接口和策略是研究者设计，不是任何引擎的现成保证。

## 已核对的依据

Fiedler 在 *Fix Your Timestep!* 的 “Free the physics” 将剩余时间留入累加器，只以固定步长推进；“The final touch” 用前后两个状态做表现插值。“Semi-fixed timestep” 说明追赶开销可能反过来扩大欠账，需留性能余量或限步。[S1]

*Deterministic Lockstep* 的 “Determinism” 指出相同步长仍不足以保证同结果：随机处理顺序、编译器和浮点差异均可能破坏复现；“Networking Inputs” 将输入绑定到模拟帧，而非到达时刻。[S2]

Unity 6000.0 文档说明最大时间步限制会让游戏/物理时间落后于真实时间；Input System 1.11.2 则明确区分 Dynamic、Fixed、Manual 输入处理模式。[S3][S4] 因此不能把帧回调频率或输入更新配置当成跨引擎统一契约。

## 原创实现方案

1. **核心契约**：`Step(state, tick, commands, config) -> (newState, events)`。核心只接收稳定 ID、数值与结构化命令，不持有 GameObject、Animator 或墙钟。技能配置用整数 tick 表示生效区间，例如 `[6,9)`，避免边界重叠。
2. **输入适配**：命令携带 `targetTick, sequence, actorId`。本地最简单策略是在采集时指定“下一个尚未执行 tick”；它有可测量延迟，不保证不同采样时序下产生相同日志。精确回放重放的是已记录的 tick 命令，而非重新采集设备。持有状态可跨 tick 延续，按下事件只消费一次。迟到命令必须显式选择拒绝、延后或回滚，不能暗中改时间。
3. **单一调度者**：使用单调时钟提供 elapsed；暂停不累积游戏时间。由引擎固定回调驱动核心，或自建累加器，二选一；不要两处同时 Step。
4. **过载策略必须可观测**：下例选择保留欠账、每渲染帧最多推进 K 步。落后时显示最新已知状态，而不外推；持续过载需降非关键表现负载或让上层决定暂停/重同步，不能偷偷跳过战斗 tick。

```text
A += elapsedGameTime
steps = 0
while A >= h and steps < K:
    previous = immutableCopy(current)
    current, events = Step(current, tick, consume(tick), config)
    publish(events)                 # 标注 tick + 序号
    tick += 1
    A -= h
    steps += 1
if A >= h:
    present(current)                # 欠账时 A/h 不是合法插值权重
else:
    present(interpolate(previous, current, A/h))
record(backlog=A, simulatedSteps=steps)
```

`previous` 初始为 `current` 的值拷贝。正常插值显示的是过去两个完成状态间的值，约引入一个模拟步的显示延迟。瞬移与离散事件不插值；伤害、声音、特效事件按事件 ID 去重，不能由渲染插值再次产生。回滚后的副作用确认另需协议，不在此实现范围。

5. **表现单向消费**：渲染/动画适配器读取快照与事件，不反向改核心冷却或命中状态。若项目要求 Root Motion 驱动物理，必须把运动结果作为显式适配输入，并承认核心仍依赖引擎的求解语义。
6. **确定性分层**：先固定命令顺序、随机种子、配置版本、序列化字段顺序；每 tick 记录规范化状态哈希。测试同一二进制后，再测试不同构建与平台。不能以“用了整数 tick”推导浮点物理也确定。

## 取舍与失败模式

保留欠账不丢逻辑但增加响应延迟；丢弃累计时间可保护本地交互，却改变墙钟与游戏钟映射，须同时重映射输入时间并记录丢失量；权威联机不能由各客户端自行跳 tick。只加 K 限制却仍用 `A/h` 插值会外推；共享可变快照会使 previous 与 current 实际相同。不同渲染帧率下直接采样按钮并重放同一按钮状态，则可能多触发攻击。

## 验证范围与验收矩阵

2026-10-31 在 Python 3.12.14 上实际运行了原创、无引擎依赖的 `Fraction` 调度模型，7 项测试通过：不同渲染分片、半 tick 余量、过载欠账、单次边沿消费、只读插值、负时间拒绝及实时采样不具帧率不变性的反例。[实验脚本](../../research/experiments/fixed-step/test_fixed_step.py)、[原始测试输出](../../research/experiments/fixed-step/test-output.txt)与[环境和范围](../../research/experiments/fixed-step/README.md)已归档。这只验证该离散模型，不验证 Unity 调用顺序、物理后端或跨平台浮点确定性；下表仍包含待执行的引擎集成检查。

| 输入条件 | 必须断言 |
|---|---|
| 同一 tick 命令日志，30/60/144 Hz 渲染 | 跑到同一 tick 时状态哈希与事件序列一致；不比较相同墙钟下的不同 tick |
| 一帧积累 10h，K=4 | 仅执行 4 步、保留 6h；表现不外推，欠账指标明确 |
| 无固定步的渲染帧后一次补 3 步 | 按下事件仅出现一次，持有值按契约延续 |
| 命令落在攻击窗口端点 | tick=6 生效、tick=9 不生效；无浮点 epsilon 特例 |
| 暂停 5 秒、恢复及失焦 | 暂停期间不推进；输入清理/恢复策略明确，不制造 5 秒补算 |
| 改编译配置、平台或物理后端 | 哈希差异可定位到首个 tick；不将单机通过写成跨平台保证 |

## 来源记录与版权

访问日期均为 2026-10-31；仅保存原创设计、短述和链接，未转载第三方代码/图表。文档开放阅读不等于允许再分发原文。

- **S1** Glenn Fiedler，2004-06-10，[*Fix Your Timestep!*](https://gafferongames.com/post/fix_your_timestep/)，英文原作者文章；定位：Semi-fixed timestep / Free the physics / The final touch。不是现代引擎性能基准。
- **S2** Glenn Fiedler，2014-11-29，[*Deterministic Lockstep*](https://gafferongames.com/post/deterministic_lockstep/)，英文原作者文章；定位：Determinism / Networking Inputs。本文不复用其网络协议实现。
- **S3** Unity，[*Input settings*](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.11/manual/Settings.html#update-mode)，页面元数据版本 **1.11.2**，定位 Update Mode。这里只核对处理时机，未推断所有输入设备时间戳语义。
- **S4** Unity，[*Handling variation in time*](https://docs.unity.com/en-us/engine/6000.0/manual/scripting/managing-time-and-frame-rate/time-handling-variations)，**6000.0**，定位 Limiting recorded time variation / Time variation and the fixed update loop。
- 多语言交叉检索：日文 [Unity 6000.0 Time](https://docs.unity3d.com/ja/6000.0/Manual/class-TimeManager.html)，固定時間ステップ / 最大許容時間ステップ；属同一厂商译版，**不算独立复核**。

## 关联方案

[转身脚滑与根运动职责](../animation/turn-in-place-foot-sliding.md)进一步讨论动画增量、控制器与足底接触之间的边界。
