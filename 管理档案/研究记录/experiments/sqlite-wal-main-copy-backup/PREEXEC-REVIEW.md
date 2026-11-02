# SQLite WAL 主文件复制：独立执行前审查

## 2026-11-02 第一阶段：来源门槛；尚不接受执行

已完整读GATE及当时的runner、launcher、isolation源文件，仅静态阅读；PROTOCOL尚未交付冻结。本节不是代码最终接受，没有导入sqlite3、创建数据库、执行候选或探测本机运行库。

### 实际原始资料

独立打开官方 [WAL](https://www.sqlite.org/wal.html) §2–2.2、§3配置及§4，确认提交可能只追加WAL；主文件复制必须考虑持久WAL状态，最后连接关闭可能改变待观察条件。这里源连接持续打开、关闭自动检查点，并核实空基线主文件身份，是合理的有限安排，不是任意活跃数据库文件复制安全方法。

独立打开 [Backup API](https://www.sqlite.org/backup.html) §1、§3.1及相关循环说明。备份复制数据库逻辑内容；并发写入可能触发重启甚至不终结，不能将单次稳定源实验升级成固定起始时刻、任意并发进展或断电保证。

独立读 [PRAGMA](https://www.sqlite.org/pragma.html#pragma_wal_checkpoint) wal_autocheckpoint和wal_checkpoint完整条款：零关闭自动检查点，TRUNCATE成功会截短WAL，返回三整数且BUSY不能当完成。候选还应实际检查空schema、空行、WAL截短与主文件后续不变，而非只凭SQL返回无异常。

独立读 [Python3.12 sqlite3](https://docs.python.org/3.12/library/sqlite3.html) Connection.backup、isolation_level、autocommit和Transaction control。此次页头为3.12.16，文档不是已运行解释器身份。backup回调逐迭代给状态/剩余/总页数；pages=1不独自限制总工作量，必须另有进度上限和进程期限。显式LEGACY_TRANSACTION_CONTROL配isolation_level=None允许显式SQL BEGIN/COMMIT；autocommit=False会持续开启新事务，不宜混同“不在事务中”。这些资料尚未证明任意Python回调异常的底层清理实现，因此不凭文档空白扩张保证。

### 有限理论结论

在单源连接、无并发、表已检查点入主文件且为空、随后单行提交进入WAL而主文件字节未变的前提下：仅复制主文件预期可读空表，连接备份预期可读(1,7)，两者并不矛盾。复制品自生边文件不等于复制源WAL；保持源连接打开直至比较完成是关键。此预期未执行，任一前提失败须保留失败，不现场换步骤。

### 初读代码需要闭合的具体点

- launcher最终finally再次读取源身份，但初版仅记录未比较，且异常时不撤销先前PASS；应在全部身份后检完成后才发布整体接受状态。
- 正式receipt初版直接写入；需防写入/关闭失败留下貌似正式PASS，采用待定文件完整关闭后原子替换等有限收尾即可。
- 初版只查最后一条success。建议按固定事件/序号及关键实际观测关系做有限消费，至少避免末行标签掩盖缺失设置、失败或缺失中间比较；不需要泛化测试框架。
- 正式协议必须明确新根拥有关系、五目录保留/清理政策、15秒子进程期限与有限终止等待；预启动验证不是全部写入审计或完整沙箱。

以上已通知主编/作者；待最终协议、冻结身份和修订源到齐再继续，不授权运行，也不改作者文件。

### 第一阶段所读文件SHA256

- `GATE.md`：`ebea6c8969232c8e3376e36f08564ac30c899ddb13b7d216ab4ea92a6662ec8d`
- `runner.py`：`137290e62cf4b61075ef16ca5c51699924e908744629fdd52ac97f924f59b059`
- `launcher.py`：`ca2c5e70c7ba9a7ce87dda4d387c433e80e3a4bdb7699da98c70c1f6ff493478`
- `isolation.py`：`bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970`

## 最终四文件静态复审：接受有限预执行方案

再次完整读取冻结PROTOCOL、runner、launcher和helper。接受本次固定schema／单行／稳定源方案的协议与代码静态审查；不是执行许可或实验通过。初版三个收尾问题已闭合：最终源身份缺失或不一致强制FAIL；receipt.pending完整写入关闭后才替换正式receipt；消费器检查连续seq、阶段前后缀、1–16个备份进度、设置／检查点／行集／主文件摘要关联和关闭角色，而不再只信最后success。

### 实际调用和生命周期

runner显式使用LEGACY_TRANSACTION_CONTROL、isolation_level=None、timeout=0，并读回连接事务状态；每条SQL都fetchall及close游标。建表提交、TRUNCATE返回检查、零长WAL、空表检查先于唯一插入事务。提交后的源行真实查询为验收输入，不以硬写success代替查询。基线主文件身份在提交后、复制后和源终检重复核对；源保持打开，复制品不取得源边文件。

backup仅一次，pages=1，进度回调拒绝非OK/DONE及超过16次；正常返回且末次DONE、剩余0才继续。目的写连接关闭后重新打开并查表和行；之后源终检及源关闭，关闭失败不能success。没有预注册重试或额外检查点，实际阶段首错进入清理而非后续比较。

launcher以全新根拒绝复用和符号链接祖先；helper逐字等于现有工具副本，准备并验证五个实际目录与传入env，runner在导入sqlite3前再次校验。子命令确为同解释器 `-I -B`。普通等待15秒，异常时仅终止拥有的直接子进程、另限5秒等待；此固定runner不生成后代进程，因此不把直接子进程处理误称通用进程树清理。成功wait才记录termination_confirmed。根与失败证据保留，不自动删除任意目录；这不是完整沙箱或所有写入追踪。

### 有意保留的边界

消费器是固定可信fixture的有限轨迹检查，不是任意敌意JSON的通用验证器；例如部分字典等值检查没有对每一个数值逐项禁止bool，json.loads也未专门拒绝重复键。原runner使用json.dumps输出，没有外部可控JSON输入。本次不把该消费器作为独立安全边界或全面schema测试；正式结果仍须独立读完整原始轨迹，不能只引用receipt标签。

前后摘要证明运行期间文件关联，不能独自证明输入等于已审版本；主执行者启动前仍须核本节四个冻结摘要。不安装、不切换参数；Python接口不支持、WAL条件不符、进度/时间/清理失败均停首轮。即使正常结束，也不证明断电持久性、运行库官方身份、并发终结或所有schema备份安全。

本次只读源码、文档及文件摘要；未导入候选、未运行纯mock或SQLite、未创建数据库、未启动子实验，也没有声称负例已执行通过。初始版本及审查问题不删除。此前源文中未明确的回调异常实现细节，不作为本轮通用保证；外层进程截止仍独立约束本次调用。

### 最终被审SHA256

- `PROTOCOL.md`：`c20fb834b16a9c8b08b382fa458665d095d4ad45a087295c67e99f7a4d3c9f5a`
- `runner.py`：`3eea751d9c09c70cc0a00c36c5d7172979d89e9713586a8b3cebff3769512712`
- `launcher.py`：`60a13b34bc050bd041d5d306724f180cff25952d921c74c8e64e07ac39f23f07`
- `isolation.py`：`bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970`
