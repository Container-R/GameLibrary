# WAL 旧读快照为什么不能直接升级为写入

同一次奖励已经由另一个连接提交，旧读事务却仍查不到那条记录。如果此时直接尝试加钱，会发生什么？这份有限观察用 SQLite 的 WAL 模式把这个问题与“写入已经完成、只是提交受阻”分开。

一个工作进程在同一线程内按预定顺序操作连接 A、B。A 先读到余额 100、没有 reward-one；B 加 12 并把处理结果 112 与余额一同提交。A 不结束原事务，再读仍是旧视图。它连续两次尝试 UPDATE，均取得实际扩展错误 `SQLITE_BUSY_SNAPSHOT`（517，主码 5），且事务仍活动。A 随后回滚、开启新事务重读，看到已有结果，选择重复请求分支，不再加钱。关闭 A/B 后重新打开文件，仍只有一条操作记录、余额 112。

这是“丢弃旧视图后重新判断”的一个具体观察，不是所有 BUSY 都应采用的恢复规则。它没有把失败 UPDATE 改成重试 COMMIT，也没有把一次 SELECT 未找到记录当成永久的发奖资格。

## 已有结果与范围

- [作者第一次输出](author-run-1/stdout.json)／[终态记录](author-run-1/result.json)
- [作者第二次输出](author-run-2/stdout.json)／[终态记录](author-run-2/result.json)

另有独立审者在相同环境、两个新目录中各执行一次，并以执行前冻结的字面表核对四份结果：

- [独立第一次输出](reviewer-run-1/stdout.json)／[终态记录](reviewer-run-1/result.json)
- [独立第二次输出](reviewer-run-2/stdout.json)／[终态记录](reviewer-run-2/result.json)
- [独立验收与限制](independent/NATIVE-REVIEW.md)

共两次作者重复、两次独立审者执行；它们共享环境和夹具，不是跨机器复现或独立数据库实现。每次恰有一个工作子进程，打开两个初始连接及一个关闭后重开的连接。每次两次 517 是同一旧快照条件内的有限重试，不是不同模式、等待时长或压力条件。四份输出各自生成，字节相同；不能把内容相同当成互相复制，也不能据此推导所有平台都相同。

输出自报 Python 3.12.14、SQLite 3.53.1；这不是官方源码或二进制来源认证。逐连接实际读回 WAL、busy_timeout=0、read_uncommitted=0，以及 Python autocommit=-1、isolation_level=null。五个新空可写位置在启动前验证；这不是系统沙箱或完整文件访问隔离。

正常关闭和重开只说明该过程后的可见内容，不证明崩溃、断电或硬件持久性。该顺序也不是操作系统并行竞争、线上奖励服务、授权验证、跨服务事务或恰好一次实现。独立审者另外运行了九项合成消费者测试，不能计入数据库执行次数。

## 查看与复查

[协议](fixture/PROTOCOL.md)在实现前确定序列；[输入清单](fixture/INPUT-MANIFEST.json)绑定六个冻结输入。协议原文保留其编写时的候选措辞，不重写成事后协议；实际作者与独立审者结果如上。清单不是签名，不证明不受信任的材料一定真实执行过。

从本目录仅检查归档，可用以下命令。这不会打开 SQLite 或启动观察子进程：

```sh
python -I -B fixture/checker.py author-run-1
python -I -B fixture/checker.py author-run-2
python -I -B fixture/checker.py reviewer-run-1
python -I -B fixture/checker.py reviewer-run-2
python -I -B independent/verify_observation.py reviewer-run-1
```

若在受控环境自行重现，需要 Python 3.12 或更高、可用的标准库 sqlite3 及相应功能支持；不满足时应停止，不替换 WAL 或错误码判据。以下是复现说明，不表示本次又执行了一轮。输出目录必须尚不存在，父目录应由运行者掌握：

```sh
python -I -B fixture/run.py fresh-observation
```

每次只启动一个观察子进程，正常通信期限为 15 秒，终止后的收尾通信另有 5 秒期限。无法确认终止则保留工作目录并失败，不删除可能仍被使用的数据；不声称 Popen 本身具有这一超时保证。失败现场由运行者保留并审查，不能自动重试到通过。

原生运行与纯检查必须分开计数。`fixture/test_checker.py` 是合成记录的消费者测试，不是数据库观察；其正常模式十个方法曾由主编运行通过，未在此附带未经筛选的运行日志。

## 公开内容与修订历史

本包保留实际成功 stdout、终态记录，以及逐个确认零字节的 `stderr.internal.txt`。该名称沿用冻结检查器要求，不代表允许发布非空失败诊断。公开记录只含技术版本、状态、数据与必要的源码／公开输出身份；没有完整环境、实际进程标识、私有路径或本机可执行文件指纹。

执行前审查发现并修复了三项问题：连接事务模式只有传参而缺少实际属性回读；终止后通信没有有限期限；归档检查只信记录里的“stderr 为空”。当前冻结版本分别加入属性回读、有限收尾与保留规则、真实 stderr 文件检查。这些是运行前源码修正，不是数据库先失败再改期望。

另一组纯 mock 初稿三个方法均失败于预期超时尚未出现；初稿使用临时目录自动清理，未留下足够的内部错误细节。修订取消对整个 Python flags/version 对象的替换并保留诊断目录后，三个方法通过。不能因此断言初次失败的唯一原因；两轮均没有真正启动子进程或调用 SQLite。此包只记安全摘要，不复制含绝对路径的测试 traceback，也不把纯 mock 当成真实进程终止测试。

旧源码与原始纯失败日志仍作为本地历史保留，不在这里重新包装或改写冻结输入清单。加入的独立结果未改写两次作者输出；独立字面表在执行前冻结，读回工具在首轮独立执行后编写，不能把工具编写日期冒充预先协议。

## 机制来源

1. SQLite，[Isolation In SQLite](https://www.sqlite.org/isolation.html)，Isolation And Concurrency 的 WAL 旧快照说明。
2. SQLite，[Result and Error Codes](https://www.sqlite.org/rescode.html#busy_snapshot)，`SQLITE_BUSY_SNAPSHOT`。
3. SQLite，[Transaction](https://www.sqlite.org/lang_transaction.html)，§2.1–2.3 的事务升级、提交与错误处理区别。

上述是机制的官方来源；本包是特定绑定和预定交错的有限观察，不把自报版本当作这些网页对应源码的认证。来源阅读日期：2026-11-02。

---

[返回经济设计文章](../../../../GameLibrary/游戏设计/系统设计/成长与经济/用收支记录检查单机游戏的成长经济.md)
