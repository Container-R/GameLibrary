# SQLite 延迟外键的两连接有限观察

辅助函数已经释放自己的保存点，为什么整次保存仍可能被拒绝？这份记录只观察 SQLite 外键检查发生的时点，以及拒绝之后事务和保存点还能怎样收束。它不是完整游戏保存系统或生产恢复方案。

## 实际观察了什么

2026-11-03，主编与独立审查者各执行一次完整夹具。每轮在新目录中分别建立 A、B、C 三个文件数据库，每个数据库使用写连接 W 与读连接 R。连接以 `cache=private` 显式打开；两连接均实际查询确认外键已开启、DELETE 日志模式和 `read_uncommitted=0`。查询耗尽结果并关闭游标。Python 使用显式 SQL 管理事务，不使用 `executescript`。

两表初始为空：`owner` 保存所有者编号，`inventory` 的非空 `owner_id` 引用该编号。预定道具行是 `(1,7)`，修复父行是 `(7)`。

| 分支 | 实际关键结果 |
|---|---|
| A：延迟外键、外层 BEGIN 与内层保存点 | 插入道具并释放内层保存点成功；COMMIT 因 787 被拒绝，W 的事务仍开、道具仍在，R 仍为空；插入父行后再次 COMMIT 成功，两连接都读到父子行。 |
| B：延迟外键、直接建立最外保存点 | 插入道具后 RELEASE 因 787 被拒绝；随后对同一保存点执行 ROLLBACK TO 成功，两表恢复为空但事务仍开；再 RELEASE 成功，事务结束。 |
| C：即时外键、显式 BEGIN | INSERT 就因 787 被拒绝，两表仍为空而事务继续打开；随后显式 ROLLBACK，事务结束。 |

三处拒绝实际捕获的名称均为 `SQLITE_CONSTRAINT_FOREIGNKEY`。A 的补父行是预先定义的教学选择，不能据此建议生产系统为了消除约束错误而创造账号或所有者。

每轮共 13 个检查点，分别是 A 的 5 点、B 的 5 点、C 的 3 点，不是 13 次独立运行。两轮原始输出逐字相同，但分别产生于两位操作者各自的一次运行；不是把首轮结果复制成第二次执行。两轮使用同一环境和相同冻结夹具，独立者已知首轮结果，不是盲复现或跨机器验证。

- [主编输出](observations/author-1/output.json)与[接收结果](observations/author-1/result.json)
- [独立输出](observations/independent-1/output.json)与[接收结果](observations/independent-1/result.json)

两个 output.json 的 SHA256 均为 `35ef98ca925be661d84c3d348f1fe158a6e26e2ee625d033d66d820264b2753b`。两份 result.json 均记录 PASS、退出码 0、stderr 为空、输入后检通过以及唯一子进程已回收。输出自报 Python 3.12.14、SQLite 3.53.1；这不是安装来源、二进制身份或固定 SQLite 源码认证。

## 输入、检查方式与复现

[冻结协议](fixture/PROTOCOL.md)、[数据库操作](fixture/driver.py)、[运行器](fixture/runner.py)、[字面预期](fixture/expected.json)由[输入清单](fixture/manifest.json)绑定。协议与源码中保留的“准备、未执行”文字是运行前冻结状态，不代表后来没有运行；为保持执行输入身份，没有在事后修改这些文件。这里的观察结果与运行前协议分开记录。

在支持这些接口的 Python 3.12 系列环境中，先读协议和源码，再从本资料目录执行以下命令；不要为复现自动安装替代版本：

```sh
python3.12 -I -B fixture/runner.py --run-name local-check-1
```

运行器会在 `fixture/local-runs/local-check-1` 下建立新目录；同名目录已存在就拒绝，不覆盖旧结果。它在启动唯一子进程前准备 11 个专用环境目录并检查可写，验证输入复制与前后摘要。子进程正常等待上限 15 秒，超时后尝试终止本次进程组并再等待至多 2 秒。`child_exit_confirmed` 只确认唯一 child 已回收，不代表另外验证了整个进程组消失；冻结 driver 不创建其他子进程。

设置、SQL 或读取检查点发生非预期异常会停止后续分支，原异常与关闭连接的异常保留在本地诊断。**各检查点的行值、事务标志及错误码是在运行结束后由运行器统一与字面预期比较**，不能将它说成每个数值偏差都在下一条 SQL 前立即终止。接收还要求退出码、stderr 和输入后检符合条件。

这里没有新增超时、故障注入或清理失败实验，也不继承旧保存点运行器的故障测试结果。正常关闭连接不等于崩溃恢复验证。范围不包含 WAL、锁竞争、并发写入、触发器、RESTRICT 动作、ORM、权限判断、断电安全或性能。

本包只保留安全技术文本与精确输入、输出，不包含数据库文件、环境目录、私有诊断和外部启动日志。自行运行产生的完整目录不要直接作为公开附件。包内文件身份见 [SHA256SUMS](SHA256SUMS)，清单不包含自身。

## 参考来源

- SQLite，[Foreign Key Support](https://www.sqlite.org/foreignkeys.html)，§2、§4.2及§4.3开头：外键启用、延迟检查和 RESTRICT 边界。
- SQLite，[Savepoints](https://www.sqlite.org/lang_savepoint.html)，§2–3：内外保存点及回滚语义。
- SQLite，[Result and Error Codes](https://www.sqlite.org/rescode.html#constraint_foreignkey)，787 条目。

上述为 2026-11-03 阅读的官方滚动文档，不是安装库实现身份。来源解释与实际两轮有限观察不能扩写成所有提交错误的统一恢复规则。

[SQLite 保存点与整次存档的提交边界](../../../GameLibrary/引擎与工具/运行时系统/缓存与存档/SQLite%20保存点与整次存档的提交边界.md)
