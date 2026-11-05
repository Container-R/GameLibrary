# UE 的可靠开火通知到了，武器模式为什么还是旧的

服务器把武器切到蓄力模式，再发出可靠的开火通知，客户端却播了普通枪口效果。先别急着把所有消息都改成 Reliable：通知里的动作与处理器读取的武器状态，可能根本不走同一条更新路径。

这份说明依据 Unreal Engine 5.5 文档，讨论已存在且正确配置复制的对象，不涉及刚生成对象、网络休眠或断线。RPC 是让远端执行函数的调用；“可靠”不能代替应用判断：**这次函数读到的状态，是否属于这次动作。**

## 两条调用有顺序，属性仍可能在后面

设客户端当前的武器模式为普通。服务器对同一个角色 Actor 按以下顺序操作：

1. 发出可靠的“开始举枪，动作7”调用，接收端只记下举枪阶段。
2. 把该角色 Actor 上的独立复制属性 WeaponMode 改为蓄力。
3. 发出可靠的“显示开火，动作7”调用，接收端读取 WeaponMode，选择枪口效果。

两条都是发给拥有该 Actor 的同一客户端的 Client RPC，使用默认发送策略；例子把三步限定在同一次相关网络更新内，没有特殊排队调用。它是原创条件推演，没有运行引擎。

UE 文档保证同一 Actor 的可靠 RPC 保持相互顺序；Actor 与其子对象也在本页讨论的范围内。但属性更新另有安排：普通非排队 RPC 排在属性数据之前，排队 RPC 在后。[1] 因而这里允许出现：客户端先处理举枪，再处理开火，随后才应用蓄力模式。两个可靠调用没有倒序，开火处理器仍可能读到旧模式。

这个例子的错处，是把“服务器先给属性赋值”理解成“客户端执行后续 RPC 前已经应用该值”。增加一条可靠的准备通知，并没有把 WeaponMode 自动变成开火调用的参数。不同 Actor 之间还没有全局 RPC 调用顺序保证，不能把拆开的武器和角色当成一条队列。[1]

也不要反过来背诵“RPC 永远先于属性”：文档另有排队调用、发送策略及丢失更新的情况。[1][2] 上面的排列只用于反驳一种依赖假设，不预测任意报文的到达顺序。

## OnRep 先后，也不是缓存准备顺序

另一个常见设计是分别复制 WeaponMode 和 ActionId：模式的 OnRep 回调重建枪口效果缓存，动作的 OnRep 回调使用缓存播放。不同变量的 OnRep 没有确定先后。[1] 若动作回调先运行，它可能消费尚未重建的缓存。

注意，这不等于另一个复制字段必然尚未赋值。**字段已应用、回调已运行、派生缓存已准备好，是三件事。** 调整字段声明位置不能建立这条业务依赖。文档建议将相关字段放进结构体，或收集更新后再处理；这有助于集中安排处理，却不是跨 Actor 的原子事务，也不保证外部资源已经可用。[1]

## 让动作使用属于自己的模式

回到这次枪口提示，如果它需要的是“动作7开火时的模式”，可以让开火通知同时携带动作身份与模式，处理器据此选择表现，而不是临时读取客户端的最新模式。这是应用设计选择，会增加消息内容；它没有替对象有效性、资源准备或权限检查作保证。

若表现必须依赖另行复制的持续状态，就要确认该状态与动作匹配，再从同一个入口准备缓存和更新表现。不能只等“任意一次 OnRep 已发生”，也不能无限等待可能已被后续状态取代的旧模式。

先做一个决定：这次提示消费的是随动作带来的模式，还是另行取得且明确匹配的状态？把这个关系写清楚，才知道应调整消息内容，还是调整接收处理；单改 Reliable 标记解决不了它。

## 来源与适用范围

2026-11-05 阅读以下官方 5.5 文档。版本标签是文档范围，不是本库验证过的引擎构建身份；上述武器例子与设计选择为原创、未执行推演，没有网络或引擎实测。

1. Epic Games，[Replicated Object Execution Order](https://dev.epicgames.com/documentation/unreal-engine/replicated-object-execution-order-in-unreal-engine?application_version=5.5)。Replicated Using Order、Order Across Actors、Order Inside an Actor、Order Between Actor and Subobjects、RPC Send Policy、Order Between RPCs and Actor Properties。已阅读全文；不采用其中未注明可靠性的跨 Actor 全排列作更宽保证。
2. Epic Games，[Remote Procedure Calls](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-procedure-calls-in-unreal-engine?application_version=5.5)。开篇、Types of RPC、Matrix of RPC Execution、Reliability、Send Policy；用于调用前提和发送策略，不把简写的可靠性描述解释为全连接屏障。

[返回客户端移动预测正文](../../GameLibrary/网络与在线服务/实时同步/移动预测/客户端移动预测与服务器纠正.md)
