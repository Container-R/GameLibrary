# 活动任务规则切换：来源核对

核对日期 2026-11-25。[试件说明](../实验/活动任务规则切换/README.md)。

- [Blizzard：Diablo IV Patch Notes (1.0–1.2)](https://news.blizzard.com/en-us/article/24092662/diablo-iv-patch-notes-1-0-1-2)，Renown Value Adjustments 的旧新数值及开发者说明。支线 20→30，地下城 30→40，并追补已完成内容的差额。只支持玩家规则承诺，未披露其数据模型。
- [Microsoft Azure Architecture Center：Event Sourcing pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)，Workflow 的重放重建与读取投影及其限制。本文使用重算思想；完整性、对局身份、冻结资格与奖励份数是本例显式条件，不是引用来源规定的游戏政策。
- [SQLite Transaction](https://www.sqlite.org/lang_transaction.html) 与 [UPSERT](https://www.sqlite.org/lang_upsert.html)：单库事务内领取与代币操作、唯一键冲突时不再插入。Python 试件按单连接顺序运行，只覆盖脚本内合成账户与异常；没有验证并发、多库或日志延迟。
