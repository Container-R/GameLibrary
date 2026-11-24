# 实时排行榜翻页与同分名次：来源记录

- PostgreSQL 18，[Window Functions 教程](https://www.postgresql.org/docs/18/tutorial-window.html)与[窗口函数参考](https://www.postgresql.org/docs/18/functions-window.html)。窗口计算以本查询层过滤后的行作为输入，rank 依据窗口排序的同伴组。资格放进内层、分页放外层是本文推演及 SQLite 验证。
- PostgreSQL 18，[Indexes and ORDER BY](https://www.postgresql.org/docs/18/indexes-ordering.html)，多列 B-tree 方向及反向扫描。本文不报告 PostgreSQL 查询计划或性能。
- PostgreSQL 18，[Transaction Isolation](https://www.postgresql.org/docs/18/transaction-iso.html#XACT-READ-COMMITTED)，Read Committed 每条普通 SELECT 的读快照；不把该结论归给应用物化版本或其他隔离级别。
- Redis，[ZRANGE](https://redis.io/docs/latest/commands/zrange/)，REV 改变分数方向及同分成员顺序；未实跑 Redis。访问日期：2026-11-24。
- [复现实验](../实验/实时排行榜翻页/README.md)：SQLite 实际查询加 Python 测试模型；均不是生产压测。
