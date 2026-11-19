# 非付费掉落保底：等待分布与规则切换

复现[正文](../../../GameLibrary/游戏设计/系统设计/成长与经济/非付费掉落的保底次数：平均等待和最晚获得不是一件事.md)的假设数据。使用 Python 3 标准库，在此目录运行：

```sh
python3 check_drop_wait.py | cmp - observed.json
python3 check_qualified_progress.py | cmp - progression-observed.json
python3 -B check_rule_cutover.py | cmp - cutover-observed.json
```

- 第一组用精确分数对比等待尾部，不依赖模拟抽样。固定兑换计算的是可兑换资格。
- 第二组用一个玩家、单写入者、临时 SQLite，检查待确认不写入最终回执、后续确认、最终不合格、重复处理、重开、自然获得及保底。持久化奖励只是一条同库记录，未连接真实背包。
- 第三组分两份临时数据库：切换资格保留原挑战的结算版本；等价存储键离线搬迁并防止重复恢复。调用者事先给可信的资格和版本，未实现挑战签发器、在线迁移协调服务或跨网络重试。没有使用玩家数据。

预期 JSON 是脚本实际输出，不是游戏记录。
