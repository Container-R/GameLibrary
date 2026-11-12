# SQLite 备份正文独立专业审稿

日期：2026-11-12。性质：未参与初稿的独立模型审稿，不是真人试读、实际开发者使用证明或学术同行评议。未读取作者自评或历史通过记录；未重新编译或执行实验；候选只读。

## 结论

**通过（正文技术范围内）。** 文章兑现了为具备文件与数据库接入基础的游戏运行时程序员解释一致备份、分步完成/取消判断及业务读回的承诺。不存在需要补实验才能消除的关键不确定性。此结论不替代导航审查或发布责任者的最终全文核对。

正文路径：`GameLibrary/引擎与工具/运行时系统/缓存与存档/SQLite 存档已经提交，为什么只复制数据库文件还会漏掉进度.md`

全文 SHA-256：`b7e59b376e698230f0f758053dfcf7afe864864767fc9c3840125c33ce8bcedb`。只适用于这一字节版本。

## 实际核对与判断

1. **问题与机制。** 开篇“源连接读到7、主文件复制品却缺行”是有价值的接口边界错误。正文交代提交可能只写WAL、连接读取结合主库与WAL、检查点回写三者关系，因此文件摘要一致无法证明逻辑数据库完整。官方 WAL §2、§2.1、§2.2、§4支持这一因果链。没有把一次空表观察泛化为所有主文件复制必丢数据。
2. **方法及必要条件。** 活动主库/WAL逐个复制不保证同一状态，检查点之后仍可能继续写入。转用数据库层备份、独立候选、不覆盖唯一可恢复副本、完成后新连接读目标，形成可操作流程。业务提交边界、跨文件引用和并发写入重启都在正文解释，没有暗示API会补上未提交的内存状态或协调截图等外部资产。
3. **C完成与取消。** 亲读 driver.c 的 branch、business、create_db，以及协议与runner。完整支实际18步，前17次0、末次101且remaining=0；取消支只一步0、remaining=17。两支finish均0，但新只读目标分别读回[1,7,65536]与[1,3,0]。两轮原始输出各27行、逐字一致。代码确实关闭创建连接，重开预检，成功init后只操作备份句柄，finish后关闭源/目标再另开只读目标；schema、唯一行及零blob内容不是只打印预期值。与官方 step/finish 契约一致。正文将DONE、收尾、业务接受分开，且说明finish后不能续用句柄；关键知识均在正文。
4. **Python/WAL对照。** 亲读协议、runner.py和两轮17行stdout及receipt。runner明确BEGIN/COMMIT，空基线TRUNCATE检查点后保持源连接打开，后续提交不再检查点。两轮均记录WAL=4152字节、主文件仍为基线摘要、普通复制品空行、backup两次进度后DONE、关闭目标写连接再重开得到[1,7]，末尾源仍为7。这里真正区分了错误复制对象与提交失败，不是因提前关闭源而掩盖WAL。Python运行版本只作自报，文章明确不当运行库认证。
5. **完整性与取舍。** 读者能依据正文判定“step OK后玩家取消、finish OK、旧目标仍为3”必须显示取消、不得发布新进度；也能判定“DONE且finish OK，但任务仍未提交”不能声称整次业务保存完整。无需后台协议才能完成这两项代表任务。正文没有提供生产重试循环，但明确交付的是三个判据，不能因未覆盖任意调度、崩溃和跨文件恢复而否决已兑现范围。可选链接涉及保存点、参数重绑、迁移及REPLACE，不是当前核心论证的必要前置。

## 一手资料复核（本轮实际读取）

- https://sqlite.org/wal.html ：§2–2.2与§4；提交/读取/检查点及WAL持久状态。
- https://sqlite.org/backup.html ：§1与§3.1–3.2；数据库层副本、源变化可能重启且频繁重启可能无法完成、进度是最近step的记录。
- https://www.sqlite.org/c3ref/backup_finish.html ：init/step/finish及Concurrent Usage of Database Handles；DONE判据、未完成finish回滚、finish OK不等于完成、句柄失效、目标连接禁止夹入其他API。特别复核BUSY/LOCKED也不影响finish返回值，正文“不以finish OK代替DONE”的判据仍成立。
- https://docs.python.org/3.12/library/sqlite3.html#sqlite3.Connection.backup ：target、pages、progress、name及示例。当前页面显示3.12.16，不混同实验自报3.12.14。
- https://www.sqlite.org/releaselog/3_50_4.html ：2025-07-30发布日期、SOURCE_ID和sqlite3.c SHA3-256与保存的SOURCE.json/协议一致。本轮没有重新下载amalgamation，不宣称另行认证原二进制。

以上是滚动页面在2026-11-12的复核，不冒充固定版本网页快照；本报告仅概述支持关系，没有整页转载。

## 证据字节绑定

C材料根：`管理档案/支持资料/SQLite备份提前收尾/`

- fixture/PROTOCOL.md：`e149374b252b7183f5a6a16ab56f0829569c0ae470ee5700664f9835b9403c31`
- fixture/driver.c：`66067210156bc72c5bb7d300b4dfba98fe6c851612632402c431938ddc7a2e2d`
- fixture/runner.py：`3bc483bcea4bd22afbd04ab15b754db11f9c30e829b771a1bc716e97ef2128b5`
- fixture/manifest.json：`f32c9f8d9f032a02de2f42ecd4217c23ee3dc4e50175c7d4050b866bb02e4505`
- observations/main-1/output.jsonl与independent-1/output.jsonl均为：`d17bc5b2c149a934e9904e7870fc88f40bdef4012bf2fd1a36faceb059850778`

Python材料根：`管理档案/研究记录/experiments/sqlite-wal-main-copy-backup/`

- fixture/PROTOCOL.md：`c20fb834b16a9c8b08b382fa458665d095d4ad45a087295c67e99f7a4d3c9f5a`
- fixture/runner.py：`3eea751d9c09c70cc0a00c36c5d7172979d89e9713586a8b3cebff3769512712`
- observations/author-1/stdout.jsonl与independent-1/stdout.jsonl均为：`8db174a843b25792afa9960401ed41e4827d60faac996372353f0c780e944e9b`

以上摘要本轮直接计算。两套原始结果分别绑定其代码，不把C的DELETE模式结果与Python的WAL结果混为同次执行。

## 反例与未验证边界

- 若已完成检查点且无后续写入，单独主文件可能包含最新数据；不推翻文章的“不能直接画等号”。
- 并发写入可能改变完成时快照或使分步操作不终止；正文已限制，有限无并发实验不承担这项保证。
- 新目标没有旧值时，取消不能被解释为“必然恢复数量3”；正文把3限定为本次有旧值测试目标。
- 新连接读回正确不能证明断电持久性、恢复替换原子性、跨设备兼容或跨文件一致性；正文已明示。
- 无需为当前结论补所有平台测试。若今后承诺上述行为，应另行研究而不是复用本通过记录。

## 集成注意（非技术退稿项）

重算提供的evidence-tree-check.json中29个本地Git blob：28个仍与expected一致；唯一差异是C材料README.md，当前blob为`1ff39b7fdd92ad9b4057999a0409363d62311da7`，表内为`198a4c25c6b6d66481e83de91e876d6d677be261`。决定本结论的协议、代码、原始输出没有变化。这已即时报告集成者，发布前应注明README的候选变更或更新核对表，不能继续无条件声称当前29个对象均等于旧远端树。本轮未另查远端树；expected的远端归属取自交付记录，不冒称亲自远端复核。

技术通过无强制正文修订项。若修改正文实质内容，必须更新摘要并复核受影响论证；若扩大到可直接投产的C接入代码，应补init失败/目标事务前置条件、错误分类及取消调度，不能把本文目前的判据说明当成完整实现。

集成者随后确认：证据表是编辑前远端基线核验，C README的两处主文回链属于本轮有意变更，并将补记阶段和最终绑定。此说明解释差异，不改变上述本轮实际复算结果与技术结论。
