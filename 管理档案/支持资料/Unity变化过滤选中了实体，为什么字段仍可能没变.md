# Unity变化过滤选中了实体，为什么字段仍可能没变

两名单位的速度原来都是3，只有A被减速到1。负责提示的系统设置了速度组件的变化过滤，却同时处理A和B。如果随后给两人都播放“已减速”，错误不一定出在筛选条件写反了，也可能是把“值得重新检查”当成了“这一名单位确实发生了变化”。

本文讨论Unity Entities文档中按数据块记录变化的机制，帮助读者把缓存刷新与逐实体业务判断分开。它是[缓存失效与重算](../../GameLibrary/引擎与工具/运行时系统/缓存与存档/Factorio缓存失效与读档后的重算.md)的可选引擎对照，不是Factorio的实现，也不继承[EnTT更新通知例子](改了组件字段，为什么缓存还没收到更新通知.md)的运行结果。本文依据访问时明确标为Entities 1.3.15的官方文档，未安装或运行Unity。

## 记录的是一块中的组件类型，不是每个字段的差值

在这里，组件是实体携带的一类数据，例如速度；archetype chunk可理解为ECS组织实体与组件存储的一个数据块。本文把它简称为“块”，不是地图上的地块。

官方说明，变化过滤作用于整块，而非逐实体。具有某组件类型写权限的工作访问该块时，即使没有真正改值，也会更新相应的变化版本。过滤命中因此是保守的候选范围，不是逐字段比较结果。[1][2]

这一点与“修改后发出事件”不同。业务事件可以表达某件事情发生过，例如速度从3降到1；变化版本表达的是某个检查基准之后，这块的这类数据可能被改过。后者适合减少不必要的检查，却不承诺告诉你谁被改了、改了多少、改了几次。

## A改了，为什么B也会进入处理

下面是原创纸面例子，不是Unity执行记录。先明确假设：

- A、B已经存在，确实位于同一个块，都有整数速度组件`Speed`，并满足查询的其他条件。具有相同组件不代表任意两个实体必定在同一块。
- 消费系统上次运行时已经记录两人的速度都是3。所谓消费系统，就是这次需要读取速度、判断是否显示提示的系统。
- 此后，具有`Speed`写权限的生产者访问该块，只把A改成1，B仍为3。生产者已经完成，消费者才读取；如何建立这一依赖不是本例演示内容。
- 不涉及首次运行、创建销毁、结构变化、组件启停、绕过正常ECS追踪的写入或其他写入者。

消费者检查这一块的`Speed`变化版本，A、B都可能成为需要处理的候选。随后读到的值分别是1和3。B被选中并不矛盾：版本记录没有为B单独保存“没有改变”这个事实。[1][2]

再构造一个独立变体：生产者仍以写权限访问该块，但两人的速度都保持3。按文档，这种访问也能更新变化版本。[2] 因而，候选集合非空，甚至不能单独证明“至少一个速度值确实不同了”。

对可以重复计算的显示缓存，多算一次B可能只是成本问题；对扣除资源、播放一次提示或累计任务次数，多处理一次却可能改变游戏行为。是否允许重复，必须由后续操作的含义决定，不能由过滤器名称替你决定。

## “自从上次”必须属于这次消费

`ArchetypeChunk.DidChange(ref ComponentTypeHandle<T>, uint version)`要求调用者提供比较基准。官方API说明，在系统中运行或调度job时，应使用该系统当时的`LastSystemVersion`。[2] 该值对应本系统上次运行的版本依据，不是上一张画面帧，也不是现实时间。[3]

因此，手写按块job时，要在调度前把消费系统的这个基准传进job，再针对所需组件调用`DidChange`。官方IJobChunk说明给出了这一用法：返回`false`时，可以跳过该块中受测组件的处理。[4] 本文不把内部版本比较简写成普通整数“大于”，也不假定版本号每帧加一。

这个“可以跳过”有范围。如果示例提示只依赖速度，检查速度足以决定要不要继续；若还依赖装备或规则配置，单独一个`Speed`结果不能证明整个派生结果仍有效。另一个常见问题是把任意系统的版本拿来比较：它即使类型正确，也不代表本消费者已经处理过相应数据。

系统管理的查询可通过`SetChangedVersionFilter`指定受测组件类型；它与系统版本的关系见`LastSystemVersion`说明。[3] 本文不据此推断系统之外自行创建和使用的任意查询如何设置初始基准。若是在已有查询上追加条件，还要注意该设置方法会替换已有chunk过滤配置；官方API指出加法式配置应使用`AddChangedVersionFilter`。[6]

## 要判断谁降速，还需要自己的比较

回到A、B的例子。假设项目只需要报告“这次观察到的速度，比上次消费时低”，可以在候选范围内比较每名实体的前后值。以下是项目策略的原创伪代码，不是可编译的Unity示例：

```text
以本消费系统的上次版本，检查这一块的 Speed：
    若没有可能更新，跳过这个只依赖 Speed 的检查。
    否则，逐个读取满足查询条件的实体：
        取当前整数速度，以及该实体上次已消费的速度。
        若当前速度更低，产生一次“本次观察到降速”的提示。
        保存当前值，供下一次消费比较。
```

在第一个纸面情形中，A是3→1，产生提示；B是3→3，不产生。第二个情形中，两者都为3→3，都不提示。这里假定每个实体的历史映射已建立并且有效；实际项目仍需设计首次观察、实体销毁与历史清理，不应把缺失的旧值随便当成零。

这种端点比较仍不是完整事件记录。如果A在两次消费之间先从3降到1，又恢复到3，两个端点相同，比较不会还原中间发生过的减速。若业务要求接收每一次转换，就应在拥有该转换的写入流程中记录业务事件，并单独处理顺序、重复与生命周期。不能让变化过滤器替代这些要求。

## 排查多余命中时，先查写权限

只读代码也可能被声明成可写，从而造成更多候选。对于本文使用的`ComponentSystemBase.GetComponentTypeHandle<T>`，`isReadOnly`参数默认是`false`；不需要修改时应明确请求只读。[5] 查询、job字段和取得的句柄也应保持相同的读写约定。[4]

这不是把所有地方改成只读的建议。实际写入必须保留正确权限；如果一个系统确实需要改A，整块中的B仍可能被保守地选中，这不是改声明就能消除的现象。是否值得再保存逐实体旧值、细分数据或重算缓存，要结合实际工作量测量。本文没有性能结果，也没有证明任何job依赖或线程访问安全。

可按问题顺序检查：先确认后续动作需要的是缓存刷新、两次观察之间的值差，还是每次业务转换；再确认比较基准属于哪个消费者；然后核对块、组件类型和读写声明。不要先把所有候选都当成“真的改了”，再靠补丁取消多余副作用。

## 参考来源与范围

以下均为Unity Technologies官方文档，2026年11月6日读取。链接使用`@1.3`入口，读取到的页面标题和包元数据明确写为Entities 1.3.15；这不是不可变补丁链接，也不代表所有后续版本。页面未给出单独发布日期。这里只核文档文字与接口声明，未编译C#、安装包、运行引擎或执行原始示例。

1. [EntityQuery filters](https://docs.unity3d.com/Packages/com.unity.entities@1.3/manual/systems-entityquery-filters.html#use-a-change-filter)，Use a change filter：整块粒度与写权限访问的保守判定。本文不照抄该页示例代码。
2. [ArchetypeChunk.DidChange](https://docs.unity3d.com/Packages/com.unity.entities@1.3/api/Unity.Entities.ArchetypeChunk.DidChange.html)，`ref ComponentTypeHandle<T>, uint`重载的Parameters、Returns与Remarks：明确比较基准、可能变化及版本更新范围。
3. [ComponentSystemBase.LastSystemVersion](https://docs.unity3d.com/Packages/com.unity.entities@1.3/api/Unity.Entities.ComponentSystemBase.LastSystemVersion.html)，Property Value与Remarks：本系统上次运行的依据及变化过滤关系。
4. [Implement IJobChunk](https://docs.unity3d.com/Packages/com.unity.entities@1.3/manual/iterating-data-ijobchunk-implement.html#skipping-chunks-with-unchanged-entities)，Skipping chunks with unchanged entities及调度前的访问声明说明。采用文字合约；其中输出句柄的只读标记与后续写入不一致，本文没有照抄该示例。
5. [ComponentSystemBase.GetComponentTypeHandle](https://docs.unity3d.com/Packages/com.unity.entities@1.3/api/Unity.Entities.ComponentSystemBase.GetComponentTypeHandle.html)，Declaration与Parameters：该接口的默认访问模式。
6. [EntityQuery.SetChangedVersionFilter](https://docs.unity3d.com/Packages/com.unity.entities@1.3/api/Unity.Entities.EntityQuery.SetChangedVersionFilter.html)，Remarks：设置已有查询过滤时的替换语义与加法接口指引。

---

[返回缓存主文](../../GameLibrary/引擎与工具/运行时系统/缓存与存档/Factorio缓存失效与读档后的重算.md) · [返回缓存与存档书架](../../GameLibrary/引擎与工具/运行时系统/缓存与存档/README.md)
