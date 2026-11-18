# 公会试炼快照与奖励：依据

- Milky Way Idle 开发者，2026-07-12，[Guild Expansion, Additional Localizations, and QOL Improvements](https://steamcommunity.com/app/3224420/announcements/)，Guild Trials 第 1 项。开发者说明定时开赛、选择的配装快照、日常并行、不耗消耗品、战斗按参与人数调节，以及通过档次与符合资格的整周奖励。公告未交代实际快照时点、资格全规则或服务器重试实现。
- PostgreSQL 17，[Transactions](https://www.postgresql.org/docs/17/tutorial-transactions.html) 解释同一事务全有或全无；本文仅用作实现建议，不表明原版使用该数据库。
- [合成实验](../实验/公会试炼与日常队列/README.md) 只比较两步日常队列的结果及合成快照／奖励。JSON 往返不代表磁盘恢复、事务原子性或真实并发。共享引用、误扣日常库存和重复发奖都由脚本注入。
