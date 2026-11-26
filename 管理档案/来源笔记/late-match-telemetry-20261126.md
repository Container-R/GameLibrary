# 完赛日报迟到与修订来源

1. Apache Beam，[Programming Guide](https://beam.apache.org/documentation/programming-guide/#watermarks-and-late-data)，§8.4 事件时间、处理时间、水位线及超越窗口边界后的晚到，§8.4.1 窗口允许迟到，§9.4.1–9.4.2 累计／清空批次和迟到处理。本文引用这些语义，不把示例中的固定墙钟封账和可见的导出检查点说成 Beam 的水位线或触发。
2. SQLite，[UPSERT](https://www.sqlite.org/lang_upsert.html)，§2.1 的末尾 WHERE 可使 DO UPDATE 成为无操作。本文用单连接事务验证示例写入流程对旧版重试、版本冲突和陈旧截止的行为。未测跨进程并发、分布式消息投递或看板权限。
3. [实际 SQL 探针和输出](../实验/late-match-telemetry/README.md)。日期以权威结束时间归属；接收时间被定义为可用于该次查询的收件时间，示例不模拟时钟漂移、闰秒和各时区的日历。
4. 资料核对日期：2026-11-26（北京时间）。
