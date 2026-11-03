# SQLite 保存点：两连接顺序观察协议

状态：执行前冻结，NOT EXECUTED。只有准备文本与摘要；本文件不是运行回执。执行须先完成独立预审并取得批准。实际结果另存，不追改此历史状态。

## 要回答的问题

内层 RELEASE 成功不等于外层已经提交。ROLLBACK TO 保留匹配的保存点；没有 BEGIN 包围的最外层 SAVEPOINT 被 RELEASE 才结束事务。业务可见性与 in_transaction 分开记录，不把事务状态布尔值当业务成功。

这是 Python 3.12 系列标准 sqlite3 调用实际 SQLite 的有限 SQL 观察，不是固定 SQLite amalgamation 的 C API 构建验证。不支持其他 Python 系列，不安装或替换工具；实际 Python/SQLite 技术版本只在成功结果中记录。既不探测设备，也不采集主机名、执行器路径或二进制指纹。

## 冻结输入与字面预期

manifest.json 固定 PROTOCOL.md、driver.py、runner.py、expected.json 四项 SHA256；manifest 不自含摘要。expected.json 是预先规定的完整检查点字面值，与 driver 分离，不能由运行输出生成或修正。每例独立新建一个文件数据库，一行 id=1、qty=10；正常初始化语句处于自动提交状态。

|例|SQL 与检查点|预期 W/R 数量，W/R in_transaction|
|---|---|---|
|A|baseline；BEGIN 后 UPDATE20；SAVEPOINT helper 后 UPDATE30；RELEASE helper；ROLLBACK|10/10 false/false；20/10 true/false；30/10 true/false；30/10 true/false；10/10 false/false|
|B|baseline；BEGIN 后 UPDATE20；SAVEPOINT helper 后 UPDATE30；ROLLBACK TO helper；RELEASE helper；COMMIT|10/10 false/false；20/10 true/false；30/10 true/false；20/10 true/false；20/10 true/false；20/20 false/false|
|C|baseline；无 BEGIN，SAVEPOINT helper 后 UPDATE40；RELEASE helper|10/10 false/false；40/10 true/false；40/40 false/false|

共 14 个检查点。B 的 RELEASE 必须实际成功才继续提交，不凭最后的数值推断保存点仍在。A/B 的 UPDATE20 发生在保存点之前。C 与前两例使用不同数据库，不继承事务。

## 控制条件与失败

两连接显式使用 autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL、isolation_level=None、timeout=1.0；普通本地 file URI 显式 cache=private，不开启 shared cache。W 初始化时设置 journal_mode=DELETE 并核返回，两连接均读回 delete；read_uncommitted 设置并读回 0。设置不符合即失败，不降级到其他 journal 模式。

所有 SQL 单条 execute；每次查询 fetchall 后关闭 cursor。R 不 BEGIN，完成短读取后才让 W 继续。没有 executescript 或连接上下文管理器自动提交。SQL 异常、BUSY、设置不符均失败，不重试；finally 尝试关闭两个连接；原始 SQL/设置/检查点错误和各连接关闭错误分别收集到异常组，保留在本地 stderr，不让后一个清理错误覆盖前者，任何一项均不报告 PASS。失败时已完成的检查点前缀写入本地原始 stdout，不能以该部分输出通过 oracle。连接关闭清理不是额外业务提交。未做故障注入，清理失败不声称经过验证。

## 复现入口与边界

获批后，在包含四输入与 manifest.json 的专用目录执行：

    python3.12 runner.py --run-name main-1

复核者使用新的 run-name。runner 拒绝已有运行目录及路径软链接；源输入先核 hash，复制后再核四项 hash；子进程返回后再核原件、副本四项和原 manifest 身份，任一变化不能 PASS。此为有限复制检查，不声称防御并发恶意篡改。

第一个子进程之前建立新的 0700 run 根目录及 11 个独立环境目录：HOME；XDG_CACHE_HOME、XDG_CONFIG_HOME、XDG_DATA_HOME、XDG_STATE_HOME、XDG_RUNTIME_DIR、XDG_CONFIG_DIRS、XDG_DATA_DIRS；TMPDIR、TMP、TEMP。每个目录写入、读回并删除小探针。子进程环境只有这 11 项与 LANG=C、LC_ALL=C、TZ=UTC，不继承 LUA_*、PYTHON* 或其他宿主变量。解释器以 -I -E -B 启动。这里只隔离约定环境和工作目录，不是操作系统沙箱，也不保证解释器没有读取其标准库。

唯一子进程超时 15 秒，独立进程组，超时尝试终止进程组，随后最多再等待 2 秒回收；launch、wait、kill、二次 wait 错误分别记录。若有限回收未成功，保留失败并人工处理，不声称已清理完成，也不无限等待。此夹具不启动孙进程。无编译、安装、网络调用或压力测试。异常退出和完整原始 stdout/stderr 留在 local-runs/<run-name>/private-logs/，不公开这些原始失败日志。公共候选 result.json 只包含类别、返回码、输入摘要、超时、目录数量和通过时技术版本/输出摘要；无本地路径、PID 或机器指纹。启动前输入/目录检查异常直接失败，不生成虚假执行回执。

仅子进程 exit0、stderr 空、JSON 无重复键/非有限常量、字段与技术版本格式符合且全部 14 检查点的值和类型与预置 oracle 严格一致（布尔值不等同整数），才输出 PASS 和 output.json。原始 stderr 非空不得被吞成成功。output.json 与 result.json 均先写同目录临时文件，再 replace 发布；失败或中断不能留下仅部分写入的正式 PASS 回执。此处不宣称断电持久性。成功不复用旧结果。

## 解释停止线

这是三个微小原创数据集、同一进程顺序驱动两连接的可见性观察。不是多线程、WAL、共享缓存、崩溃恢复、断电持久性、磁盘同步设置或完整 C API 生命周期认证。DELETE 及正常 COMMIT 成功不能证明断电安全。内层 RELEASE 不提交也不意味着期间绝无磁盘 I/O。辅助函数能否提交外层事务仍由项目调用契约决定。

## 原始依据

- SQLite [Savepoints](https://www.sqlite.org/lang_savepoint.html)，Savepoints 与 Transaction Nesting Rules。
- SQLite [Transaction](https://www.sqlite.org/lang_transaction.html)，读写事务、隐式/显式事务、错误响应。
- Python [3.12 sqlite3 transaction control](https://docs.python.org/3.12/library/sqlite3.html#transaction-control)，legacy 与 isolation_level=None。
- SQLite [Isolation](https://www.sqlite.org/isolation.html)，独立连接及 shared-cache 例外；[journal_mode](https://www.sqlite.org/pragma.html#pragma_journal_mode)，设置返回实际模式。

读取日期 2026-11-03；滚动文档不是运行版本身份，来源门记录确切阅读范围。
