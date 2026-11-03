# 保存点的两连接有限观察

本包对应[辅助保存函数与外层回滚](../辅助保存函数已经成功，为什么外层回滚仍会撤销它.md)。它把文档中的事务归属区别变成顺序可读的数量变化，不是完整游戏存档实现。

2026-11-03，主编与独立审查者各执行一次相同冻结输入，均用新目录、新数据库。第二位操作者事先知道首轮结果，因此不是盲复现；两次在同一环境，不是跨机器或跨平台验证。没有重新编译 SQLite。

## 实际结果

每例初始唯一行 `id=1、qty=10`。写连接 W 与读连接 R 指向同例文件，明确私有缓存。逐条 SQL 操作，R 每次取完结果并关闭游标，无显式读事务。两连接均实际查询确认 DELETE 模式和 read_uncommitted=0；这些是 driver 中通过的检查，不是输出新增的打印字段。

|分支|关键检查点|W/R 数量|W/R in_transaction|
|---|---|---|---|
|A|外层改20，内层改30并释放|30/10|true/false|
|A|外层回滚|10/10|false/false|
|B|内层回滚到保存点，再释放该点|20/10|true/false|
|B|提交外层|20/20|false/false|
|C|最外保存点内改40|40/10|true/false|
|C|释放最外保存点|40/40|false/false|

两轮全部14检查点与执行前字面预期一致，正常退出0，stderr为空，没有运行失败后重试。两份技术输出逐字节相同，SHA256均为 `6caeea06bf0bb5447c48c0da3d5757cccbebe30752f579f0a411b88c7f00627a`。运行自报 Python 3.12.14、SQLite 3.53.1；未认证运行库安装来源或与某固定源码提交相同。

- [主编输出](observations/main-1/output.json) / [回执](observations/main-1/result.json)
- [独立操作者输出](observations/independent-1/output.json) / [回执](observations/independent-1/result.json)
- [冻结协议](fixture/PROTOCOL.md)、[driver](fixture/driver.py)、[runner](fixture/runner.py)、[字面预期](fixture/expected.json)、[输入manifest](fixture/manifest.json)

以上文件保留实际执行字节。协议和 manifest 的“未执行”是冻结时状态，不事后改写；本说明和回执给出执行结果。没有公开数据库文件、解释器指纹或原始私有日志。成功技术输出与本地stdout逐字节相同，公开回执无删字段变换。

## 怎样重做

需要已有 Python 3.12 与标准 sqlite3 模块；不满足时停止，不自动安装。进入 `fixture` 目录执行：

```sh
python3.12 runner.py --run-name reproduction-1
```

runner先核manifest与四输入，再复制到全新运行目录并核副本；重复run-name或符号链接被拒绝。第一个子进程前建立并检查11个新的0700环境目录，子进程只继承明确的小环境集合，不将这种隔离称为操作系统安全沙箱。

唯一子进程上限15秒，超时终止进程组并最多再等2秒；失败不得写成成功。运行后再核原输入、副本与manifest。JSON重复键、非有限常量及类型不符均拒收，14项预期不得依据结果改写。输出和回执通过同目录临时文件替换，避免直接写正式PASS文件时产生残片；这不声称已验证断电原子性。完整日志留在复现者自己的运行目录。

冻结manifest SHA256为 `111ec2d9a6b460ced9a63b2d48cfacd905b7428f53aea559f8f62256b73ada06`。本文不是一份包管理锁文件，运行技术版本与当前滚动文档版本分开记录。

## 执行前修正与限制

初稿runner静态预审未通过：终止后等待无明确期限、缺少执行后输入身份核对、正式回执直接写入、JSON比较未严格区分类型与重复键。四项修正并重新冻结、独立复审后才第一次运行；driver与14项字面预期没有因此更改。初稿及拒稿本地保存，公开审查保留其身份和原因。没有实际触发超时、故障清理或恶意JSON反例，不能把代码审读当成这些失败分支已运行。

这仅是单线程顺序调度的三例、两个连接、少量原创整数数据。没有多线程竞争、WAL、共享缓存、磁盘满、崩溃、断电、关闭重开或性能测试；也没有验证 ORM、连接池、外部文件、云端同步及整个游戏保存流程。内层释放未提交不代表期间没有磁盘I/O。游戏层由谁发出保存完成通知，仍需要项目定义，而不是由SQLite识别业务职责。

## 参考来源

1. SQLite，[Savepoints](https://www.sqlite.org/lang_savepoint.html)，§2–3。
2. SQLite，[Transaction](https://www.sqlite.org/lang_transaction.html)，显式/隐式事务、读写与错误边界。
3. SQLite，[Isolation](https://www.sqlite.org/isolation.html)，同连接与独立连接的可见性。
4. Python，[3.12 sqlite3 transaction control](https://docs.python.org/3.12/library/sqlite3.html#transaction-control)，LEGACY_TRANSACTION_CONTROL 与 isolation_level=None。
5. SQLite，[journal_mode](https://www.sqlite.org/pragma.html#pragma_journal_mode)及[URI查询参数](https://www.sqlite.org/uri.html)，DELETE实际返回与cache=private。

均于2026-11-03阅读相关技术段，SQLite为滚动文档，Python网页标识3.12.16；不是对运行库全实现的审计。

[返回技术解释](../辅助保存函数已经成功，为什么外层回滚仍会撤销它.md)
