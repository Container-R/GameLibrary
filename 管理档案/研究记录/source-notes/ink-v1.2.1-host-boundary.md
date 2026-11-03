# ink v1.2.1：外部绑定与故事检查点的固定版本来源审计

状态：**来源审计，不是运行时验证或完整解决方案**。2026-10-31 通过已授权 GitHub 插件解析真实标签 `v1.2.1` 到 `35c63e52f1d36060930dc7ed3cfba38ea224b528`，提交时间 2026-05-05；五份文件的不可变链接与 Git blob SHA 见[取证清单](ink-v1.2.1-receipt.json)。独立审查者另行获取固定提交，集成者复核关键绑定及调用分支。没有执行 ink、编译故事或复制第三方实现。

## 1. 不能把所有绑定入口的默认值视为相同

[Story.cs](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L1943-L2054) 的 `BindExternalFunctionGeneral` 默认 `lookaheadSafe=true`；独立检查的十个 `BindExternalFunction` 便捷签名默认 `false`，并转交该参数。`false` 在字符串生成上下文先报错；存在换行预读快照时设置标记并返回，后续步进恢复快照、结束当前行。不能从这些分支推算任意故事的实际调用次数。当前公开可见选项的 `index` 还会由 `currentChoices` getter 顺序重编，因此不是跨内容版本的持久业务 ID。

**应用建议（原创）**：封装外部绑定时显式声明纯度，带奖励、库存或任务副作用的绑定明确传 `false`，包括 General 入口；不能依赖方法名字相似而省略参数。此规则约束预读，不提供持久化恰好一次、宿主事务或异常回滚。不要将有副作用调用放进选项文本/字符串插值，再以 `true` 掩盖错误。

## 2. 运行指南不是整个游戏存档协议

固定版本[RunningYourInk.md](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/Documentation/RunningYourInk.md) 解释运行循环、选择、故事状态保存/恢复及外部函数纯度。指南的便捷用法不能替代全部重载签名审查；保存故事状态也不意味着同时保存宿主库存。不能把“避免某类预读副作用”扩大为“读档永不重复发奖”。

## 后台保存读取哪份状态

故事继续推进时，可以把保存工作移到后台，但必须先分清：后台读取的是捕获时的状态，还是稍后已经前进的运行状态。ink v1.2.1 的 `CopyStateForBackgroundThreadSave()` 提供了一个特定交接方式，并没有把整个Story变成可以任意多线程访问的对象。

这个方法实际返回调用前的旧状态，同时把运行中的 `story.state` 换成带 patch（用于暂存后续变化的差异记录）的新状态。[1] 因而，应保留它返回的引用，供后台执行 `ToJson()` 字符串序列化；不能等后台任务开始后，再去取一次 `story.state` 代替。后者已经不是原来的保存点，其当前流程与尚未合并的全局值也不能未经核对就当成同一时刻的检查点。

### 用一个计数看清保存点与当前进度

下面只作纸面推演。假设故事声明全局 `report_count`，默认值为0；捕获时值已为1，随后正常当前流推进把它改成2。开始时没有旧patch或换行预读快照；这段期间完成信号尚未发出，不加载或重置状态，也不切换、移除等管理故事流程（flow），不直接修改运行时对象。

- 捕获时，保留返回的旧状态作为本次序列化对象，运行端转入patch状态。
- 推进到2时，正常全局赋值先记录在patch中，运行端读取也优先看到patch里的2。
- 后台对返回状态调用 `ToJson()`，全局变量写入路径读取基础字典中的1，而不是运行端patch里的2。[2][3]

这说明保存点可以落在1，而当前故事已经前进到2；不是保存期间停止了整个故事，也不是保存结束后应把故事改回1。默认值设为0，是为了避免把本例与“等于默认值而省略保存”的规则混在一起。这里没有编译故事、生成实际JSON或观察线程竞争。

这种分离不是完整深拷贝。两个状态仍共享 `VariablesState` 和基础计数字典；它依靠正常更新进入patch、序列化读取基础数据的路径来工作。[2] 即使拿着返回状态，也不能把它的变量getter、setter或其他公开成员当成私有副本任意操作。尤其变量getter会优先读取共享对象上的patch，不能拿一次普通读值替代保存结果的含义。

### 何时交回完成信号

在后台不再读取返回状态之后，宿主需要把完成交接回串行操作Story的拥有线程，再调用 `BackgroundSaveComplete()`。这是接入方应建立的同步约束，不是源码自动检查某个线程ID或替调用方加锁的保证。不能先发完成信号，再让后台继续遍历旧状态。

完成方法会让后续变化合并回基础状态；若当时还有换行预读快照，合并会延后到该快照恢复或丢弃时，按最终保留的运行分支处理。[1] 所以它不是回滚到保存点，也不保证每次调用都立刻合并全部预读变化。它本身没有检查文件是否写入成功，更不等于存档已经可靠落盘。字符串序列化、文件提交和宿主库存的保存仍需分别安排。

该版本会拒绝尚在后台保存模式时再次调用Copy，也会拒绝在一次尚未完成的 `ContinueAsync()` 求值中开始捕获。[1][4] 后者是分帧限时求值接口，不是自动启动工作线程。反过来，`LoadJson`入口没有对应的“正在后台保存”门禁；这不意味着同时加载受支持。[5] 不要期待所有违反交接约定的操作都由库自动拒绝。

本节仅解释固定源码的这条保存路径，不提供通用线程安全、异常恢复或整个游戏检查点一致性保证。与前面的外部函数边界一样，叙事状态可序列化，仍不证明宿主动作已经提交。

本节固定原源（2026-11-03读取；均为同一v1.2.1提交）：

1. [Story.cs 783–869：换行快照、捕获与完成](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L783-L869)。
2. [StoryState.cs 548–700：复制、共享字段、patch恢复与序列化](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/StoryState.cs#L548-L700)；同文件[ToJson字符串入口37–40](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/StoryState.cs#L37-L40)、[计数读写65–159](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/StoryState.cs#L65-L159)。
3. VariablesState.cs：[getter优先读patch，75–108](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/VariablesState.cs#L75-L108)、[合并及序列化基础globals，131–195](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/VariablesState.cs#L131-L195)、[全局赋值，355–378](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/VariablesState.cs#L355-L378)。
4. Story.cs：[ContinueAsync语义，395–421](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L395-L421)、[未完成求值门禁，1775–1779](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L1775-L1779)。
5. StoryState.cs：[LoadJson入口，52–61](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/StoryState.cs#L52-L61)、[字段加载，704–794](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/StoryState.cs#L704-L794)。

## 3. 三种版本身份要分开

[StoryState.cs](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/StoryState.cs#L654-L794) 在本提交使用存档状态格式版本 10、最低加载版本 8；检查的序列化字段没有项目内容摘要或宿主奖励收据。`LoadJsonObj` 对缺失/过旧状态版本检查后更新字段，该方法未提供“失败后现场保持原样”的事务承诺。**仅此状态方法**未见未来版本上界检查，不代表整体加载器支持未来格式：`Story(string)` 对编译故事的 `inkVersion` 有上界检查。状态格式版本、编译故事格式版本、项目叙事内容版本不能互相替代。

**应用建议（原创，未执行）**：项目检查点显式关联内容摘要、故事状态和宿主状态/收据；必要时在可丢弃候选运行时上验证恢复，不假定损坏加载不会部分改变活实例。这里不指定未经验证的原子提交实现。只有收据而叙事位置/库存来自不同检查点，仍可能重复或漏发奖励。

## 4. 选项身份需要项目契约

[Choice.cs](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Choice.cs) 暴露索引、路径与标签，但没有声明它们是跨任意内容编辑稳定的项目标识。结合前述 getter，UI 应把索引视为当前可见选项快照的位置；若要持久选择身份，需另定义、校验作者 ID 并防止旧 UI 快照提交。尚未运行重排、翻译或内容迁移实验。

## 待验收与停止边界

下一项真正有价值的实验需要固定运行时、原创故事及编译结果摘要，比较显式 `false` 与 General 省略参数的实际轨迹，并观察奖励前后检查点恢复；不能预设任何故事必然重复调用。还需区分恢复旧兼容检查点与加载不同内容版本。

当时未具备运行 ink 的已确认条件，因此没有执行运行时验证；不据此断言所有可用实现均不存在。本轮不安装依赖、不执行下载代码，不以抽象 Python 模型冒充 ink 行为。无运行时证据时停止在本来源审计，不新增“已验证叙事方案”。

固定版本 [MIT 许可](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/LICENSE.txt) 已检查；本文为原创分析，没有转载实现代码。关联已有[经济事件账本](https://github.com/Container-R/GameLibrary/blob/1a7bf18b24ba56395892c4c0cdb3b2acecc16985/solutions/design/single-player-economy-ledger.md)和[云存档边界](https://github.com/Container-R/GameLibrary/blob/1a7bf18b24ba56395892c4c0cdb3b2acecc16985/solutions/platform/cloud-save-resume-boundary.md)，但二者不证明叙事与宿主状态的一致检查点。

[独立源码复核记录](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/research/audits/ink-source-independent-review.md)保存行号与两项措辞纠正；其确认的是固定版本源码事实，不是运行结果。

## 追加的内容兼容性深审

[旧状态遇到新内容](ink-save-content-compatibility.md)进一步追踪近似路径恢复、load阶段warning缓存、Continue报告分支和onDidLoadState重入风险。保存格式版本/编译故事格式/项目内容身份不混同；协议仅来源支持，仍没有ink运行时验证。

公开衍生维护说明：本次仅省略安装环境信息，保留原有技术结论、失败与证据限制及已修正的固定历史链接；未运行旧实验，也未重写历史记录。
