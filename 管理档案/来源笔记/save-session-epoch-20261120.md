# 存档写入代次：证据与适用范围

- SQLite 官方 [Transaction](https://www.sqlite.org/lang_transaction.html) 和 [Isolation](https://www.sqlite.org/isolation.html)：独立连接只见已提交内容，同一时刻只有一个写者，`BEGIN IMMEDIATE` 可返回 `SQLITE_BUSY`。[SQL Language Expressions 的运算符段](https://www.sqlite.org/lang_expr.html#operators_and_parse_affecting_attributes) 支持整数运算溢出时转换到浮点。
- [SQLite 双连接试件](../实验/存档写入代次/README.md) 实际运行于 SQLite 3.53.1。通过明确调用顺序暂停旧请求，比较 B18 接管提交后且首次新写之前的内容与回执。不带代次可写一行；有守卫命中零行且提前暂写的旧回执回滚。现场随后 B18 的合法写与回执实际提交。A17→B18→A19 分别比较名字、旧代次、现任代次，命中 1、0、1，三个对照均回滚。另跑溢出与有界递增对照，无上限转 REAL 后再递增不变，有界试件命中 1、0，保留最大整数。观测 SHA256 `138c1c71ad0fc8107fccc7c90e527268a434462a3a9dbb9e60aab95dd8f42ad2`。
- PostgreSQL 18 [Transaction Isolation §13.2.1](https://www.postgresql.org/docs/18/transaction-iso.html#XACT-READ-COMMITTED) 与 [Explicit Locking §13.3.2](https://www.postgresql.org/docs/18/explicit-locking.html#LOCKING-ROWS)：文档说明目标行重验和行锁；分表方案是基于文档的推导，不是 SQLite 试件测得，更不外推到其他隔离级别或跨库。
- Mike Burrows, [The Chubby lock service for loosely-coupled distributed systems](https://www.usenix.org/legacy/event/osdi06/tech/full_papers/burrows/burrows_html/index.html), OSDI 2006 §2.4：接收方核验 sequencer；本文只取接收方校验的原则，不声称实现完整协议。
