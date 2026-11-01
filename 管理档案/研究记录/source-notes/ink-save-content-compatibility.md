# ink旧存档遇到新内容：路径恢复、警告传播与叙事验收

2026-10-31。**固定源码分析，没有执行ink运行时、编译故事或验证迁移成功。** 仓库inkle/ink，v1.2.1固定commit `35c63e52f1d36060930dc7ed3cfba38ea224b528`。本目录[能力门槛](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/research/audits/ink-runtime-gate/gate.md)说明没有找到可用运行时。以下“会进入某分支”都是给定源码条件的控制流分析，不是观察到某个故事修改后的轨迹。

## 核心结论

`LoadJson`正常返回、保存格式版本可接受、内部路径能找到对象、内容作者认可恢复位置，是四种不同证据。源码允许某些路径查找产生approximate结果并记录warning，但**不能简化为“warning不影响Continue”**：后续Continue可能提前失败、产生新的错误，或在没有onError处理器时因累计warning抛异常。反过来，即使路径完全精确，也没有证明这个位置在新剧情中的含义未变。

## 逐段调用链证据表

下列链接均为同一不可变提交；没有复制完整实现。

|阶段|已读位置|精确支持与边界|
|---|---|---|
|公开加载入口|[StoryState.cs 56–60](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/StoryState.cs#L56-L60)|先把JSON转换成字典，再LoadJsonObj，返回后才触发onDidLoadState。入口没有包住解析/加载/该回调的catch；事件触发不是全部宿主加载成功的认证。|
|保存格式检查|[StoryState.cs 25–26](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/StoryState.cs#L25-L26)、[704–712](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/StoryState.cs#L704-L712)|当前保存格式10、最低8；缺少或低于最低版本抛Exception。这里只读到下界判断，不等于未来保存格式整体受支持。|
|流与栈重建|[StoryState.cs 714–764](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/StoryState.cs#L714-L764)、[Flow.cs 18–28](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Flow.cs#L18-L28)、[CallStack.cs 230–243](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/CallStack.cs#L230-L243)|当前格式构造Flow并调用SetJsonToken；旧格式直接设置当前栈。SetJsonToken清线程后逐个构造Thread。不是先验证全量对象再原子交换的存档事务。单流分支存在两次Flow构造语句，不能据此给未执行故事报告固定警告次数。|
|保存container/index|[CallStack.cs 53–102](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/CallStack.cs#L53-L102)|读取cPath，ContentAtPath结果转container，恢复idx。obj为空直接Exception；approximate进入两种warning文字路径，分别根据container是否非空。previousContentObject则另走PointerAtPath。不能把所有保存指针当成同一种严格解析。|
|部分路径查找|[Story.cs 740–742](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L740-L742)、[Container.cs 229–274](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Container.cs#L229-L274)、[SearchResult.cs 10–16](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/SearchResult.cs#L10-L16)|Story转发根container查找；逐路径分量失败/类型不合适时标记approximate并停止，结果保留已到达对象。container属性只是obj的container转换；correctObj在approximate时为null。Thread用的container不是correctObj。该机制不是按对话含义或作者ID匹配。|
|另外的指针路线|[Story.cs 754–780](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L754-L780)、[StoryState.cs 775–778](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/StoryState.cs#L775-L778)|PointerAtPath对尾部数字index与其他路径分支处理。无对象，或非空请求只退到root，走Error；其他approximate走Warning。保存的currentDivertTarget也走此方法。别用Thread分支的判断条件替代这里。|
|选择对应线程|[Flow.cs 79–89](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Flow.cs#L79-L89)|当前choices若找不到活动thread，会从保存的choiceThreads新建Thread，复用上述位置恢复路线。只检查当前主指针不足以审查选择恢复。|
|警告与异常生成|[Story.cs 2826–2857](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L2826-L2857)、[StoryState.cs 1332–1339](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/StoryState.cs#L1332-L1339)|Error直接throw StoryException；Warning经AddError带isWarning=true追加到state.currentWarnings，非直接调用onError；warning路径不执行AddError末尾的ForceEnd。这不保证后续代码/格式化/宿主回调无异常。|
|Continue前置门槛|[Story.cs 416–470](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L416-L470)|ContinueAsync先检查外部绑定；ContinueInternal在!canContinue时直接Exception。单步处catch StoryException然后AddError。警告不应靠“随便Continue一下”来刷新，因为它推进故事且可能走其他失败路线。|
|后续报告分支|[Story.cs 533–580](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L533-L580)|如果执行到这段且state有错误/警告，存在onError时分别调用处理器，之后ResetErrors；没有处理器时累计warning也足以导致StoryException。若处理器自身throw，后续reset也不能被当作必达。|

## 警告在何时对宿主可见？

在已检查的正常Warning路径，列表先被填充，Story.currentWarnings公开访问state列表（[Story.cs 90](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L90)）。在候选实例的加载回调被限制为只记录、不推进/清诊断/改状态的前提下，宿主应在LoadJson返回后立即复制诊断，再考虑后续推进；不要假设绑定onError就会在LoadJson内部立刻收到每条warning。`onDidLoadState`是调用结束后的通知，没有检查“没有warning”的条件；其处理器又可能执行任意宿主逻辑。这里不预测事件回调次数或真正出现的消息，因为没有运行原始故事。

若LoadJson某阶段throw，onDidLoadState通常尚未到达；但也可能是onDidLoadState处理器自身throw，不能把所有入口异常都解释为JSON解析失败。应记录阶段与异常类型。当前加载方法已可修改部分字段，不应在失败候选实例上继续正常游戏来猜测可恢复性。

## 三种版本身份，不互相代替

1. **保存格式版本**：上述inkSaveVersion只约束序列化结构兼容路径。
2. **编译故事格式版本**：[Story.cs构造器](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L210-L229)对inkVersion另做范围检查；它不是项目剧情revision。
3. **项目内容身份**：已检查的[WriteJson 654–700](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/StoryState.cs#L654-L700)、LoadJsonObj及上述路径解析未见拿项目编译内容hash与存档封套作相等校验。限定在这些具体路径，不声称所有宿主/插件都没有内容校验；项目可自行封装，或把字段写入变量。序列化还写inkFormatVersion，但这不等于编译内容字节摘要。

因此“格式没变”不能批准换剧情后沿用旧检查点；“路径精确”也不能批准作者把同一路径改成另一剧情。源代码没有替项目做语义迁移判断。

## 原创工程验收协议（尚未执行）

目标不是证明奖励只执行一次，而是证明**恢复后讲的仍是批准的那段故事**。

- 内容作者先声明旧checkpoint的可接受新位置：下一段对话的项目语义ID、可见选择的作者ID/顺序规则、哪些分支或已读状态必须保留。不要只用屏幕字符串相等，翻译和文字修订可改变文本；不要以当前choice index作为永久身份。
- 封套保存编译内容hash/revision、状态格式、宿主内容配置；先分类“同内容恢复”“明确批准的跨内容迁移”“不支持的跨内容加载”。hash不匹配不是自动证明恶意或损坏，而是需要迁移决策。
- 使用可丢弃候选Story载入；将候选onDidLoadState/onError处理器限制为非变更、只记录，不在加载回调中重入Continue、保存、ResetErrors、修改状态或执行外部副作用；候选实例本身并不自动约束宿主回调。若必须执行宿主动作，应先在回调内捕获诊断，再明确记录该动作。保留加载前后诊断列表、入口异常阶段、onDidLoadState/onError调用记录。检查警告要在任何后续Continue前完成，别为触发回调而无条件推进；不能承诺候选实例消除了外部函数副作用，需要受控宿主绑定。
- 只有加载检查通过并允许推进时，再按规定步数/终止条件获取下一段对话或choices；记录实际内容身份与原始文本、选择作者ID、canContinue与任何新诊断。出现approximate warning不能自动批准；由内容负责人判断拒绝、迁移或明确降级恢复。
- 将“入口返回”“没有诊断”“下一段匹配”“选择匹配”分别报告。不匹配时保留旧存档，不在旧内容/新内容之间反复试读后悄悄保存成新状态。

未来有限runtime实验需先有已验证运行时/编译器，再构造两份原创内容的特定结构修改。必须先观察该修改是否真正触发approximate路径，而不是预设“删一个knot必定出现warning”。并加入同路径语义改变但可能无warning的对照，比较作者批准结果。当前无此运行时：不输出调用次数、warning实际列表、迁移成功率或用户体验收益。

## 尚未解决的范围

未跑旧/新内容、损坏JSON、宿主回调throw或不同运行时(inkjs)兼容；未穷尽SimpleJson/变量/输出流所有反序列化路径；未验证外部绑定对探测推进的影响。源码确有近似恢复与延迟报告路线，但不保证任意旧存档能恢复、任何warning总能正常Continue、或候选实例失败后内部完全不变。此研究保持source-only，不能升级为runtime-tested。

[独立固定源码复核](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/research/audits/ink-content-compatibility-review.md)确认调用链与回调诊断条件；没有执行故事或验证迁移。

## 2026-11-01：省略默认值的迁移审查

[有限反证审查](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/research/audits/ink-default-migration/review.md)保留上述中心结论，并分析一个尚未执行的布尔状态情景：当前输出核对不能替代被省略状态的历史解释与明确迁移政策。它不是运行复现或对全部存档的兼容认证；原说明的受控宿主绑定及内容版本门继续有效。
