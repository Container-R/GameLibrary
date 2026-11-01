---
id: SOL-NET-001
title: 客户端移动预测的权威边界与确认重放契约
type: solution
status: source-backed
primary_discipline: NET
related_roles: [network-programmer, gameplay-programmer, qa-engineer]
related_topics: [client-prediction, server-reconciliation, entity-interpolation, fixed-timestep, replay-dependencies, partial-snapshots, rpc-ingress, queued-sender-identity, prediction-barrier, host-frame-advance]
engines: [engine-agnostic, Unity, Godot]
versions: ["GGPO source 7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a", "Netcode for Entities 1.4.1 文档", "Netcode for GameObjects 2.2.0 历史文档", "Godot 4.6.3.stable.official.7d41c59c4 本机自报；发行及源码对应未认证"]
updated_at: 2026-11-01
verification_method: 原始来源核对与既有原创离散协议模型16项测试；跨实体依赖补充为未执行手算与验收提案；新增本机自报Godot4.6.3双进程回环RPC入口与应用授权观察及独立重复，保留初次解析失败；另核对固定GGPO回放、宿主输出及正常推进屏障，控制流与验收矩阵未执行；未验证实际预测纠正、WAN、Unity或跨平台物理
sources:
  - https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/doc/DeveloperGuide.md
  - https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/include/ggponet.h
  - https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/lib/ggpo/sync.cpp
  - https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/lib/ggpo/backends/p2p.cpp
  - https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/apps/vectorwar/vectorwar.cpp
  - https://www.gabrielgambetta.com/client-side-prediction-server-reconciliation.html
  - https://www.gabrielgambetta.com/entity-interpolation.html
  - https://docs.unity3d.com/Packages/com.unity.netcode@1.4/manual/intro-to-prediction.html
  - https://docs.unity3d.com/Packages/com.unity.netcode@1.4/manual/prediction-details.html
  - https://mp-docs.dl.it.unity3d.com/netcode/2.2.0/advanced-topics/client-anticipation/
  - https://docs.godotengine.org/en/4.6/classes/class_multiplayerapi.html
  - https://docs.godotengine.org/en/4.6/classes/class_enetmultiplayerpeer.html
  - https://docs.godotengine.org/en/4.6/classes/class_callable.html
  - https://docs.godotengine.org/en/4.6/classes/class_node.html
---

# 客户端移动预测的权威边界与确认重放契约

## 要解决的问题

本地角色必须迅速响应，但客户端位置不能成为服务器事实。收到较旧的服务器结果时，直接覆盖当前预测位置会倒退；对同一输入反复重放又可能重复播放音效、产生伤害。本方案限定为服务器权威、单角色离散运动，给出可审计的协议契约。它不实现命中延迟补偿，不宣称完整防作弊，也不替代具体引擎的预测框架。

## 来源实际支持什么

Gambetta 的 *Server reconciliation* 用输入序号标识服务器已处理范围，客户端从权威状态重放尚未确认的输入；相邻的 *Entity interpolation* 将远端对象历史快照插值与本地预测分开。[S1][S2]

Unity Netcode for Entities **1.4.1** 描述了快照回退、重模拟及其 CPU 代价，还区分 owner-predicted 与其他客户端插值；部分快照只回退被更新实体，可能出现跨实体时序问题。[S3][S4] Netcode for GameObjects **2.2.0 历史文档**明确将 anticipation 定义为不含完整 rollback/replay 的简化路径。[S5] 这些版本事实不能推广成所有 Unity 包或未来版本的保证。

以下协议字段、拒绝策略与测试为原创设计推导，不是上述框架的线上报文格式。

## 最小协议和不变量

| 对象 | 字段与含义 |
|---|---|
| 命令 | `epoch, seq, axis`；epoch 隔离重连/重生，seq 在该 epoch 单调增加，axis 为有界意图 |
| 快照 | `epoch, serverTick, ack, movementState`；状态必须与 ack 对应同一次服务器结果 |
| 客户端历史 | 尚未被最终处理的命令，按 seq 排序；同时保存必要的版本、随机状态与预测依赖 |
| 表现事件 | `(epoch, seq, eventIndex)` 作为预测副作用身份；持久交易另走服务器确认路径 |

**ack 是连续最终处理前缀，不是收到的最大序号。** 若先收到命令 12 而 11 丢失，不能把 ack=12 发出却没有确定 11 的结果，否则客户端会误删 11。无效但序号合法的命令可最终处理为 no-op，或返回显式拒绝结果；不能永久悬置使客户端每次回退都重放它。

示例刻意不接受客户端 `dt` 或位置：每个服务器模拟步最多消费一个移动量子，突发到达 20 条命令不能获得 20 倍当帧速度。真实项目还要按已认证连接验证角色所有权、命令窗口、输入范围、状态机许可、资源与冷却，并限制历史/乱序缓存大小。连接认证、角色绑定和作弊检测不由本文模型覆盖。

## 客户端处理流程

1. 采集并编号意图，保存到有界 pending 历史；立即预测本地运动并发送命令。重新发送未确认命令只保证尽力恢复，不能承诺任意丢包条件下必然送达。
2. 收到完整可用快照后，先核对 epoch；忽略 `serverTick <= lastAcceptedTick` 的旧/重复快照。**相同 ack 但更新的 serverTick 不应直接丢弃**，环境碰撞、击退或平台移动可能已改变权威状态。
3. ack 不得倒退或超过本 epoch 已发送序号。以权威 movementState 替换模拟状态，删除 `seq <= ack` 的命令，按顺序重放其余命令。先恢复所有影响运动的字段，不能只恢复位置而保留错误速度、grounded 或跳跃冷却。
4. 将重放模拟与外部输出分离：不因重算重复提交外部副作用请求、扣永久资源或执行不可逆效果。对已经输出的同一有效预测声音/粒子，不因重算而重复输出；纠正后新增、先前未输出的有效事件须由另行定义的表现协调策略处理，不能将“避免重复”实现为无条件丢弃全部重放事件。被服务器否决的可撤销预测效果需要撤销标记，而不是靠去重就解决。击杀、奖励、交易等持久副作用等待权威确认并具备幂等标识。
5. 模拟状态立即纠正，视觉位置可另存偏移并平滑收敛；碰撞/后续预测不能读取正在平滑的视觉位置。大幅瞬移、重生应重置历史/显示状态，避免“从旧尸体滑回新位置”。

## 乱序、丢失与历史耗尽

附带模型在缺少下一个序号时保留乱序命令，并让**该角色**不消费新移动量子；服务器世界 tick 仍继续。这是便于验证 ack 契约的保守教学策略，不是实时运动的默认推荐。生产系统应定义输入 tick 与服务器时钟映射、有限等待期限和缺失输入规则：如重复已确认的持有输入或中性输入，并记录哪些命令已过期。采用这种策略时，快照/ack 的“已最终处理”语义也必须随之定义，不能只把教学模型改成跳 seq。

客户端历史达到上限时停止增加预测并请求重同步，明确显示连接问题；禁止悄悄删除未确认历史后仍声称能够精确重放。长 RTT 也增加重模拟工作量，需测量每帧重放 tick 数、CPU 时间和纠正距离，而非只看平均帧率。

## 本地预测不等于远端插值

本地拥有即时输入，故可先模拟；远端实体通常只有离散服务器样本，可延迟显示并在历史快照间插值。这里的“延迟”是有意的缓冲。它不是本地输入重放，也不能直接提供射击命中判定。远端也可在有足够输入/模型时预测，但这是额外选择，不能宣称“远端永远无法预测”。

## 实际模型验证与未验证边界

原创 Python 标准库模型位于 `research/experiments/client-prediction/test_prediction.py`；运行方式：

```sh
python3 research/experiments/client-prediction/test_prediction.py
```

2026-10-31 实际运行 **16 项通过**，记录见同目录 `test-output.txt`：

- 确认前缀删除与后缀重放；乱序不能越过缺口确认；重传不重复运动。
- 旧快照丢弃；较新快照相同 ack 仍接受纠正；无效输入最终处理为 no-op。
- 重放不重复表现效果；旧 epoch 被拒绝；历史耗尽明确报错。
- 超出已发送序号或倒退的 ack 被拒绝；突发命令最多每服务器 tick 消费一条。
- 命令/快照类型与整数边界检查，拒绝布尔或浮点序号；错误快照不能先修改状态；命令窗口及零 tick/ack 边界。

表现测试以追加日志计数，重放不得追加发射记录；此日志仅用于有限测试审计，会随输入增长，不是生产去重缓存。运行时缓存需定义安全退休水位与 epoch 清理。

模型使用一维整数加法，没有 socket、丢包概率分布、碰撞世界、序号回绕、认证、客户端时钟同步或跨平台浮点。测试通过只验证该模型中的协议性质，**不证明真实游戏网络正确或反作弊安全**。下一步集成验收：加入真实阻挡/移动平台状态、不同 RTT/乱序/丢包、重连 epoch、历史溢出、敌对超速输入和副作用撤销；对每次纠正保存输入范围及状态差异。

## 重放依赖的时间归属：正确ack仍不足以恢复正确交互

现有单角色整数加法模型及16项测试不读取其他实体，仍按原合同有效；它们不能验证跨实体重放依赖。这里补充**来源核对与原创手算，没有新增执行模型或Unity运行结果**。

[Unity Netcode for Entities 1.4.1](https://docs.unity3d.com/Packages/com.unity.netcode@1.4/manual/prediction-details.html#interactions-between-predicted-ghosts-using-partial-snapshots)说明，部分快照可使被回退实体与仍保留较新状态的实体交互。[Gambetta原文的Odds and ends](https://www.gabrielgambetta.com/client-side-prediction-server-reconciliation.html)也提醒，多玩家场景中纠正后不匹配并不必然意味着作弊或非确定性。不能只检查输入后缀是否正确，还要问它读取了哪个时刻的世界。

**原创未执行反例**：A在整数格移动，每tick尝试+1；先读取该tick的B占用格，目标格等于B时A不动。权威基线tick0为A=0、ack=0；本例仅约定seq1/seq2分别在tick1/tick2消费，不推广成seq等于serverTick。

|重放的依赖|tick1：B格→A结果|tick2：B格→A结果|
|---|---|---|
|各tick的B历史|1→0，被阻挡|3→1|
|B始终冻结为较新的tick2状态|3→1|3→2|

两行基线和输入相同，只差依赖时间。若稍后收到完整tick2、ack2、A=1快照，可以再次纠正；这不是永久失同步证明、物理碰撞实验或Unity ECS复现。

建议为纠正验收保留以下**原创逻辑信息，不是Unity报文schema**：

|信息|应确认的关系|
|---|---|
|基线stateTick与字段范围|所有需恢复状态属于哪个时刻，不能只恢复位置|
|最终处理命令边界|ack与权威状态对应，且含义为连续最终处理前缀|
|输入到tick的映射|明确何时消费及缺口策略，不把序号当时钟|
|依赖身份、时间与覆盖|本次重放读什么、各tick从何处取得，哪里缺历史|
|缺失历史政策|拒绝本次精确候选并重同步、有限等待，或显式近似|

拒绝精确候选不等于宣告服务器状态无效；等待需有容量/超时回退；近似可能引入误交互和更大纠正，必须标明，不能悄悄使用最新值却称精确重放。这些选择均未在本文实现，也不是要求全世界一起回滚。完整的[依赖验收矩阵、代价与来源定位](../../research/source-notes/prediction-dependency-time-contract.md)区分项目策略与特定引擎版本事实。

## 来源、定位与版权

访问日期均为 2026-10-31。仅保存原创分析、模型与链接，无第三方代码或图表转载。本文证据状态 source-backed，测试范围单独限定。

- **S1** Gabriel Gambetta，[*Client-Side Prediction and Server Reconciliation*](https://www.gabrielgambetta.com/client-side-prediction-server-reconciliation.html)，原作者文章，定位 Server reconciliation / Odds and ends；页面未明确发布日期。
- **S2** Gabriel Gambetta，[*Entity Interpolation*](https://www.gabrielgambetta.com/entity-interpolation.html)，定位 Entity interpolation / Summary；远端历史显示的解释，不将示例 100ms 当默认调参。
- **S3** Unity，[*Introduction to prediction*](https://docs.unity3d.com/Packages/com.unity.netcode@1.4/manual/intro-to-prediction.html)，页面元数据 **Netcode for Entities 1.4.1**，定位 CPU usage / Predicted and owner predicted modes / Rollback and replay。不同包版本需重新核对。
- **S4** Unity，[*Prediction edge cases and known issues*](https://docs.unity3d.com/Packages/com.unity.netcode@1.4/manual/prediction-details.html)，**1.4.1**，定位 Interactions between predicted ghosts using partial snapshots。本文模型未复现 ECS 部分快照。
- **S5** Unity，[*Client anticipation*](https://mp-docs.dl.it.unity3d.com/netcode/2.2.0/advanced-topics/client-anticipation/)，页面明确 **2.2.0** 且标注站点不再更新；仅作为历史版本对照，不据此评价当前包能力。

研究限制：Valve 的 Latency Compensating Methods 原页返回 403，未阅读、未引用其细节，也未绕过限制。

## 关联知识

[固定Tick与输入流](fixed-step-simulation-boundary.md)区分重放不变量与实际采样；[玩法程序交付](../../roles/programming/gameplay-programmer.md)用于明确集成与验收责任。

## 有种子的对抗性复核

[独立模型审查](../../research/experiments/deep-model-qa/README.md)使用200个预测调度和200个固定步调度、独立状态/事件判据及4类故障变异；原始输出含模型内容哈希。该结果加强有限模型证据，不替代真实输入、网络、引擎或物理集成。

## RPC 入口补充：可远程调用，不等于有权修改这个角色

前面的 16 项整数协议测试验证确认、重放与有限输入窗口；跨实体时间依赖部分仍是未执行提案。下面新增的是 **本机自报 Godot 4.6.3 的本地双进程 RPC 入口实验**，不把它当作预测、纠正、移动或物理集成的证据。

### 三种身份不能合并

[Godot 4.6 的 `any_peer`](https://docs.godotengine.org/en/4.6/classes/class_multiplayerapi.html#enum-multiplayerapi-rpcmode) 允许其他 peer 调用被开放的方法。它没有替项目定义“这个 peer 能控制哪个角色”。另一个容易遗漏的边界是：[`get_remote_sender_id()`](https://docs.godotengine.org/en/4.6/classes/class_multiplayerapi.html#class-multiplayerapi-method-get-remote-sender-id) 属于当前 RPC 上下文，离开该调用后不能再把新读取的结果当作原始发送者。

应分别记录：

| 层次 | 本实验观察或设定 | 不能替代什么 |
|---|---|---|
| 节点 RPC authority | 两端同名 Endpoint 的 authority 都是服务器 ID `1`；`submit` 明确开放 `any_peer` | 不是每个游戏角色的所有权表 |
| 实际调用者 | 在 `submit` 入口立即读取真实 peer ID，并由服务器复制进待处理记录 | 不是客户端自报的 actor、owner 或账号身份 |
| 应用规则授权 | 服务器自己的 `{A: client, B: server}` 映射，以及整数轴值 `-1/0/1` | 不是网络库自动提供的反作弊结论 |

peer ID 是这次连接中的标识，不是已认证用户。本实验显式关闭对象解码，但没有实现账号认证。

### 实际收到三条请求，规则只接受一条

原始场景只含普通 Node。两个进程请求绑定 `127.0.0.1` 的两个固定非零端口，并读取实际本地端口；没有扫描、端口重试或外部服务器。客户端逐条等待实际 outcome，随后才发送下一条命令。

服务器入口只捕获 sender、复制数据、排队；两种算术处理都在 deferred 回调内进行。每条请求都实际进入 RPC，入口 sender 为客户端；回调中保留的 sender 仍为客户端，而重新读取的上下文 sender 为 `0`。这不是“一定延迟整帧”的证据。

| 请求 | 不检查所有权/范围的累计结果 A/B | 服务器规则结果 | 规则累计结果 A/B |
|---|---:|---|---:|
| `A, +1` | `1 / 0` | 接受 | `1 / 0` |
| `B, +1` | `1 / 1` | 拒绝：角色不属于发送者 | `1 / 0` |
| `A, 10000` | `10001 / 1` | 拒绝：超出本例轴值范围 | `1 / 0` |

这些整数是原创教学状态，不是实际位移或伤害。实验没有通过让客户端自报 sender 来伪装身份；第二条请求故意指向另一个角色，第三条使用超界整数。代码显式检查 Variant 类型，纯检查覆盖有限类型替换；没有追加布尔或浮点网络输入场景。

发送 API 返回成功与对端实际处理分开记录。最后一条 outcome 到达客户端后，客户端发出 finish；服务器实际收到确认后，两端终态还须通过父进程检查，才由父进程创建 STOP。这里共有 **3 次命令 RPC、5 次控制 RPC**，不是 8 个网络包，也不是可靠性压力测试。

### 可交付给网络与玩法团队的最小检查表

以下是原创项目验收建议，不是已经执行的生产网络方案：

1. **入口复制身份，而非延后查询。** 若要跨队列处理，把实际 sender 与有限请求字段一起存入服务器拥有的记录；不要稍后再读上下文 getter，也不要信任 payload 中的 owner。连接重建后如何失效这份身份，需要另行规定，本实验未覆盖。
2. **分别定义开放入口与对象授权。** 对每种命令写清开放给谁、目标对象由谁控制、权限在哪个时刻判断。节点 authority 与游戏对象所有权可能不同，不应复用一个布尔变量掩盖两层判断。
3. **先验证类型和范围，再改变权威状态。** 本例先做严格 Variant 类型检查，避免 `int()` 把浮点或布尔转换为“合法整数”；再查服务器映射和轴值范围。不要把本例范围或静态映射照搬到真实技能、载具与观战系统。
4. **证明拒绝没有产生规则效果。** 同时保留入口、决定和前后状态，而不是只统计“服务器收到了三条消息”。若系统有日志、奖励或表现副作用，需另设对应的拒绝判据；本实验只有两个整数累计器。
5. **把排队成本写进设计。** 捕获身份不等于允许无限排队。生产方案仍需容量、过期、断线、所有权转移、速率与重复命令策略；这些代价没有在三条 stop-and-wait 请求中得到测量或解决。

### 证据与失败边界

[可复查原始场景、双方输出及静态 consumer](../../research/experiments/godot-rpc-authority-boundary/README.md) 保留 23 条服务器事件和 13 条客户端事件，绑定源码、命令、实际退出状态和原始 JSON。初次 author attempt 因错误地向 `Callable.rpc_id()` 的 void 返回值赋值而出现 4 个解析错误：服务器未 READY，客户端未启动。这是实验代码错误，不是网络拒绝或引擎缺陷；失败没有被改记为成功。随后仅将 4 处发送改为返回 Error 的 `Node.rpc_id(peer, method, ...)`，原协议、端口、判据及超时保持不变。

修正后的 author sequence 和独立同源重复各有 1 个服务器、1 个客户端，全部正常退出且 stderr 为空。计入首次解析失败，合计 3 次版本查询、3 个服务器进程、2 个客户端进程；只有 2 次交换被接受，仍是同一套三命令配置，而非 8 种情景。纯合成变异、预置合成旧 PASS 的 `-O` 启动拒绝均不是网络运行。后者使用改正 Callable 调用前的源码快照，只证明相同 runner 的前置启动保护。

已安装二进制的 SHA 与自报版本已记录，但它与用于比较的官方源码提交没有完成来源认证。该有限回环实验不证明账号安全、通用反作弊、丢包/重连、重放去重、WAN 表现、预测纠正、物理确定性或其他引擎行为。更完整的[来源定位与分层证据说明](../../research/source-notes/godot-rpc-authority-boundary.md) 将原始文档、源码比较和实际观察分开。

## 补充：模拟重放不等于表现输出重放

**本节只核对固定 GGPO 源码和文档，验收表是原创未执行建议。** 本文前面的权威服务器纠正模型与 GGPO 的对等端回滚不是同一协议；不能把前者的确认、epoch 或事件身份字段当成 GGPO 内建接口。原16项模型测试不变，也不因本节获得声音、粒子或 GGPO 运行证据。

### SDK 恢复了什么，没有替应用完成什么

固定于 `7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a` 的 [GGPO 开发指南](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/doc/DeveloperGuide.md#separate-updating-game-state-from-rendering-in-your-game-loop)要求分离模拟与渲染，并将回滚期间产生的声音/效果延后处理；只有不影响游戏结果的表现部分才可排除在游戏状态之外，模拟使用的随机数状态需保存。指南也提醒，短暂视觉事件可能在追赶中耗尽，玩家根本没有看到它；这不是“只显示最终状态”总能保留反馈的保证。

[回调头文件](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/include/ggponet.h)把保存、恢复和逐帧推进交给应用。[Sync::AdjustSimulation](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/lib/ggpo/sync.cpp)恢复旧帧后反复调用推进回调，再结束追赶；所读路径没有提供音频投递确认或应用交易提交。**追赶结束不等于持久奖励已经得到权威确认。**

### 正常推进还有一道门：预测上限拒绝不能被后续成功覆盖

以下仍是同一固定 GGPO 提交的 **P2P 源码分析**，限定初始同步已完成、一个有效本地玩家的正常前进路径；不适用于回滚回调或 spectator，也不借用前文服务器 ack 的含义。

记当前帧为 F、内部最后确认帧为 C、配置预测上限为 M。[`Sync::AddLocalInput`](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/lib/ggpo/sync.cpp#L57-L77) 在 `F >= M && F−C >= M` 时拒绝，且拒绝发生在本次队列写入之前；P2P 层将其映射成 `GGPO_ERRORCODE_PREDICTION_THRESHOLD`。

容易误接的是下一步：[`SyncInput`](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/lib/ggpo/backends/p2p.cpp#L263-L338) 不重复这个屏障检查。初始同步完成、内部输入队列及断言前提成立且调用正常返回时，它走到 OK，并不表示先前遭拒的本地输入被补接纳。取得同步输入与获准执行这个正常模拟步，不能合并成最后一个返回码。

**原创条件例，未执行：** 若 M>0、F=M、C=0，两项拒绝条件同时成立。此算式只说明分支条件，不证明已构造出相应网络历史，也不保证继续调用同步接口一定正常返回。

正常步的接收逻辑应保留第一处失败，而不是让后一次调用覆盖它：

1. 提交本地输入；若失败，结束**本次正常前进分支**，不要为这一分支更新玩法或通知 GGPO 前进一帧。
2. 只有提交成功，才取得同步输入；再次成功后，用返回的输入更新玩法，再通知 GGPO 完成该帧。
3. 将绘制与会话服务安排在各自路径；不要因为第 1 步拒绝，就把网络服务也停掉。

这是从上游 [VectorWar 的正常循环](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/apps/vectorwar/vectorwar.cpp#L395-L439)提炼的有限控制流，不是可直接粘贴的完整集成。尤其 `ggpo_idle` 可能处理回滚，因此“此次不正常前进”**不是所有游戏状态被冻结**。失败期间的短按要保留、重采样还是消费，仍须应用另定，不能从示例推出无丢输入或必然恢复。

本补充没有执行 GGPO、制造迟到输入或测量停顿；不处理多个本地玩家的部分提交、其他后端、断连策略或最佳预测窗口。它新增的是正常推进门禁的具体位置，不改变既有模型与 RPC 实验的证据范围。

### “不重复播放”与“不丢新事件”是两个条件

先前已经输出的预测事件，不应仅因重算同一事件就再次播放；但纠正后的重放也可能产生原先不存在的有效事件。若把所有重放一律静音，可能把后者一起丢掉。反过来，每次模拟调用都立即输出，会重复旧事件，也无法通过恢复状态撤回已经听到的声音。

因此需要应用自己定义事件的可比较身份、有效性变化、延后与撤销策略。下面是待执行的验收问题，不是 GGPO 已提供的算法；也不宣称所有效果都适合撤销或延后。

| 情况 | 原创接收条件与需保留的证据 | 不能据此声称什么 |
|---|---|---|
| 同一有效事件再次模拟 | 分开记录逻辑事件与实际输出调用，检查没有因重算重复输出 | 状态相同或集合去重不自动证明实际调用只有一次 |
| 纠正后新增短事件 | 记录其此前不存在、重放后有效，以及选定策略何时将它交给表现层 | 只看最终状态不能证明中间事件被看到或听到 |
| 旧预测事件失效 | 明确可撤销部分、不可撤销部分及补偿/淡出等项目政策，记录实际结果 | 删除日志不能撤回已经发出的声音；没有通用无痕撤销 |
| 影响规则的效果或随机性 | 将影响后续模拟的状态纳入恢复和重放判据；区分视觉装饰与实际命中/阻挡 | 名称叫粒子或特效，不代表它可排除在模拟之外 |
| 永久奖励或外部交易 | 使用另行规定的权威确认与幂等/事务证据，禁止从重放回调直接推导提交许可 | GGPO完成追赶不是服务器授权、数据库原子性或exactly-once保证 |

若准备集成，应先选择一个明确效果和输出接口，再冻结重复、新增、失效各自的预期。当前只有源代码路径和协议建议，没有运行 GGPO、网络对端、音频中间件或粒子系统；也没有新增任何生产投递或玩家感知结论。详见[来源与范围记录](../../管理档案/来源笔记/rollback-presentation-boundary.md)。
