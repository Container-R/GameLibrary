# SQLite本地账本事务：来源与有限实验提案

核对2026-10-31；目前仅能力查询和资料阅读，没有运行写入/中断夹具。现有`solutions/design/single-player-economy-ledger.md`及`research/experiments/economy-ledger/model.py`已读：纯内存Ledger保留balance/entries/seen，重复ID拒绝，正文明确未验证原子存储与崩溃恢复。新单元只补存储边界，不替换经济数值、成长可达性或实际玩家验证。

## 本机能力

Python3.12.14；标准库sqlite3报告SQLite3.53.1，`SELECT sqlite_source_id()`实际为：

`2026-05-05 10:34:17 c88b22011a54b4f6fbd149e9f8e4de77658ce58143a1af0e3785e4e6475127e9`

运行时版本/source_id不是已独立认证的构建来源。实际执行时还需记录Python可执行文件、_sqlite3扩展及实际链接SQLite文件（如动态链接）的路径/hash，不凭文件名猜安装版本；不安装或替换库。

## 原始来源与支持边界

- [SQLite Transaction](https://www.sqlite.org/lang_transaction.html)，2/2.1/2.2/2.3：显式事务、单写者及BEGIN IMMEDIATE；BUSY可能发生，不能把调用COMMIT当作一定成功。
- [Atomic Commit in SQLite](https://www.sqlite.org/atomiccommit.html)，1/2/3/4/9：该实现说明讨论rollback模式，硬件/同步/锁假设不能省略；journal存在也不自动等于本次已测过热日志回放。
- [PRAGMA synchronous](https://www.sqlite.org/pragma.html#pragma_synchronous)：DELETE模式EXTRA包括额外目录同步；FULL在回滚模式下的断电持久性不能无条件外推。本实验指定EXTRA只是配置，不是实际断电测试证据。
- [Python3.12 sqlite3 transaction control](https://docs.python.org/3.12/library/sqlite3.html#transaction-control)：设置isolation_level=None时不隐式开启事务，可以用SQL显式控制。固定LEGACY_TRANSACTION_CONTROL以免依赖未来默认值变化，检查in_transaction与实际PRAGMA。

四页为官方接口/实现说明，不是本夹具实测结果；全部访问2026-10-31。无关SQLite全库源码、WAL、跨文件super-journal不纳入本轮。

## 一个应用合同

一个本地存档、一个币种coin、整数余额；ID在此存档内唯一。示例字段：`receipt(event_id PRIMARY KEY, amount INTEGER, reason TEXT, balance_after INTEGER)`与`account(id PRIMARY KEY,balance INTEGER CHECK(balance>=0))`。一次post将余额与唯一receipt写在同一事务。初始化余额0，再用独立opening事件记入100，保证余额可与账本总和相等；不得偷偷把100作为无来源库存。

固定请求R：event_id=reward-1，amount=25，reason=quest。BEGIN IMMEDIATE后查ID：

- 已存在且amount/reason完全相同：返回原receipt，不再次修改余额。
- 已存在而payload不同：拒绝并ROLLBACK，保持旧状态。
- 不存在：检查余额条件，更新余额并插入receipt，只有SQL COMMIT成功后才视为已提交。

对重复请求返回的是该事件原balance_after，不承诺等于当前总余额。事件身份和payload范围是本例合同；生产还需saveId、币种、配置/业务类型等，不把只比较amount当成任何游戏通用幂等算法。无需哈希payload来掩盖规范化问题，本例直接比较有限字段。

## 建议有限进程矩阵

为两个中断点分别创建独立数据库，避免前一case污染后一case。脚本只接收白名单case与受控路径。

| case | 实际进程行为 | 新进程查询的预期，不预先当作结果 |
|---|---|---|
| before_commit | R余额更新与receipt插入均完成后，写出flush日志标记，直接os._exit(预定码)，无close/rollback/finally | 余额100，只有opening；R不存在 |
| after_commit | 同样写入，COMMIT返回成功后flush日志，直接os._exit(另一预定码) | 余额125，opening与R均存在；R的balance_after=125 |
| retry_same | 对after_commit数据库在新进程重发相同R | 返回原R；余额125，R仍仅一条 |
| retry_changed | 再以同ID把amount改26或reason改变（预先选一个） | 明确冲突拒绝；余额与所有receipt不变 |

每次最终查询用新的进程/连接，而不是用写者的对象内存。输出所有receipt、余额、sum(amount)、R数量、完整性检查结果与真实PRAGMA。错误恢复不能靠删除journal：保留数据库及相关文件原名，直到SQLite自行打开读取。

本轮没有多写者竞争测试。BEGIN IMMEDIATE只是明确单写者入口，不构成并发公平性、吞吐或重试策略证明。若失败原因是非预期SQL错误/锁错误/进程启动失败，应归类失败，不能把它冒充预定中断。

## 重要限制与假阳性预防

1. `os._exit`证明进程被直接终止，未运行连接清理，但不是整机掉电、磁盘写撕裂、OS崩溃或缓存掉失。不能从四case宣称断电安全。
2. 小事务可能仍在页缓存，不能仅凭恢复到100就声称已实际执行热journal回放。保留journal观察但不强制每环境出现相同内部文件状态。
3. 到COMMIT返回之后的日志用于区分“数据库已提交但调用者未获响应”窗口；重发验证幂等，而不是网络恰好一次保证。
4. 余额与receipt都应对照SQL读回，检查sum(delta)==balance和R唯一性；只检查余额会漏掉receipt缺失，反之亦然。
5. 配置每个连接的journal_mode=DELETE/synchronous=EXTRA并读取实际值，事务外设置。未知PRAGMA可能被忽略，所以不只记录请求字符串。
6. 无外部授权、远程购买凭证、跨存档迁移、云同步、反作弊或防篡改。可编辑本地文件的人仍可改变数据，事务不是安全边界。

## 归档与停止条件

拟用worker+runner，显式SQL参数绑定，禁止拼接任意SQL。记录每个进程命令/退出码/stdout/stderr、预定中断标记、独立query载荷、库版本/hash、源hash。runner拒绝-O且先清旧成功摘要；超时保留部分输出，非预期失败无PASS。原数据库文件归档供检查但不假定字节一致性；独立复跑使用全新目录。

止于声明的四case和独立审查，不扩大到全存档框架、不推荐所有游戏改用SQLite、不拿存储正确性替代经济设计价值。父代理批准后再实现。
