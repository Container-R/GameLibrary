# 游戏交易所手续费：来源与范围

| 正文主张 | 原始资料及准确定位 | 推导或限制 |
| --- | --- | --- |
| 整数算法的除法向零截断 | ECMA-262，§6.1.6.2.5 [BigInt::divide](https://tc39.es/ecma262/multipage/ecmascript-data-types-and-values.html#sec-bigint::divide)，对整数商调用 truncate。 | 非负金额与正分母时等于 floor；负数补偿不直接照搬。 |
| 冲突跳过不会返回未插入的行 | PostgreSQL 18 [INSERT](https://www.postgresql.org/docs/18/sql-insert.html)，RETURNING、ON CONFLICT。 | 以唯一键识别哪笔成交曾入账的流程是本文设计，不是数据库自动去重所有副作用。 |
| 已提交的冲突记录可能不在 INSERT 本身的快照内 | PostgreSQL 18 [§13.2.1 Read Committed](https://www.postgresql.org/docs/18/transaction-iso.html#XACT-READ-COMMITTED)，ON CONFLICT DO NOTHING 段；下一语句取得新快照。 | 设计依赖凭据与账项一起提交且冲突记录不被删除。 |
| 行锁隔离同一订单上的状态变化 | PostgreSQL 18 [§13.3.2 Row-Level Locks、§13.3.4 Deadlocks](https://www.postgresql.org/docs/18/explicit-locking.html)，FOR UPDATE 及锁顺序建议。 | 锁订单不等于锁共享资金、库存；用同库事务提交写集。 |
| 同一事务中的修改全有或全无 | PostgreSQL 18 [§3.4 Transactions](https://www.postgresql.org/docs/18/tutorial-transactions.html)。 | 不覆盖跨库、独立队列或外部钱包。 |
| 累计费用对同单正向成交分割不敏感 | 正文差值公式的消项推导；自建 [Node 顺序试件](../实验/游戏交易所的部分成交与手续费取整/README.md)。 | 无真实货币与生产数据。未执行 PostgreSQL 并发、故障恢复或物品转移。 |

调阅日期：2026-11-22。
