# 来源笔记：ink v1.2.1 前瞻与宿主动作

对应正文：[ink 对话还没显示下一句，为什么游戏动作已经执行](../../GameLibrary/叙事设计/运行时叙事/对白推进与游戏交接/ink%20对话还没显示下一句，为什么游戏动作已经执行.md)。

| 主张 | 原始资料与定位 | 适用范围 |
| --- | --- | --- |
| Glue 可在逻辑与新行之间拼接输出 | [Writing With Ink](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/Documentation/WritingWithInk.md)，Glue；[Story.cs 608–655](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L608-L655) | 同一同步 Continue 路径；非 UI 自动换行 |
| 试探读更多输出，回滚的是 ink 状态 | [Story.cs 788–821](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L788-L821) 与 [1945–2059](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L1945-L2059) | 本试件直接写宿主 C# 计数；未模拟异步或外部事务 |
| 前瞻不安全的绑定会在已存在换行快照时避开调用、在字符串求值时报错；常用绑定和通用绑定默认值不同 | 同上外部函数路径与 [2105–2151](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L2105-L2151)，[Running Your Ink](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/Documentation/RunningYourInk.md) 的 External functions | 明示 C# 参数，不扩展到其他语言移植；不会保证等待 UI 展示 |
| 从 Continue 返回后取 currentTags，动作提交与去重由项目负责 | 同版本 Running Your Ink 的 Tags；[实际复现](../实验/ink前瞻与宿主动作/README.md) | 原生试件验证标签与宿主内存去重；重启、延迟、取消和存档一致性为设计约束 |
