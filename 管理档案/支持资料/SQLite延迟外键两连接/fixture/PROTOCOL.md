# SQLite 延迟外键：冻结前准备协议

状态：准备、未执行。须先独立预审接受并取得主编明确执行批准。计划两位操作者各一次完整新目录运行，同环境、同夹具，不称盲复现或跨平台。此协议、driver、runner与字面expected由独立manifest绑定，不改旧保存点夹具。

## 问题与原源

本观察限定：内层释放成功不替代延迟外键的提交检查；该约束拒绝提交后事务仍开放，可作预定修复。最外保存点的释放受提交检查，而即时外键在INSERT时拒绝。

官方滚动来源：foreignkeys.html §2、§4.2及§4.3开头；lang_savepoint.html §2–3；rescode.html 的 SQLITE_CONSTRAINT_FOREIGNKEY 条目/列表（787）。读取日期2026-11-03，不认证安装来源。不是通用COMMIT错误恢复。

## 输入与前提

Python 3.12系列，标准sqlite3，不安装。显式LEGACY_TRANSACTION_CONTROL和isolation_level=None并检查实际属性。A/B/C各新文件，两个private-cache连接；检查DELETE、read_uncommitted=0，在任何事务前分别开启并读回foreign_keys=1。若不支持则失败停止，不降级。不使用executescript、连接上下文自动事务、并发、触发器、RESTRICT动作或WAL。各查询耗尽结果并关闭游标，读连接不保留显式事务。

owner(id INTEGER PRIMARY KEY)；inventory(id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL REFERENCES owner(id))。A/B外键明确DEFERRABLE INITIALLY DEFERRED，C明确NOT DEFERRABLE INITIALLY IMMEDIATE。初始两表空，预定子行(1,7)，修复父行(7)。父表存在，错误不是缺表或键配置不匹配。

## 固定三分支与13检查点

全部SQL逐条执行；只有以下三处预期拒绝。必须捕获sqlite3.IntegrityError，实际扩展码787且名称SQLITE_CONSTRAINT_FOREIGNKEY，否则失败并保留原错误。成功执行本应失败的语句也失败。

A五点：baseline空；BEGIN、SAVEPOINT helper、INSERT子行、RELEASE后nested_release；COMMIT拒绝后的commit_rejected；插父行后的parent_inserted；COMMIT成功后的committed。中间写连接有子行、读连接为空；补父后仅写连接有父行；最终两连接都读到父子行。事务标志依次false/true/true/true/false。

B五点：baseline空；直接SAVEPOINT helper并插子行后的outermost_insert；RELEASE拒绝后的release_rejected；ROLLBACK TO helper后的rollback_to（两表空、事务仍在）；RELEASE helper后的released_empty（空且事务结束）。失败释放后同一保存点仍可回滚并释放是必须实查的结果。读连接全程空。

C三点：baseline空；BEGIN后INSERT即时拒绝后的insert_rejected（空但事务仍在）；ROLLBACK后的rolled_back（空且事务结束）。

完整字面表见expected.json。每点记录case/phase、两个连接的两表精确行、事务标志和本阶段捕获错误或null；读连接标志全部false。13点不是13次独立数据库运行。此设计不允许据结果修改期望或错误分类。

## 执行与失败边界

runner复用已审保存点runner，仅改execution_scope字符串。实际运行命令待批准后为 `python3.12 -I -B runner.py --run-name author-1`（独立者另用新名称）。不在本准备阶段执行。其新根/祖先符号链接拒绝、11个新0700环境目录、写入读回删除检查、小环境、四输入复制前后hash、manifest前后hash、严格JSON类型/重复键/非有限数拒绝、临时文件替换回执均保留。

唯一child运行driver，15秒期限，超时杀本次进程组并最多再等2秒；未确认退出标失败且不清现场。driver不创建子进程。每位操作者只运行一次，无失败重试。配置检查在此child内，不另加隐式探测。

driver遇非预期错误保留已记录检查点，在本地stderr保存原异常和清理异常，首分支失败即不开始后续分支。所有连接在finally关闭；关闭不是实验中提交/回滚检查的替代。runner只有退出0、stderr空、全部严格字面匹配及后检通过才可PASS。未执行阶段不能拼接旧记录。

## 公开与限制

准备期间不产生数据库。未来仅安全技术输出、回执、源码/协议/字面期望身份可作为候选公开包；不要直接整体复制运行目录。数据库文件、11个环境目录、非空诊断、绝对路径、PID、解释器/安装二进制指纹不公开。版本只自报；预期异常捕获只输出其码/名称，不输出任意异常文本。

两轮计划不验证锁争用、断电、性能、共享缓存、WAL、ORM或整个游戏保存。补父行是预先定义的教学恢复，不授权生产中自动创造所有者。各SQL成功与约束成立也不证明业务权限或存档语义正确。
