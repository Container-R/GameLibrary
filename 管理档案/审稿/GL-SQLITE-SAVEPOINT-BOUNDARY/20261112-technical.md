# SQLite 保存点与整次存档的提交边界：独立专业模型全文审稿

日期：2026-11-12。结论：**通过（限定本文明确的事务接受边界，不认证完整存档系统）**。

## 身份、范围与结论

本轮为未参与正文写作的独立模型审稿，不是实际开发者试读、学术同行评议或新增实验复现。已读全文、两包 README、协议、driver、runner、字面预期、全部四份 output 与回执；未读作者计划或旧审稿。没有以历史 PASS 作为文章合格依据。

选题值得独立成文：它解决的是分模块保存中谁有权宣布整次保存被接受、失败应撤销哪一层，而不是备份文件是否完整。数量例、独立调用例和外键拒绝例共同支持这个单一问题，并未扩散为泛化数据库教程。正文包含决定操作的机制与步骤，复现包只提供可核查的输入输出，没有把必要解释藏到后台。

对于懂基本 SQL 与事务的游戏存档接入程序员，正文足以建立同连接调用契约、选择局部取消或整次取消、识别外层接受失败，并在本文的延迟外键条件下决定合法修复或明确放弃。不应把通过理解成提供了可直接投产的通用异常处理函数；正文自己已排除这种承诺。

## 逐项专业判断

- “同一份数量，三个阶段”：修改归属与同连接可见性区分清楚；先改20再立保存点是关键，能解释为何局部取消与整体取消不是同一个结果。
- “只撤销辅助函数”：替代结尾的提示防止读者把 ROLLBACK TO 接到已结束的事务后面。保留目标标记、随后释放再由外层提交的步骤完整。
- “RELEASE 也并非永远不提交”：独立调用是最重要的反例，正文正面处理，避免将内层规则误用到最外层；不建议辅助函数擅自 COMMIT 整个连接。
- “局部步骤成功，约束也可能等到提交才检查”：明确启用并读回外键，区分合法补父与制造业务实体，解释787不是自动恢复策略。外层失败后保留事务的结论仅针对这里的错误。
- Python 段准确限定 legacy 与 isolation_level=None，指出 executescript 破坏已有边界的具体风险，没有把包装层模式等同于 SQLite 事务状态。
- 两张实验表分别对应正常操作和约束拒绝，不以一个事务布尔值替代行值、错误码和后续可操作性的证据。

## 主动反例检查

1. 辅助函数无外层事务独立运行：释放可能结束事务，正文已处理，未发现反例漏洞。
2. 内层成功但跨模块关系仍缺失：外层不能宣布保存成功，正文提供延迟外键例和修复/取消分叉。
3. 读连接保留旧快照、共享缓存或大写事务锁阻塞：会改变简单数量表的可见性或执行结果。本文固定私有缓存、短查询与小顺序操作，且明确不外推并发，不构成表格的反证。
4. ON CONFLICT ROLLBACK 或部分资源错误可能终止整笔事务，不能一律在错误后 ROLLBACK TO。正文未作此保证，并明确排除任意提交错误恢复，因此不要求为了本篇扩建错误矩阵。
5. 多层帮助函数复用同名保存点会涉及最近匹配与栈纪律；本文只示范一层、固定次序，不是假装提供可重入封装。若未来扩大为通用辅助函数库，应补名称/栈所有权契约；这不是当前稿件阻断项。

未发现需要修订才能成立的实质错误或隐藏必要步骤。

## 本轮直接核对的一手来源

2026-11-12 重新打开官方滚动页面，而非采用旧审稿结论：

- https://www.sqlite.org/lang_savepoint.html ：§2–3，核对释放、回退和嵌套规则；未检查语法图图像。
- https://www.sqlite.org/foreignkeys.html ：§2、§4.2及§4.3开头，核对启用、延迟检查、拒绝后状态及 RESTRICT 的不同边界。
- https://docs.python.org/3.12/library/sqlite3.html ：连接参数和 Transaction control 相关段，核对 legacy、显式 SQL 和 executescript。
- https://www.sqlite.org/isolation.html ：同/异连接隔离与读事务边界。
- https://www.sqlite.org/lang_transaction.html ：事务嵌套与错误响应相关段。
- https://www.sqlite.org/rescode.html#constraint_foreignkey ：主/扩展码及787条目。

这些资料支持语义核对，不认证自报 SQLite 3.53.1 的安装来源。本轮没有采用候选中的历史来源/审查笔记来替代直接来源读取。

## 实验材料审计

保存点包：driver 确实在 A/B 的 SAVEPOINT 之前执行 UPDATE20；B 实际执行 ROLLBACK TO、RELEASE、COMMIT；C 无 BEGIN、单独新文件。两连接显式 cache=private、legacy/None，DELETE 与 read_uncommitted 读回检查，查询 fetchall 后关闭游标。协议的14点与 driver 顺序一致，两个 output 的完整检查点与 expected 按 JSON 值及类型表达完全一致，正文摘取值一致。

延迟外键包：driver 的父表先创建，A/B 使用 DEFERRABLE INITIALLY DEFERRED，C 使用即时声明；外键在事务外开启并检查。三处拒绝都通过实际 IntegrityError 的787和名称检查。B 并非凭 in_transaction 猜测保存点还在，而是继续实际执行同名回退及释放。13点精确行集、事务标志及错误字段与两份输出一致，正文摘要无偷换。

两包 manifest 所列各四输入的本地 SHA-256 均核对一致；四份输出摘要均与回执及 README 一致。runner 静态核对显示严格 JSON 比较在运行结束后统一发生，而不是每点即时 oracle；两个 runner 除 execution_scope 外相同。回执保存退出0、空 stderr、输入后检等字段，但本轮只审核这些现存材料，不新增或重新证明历史执行者身份。

本轮未重跑 driver/runner、未构建 SQLite、未故障注入、未做跨平台、锁竞争、WAL、崩溃/断电、性能或游戏端集成验证。此次分类回链更改没有改变实验程序或技术结论，无必要为了迁移另跑相同案例。未做远端写入或独立逐 blob 远端认证；交付者提到的4ed6db29对照不作为本次自行完成的工作。

## 最终字节绑定

以下为本轮实际读取的最终主文及两个包全部文件的 SHA-256 清单。此通过只适用于这些字节；后续实质正文修改需复核。

```text
9aa2c84deb980f5955f5fd7d2d1916ba411fc4a0fd7fbaab8f325e23e7c65406  GameLibrary/引擎与工具/运行时系统/缓存与存档/SQLite 保存点与整次存档的提交边界.md
5153716ffe6446640c4a80bb00fc3ce98f72525f0e6385e86695b6b894f95978  管理档案/支持资料/SQLite保存点两连接/README.md
ba30dd2bfc251866c1862edb15e3f009d019ae35139eecf01fd1706eca9a2537  管理档案/支持资料/SQLite保存点两连接/fixture/PROTOCOL.md
284abd85728d19ff601af7e3e59e837e83dee262c9f2807bf5b141b4a31227d6  管理档案/支持资料/SQLite保存点两连接/fixture/driver.py
085a819e5fa206f99f08ff63b1664cbf94c68032d2bac34cd77b8d1e36c3e363  管理档案/支持资料/SQLite保存点两连接/fixture/expected.json
111ec2d9a6b460ced9a63b2d48cfacd905b7428f53aea559f8f62256b73ada06  管理档案/支持资料/SQLite保存点两连接/fixture/manifest.json
4683d9aebdeacd5f15985e0e34bfa502e30978e98b7150a68b0f9b64ae899a38  管理档案/支持资料/SQLite保存点两连接/fixture/runner.py
6caeea06bf0bb5447c48c0da3d5757cccbebe30752f579f0a411b88c7f00627a  管理档案/支持资料/SQLite保存点两连接/observations/independent-1/output.json
62e39ccfccd91bdd8b374432c6ccc52b0f4b0e54d2124afba8b3a19ad499d988  管理档案/支持资料/SQLite保存点两连接/observations/independent-1/result.json
6caeea06bf0bb5447c48c0da3d5757cccbebe30752f579f0a411b88c7f00627a  管理档案/支持资料/SQLite保存点两连接/observations/main-1/output.json
62e39ccfccd91bdd8b374432c6ccc52b0f4b0e54d2124afba8b3a19ad499d988  管理档案/支持资料/SQLite保存点两连接/observations/main-1/result.json
f14751097c34cee456e4202d2f608a8ed725b82218eb41af80a7f2eab5fe2741  管理档案/支持资料/SQLite延迟外键两连接/README.md
aa33cc981b3b2bd5f950a891d3a29c99d8439138f3f075d7d1d553561127b319  管理档案/支持资料/SQLite延迟外键两连接/SHA256SUMS
d6b8c8c59714e57f563e7bccacf5f09c52d52b221f68fa1ac4a29c31ba362371  管理档案/支持资料/SQLite延迟外键两连接/fixture/PROTOCOL.md
bde55c41d1dd5f94498b5bef58f3a2b958c45d91a862fe3c746048ce89b8057a  管理档案/支持资料/SQLite延迟外键两连接/fixture/driver.py
0e66839cb98b1a5ceed92a9e82b3780790b81830e6519ae4970af071b062c742  管理档案/支持资料/SQLite延迟外键两连接/fixture/expected.json
9e458ae0cad8cdd91e6e0946a8320f30c8b5472671b531aea2257c87c5f002b7  管理档案/支持资料/SQLite延迟外键两连接/fixture/manifest.json
bfe6fe2890ecee42e9e36821704aa471d9e2767944b620782bfd46ace6e18551  管理档案/支持资料/SQLite延迟外键两连接/fixture/runner.py
35ef98ca925be661d84c3d348f1fe158a6e26e2ee625d033d66d820264b2753b  管理档案/支持资料/SQLite延迟外键两连接/observations/author-1/output.json
6e16f4ee6f257dcbd1d9ea5daf48a5c231adda77232b0ac3651a42901b4a7961  管理档案/支持资料/SQLite延迟外键两连接/observations/author-1/result.json
35ef98ca925be661d84c3d348f1fe158a6e26e2ee625d033d66d820264b2753b  管理档案/支持资料/SQLite延迟外键两连接/observations/independent-1/output.json
6e16f4ee6f257dcbd1d9ea5daf48a5c231adda77232b0ac3651a42901b4a7961  管理档案/支持资料/SQLite延迟外键两连接/observations/independent-1/result.json
```
