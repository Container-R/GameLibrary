# SQLite WAL 主文件复制与连接备份：预执行冻结候选

状态：代码与协议供独立审查，未执行。能力检查由主审另行完成，不是本实验结果，也不继承旧实验的环境身份。本候选不允许自行试跑、参数扫描或失败后换条件重试。

## 来源与事务契约

沿用 GATE.md 的 SQLite 官方 WAL §2–4、Backup API §1/§3.1、PRAGMA wal_autocheckpoint/wal_checkpoint 阅读。本次另读 [Python 3.12 sqlite3](https://docs.python.org/3.12/library/sqlite3.html)：Connection.backup 参数及进度说明、connect 的 isolation_level/autocommit 条件、Transaction control via the isolation_level attribute。该版本分支当前页显示 3.12.16，不冒充主审能力检查的 Python 补丁版本。

所有连接显式使用 `autocommit=LEGACY_TRANSACTION_CONTROL, isolation_level=None, timeout=0`，SQL 明确 BEGIN/COMMIT；不使用 executescript、隐式提交或上下文管理器代替关闭。每条语句取完结果并关闭游标。备份参数固定 `pages=1, name='main', sleep=0.0`，进度每次记录 status/remaining/total；最多 16 次，状态仅接受 SQLITE_OK 或 SQLITE_DONE。超过次数或其他状态立即抛错。调用正常返回、末次 DONE、remaining=0 和目的连接无事务全部必要。无并发写，不推广为任意负载的备份保证。

## 启动与边界

四个执行输入：本协议、runner.py、launcher.py、isolation.py。isolation.py 是已读 `管理档案/工具/evidence/isolation.py` 的逐字副本，不修改其契约。

launcher 与 runner 分离。launcher 只接受绝对且不存在的运行目录，拒绝 `..`、根目录、符号链接祖先及复用；不递归补建缺失父目录。然后调用 prepare_environment 创建五个专用目录，调用 validate_environment 校验实际目录和环境映射，紧接着启动唯一子进程。runner 在导入 sqlite3 之前再验证同样五目录。不是整个进程环境隔离或安全沙箱。

启动形态是 `python3 -I launcher.py <新目录>`，内部以同一解释器的 `-I runner.py` 启动一个子进程，工作目录为新目录。最多一次子进程，等待上限 15 秒（从成功 Popen 后开始，不声称包含进程创建开销）；超时 kill 自己拥有的直接子进程，最多再等 5 秒回收，无重试。runner 不创建其他进程。强杀不保证执行 finally 或正常关闭，绝不记为通过。

## 固定输入、次序与全部 oracle

表定义：`CREATE TABLE save_item(id INTEGER PRIMARY KEY, qty INTEGER NOT NULL)`。唯一插入 `(1,7)`。每次查询同时核 table_info 字面结构和 `SELECT id, qty FROM save_item ORDER BY id`，不以文件存在或只数行代替。

1. 创建 source/plain/backup 三个新目录；源 `source/save.db`。读回 journal_mode 为 wal、wal_autocheckpoint 为 0、busy_timeout 为 0。
2. BEGIN 建表 COMMIT，无未结束事务。只在此时做一次 `wal_checkpoint(TRUNCATE)`：一行三整数，首列 0、后两列非负且相等；源 WAL 文件存在且大小为零；源表精确空。记录主文件摘要作为空基线。
3. BEGIN 插入 COMMIT，无未结束事务；源行集精确 `[(1,7)]`。主文件摘要仍等于空基线，WAL 大于零。源连接直到两个目的库的读回结束及源终检之后才关闭。
4. 只复制主文件到 `plain/save.db`，不复制/删除/移动源 WAL 或 SHM。复制品与源主文件摘要均等于基线。打开复制品，schema 匹配、行集 `[]`；关闭复制品连接。
5. 新建 `backup/save.db` 连接。源、目的均不在事务中。一次 backup 调用按上述进度限制完成；关闭目的写连接，重新打开目的库，schema 匹配、行集 `[(1,7)]`，然后关闭。
6. 源最后读回 `[(1,7)]` 且主文件仍为基线字节，再关闭源。只有所有关闭成功才输出 success。

阶段失败就不进入后续阶段。finally 只清理仍拥有的连接，不再执行比较或重做备份。首次异常保留，清理失败也导致失败。不能为了获得期望结果提前关闭源或新增检查点。

## 输出与审查

runner 输出按顺序编号的 JSONL：设置、基线、提交、复制、两种读回、备份每步、源终检、关闭、最终成功。失败仅公开异常类别，原始异常及栈写私有本地 private-error.txt，不纳入公开材料。launcher 以文件收集原始 stdout/stderr（包含超时前部分），保存安全 receipt：相对环境目录名、源文件前后摘要、返回码、输出摘要、状态和失败类别。原异常保留在私有 private-launcher-error.txt，不能整体上传运行目录。

父级接受必要条件：子进程退出 0、stderr 空、源代码前后不变、最终 success；随后独立审阅原始逐阶段记录是否满足上述字面 oracle。receipt 的 PASS 是本 runner 条件完成，不代替独立复核或运行库真实性认证。执行源摘要与数据库内容摘要不是安装二进制指纹。

## 停止与不覆盖范围

不支持 WAL、准备失败、任何结果不符、进度异常、超时、清理失败均终止首轮并保留证据；不调参数追成功。无断电/崩溃恢复、并发写入、云同步、跨文件资产一致性、任意 schema 或任意系统认证。普通文件复制故意只取主文件，不提供“活跃库三个文件依次复制”的通用建议。

未经独立协议/代码审查和明确执行许可，不运行 launcher 或 runner；目前没有本实验的实际数据库输出。

预执行审查收紧：launcher 对固定事件顺序、连续 seq、备份进度状态/次数、设置、空基线/两种行集及主文件摘要关联进行有限消费，不仅看末尾 success。最终再次取得源码摘要必须匹配，否则 FAIL；回执先写 receipt.pending、关闭后再替换 receipt.json。目录从不自动删除；若无法确认子进程终止，保留现场并失败，不能宣称正常清理。连接同时读回 autocommit 的 LEGACY_TRANSACTION_CONTROL 状态。
子进程命令同时加 `-B` 禁止写字节码缓存；推荐 launcher 入口同样使用 `python3 -I -B`。settings 记录实际连接 autocommit/isolation_level。成功 wait 或 kill 后成功 wait 才设置 termination_confirmed=true；若回收未确认保持 false，不能以退出文件存在替代终止事实。
