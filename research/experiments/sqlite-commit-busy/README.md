# COMMIT BUSY：保留当前事务，重试提交而非重做奖励

## 归档恢复说明

2026-10-31 20:56 UTC执行环境重置丢失了之前本地作者与审查者档案。以前的通过报告不作为本目录原始证据；旧数据库、日志无法恢复。这里重新冻结协议、重建源码并实际新运行，源hash重新计算，未伪造旧档案。当前作者证据为 `results/64d9242a-4f54-491f-b959-2b54196a7521/`。本轮首次运行通过，无本轮初始失败。

## 新执行的结果

一个工作进程拥有两个独立连接，顺序调用SQL但保留重叠事务；第二个新进程只读核验最终DB。不是两个SQL工作进程的并发压力测试。Python3.12.14、SQLite自报3.53.1；实际source_id、解释器/源码hash、平台、命令及退出码见summary与原始输出。身份字符串和摘要不是官方构建认证。

两读写连接均回验DELETE journal、EXTRA(synchronous=3)、busy_timeout=0，连接timeout=0。显式LEGACY_TRANSACTION_CONTROL与isolation_level=None，使用SQL控制事务。

| 门槛 | 结果 |
|---|---|
| 读者BEGIN后完全读取并关闭cursor，保留事务 | 余额100/仅opening，in_transaction=true |
| 写者BEGIN IMMEDIATE，UPDATE+25/INSERT reward-1 | 写者125/两条receipt，in_transaction=true |
| 第一次COMMIT | code5、nameSQLITE_BUSY，写者事务仍活动 |
| BUSY后双方读取 | 写者125，读者100；双方事务仍活动 |
| 读者COMMIT释放，然后写者仅重试COMMIT | 成功，写者in_transaction=false；读者新查询125 |
| 两连接关闭，新只读进程打开 | 完整行opening100/reward-1金额25和结果125；余额125守恒，integrity_check=ok |

写者trace callback实际记录一次奖励UPDATE、一次INSERT、一次BEGIN IMMEDIATE、两次COMMIT；初始化不在这段trace内。不是只用最终余额推断“没有重做”。Python Connection.in_transaction是实际观测，没有直接调用C autocommit API。integrity_check不能替代业务行集合检查。

## 工程意义

旧双写者实验是BEGIN被拒绝，未进入事务；本例是DML已执行而COMMIT受读者阻塞。不能把两者都按“没有做事”处理后直接重复非幂等UPDATE。本例释放已知读者后只重试当前COMMIT。生产还需按错误分类、实际事务状态和截止期限决定继续提交，或明确ROLLBACK后按幂等请求重试；这些替代策略未实测，不建议无限立即重试。

## 运行/失败边界

`python -B run.py /tmp/new-sqlite-commit-evidence`

每次UUID目录先STARTED，再PASS或FAIL，旧summary不是本次成功。每子进程timeout10s，SQLite忙等待0；无sleep协调。Python超时终止并等待直接子进程；worker不创建后代，不提供OS不可终止调用的普遍保证。临时DB自动清理，失败DB不保证保留；原始输出和错误保留。成功关闭后的DB无损base64及解码hash不是热journal/崩溃瞬间镜像。仅在新临时位置解码核验，勿覆盖存档。

protocol.md及预代码protocol.sha256明确判据。验收没有assert，作者本轮只实际执行普通模式。源/输出hash提供归档一致性，不是抗伪造执行证明。既有实验源码、档案未修改。

## 来源与边界

2026-10-31已读取的滚动官方资料：
- [SQLite Transaction §2.2–2.3、§3](https://www.sqlite.org/lang_transaction.html)：读者阻塞COMMIT的活动事务/提交重试，与其他错误可能回滚的区别。
- [SQLite File Locking §3](https://www.sqlite.org/lockingv3.html)：rollback-mode锁兼容性；不描述WAL。本实验没有直接探测OS锁。

不证明断电/硬件flush、WAL、云同步、真实游戏、吞吐、公平性、完整隔离性或自动恢复队列。配置读回不是持久性测试。只扩展现有单玩家账本文章，不新增文章数量。

## 重置后的独立复核

[独立复核](review/REVIEW.md)以新UUID `09655ed4-1da6-452e-a086-97a8960926cc` 重跑两个进程，再以独立字面判据核对原始事件、SQL trace、事务状态、完整行集合及双方数据库base64摘要。当前可归档证据是重置后作者两个进程与审查者两个进程，各一轮相同序列；没有把重置前丢失的日志计入可复验档案。
