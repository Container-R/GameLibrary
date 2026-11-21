# 匹配确认与提案代次：两个可运行对照

[返回正文](../../../GameLibrary/网络与在线服务/在线服务/匹配与组局/匹配确认超时后，迟到的接受该算给哪一场.md)。

```sh
node proposal.js
python3 -B transaction.py
```

- [proposal.js](proposal.js) / [实际输出](proposal.observed.json)：同一组固定时间输入运行两个自有状态模型。对照票号校验、提案校验、已存回执、重复确认、迟到计时器和显示修订。Node v24.22.3。截止例输入的是模拟服务时刻；没有真实网络或后台计时调度。
- [transaction.py](transaction.py) / [实际输出](transaction.observed.json)：SQLite 3.53.1 临时库，两条连接以 BEGIN IMMEDIATE 竞争写权；旧已登记键重放、旧未登记键拒绝、最后一人回滚或事务提交以及回执和 outbox 同步。只有一种接受载荷，没有模拟指纹冲突。rollback 参数仅模拟测试失败，返回是内部试验标记，不应当作对外成功响应。写竞争用两个串行控制的连接触发，不代表任何其他数据库的隔离强度。

两个程序不调用 AWS、PlayFab、数据库之外的分配器或真实游戏服务器。只得到应用内数字或本地意图，不证明外部只分配一次。
