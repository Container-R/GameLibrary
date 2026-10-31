# SQLite写者竞争：显式握手扩展提案

2026-10-31。只提案，未改原sqlite-ledger-boundary夹具，未运行竞争测试。不新增广泛存储文章。

## 原始依据与要填的缺口

[SQLite Transaction §2.1/2.2/2.3](https://www.sqlite.org/lang_transaction.html)说明只能有一个同时写事务；BEGIN IMMEDIATE在其他写者活动时可返回SQLITE_BUSY。COMMIT也可因其他读连接返回BUSY，但该情况下事务仍活动，可稍后重试。这是两种不同位置的状态，不能把任意BUSY统一解释成没有写入。

[Python3.12 sqlite3异常属性](https://docs.python.org/3.12/library/sqlite3.html#sqlite3.Error.sqlite_errorcode)提供sqlite_errorcode/sqlite_errorname，适合校验实际数据库错误而不是匹配本地化错误文字。公开滚动文档标题3.12.16，本机原夹具实际3.12.14/SQLite3.53.1；运行时身份/hash需重新记录，非精确源码认证。访问2026-10-31。

原夹具已证明本机退出/重开与幂等重试，但没有竞争写者。本扩展仅验证A持有写事务时B在BEGIN被拒绝，随后A提交后B重试相同业务请求返回原receipt，不重复发奖。

## 同一请求，两个长期存活的独立子进程

独立新数据库：opening=100；请求R=(reward-1,25,quest)。DELETE+EXTRA，显式LEGACY_TRANSACTION_CONTROL/isolation_level=None。A与B用独立连接；B设置timeout=0并回读busy_timeout=0，避免库内部等待掩盖起点。

父进程用每子进程独立stdin/stdout管道，按行JSON消息驱动；stdout仅作有序协议，stderr独立保存。消息带角色/阶段/请求标识。等待使用select或读线程+Queue.get(timeout)，超时只判失败并保存证据，不依靠sleep猜谁先获得锁。

## 确定的状态序列

1. 初始化子进程提交opening，关闭连接。启动A/B；各自报告READY及配置/身份，任何配置不符即停止。
2. 父命令A APPLY_HOLD。A执行BEGIN IMMEDIATE，查R不存在，UPDATE余额与INSERT receipt，但不COMMIT；返回HELD，包含in_transaction=true、事务内余额125/R一次。
3. **只有收到HELD后**父命令B TRY_BEGIN。B实际执行BEGIN IMMEDIATE并捕获数据库异常。预期sqlite_errorcode=SQLITE_BUSY（5）、sqlite_errorname=SQLITE_BUSY、in_transaction=false。此分支不执行任何UPDATE/INSERT。B用独立的SELECT语句读取持久快照100/onlyopening，然后结束该读取语句，报告BUSY_OBSERVED。
4. **只有收到BUSY_OBSERVED后**父命令A COMMIT。A真正SQL COMMIT成功后报告COMMITTED且in_transaction=false。若COMMIT出现BUSY，不将其归为步骤3已验证情况，直接记录失败；本测试不安排长读事务。
5. **只有收到COMMITTED后**父命令B RETRY_SAME。B重新BEGIN IMMEDIATE，查到同payload的R，返回存储的balance_after=125，不UPDATE/INSERT，COMMIT结束，报告DUPLICATE。
6. A/B按命令关闭连接，父核对正常退出；第三个全新读取进程验证最终余额125、opening与R两条、sum(amount)=125、R数量1、integrity_check=ok。

B的持久快照100只在A仍持有事务时读取。查询cursor须fetchall/close后才报告，从而不让自己意外持读锁影响A COMMIT。数据库很小不会刻意触发cache spill；若环境让该读取也出现BUSY，须记录并评估，不静默加sleep直到过。

## Oracle：不能让故意raise假装锁行为

- BUSY必须来自B实际调用BEGIN IMMEDIATE的sqlite3异常，保存code/name/原message/阶段；不能手写异常作为证据。
- HELD前后的A事务状态、B拒绝后状态、A COMMIT返回以及B重试结果各有真实查询；父接受顺序来自握手记录而非时间差。
- 所有请求R相同，不换新ID绕过重复；最终独立读回不只比较余额，也核对receipt身份与payload。
- 保存完整各进程收发序列、stdout/stderr、退出码/超时，原始数据库文本封装/hash及源/runtime身份。先清旧summary，异常不产PASS。
- 若应用路径记录SQL操作，可作为辅助核对，但请求日志不代替数据库状态；本例业务写仅允许在A，B成功重试只返回现有记录。

## 界限与停止

只做一个竞争→提交→同请求重试序列。不另加改payload，因为原夹具已实测此冲突；它不是并发相关缺口。也不测试COMMIT BUSY场景、多个公平排队、死锁、WAL、网络、断电或性能。

本例在明确收到A提交后再重试，是测试驱动的时序控制，不是生产通用重试建议。真实系统须处理超时、取消、重试上限、外部响应未知及其他SQLite错误；不能由这一个序列推出“BUSY就立即无限重试”。

获准后仅在本目录新建worker/runner，原fixture源码/结果保持不动。停止于一次完整握手执行与独立复跑，不扩展成锁测试套件。
