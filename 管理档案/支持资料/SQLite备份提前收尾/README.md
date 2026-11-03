# SQLite C 备份的完成与提前收尾

本包对应[取消备份也返回 OK 的解释](../取消备份也返回OK，怎样判断新存档是否真的备份完成.md)，不是完整游戏存档实现。2026-11-03，作者与另一操作者各执行一次冻结夹具，两轮均使用同一宿主、新目录和新编译。第二位操作者事先知道首轮结果，不是盲复现或跨平台验证。

## 两条实际路径

源中唯一道具数量是7，旧目标中是3。各分支分别新建数据库，使用4096字节页和DELETE日志；源行含65536字节零blob，使本次源实际占18页。目标不被其它连接同时访问。

| 分支 | step实际结果 | finish | 关闭后新只读连接读回 |
|---|---|---|---|
| 完整 | 前17步OK，第18步DONE，剩0页 | OK | 唯一行id1，数量7，零blob长度65536 |
| 提前收尾 | 仅第一步OK，仍余17页 | OK | 唯一行id1，数量3，零blob长度0 |

两轮均27行技术输出，逐字节一致；编译与运行返回0，编译stdout/stderr和运行stderr实际均为空。正常收尾的OK没有把取消分支变成新备份成功。

- [作者输出](observations/main-1/output.jsonl) / [回执](observations/main-1/result.json)
- [独立操作者输出](observations/independent-1/output.jsonl) / [回执](observations/independent-1/result.json)
- [冻结协议](fixture/PROTOCOL.md)、[C driver](fixture/driver.c)、[离线runner](fixture/runner.py)、[输入manifest](fixture/manifest.json)
- [固定来源身份](SOURCE.json)

以上协议、driver、runner、manifest、技术输出和回执保持执行时原字节。协议开头的“候选、未执行”是冻结前状态，不回改原协议；实际执行状态由本说明和两份回执给出。SOURCE.json为来源准备记录的公开字段子集，未改变URL、源码摘要、来源身份或测得字节数。没有复制私有stderr原件、数据库、可执行文件或完整第三方源码。

## 如何重做同一个有限观察

先从[官方历史包](https://www.sqlite.org/2025/sqlite-amalgamation-3500400.zip)取得原字节sqlite3.c和sqlite3.h，放在本包下新建的`source/`目录。不得用系统库替代。核对SOURCE.json的ZIP/c/h摘要，以及[官方3.50.4发布页](https://www.sqlite.org/releaselog/3_50_4.html)的sqlite3.c SHA3-256；它不是ZIP摘要，也不是SHA256。

在具备Python3、POSIX进程组和C编译器的环境，从本包运行：

```sh
python3 fixture/runner.py --run-name reproduction-1
```

runner离线校验全部输入，复制后再校验；只在新`executions/reproduction-1`中构建和运行，拒绝重用旧轮次。固定编译选项是`-O0 -std=c99 -DSQLITE_THREADSAFE=0 -DSQLITE_OMIT_LOAD_EXTENSION`，不是默认发行配置验证。编译期限120秒、程序5秒，超时使用进程组终止并记录失败；这段清理只经静态审读，没有实际触发超时测试，也不等于对任意程序的安全沙箱。

公开manifest包含必需c/h的身份，但源码不在仓库内；未先取得并核对原件时，输入校验应失败，不能称包开箱即完整。两次观察的output摘要均为`d17bc5b2c149a934e9904e7870fc88f40bdef4012bf2fd1a36faceb059850778`，冻结manifest摘要为`f32c9f8d9f032a02de2f42ecd4217c23ee3dc4e50175c7d4050b866bb02e4505`。

## 失败与范围

执行前初稿runner被拒：超时只终止直接编译器，未处理同组子进程；目录权限及符号链接检查也需补齐。修正、重新绑定输入并独立复核后才首次执行；不是先运行失败再改变SQLite预期。实际两轮编译/原生执行没有失败重试。原始初稿和拒稿记录本地保留，公开审查另述精确修订身份。

这只观察正常单线程文件访问中的两条C生命周期。关闭再打开是新连接，不是进程崩溃、断电、磁盘满或硬件落盘保证；没有并发写入、BUSY/LOCKED策略、WAL复制、跨文件一致性、云同步或性能测试。它也不替代已有Python备份观察。

## 参考来源

1. SQLite，[3.50.4 release](https://www.sqlite.org/releaselog/3_50_4.html)，2025-07-30，固定源码身份。
2. SQLite，[Online Backup API](https://www.sqlite.org/c3ref/backup_finish.html)，2026-11-03读取，step/finish、进度及目标连接限制。
3. 固定包sqlite3.c的backup_step/backup_finish（83378–83720附近）与sqlite3.h的Online Backup API注释；只审相关路径，不是完整SQLite审计。源码公开领域声明见[官方许可说明](https://www.sqlite.org/copyright.html)。

[返回技术解释](../取消备份也返回OK，怎样判断新存档是否真的备份完成.md)
