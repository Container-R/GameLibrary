# 新手引导完成率分母：来源与证据

访问日期：2026-11-23。

| 正文主张 | 一手来源与定位 | 适用条件 |
| --- | --- | --- |
| 给实验两臂记录共同的资格或反事实触发，而不是只记录实际收到新功能的人 | Microsoft Research，[Patterns of Trustworthy Experimentation: Pre-Experiment Stage](https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-pre-experiment-stage/)，Set Up Counterfactual Logging | 天气答案示例是在对照也能评价同类请求。游戏例子要求用变更影响前的共同输入；不能借该来源宣称任意后置条件都能用于因果比较。 |
| 检查触发内和补集，补集有明显差异值得追查 | Microsoft Research，[Patterns of Trustworthy Experimentation: Post-Experiment Stage](https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-post-experiment-stage/)，Segment By Triggered/Non-Triggered Users | 不以没有显著差异证明无效应，主指标保留全分配人群。本文不把触发子集提升率乘比例当万用修正。 |
| 200 人可产生 50/70% 与 50/42% 的反向结果；直接事件连接可多算；覆盖未知单列 | [SQLite 合成试件](../实验/新手引导完成率分母/README.md)，脚本和日志 | 固定 200 账号、单位为账号、明确发生/收件时刻。是本地实际执行的合成数据查询，不能作玩家总体推断。 |
