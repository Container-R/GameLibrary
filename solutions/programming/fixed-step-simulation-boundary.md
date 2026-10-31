---
id: SOL-PROG-001
title: 用固定 Tick 划清战斗模拟与引擎表现边界
type: solution
status: source-backed
primary_discipline: PROG
related_roles: [gameplay-programmer, animation-programmer, engine-programmer, network-programmer]
related_topics: [fixed-timestep, input-buffering, deterministic-simulation, presentation-adapter]
engines: [engine-agnostic, Unity, Godot]
versions: ["Unity 6000.0 文档", "Input System 1.11.2 文档", "Godot4.6.3.stable.official.7d41c59c4 本地程序自报；发行与源码对应未确认"]
updated_at: 2026-10-31
verification_method: 原始文档核对、原创模型与本地Godot实际无头回调夹具；未运行Unity或跨平台确定性测试
sources:
  - https://docs.godotengine.org/en/4.6/classes/class_node.html
  - https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/main/scene_tree.cpp
  - https://docs.godotengine.org/en/4.6/classes/class_animationplayer.html
  - https://docs.godotengine.org/en/4.6/classes/class_animationmixer.html
  - https://docs.godotengine.org/en/4.6/tutorials/scripting/idle_and_physics_processing.html
  - https://docs.godotengine.org/en/4.6/tutorials/editor/command_line_tutorial.html
  - https://gafferongames.com/post/fix_your_timestep/
  - https://gafferongames.com/post/deterministic_lockstep/
  - https://docs.unity3d.com/Packages/com.unity.inputsystem@1.11/manual/Settings.html
  - https://docs.unity.com/en-us/engine/6000.0/manual/scripting/managing-time-and-frame-rate/time-handling-variations
  - https://docs.godotengine.org/en/4.6/tutorials/scripting/pausing_games.html
  - https://docs.godotengine.org/en/4.6/classes/class_input.html
  - https://docs.godotengine.org/en/4.6/classes/class_inputeventaction.html
---

# 用固定 Tick 划清战斗模拟与引擎表现边界

> **运行身份说明（2026-10-31）：** 下述 Godot 版本为已安装程序自报，不代表已认证官方发行包或精确源码身份。[共享取证与缺口](../../research/source-notes/godot-runtime-provenance.md)保留原始版本、文件摘要及公共标签查询差异；各次有限行为观察仍按实际归档字段解释。

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
6. **确定性分层**：先固定命令顺序、随机种子、配置版本、序列化字段顺序；每 tick 记录规范化状态哈希。测试同一二进制后，再测试不同构建与平台。不能以“用了整数 tick”推导浮点物理也确定。 同样，固定排序只能决定可重复的执行次序，不能替代项目对同 tick 冲突的规则选择。

## 同 tick 规则补充：可重复结果仍可能实现错了政策

固定步回答“何时推进”，不自动回答“这一 tick 内谁仍有攻击资格”。新增的[有限规则模型](../../research/experiments/simultaneous-combat-policy/README.md)在实现前冻结一条**原创项目政策**：攻击者和目标在本 tick 开始时都存活，攻击才合格；已合格攻击不因本 tick 内受到致死伤害而取消，先收集伤害，再统一提交。无碰撞、护盾、治疗或复活，每个角色最多一条攻击，仅两名角色、HP 为 0 或 1。

设 A、B 各 1 HP，本 tick 互相造成 1 点伤害：

| 实现 | 结果 | 与选定政策关系 |
|---|---|---|
| 根据当前 tick 开始快照判断资格，再统一提交 | 双方 0 HP，两条伤害、两条死亡记录 | 符合同时结算政策 |
| 逐条检查当前 HP 并立刻修改目标 | 先遍历者存活，后遍历者不能反击 | 改变遍历顺序会改变胜者 |
| 先按稳定身份排序，再逐条立即修改 | A 始终先行动并存活 | 完全可重复，但仍违反本例同时结算政策 |

这不是要求所有游戏都允许相杀。先手击杀中断反击也可以是有意的设计；问题是不能让容器遍历顺序在未声明的情况下替设计者选规则。Fiedler 的处理顺序讨论仅是复现背景，不为本例政策背书。

实际枚举三种冻结初态（双方存活、A 已死、B 已死），各组合两种 actor 插入顺序与两种命令顺序，共 **12 个有限输入**。同时结算全部符合手写状态/事件判据；两种立即修改实现各在四个双方存活输入中不符合该政策，另八个初始死者输入符合边界约定。死亡结果再进入下一 tick 的四次检查均无攻击事件，不能拿旧的存活资格无限沿用。

[独立复验](../../research/experiments/simultaneous-combat-policy/review/REVIEW.md)重跑 normal / `-O`，使用不导入作者规则函数的字面判据核对 12 个唯一输入；另有五个输入域/状态别名 unittest 方法。一项将同时结算实现替换成“稳定排序立即修改”的定向变异被合同判据以非零退出拒绝。这里比较规范化状态和事件记录，**没有规定实际事件发布顺序，也没有提供跨调用去重或 exactly-once 提交**。

原先每 tick 一个加法标量的模型与单 x/axis 的 Godot 夹具不能表达这类相互致死关系；本补充是规则语义证据，不把原有窄验证说成缺陷。这一模型本身只运行 Python 标准库，不覆盖引擎调度、物理命中、联网回滚或动作取消。下面的独立引擎夹具仅补其中的节点调度边界，其他需求仍需另外的政策与证据。

### 真实节点调度补充：优先级会改变先手，不会替项目选择结算政策

[实际 Godot 四进程夹具](../../research/experiments/godot-combat-policy/README.md)不是把上述 Python 循环换成 GDScript：A、B 是各自接收 `_physics_process` 的独立节点。实际子节点顺序固定为 Begin、A、B、End；Begin 的物理优先级为 -100，End 为 100，交换的仅是 A、B 的 `process_physics_priority`（0 与 10），所有节点继承同一默认主线程处理组。

| 模式 | A / B 物理优先级 | 实际回调顺序 | 最终 A / B HP |
|---|---|---|---|
| 立即修改当前状态 | 0 / 10 | Begin、A、B、End | 1 / 0 |
| 立即修改当前状态 | 10 / 0 | Begin、B、A、End | 0 / 1 |
| 快照资格、末阶段提交 | 0 / 10 | Begin、A、B、End | 0 / 0 |
| 快照资格、末阶段提交 | 10 / 0 | Begin、B、A、End | 0 / 0 |

每个进程四条原始回调记录共享同一个实际 `Engine.get_physics_frames()` 值（本次均为 1）。记录还包含实际节点优先级、处理组、进入回调时的 HP 与资格；最后通过 `get_children()` 读取真实子节点顺序。立即模式第二名角色进入时已见到第一次伤害；分阶段模式两者资格都来自 Begin 的同一快照。End 在已收集资格后提交伤害，不重新用中途 HP 否决第二个意图。

因此，换优先级确实改变了**引擎实际分发的 actor 顺序**；同时结算政策的结果不随这两种顺序改变。但这是应用代码划分的阶段，不是引擎提供的原子事务，也不是所有游戏都应采用的架构。分阶段事件的实际追加顺序仍会变化；本例保证的是规范化内容，而非相同发出次序。

[独立复验](../../research/experiments/godot-combat-policy/review/REVIEW.md)用最终源码重新执行四个进程，并直接解析原始 TRACE / RESULT，核对字面 HP、伤害/死亡记录、资格与回调轨迹。三项独立启动负例（`-O`、不可执行文件导致实际启动错误、成功退出但缺少结果的假工具）均拒绝且移除旧 PASS；它们不是额外 Godot 行为案例，也未注入超时。初版树序仅回显常量的取证弱点及后续修正/重复记录被保留，不能把重复四例写成更多独立场景。

新的二进制摘要仍为 `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`；自报源码身份与公开官方标签的差异仍[未解决](../../research/source-notes/godot-runtime-provenance.md)。[Godot 4.6 Node 文档](https://docs.godotengine.org/en/4.6/classes/class_node.html#class-node-property-process-physics-priority)及[固定官方比较源码](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/main/scene_tree.cpp#L1151-L1209)支持优先级/分发机制的来源分析，不认证本地程序来源。没有测试相同优先级、跨处理组、真实碰撞、第二 tick、并发、网络或性能；Python 模型中的初始死者与下一 tick 检查不能挪算成引擎测试。

## 取舍与失败模式

保留欠账不丢逻辑但增加响应延迟；丢弃累计时间可保护本地交互，却改变墙钟与游戏钟映射，须同时重映射输入时间并记录丢失量；权威联机不能由各客户端自行跳 tick。只加 K 限制却仍用 `A/h` 插值会外推；共享可变快照会使 previous 与 current 实际相同。不同渲染帧率下直接采样按钮并重放同一按钮状态，则可能多触发攻击。

## 验证范围与验收矩阵

2026-10-31 在 Python 3.12.14 上实际运行了原创、无引擎依赖的 `Fraction` 调度模型，8 项测试通过：不同渲染分片、半 tick 余量、过载欠账、单次边沿消费、只读插值、负时间与非法步数预算拒绝及实时采样不具帧率不变性的反例。[实验脚本](../../research/experiments/fixed-step/test_fixed_step.py)、[原始测试输出](../../research/experiments/fixed-step/test-output.txt)与[环境和范围](../../research/experiments/fixed-step/README.md)已归档。这只验证该离散模型，不验证 Unity 调用顺序、物理后端或跨平台浮点确定性；下表仍包含待执行的引擎集成检查。

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

## 有种子的对抗性复核

[独立模型审查](../../research/experiments/deep-model-qa/README.md)使用200个预测调度和200个固定步调度、独立状态/事件判据及4类故障变异；原始输出含模型内容哈希。该结果加强有限模型证据，不替代真实输入、网络、引擎或物理集成。

## Godot 4.6.3 实际回调集成补充

2026-10-31 使用 `4.6.3.stable.official.7d41c59c4` 实际运行原创无头夹具：唯一 `_physics_process` 调度者以60 Hz消费规范化tick输入，`_process` 只读数值快照，不再叠加自建累加器。六个进程分别使用 `--fixed-fps` 与 `--max-fps` 的30/60/144配置；全部运行到120规则tick，逐tick整数状态与独立Python判据一致，最终x=-30、攻击事件[6,8]，tick9边界事件不生效。原始计数、版本、命令、配置和输出见[实际引擎夹具](../../research/experiments/godot-fixed-step/README.md)。集成复核还断言低频多步/高频零步确实发生、每帧tick与steps一致，并核对数值插值和核心/previous快照只读。

人工固定时间组的主回调数为60/120/289，并不等于实际显示帧；Godot官方CLI说明 `--fixed-fps` 关闭实时同步，本机约0.2秒墙钟就完成约2秒模拟。`--max-fps` 组按实时上限运行约2秒，主回调数与启动/调度有关，不保证精确目标频率。这里比较的是相同规则tick终点，而非相同墙钟时刻。

此结果将“单调度者、规范化输入、只读表现”的证据推进到真实Godot回调，但没有运行设备输入、可见渲染、物理刚体、跨平台/不同构建或Unity；也没有测试卡顿欠账策略。不能把原文自定义Python调度器的保留欠账语义归给Godot。整篇仍为source-backed，以上有限夹具结果为实际执行证据。

官方定位：[Godot4.6 Idle and Physics Processing](https://docs.godotengine.org/en/4.6/tutorials/scripting/idle_and_physics_processing.html)、[Godot4.6 CLI reference](https://docs.godotengine.org/en/4.6/tutorials/editor/command_line_tutorial.html)；访问2026-10-31。

## 暂停不等于清空应用输入队列：Godot 4.6.3 反例

新增真实引擎夹具以 `Input.parse_input_event(InputEventAction)` 合成三组按下/释放，经引擎 `_input` 分发。常驻ALWAYS输入适配器仍能在场景暂停时收集攻击，而显式PAUSABLE玩法节点不执行固定回调。三个30/60/144人工主帧配置均观察到：朴素队列在恢复后的玩法步执行了暂停前未消费与暂停期间的两次旧攻击；暂停/恢复边界清队列并递增输入代次的对照队列只执行恢复后的新攻击。

这证明“暂停玩法消费者”不足以约束另一个常驻节点的应用队列，不是Godot自身偷偷缓存攻击。原始日志同时检查暂停期间至少2次ALWAYS固定心跳出现时玩法tick仍不变、真实输入接收列表，以及新输入前的已消费列表。实验没有物理键盘/手柄输入，也没有验证真实5秒暂停补时；`--fixed-fps` 为人工时间。组合策略中的epoch过滤未被异步旧投递单独触发，不能推导它会识别恢复后才收到且被标成新epoch的旧设备事件。

工程上应明确攻击、移动持有态及菜单输入各自的暂停策略，并通过单一暂停入口协调输入上下文、队列和代次；暂停节点仍可能接收信号，不是全局业务写屏障。来源：[Godot4.6暂停模式](https://docs.godotengine.org/en/4.6/tutorials/scripting/pausing_games.html)、[Input API](https://docs.godotengine.org/en/4.6/classes/class_input.html)、[InputEventAction](https://docs.godotengine.org/en/4.6/classes/class_inputeventaction.html)，访问2026-10-31。

[夹具、来源与原始证据](../../research/experiments/godot-pause-input/README.md)。

## 表现跳转不是规则事件重放：实际方法轨观察

[六进程动画夹具](../../research/experiments/godot-animation-events/README.md)使用本地已安装、自报 4.6.3 的同一字节身份程序，显式 MANUAL 推进与 IMMEDIATE 方法模式；方法只记录标签，没有真实伤害或物理。两个键位于 0.25（A）与 0.6（B）。`seek(0.75, true, false)` 再 `seek(1.0, true, false)` 得到 **B,B**；从相同初态 `advance(0.75)` 再 `advance(0.25)` 得到 **A,B**。两者属性采样与播放位置相同，完成信号却分别为 0 和 1。

这纠正了初始“seek 跨越方法键就不会调用方法”的过强推断。失败判据、原始输出、修正后的四例及新增两标签例全部保留；不是把错误预期悄悄改成通过。另两例说明在该配置下，恰落键位的 seek 可以调用方法，而 `update_only=true` 抑制该方法但仍更新属性。

因此，用表现位置追赶模拟时间不能证明规则事件已按区间完整交付或恰好一次；是否补算、跳过、去重，仍需应用合同。不能反向断言动画事件永远不应参与玩法，更不能把 IMMEDIATE 当作生产默认建议。本实验不覆盖 DEFERRED、循环、倒播、混合、AnimationTree、其他构建或引擎。

官方固定提交的实现只作语义参照，与本地二进制的精确来源对应尚未建立；详见[身份取证](../../research/source-notes/godot-runtime-provenance.md)。[独立复核](../../research/experiments/godot-animation-events/review/README.md)使用原始 CONFIG/TRACE/SIGNAL 重新验收，不把同摘要复跑变成发行真实性认证。
