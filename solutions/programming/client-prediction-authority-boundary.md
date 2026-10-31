---
id: SOL-NET-001
title: 客户端移动预测的权威边界与确认重放契约
type: solution
status: source-backed
primary_discipline: NET
related_roles: [network-programmer, gameplay-programmer, qa-engineer]
related_topics: [client-prediction, server-reconciliation, entity-interpolation, fixed-timestep]
engines: [engine-agnostic, Unity]
versions: ["Netcode for Entities 1.4.1 文档", "Netcode for GameObjects 2.2.0 历史文档"]
updated_at: 2026-10-31
verification_method: 原始来源核对与原创离散协议模型16项测试；未进行引擎、真实网络或跨平台物理验证
sources:
  - https://www.gabrielgambetta.com/client-side-prediction-server-reconciliation.html
  - https://www.gabrielgambetta.com/entity-interpolation.html
  - https://docs.unity3d.com/Packages/com.unity.netcode@1.4/manual/intro-to-prediction.html
  - https://docs.unity3d.com/Packages/com.unity.netcode@1.4/manual/prediction-details.html
  - https://mp-docs.dl.it.unity3d.com/netcode/2.2.0/advanced-topics/client-anticipation/
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
4. 重放只计算状态，不重复发网络请求、扣永久资源或执行不可逆效果。一次性预测声音/粒子仅首次执行；被服务器否决的可撤销预测效果需要撤销标记，而不是靠去重就解决。击杀、奖励、交易等持久副作用等待权威确认并具备幂等标识。
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
