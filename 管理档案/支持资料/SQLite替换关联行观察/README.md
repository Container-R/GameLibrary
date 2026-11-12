# REPLACE 与 UPSERT：父行相同，词条是否保留

2026-11-04，作者与独立执行者各完成一次同结构 SQL 观察，两轮结果一致。它补充[SQLite REPLACE 与 UPSERT：更新存档时保留关联数据](../../../GameLibrary/引擎与工具/运行时系统/缓存与存档/SQLite%20REPLACE%20与%20UPSERT：更新存档时保留关联数据.md)中的文档推导，不是新游戏案例，也不替代 SQLite 官方机制说明。

## 直接查询的结果

两支各建立一个独立内存数据库，普通父表保存装备，子表以 `ON DELETE CASCADE` 外键引用装备。每支初始父行均为 `(41,8)`，子行均为 `(41,'frost')`；先结束初始化事务，再分别执行正式正文所示的保存语句。没有其他修改者或用户定义触发器。

| 保存分支 | 保存前装备 / 词条 | 保存后装备 | 保存后词条 |
|---|---|---|---|
| INSERT OR REPLACE | `(41,8)` / `(41,'frost')` | `(41,9)` | 空集 |
| ON CONFLICT(item_id) DO UPDATE | `(41,8)` / `(41,'frost')` | `(41,9)` | `(41,'frost')` |

表中结果来自实际 SELECT 并取完结果，不是由预期值回填。两条保存语句均完成 execute、fetchall 和 cursor.close，随后连接的 `in_transaction` 均为 false；两支连接最终正常关闭。相同父行并不能证明从属数据仍在，关闭 `recursive_triggers` 也没有阻止这个例子的外键级联删除。

## 每个连接都确认的条件

- 显式 `autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL`、`isolation_level=None`，读回符合要求。
- 在事务外设置 `foreign_keys=ON`，各连接读回 `[(1,)]`。
- 设置 `recursive_triggers=OFF`，各连接读回 `[(0,)]`。
- 分支独立初始化，未从 REPLACE 已删除词条的结果继续做 UPSERT。
- 普通内存表、单线程、单连接分支，无扩展、网络、引擎包装器或用户数据。

运行自报 Python 3.12.14、链接的 SQLite 3.53.1。技术版本是运行库自报，不是官方二进制或固定源码来源认证。两轮执行返回码均为 0、stderr 均为空，关闭与输入前后检查通过，均未做失败重试。

## 冻结输入与两轮输出

- [执行前协议](fixture/PROTOCOL.md)
- [驱动代码](fixture/driver.py)、[启动与结果核对代码](fixture/runner.py)
- [预先写定的字面期望](fixture/expected.json)、[输入摘要清单](fixture/manifest.json)
- [作者直接查询输出](observations/author-1/output.json)、[作者执行回执](observations/author-1/result.json)
- [独立执行直接查询输出](observations/independent-1/output.json)、[独立执行回执](observations/independent-1/result.json)

协议中的 NOT EXECUTED 是执行前冻结时的历史状态，保留原字节；实际执行状态以本说明和回执区分，不追改协议来伪装历史。两轮使用的 manifest SHA-256 为 `e5961d67d7382f9bbc44506fbd2754aa9ad86e210ab923128aecbb98bbcf4de2`。

独立执行者先阅读作者结果，再使用同一冻结夹具在自己的新运行目录执行一次。两轮在同一环境中，各分支重新创建独立内存数据库；这是同环境复验，不是盲复现、跨平台或另一实现验证。

## 复现入口与停止边界

先阅读协议和代码。需要已有 Python 3.12 或更新版本、标准 sqlite3 与 SQLite 3.24.0 或更新版本；缺少能力时停止，不安装替代库。进入包含上述五个输入文件的 fixture 目录，以尚未使用过的运行名执行：

    python3 -I -B runner.py --run-name reader-1

启动器拒绝复用运行目录，检查固定输入，准备有限隔离环境，以 15 秒期限执行一个驱动子进程。结果必须完整符合预先写定的两支行集合、配置和完成状态；部分输出、超时、清理失败或输入变更都不能通过。十个检查点属于一次两支观察，不是十次独立试验。

公开材料只包含审过的固定输入、技术输出及回执；不包含私有错误日志、环境目录、执行机器路径或二进制指纹。输入摘要用于一致性检查，不是不可伪造的执行证明。

这不测试磁盘持久性、关闭重开、崩溃、并发、其他 SQLite 版本、任意 UPSERT、用户触发器、ORM、生产迁移或词条恢复。两轮两支全部使用同一运行环境。机制依据与原始官方资料见[正式正文的参考来源](../../../GameLibrary/引擎与工具/运行时系统/缓存与存档/SQLite%20REPLACE%20与%20UPSERT：更新存档时保留关联数据.md#参考来源)及冻结协议。
