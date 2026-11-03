# SQLite 3.50.4：C 分步备份完成与提前取消

状态：候选输入，未编译、未执行；须经主审与独立预执行审查、单独执行批准后才能运行。此协议不替代旧 Python 备份观察，也不改变其身份。

## 问题与固定范围

仅观察两个互斥生命周期：完整复制到 DONE 后 finish，以及只复制一页、仍未完成时 finish。两个分支分别建立独立 source.db / dest.db。完成后的业务读回是每个分支的共同检查，不是第三分支。

固定官方 SQLite 3.50.4 amalgamation：
- URL：https://www.sqlite.org/2025/sqlite-amalgamation-3500400.zip
- 官方发布说明：https://www.sqlite.org/releaselog/3_50_4.html
- sqlite3.c SHA3-256：9145255e83da6529e70121ee4d7a4c88fe83ca4511da0c9ed13d10842df36782
- SOURCE_ID：2025-07-30 19:33:53 4d8adfb30e03f9cf27f800a2c1ba3c48fb4ca1b08b0f5ed59a4d5ecbf45e20a3
- 这不是 ZIP 的 SHA3，也不是 SHA256。manifest 另列 c/h 与本协议、driver、runner 的 SHA256。源文件保持原字节。

复现时先由操作者从上述固定官方 ZIP 手动取得原字节 sqlite3.c 与 sqlite3.h，放入相邻 source/ 目录，核对 manifest 中各自 SHA256；runner 只离线核验，不自动下载或寻找替代库。公开材料不附这两份大源码或 ZIP，仅保留官方 URL、准确摘要和获取说明。

仅本地 cc 从 driver.c 和 sqlite3.c 构建，不链接 -lsqlite3，不安装软件。固定选项：`-O0 -std=c99 -DSQLITE_THREADSAFE=0 -DSQLITE_OMIT_LOAD_EXTENSION`。这是有限单线程构建，不证明发行版默认配置或并发语义。运行前 driver 核对库版本号 3050004、SOURCE_ID 与 threadsafe=0。

## 数据、预检查和字面判定

两支分别在 complete/ 与 cancel/ 目录中建立新的数据库。页大小固定 4096，journal_mode=DELETE，全部写入正常提交。只有一个用户表，精确 schema：

`CREATE TABLE save_item(id INTEGER PRIMARY KEY,qty INTEGER NOT NULL,pad BLOB NOT NULL)`

源恰一行：id=1，qty=7，pad 为 65536 字节零 blob。原目标恰一行：id=1，qty=3，pad 为零长度 blob。校验用户 schema 对象数、CREATE SQL、行数、id、qty、blob 类型、长度与所有字节为零。不是仅比较文件存在或长度。

创建连接先关闭。源以只读连接重开，目标以读写连接重开；再次核对配置和业务值。源 page_count 必须在 2..128 内。预检查不满足即失败，不能临场改变数据使首步返回 OK。运行没有其它进程或线程参与数据库访问。

1. 完整分支：init 成功后 step(1) 最多 128 次；每次记录实际 rc、remaining、pagecount。只接受 OK 或 DONE。pagecount 必须等于预查源页数。OK 必须 remaining>0，DONE 必须 remaining=0。必须见 DONE，然后 finish 恰一次且返回 OK。
2. 取消分支：成功 init 后仅 step(1) 一次，必须实际返回 OK 且 remaining>0；立即 finish 恰一次且返回 OK。不再 step，不把直接 DONE 当取消成功。
3. 每支 finish 后关闭原目标和源连接，另开只读目标连接，重新核对配置、精确 schema 和一行业务值。完整支必须 `(1,7,65536)`，取消支必须 `(1,3,0)`；第三项是零 blob 长度。关闭读回连接也必须成功。

成功 init 至 finish 之间不调用目标连接上的其它 API。只在备份句柄有效期间读取 remaining/pagecount；finish 之后不访问备份句柄。目标内容是在 finish 和关闭连接之后读回，不从缓存中的变量冒充查询。原目标文件不要求逐字节不变。

任何检查或 SQLite API 失败都使该轮失败；无错误重试。持有成功 init 的句柄时，失败清理仍恰一次 finish；清理返回码另记为 cleanup_finish，不当成正常分支成功。语句均 finalize；连接均尝试关闭，关闭失败不报告成功。若 init 返回 NULL，不对 NULL 调用 finish。操作系统在进程退出时回收剩余资源不算成功关闭观察。

## 执行、身份和保留

从原输入读取并检查全部五项 SHA256，再核 sqlite3.c 的官方 SHA3-256 和 c/h SOURCE_ID/version 声明。保存到新工作副本后再次核全部五项 SHA256。manifest 自身 SHA256 记录在 result 中；manifest 不包含自己的摘要。两次读取的输入不是已安装二进制身份。

拟运行方式：`python3 fixture/runner.py --run-name main-1`。只有明确批准后执行。runner 为每轮独占新 executions/<run-name>，拒绝复用。编译 120 秒、单次程序运行 5 秒。每个命令通过 Popen(start_new_session=True) 建立新的 POSIX 会话/进程组；超时对整个组发送 SIGKILL，再 wait 回收直接子进程，失败保留已有记录，不自动重跑。这仅是有限进程组清理，不是安全 sandbox；不承诺清理主动脱离该进程组的任意程序。只接受 POSIX 宿主。每支最多 128 次 step，取消支恰一次；无第三输入、无随机生成或依据结果调整 fixture。

输入文件、manifest、脚本与运行根的路径在 resolve 前逐级拒绝符号链接祖先。新建 executions、轮次、private-logs、work、工作副本子目录、分支目录及隔离目录均要求权限 0700；既存 executions 也必须是非符号链接的 0700 目录，否则停止，不自行放宽权限。这是受控输入下的静态路径检查，不声称消除恶意并发替换的竞态。

环境从白名单新建，不继承调用者环境。PATH 是预先写定的 `/usr/bin:/bin` 配置，不是观测到的编译器安装路径。HOME、XDG_CONFIG_HOME、XDG_DATA_HOME、XDG_CACHE_HOME、XDG_STATE_HOME、XDG_RUNTIME_DIR、XDG_CONFIG_DIRS、XDG_DATA_DIRS、TMPDIR、TMP、TEMP 指向该轮新隔离目录。固定 C locale 与 UTC。不联网、不探测硬件、不获取编译器版本或二进制摘要。

result 在准备开始即写 failed；只有完整编译成功、程序成功退出且明确输出通过标记及两支 finish/readback 判定才改 passed。保留 compile/run 返回码、输出摘要、复制核对标记、stderr/stdout 是否为空。发生超时或准备异常仅公开安全类别，不把包含本机路径的异常文本复制进摘要。源文件/协议哈希、实际技术结果可公开；private-logs、数据库文件、可执行文件、隔离目录不公开。stdout 由固定 driver 仅输出技术 JSONL，stderr 原件只在本地保留。无实际本机绝对路径、PID、主机名或编译器指纹进入公共 result。

## 解释边界

finish=OK 表示此调用链的收尾返回值，不等于先前已见 DONE。取消支保留旧业务值才支持所选内容回滚结论。独立读回是新连接，不等于另一个进程、另一主机或不同实现。若日后两名操作者运行同一源码，应明确是同宿主同输入的重复，不称跨平台验证。

不测试并发写入、BUSY/LOCKED 重试、WAL 文件复制、崩溃或断电、磁盘满、多个数据库文件一致性、云同步、性能或任意应用存档可靠性。旧 Python/WAL 观察保持原身份；本候选不冒领其结果。
