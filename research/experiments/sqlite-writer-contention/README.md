# SQLite双写者：握手确认BEGIN拒绝与提交后幂等重试

2026-10-31，本机Python3.12.14/SQLite3.53.1，一个确定性序列实际通过，四个子进程为初始化、写者A、写者B和最终新读者。它扩展原账本存储证据，不替代原退出/重开实验；原fixture未修改。

## 实测序列

| 顺序 | 实际证据 |
|---|---|
| READY A与B | 两连接均已配置DELETE/EXTRA，busy_timeout=0，in_transaction=false |
| A收到APPLY_HOLD | BEGIN IMMEDIATE后修改余额/插入R，未COMMIT；HELD报告125/R一次、in_transaction=true |
| B收到TRY_BEGIN | 实际BEGIN IMMEDIATE抛OperationalError；code5、nameSQLITE_BUSY、message database is locked；in_transaction=false |
| B在A仍持有时读取 | 余额100/仅opening；所有读cursor显式关闭后发BUSY_OBSERVED |
| A收到COMMIT | SQL成功返回，COMMITTED报告in_transaction=false |
| B收到RETRY_SAME | 同R=(reward-1,25,quest)返回duplicate及原balance_after125；余额125/R一次 |
| A/B关闭后新读者 | 完整receipt为opening100和R25，sum=余额125，R唯一，integrity_check=ok |

没有sleep决定竞争顺序。父仅收到对应事件后才发送下一条命令；stdout读线程通过Queue传递行消息，每次等待上限5秒。超时是失败，不是同步依据。配置在两者READY前完成，避免把配置过程锁冲突误当成被测BEGIN冲突。

B失败分支不执行经济DML；它只记录真实异常和持久视图。重试调用本例幂等post，因已存在同payload返回原receipt。最终行集合和守恒也由独立新进程核对，不凭父发出的请求次数证明。

## 运行和归档

```
python run.py
```

本目录ledger.py是原创先前夹具方法的本地副本，snapshot读取在此明确close cursor；不依赖导入另一个未归档draft。run.py先清旧summary再拒绝-O，为每轮新建database-*目录，不删除旧数据库或journal。

results/transcript.json保留所有父发送命令和解析接收消息。各角色stdout/stderr原文、命令与退出码单独保留；遇到异常，finally终止仍运行的子进程，限时等待后必要时kill再wait，避免留下持锁孤儿。失败不生成PASS，且不删除数据库以掩盖中间状态。这里正常路径全部退出0，超时清理逻辑未另行故障注入测试，不宣称已覆盖每个故障路径。

results/summary.json含三源hash、实际运行时身份、可执行文件hash、四进程命令、当前数据库目录及最终文件hash。ledger.db.base64是本轮关闭后数据库的无损文本封装，不是SQL重建；可在新建临时目录解码，校验bytes与sha256后再读取，不覆盖已有存档。旧database-*目录属于历史运行，不是当前summary指向的证据。

## BEGIN BUSY不等于COMMIT BUSY

[SQLite Transaction §2.1–2.3](https://www.sqlite.org/lang_transaction.html)分别说明写事务开始与提交的锁失败：本轮观察到的是**BEGIN IMMEDIATE失败且B未进入事务**。若COMMIT返回BUSY，事务可能仍活动，不能照搬这个结论。我们没有安排长读事务来制造COMMIT失败，没有验证其重试策略。

[Python sqlite3错误属性](https://docs.python.org/3.12/library/sqlite3.html#sqlite3.Error.sqlite_errorcode)使我们按实际code/name检查，不只匹配英文错误信息。该3.12滚动页面标题3.12.16，运行时3.12.14。两页访问2026-10-31；source_id与版本仍为运行时自报，非独立认证构建来源。

B在锁持有期读到100只证明此序列的一个视图，不是完整的并发快照隔离测试。同步等待A提交后再重试是实验协议，不是推荐生产环境立即无限重试所有BUSY。公平性、性能、多写者队列、取消策略、WAL、云同步、断电/硬件flush/反作弊均不在范围内。数据库可持久化，不表示调用者具备发奖授权。

## 独立验收

[独立复跑](review/README.md)重复一个握手序列、四个子进程，并以另一判据将各角色原始行与父协议记录对应，验证先后门槛和最终数据。不是四种竞争场景，也不是四轮压力测试。作者和审查者各自保留最终数据库 base64；文本归档省略原始 database-* 目录，summary 的绝对路径不是检出依赖。集成者复核保存的原始日志与解码摘要，没有第三次执行并发序列。
