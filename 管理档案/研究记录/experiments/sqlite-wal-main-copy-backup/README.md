# SQLite WAL：只复制主文件与连接备份的有限观察

本包只研究一个正常提交、无并发写入的小数据库。源连接保持打开时，主文件复制品中的表为空；连接备份的读回包含 `(1,7)`。这不是通用备份安全认证，也不是崩溃、断电或云同步实验。

## 当前实际证据

当前包包含 **1 次作者侧 + 1 次独立数据库观察，共 2 次 SQLite 子进程**。作者记录：[原始逐行输出](observations/author-1/stdout.jsonl)、[回执](observations/author-1/receipt.json)、[空 stderr](observations/author-1/stderr.bin)。子进程退出 0，终止已确认，四个执行输入前后摘要一致。记录中 Python/SQLite 版本是运行时自报，不是安装来源认证。

两次观察中，准备阶段检查点返回 `[0,0,0]`、WAL 为零字节；提交后源读到一行，WAL 为 4152 字节，主文件摘要仍等于空基线。只复制主文件后读到空表；每轮一次连接备份经两次进度回调正常返回，关闭目的连接再打开读到同一行。源最后仍有一行。具体数值是这两次输出，不承诺其他系统的 WAL 大小或备份步数一致。

独立记录：[逐行输出](observations/independent-1/stdout.jsonl)、[回执](observations/independent-1/receipt.json)、[空 stderr](observations/independent-1/stderr.bin)。两轮在同一环境、同一夹具和同一条件下，分别在新目录实际执行；文本输出相同，不是复制作者结果来冒充重复，也不算跨机器验证。独立者先读作者结果，然后在独立执行前冻结 [接受表](INDEPENDENT-ACCEPTANCE.json)，因此不是盲复现。完整 [独立审查](NATIVE-REVIEW.md) 保留这一时间边界。没有复制数据库二进制、运行环境目录或私有异常诊断。

另有 **1 次纯合成消费者测试**，调用 `check_events` 共 7 次：1 条字面合法轨迹被接受，删除阶段、改变序号、改变复制结果、改变备份剩余页、改变最终成功数据、改变主文件摘要这 6 个突变被拒绝。[输出](pure/pure-trace.stdout)、[stderr](pure/pure-trace.stderr)、[退出码](pure/pure-trace.exit)。它不导入 SQLite，也不启动子进程，不能算数据库运行或数据库行为验证。

## 如何复现这个有限配置

先阅读 [冻结协议](fixture/PROTOCOL.md)，并在拥有 Python 3.12 `sqlite3.Connection.backup` 的环境中自行审查。未承诺所有平台都有 WAL 支持。解压本包后，在包根目录执行：

```sh
python3 -I -B fixture/launcher.py "$PWD/fresh-observation"
```

`fresh-observation` 必须不存在，父目录必须已经存在；拒绝复用和符号链接祖先。launcher 创建并验证 HOME、三个 XDG 目录及 TMPDIR，然后启动唯一的 runner。等待 15 秒，超时只终止其拥有的直接子进程并有限等待；不重试，不自动删除失败现场。若终止未确认，回执不会将它写成成功。

四个冻结执行输入在 `fixture/`，逐字保留。`test_trace.py` 是另附的纯消费者检查，可以单独运行：

```sh
python3 -I -B fixture/test_trace.py
```

不能把新运行产生的整个目录直接公开：其中可能有私有错误栈、实际环境目录和数据库文件。当前包仅选择安全原始文本；数据库摘要只关联本实验复制字节，不是安装二进制指纹。

## 预执行修订记录

最初候选的父级只检查末尾成功标签，最终收尾摘要未再次参与判定。审查后增加了有限事件顺序和核心结果关系检查、最终源码摘要缺失或不符即失败、临时回执关闭后替换正式回执；同时明确实际事务属性读回、`-B` 及子进程终止确认。这些是执行前源码修订，没有把失败的数据库观察改写成成功。原始私有诊断和历史工作副本不随包发布。[预执行独立审查](PREEXEC-REVIEW.md) 保留实际初稿问题、最终四输入及有限消费者的类型检查边界。

## 不应从结果推出什么

正常关闭不代表断电耐久性；一次无并发写入备份不证明任意并发负载一定完成。只复制主文件在本配置中缺少提交，不意味着所有时刻的主文件副本都必然缺数据。实验也没有提出把活跃库的主文件/WAL/SHM 分别复制的安全算法，未覆盖数据库之外的资产版本或跨文件一致性。

## 原始依据

- [SQLite WAL §2–4](https://www.sqlite.org/wal.html)：提交、检查点与 WAL 的持久状态。
- [SQLite Backup API](https://www.sqlite.org/backup.html)：数据库内容备份及并发写入限制。
- [SQLite PRAGMA](https://www.sqlite.org/pragma.html#pragma_wal_checkpoint)：检查点返回值及自动检查点配置。
- [Python 3.12 sqlite3](https://docs.python.org/3.12/library/sqlite3.html)：Connection.backup 和显式事务控制。本次阅读的 3.12 文档分支显示 3.12.16，不等于本观察自报的补丁版本。

协议中的 GATE 是前置来源与去重审查记录，不是执行依赖；以上列出可直接阅读的官方入口。滚动文档读取日期为 2026-11-02，不据此认证底层实现版本。

---

[返回存档备份文章](../../../../GameLibrary/%E5%BC%95%E6%93%8E%E4%B8%8E%E5%B7%A5%E5%85%B7/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%B3%BB%E7%BB%9F/%E7%BC%93%E5%AD%98%E4%B8%8E%E5%AD%98%E6%A1%A3/SQLite%20%E5%AD%98%E6%A1%A3%E5%B7%B2%E7%BB%8F%E6%8F%90%E4%BA%A4%EF%BC%8C%E4%B8%BA%E4%BB%80%E4%B9%88%E5%8F%AA%E5%A4%8D%E5%88%B6%E6%95%B0%E6%8D%AE%E5%BA%93%E6%96%87%E4%BB%B6%E8%BF%98%E4%BC%9A%E6%BC%8F%E6%8E%89%E8%BF%9B%E5%BA%A6.md)
