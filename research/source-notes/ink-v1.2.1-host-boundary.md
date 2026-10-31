# ink v1.2.1：外部绑定与故事检查点的固定版本来源审计

状态：**来源审计，不是运行时验证或完整解决方案**。2026-10-31 通过已授权 GitHub 插件解析真实标签 `v1.2.1` 到 `35c63e52f1d36060930dc7ed3cfba38ea224b528`，提交时间 2026-05-05；五份文件的不可变链接与 Git blob SHA 见[取证清单](ink-v1.2.1-receipt.json)。独立审查者另行获取固定提交，集成者复核关键绑定及调用分支。没有执行 ink、编译故事或复制第三方实现。

## 1. 不能把所有绑定入口的默认值视为相同

[Story.cs](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L1943-L2054) 的 `BindExternalFunctionGeneral` 默认 `lookaheadSafe=true`；独立检查的十个 `BindExternalFunction` 便捷签名默认 `false`，并转交该参数。`false` 在字符串生成上下文先报错；存在换行预读快照时设置标记并返回，后续步进恢复快照、结束当前行。不能从这些分支推算任意故事的实际调用次数。当前公开可见选项的 `index` 还会由 `currentChoices` getter 顺序重编，因此不是跨内容版本的持久业务 ID。

**应用建议（原创）**：封装外部绑定时显式声明纯度，带奖励、库存或任务副作用的绑定明确传 `false`，包括 General 入口；不能依赖方法名字相似而省略参数。此规则约束预读，不提供持久化恰好一次、宿主事务或异常回滚。不要将有副作用调用放进选项文本/字符串插值，再以 `true` 掩盖错误。

## 2. 运行指南不是整个游戏存档协议

固定版本[RunningYourInk.md](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/Documentation/RunningYourInk.md) 解释运行循环、选择、故事状态保存/恢复及外部函数纯度。指南的便捷用法不能替代全部重载签名审查；保存故事状态也不意味着同时保存宿主库存。不能把“避免某类预读副作用”扩大为“读档永不重复发奖”。

## 3. 三种版本身份要分开

[StoryState.cs](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/StoryState.cs#L654-L794) 在本提交使用存档状态格式版本 10、最低加载版本 8；检查的序列化字段没有项目内容摘要或宿主奖励收据。`LoadJsonObj` 对缺失/过旧状态版本检查后更新字段，该方法未提供“失败后现场保持原样”的事务承诺。**仅此状态方法**未见未来版本上界检查，不代表整体加载器支持未来格式：`Story(string)` 对编译故事的 `inkVersion` 有上界检查。状态格式版本、编译故事格式版本、项目叙事内容版本不能互相替代。

**应用建议（原创，未执行）**：项目检查点显式关联内容摘要、故事状态和宿主状态/收据；必要时在可丢弃候选运行时上验证恢复，不假定损坏加载不会部分改变活实例。这里不指定未经验证的原子提交实现。只有收据而叙事位置/库存来自不同检查点，仍可能重复或漏发奖励。

## 4. 选项身份需要项目契约

[Choice.cs](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Choice.cs) 暴露索引、路径与标签，但没有声明它们是跨任意内容编辑稳定的项目标识。结合前述 getter，UI 应把索引视为当前可见选项快照的位置；若要持久选择身份，需另定义、校验作者 ID 并防止旧 UI 快照提交。尚未运行重排、翻译或内容迁移实验。

## 待验收与停止边界

下一项真正有价值的实验需要固定运行时、原创故事及编译结果摘要，比较显式 `false` 与 General 省略参数的实际轨迹，并观察奖励前后检查点恢复；不能预设任何故事必然重复调用。还需区分恢复旧兼容检查点与加载不同内容版本。

本环境 `command -v dotnet`、`mono`、`inklecate` 均未发现 PATH 入口；这不是全盘不存在的证明。本轮不安装依赖、不执行下载代码，不以抽象 Python 模型冒充 ink 行为。无运行时证据时停止在本来源审计，不新增“已验证叙事方案”。

固定版本 [MIT 许可](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/LICENSE.txt) 已检查；本文为原创分析，没有转载实现代码。关联已有[经济事件账本](../../solutions/design/single-player-economy-ledger.md)和[云存档边界](../../solutions/platform/cloud-save-resume-boundary.md)，但二者不证明叙事与宿主状态的一致检查点。

[独立源码复核记录](../audits/ink-source-independent-review.md)保存行号与两项措辞纠正；其确认的是固定版本源码事实，不是运行结果。
