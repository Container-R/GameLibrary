# Unreal Notify 执行资格与权威请求：来源边界

访问日期：2026-11-01。对应[固定 Tick 与引擎表现边界](../../solutions/programming/fixed-step-simulation-boundary.md)的源文本补充，不是 Unreal 运行报告。

## 执行资格与权威判定

既有固定步文章中的方法轨观察不验证 Unreal 的事件资格。这里是另一个**仅经官方文本核对**的边界：事件已经放在正确的动画位置，不表示它在承担规则职责的机器上具备执行资格。

Epic 的 5.6 文档列出权重、概率、LOD、同步组 follower 与专用服务器等 Notify 条件；生成的 `AnimNotifyEvent` API 说明，关闭专用服务器触发会在 dedicated server 上跳过该 Notify。不能从编辑器或客户端的一次回调反推服务端具备同样条件。[Notify 属性](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-notifies-in-unreal-engine?application_version=5.6)、[专用服务器属性](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AnimNotifyEvent?application_version=5.6)

**原创条件例子，未执行：**某攻击使用普通 Animation Sequence 中的自定义 Notify；项目把**服务端本地的这个处理器**设为请求权威命中判定的唯一入口，没有客户端转发、RPC 或其他请求路径。若该事件关闭专用服务器触发，作者预期的唯一入口就与资产资格配置冲突。客户端预览播放成功不能补上这个缺口。这不是实际丢失命中的报告，也不反驳“客户端产生请求、服务端验证”的合法架构——后者已经改变了例子的唯一入口前提。

### 原创配置／职责接收清单（未执行）

| 要核对的交接 | 应保留的具体信息 | 不能据此跳过的判断 |
|---|---|---|
| 动画资产 → 规则入口 | 实际序列、Notify 身份及专用服务器触发配置；规则要求在哪个 world／角色执行 | 客户端出现回调，不证明服务器本地入口执行 |
| 动画求值 → 事件资格 | 该事件的权重阈值、概率、LOD、follower 设置及实际求值上下文 | 不能把表现优化条件默认为强制规则请求的业务条件；也不假定所有 Notify 类型共用相同过滤路径 |
| 处理器 → 权威判定 | 攻击身份、执行位置、收到的意图、服务端合法性与命中判定结果 | 处理器运行不是碰撞成立、伤害提交或重复处理已被防止的证据 |
| 改配置 → 验收 | 改动前后的资产配置、请求路径与结果记录 | 打开服务器触发只移除这一项明确排除，不能证明其他求值和规则前提全部成立 |

Unreal 的网络说明把服务端权威世界与各客户端世界分开；它并未给每个 Notify 自动建立请求、验证和复制链路。[Networking Overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/networking-overview-for-unreal-engine?application_version=5.6) 项目可以保留经验证的动画驱动入口，也可以由其他权威机制产生规则意图并保留表现 Notify；应说明各自的时间与资格合同，而不是统一改成计时器或一律禁止 Notify 参与玩法。

**Montage 的时序选择另行讨论。** 文档将 Queued 与 Branching Point 区分为异步／同步的执行方式，并明确提到后者可用于改变玩法的分支决定。更精确的时序不是过滤绕过、线程归属、网络权威或恰好一次交付的保证；这里也不把 Montage 的说明套到上述普通序列例子。[Common Notify Properties](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-notifies-in-unreal-engine?application_version=5.6)

本说明没有读取引擎调度实现或运行 Unreal，没有验证过滤先后、打断清理、命中检测或网络行为。关联文章的既有证据范围完全不变；本说明不修改其验证状态。

## 原始资料与定位

| Epic 原始页面 | 阅读位置 | 采用范围 |
|---|---|---|
| [Animation Notifies](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-notifies-in-unreal-engine?application_version=5.6) | Keyframe Editing；Common Notify Properties；另读 Montage Notify / Window | 事件资格与 Montage 时序是不同问题；支持玩法用途，不支持一律禁止 Notify 的结论 |
| [AnimNotifyEvent](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AnimNotifyEvent?application_version=5.6) | Editor Properties；trigger_on_dedicated_server | 专用服务器配置的明确排除条件；生成的构造签名不当作项目资产默认值 |
| [Networking Overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/networking-overview-for-unreal-engine?application_version=5.6) | Networking Architecture；Client-Server Gameplay Example | 不同 world 的职责和显式网络交接，不提供 Notify 特有的权威桥接机制 |

三个返回页面标题均标示 **5.6**；未建立具体补丁版本、发布日期或不可变实现提交。这些是版本选择网址，不是固定源码快照。Python API 页面标记 Experimental，虽给出 `AnimTypes.h` 定位，本次并未取得或检查该实现。读取正文，不声称观看视频或从图片得到实测结果。

## 原创推理与排除项

正文的唯一服务端本地入口例子和四行交接清单是原创、未执行建议。例子的关键前提是没有客户端转发、RPC 或另一条请求路径；仅仅由服务端决定伤害，不能推出所有发起回调都必须在服务端执行。回调、请求接收、合法性判断、命中与伤害提交应各自有证据，但本文没有实现该日志结构或安全协议。

文档中的异步／同步描述不被解释为工作线程合同；没有据此建立过滤优先级、Branching Point 绕过条件、打断后状态清理或精确交付次数。Montage Notify 的特定 Blueprint 播放节点要求也不泛化到普通序列自定义 Notify。

历史 4.27 页面曾用于检索辨别，但其中 Notify State 顺序说明未移植到本节。一个猜测的 C++ API 页面无法打开，没有借镜像或受限源码补齐实现结论。未执行 Unreal、网络、碰撞或伤害测试；旧 Godot 方法轨与根运动证据只对各自归档配置有效。
