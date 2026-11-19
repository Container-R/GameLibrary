# 游戏每日重置：来源和证据

- Bungie [Destiny 2 Ritual Reset Guide](https://help.bungie.net/hc/en-us/articles/360049199911-Destiny-2-Ritual-Reset-Guide)，官方面向玩家规则部分说明日与周重置 UTC 17:00，显示太平洋时区夏 10:00、冬 9:00。文章只引用固定 UTC 发布范式，不推导服务实现。
- Python [PEP 495](https://peps.python.org/pep-0495/#temporal-arithmetic-and-comparison-operators) 描述同一 tzinfo 的减法与比较、时钟重复的 fold、缺失的 gap；[zoneinfo](https://docs.python.org/3.12/library/zoneinfo.html) 定义 IANA 依赖。真正用系统 tzdb 2026b 核对加州 2026 两次换时。本例边界选择是产品政策，不等于库的默认。
- IANA [Time zone and daylight saving time data](https://data.iana.org/time-zones/tz-link.html) 说明时区规则会因辖区规则而变，客户端与服务器可能处于不同版本。保存已经生效的时间表是本文的运维做法，不是 IANA 对游戏发放的建议。
- SQLite [UPSERT](https://www.sqlite.org/lang_upsert.html) 说明冲突目标只适用于唯一约束；[Transaction](https://www.sqlite.org/lang_transaction.html) 说明本地事务与 BEGIN IMMEDIATE 获取写入，可能因其他写入者而失败。实测仅单连接进度与领取事件同库，不外推分布式正好一次、并发吞吐或真正玩家奖励。
- [复现](../实验/每日重置周期/README.md)，精确前一秒／相等边界、成功后重试、改请求意图、拒绝迟到旧期、回滚与新期唯一性，采用合成输入。
