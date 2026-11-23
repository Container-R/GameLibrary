# 合作解谜晚加入：复现材料

运行：
```sh
python3 late_join_model.py
python3 reward_sqlite.py
```

2026-11-23，Python 3.12.14，sqlite3 模块链接 SQLite 3.53.1，使用 Python 标准库，无需联网。第二个试件自行创建并删除临时数据库。

```text
120 delivery orders converge; global-revision adjacency rejects r42
Actual missing seq 9: no early hint, deadline abandons old generation, fresh state recovers
r42 at the join boundary: naive live-only subscription loses it; catch-up keeps it
SQLite 3.53.1: rollback=0; writers=1 receipt + 1 credit; ACK-lost retry=same receipt; B=ineligible
```

同步试件通过受控交付顺序验证接收状态机；世界 r41 只发给 A，B 收到的 r42、r43 依次编号 9、10。120 次涵盖五条指定消息的全排列，之后追加一次重复提示。测试用直接触发截止方法来表示等待结束，不是计时测量。门的字符串表示快照状态，没有运行渲染、碰撞、真实传输、引擎、或生产保留日志。

数据库试件在真实 SQLite 内提交和读回。两个写入者由事件屏障启动，使用独立连接和 `BEGIN IMMEDIATE`；只有插入了唯一收据的一方在同一事务改余额。提交前注入故障单独测试，余额和收据都未留下；模拟丢响应的方法是不把已提交调用的返回交给玩家，重新创建连接请求。A 得到相同收据，余额仍只有 25；B 无资格。不是 PostgreSQL 或分布式发货验证，不测掉电。

[返回正文](../../../GameLibrary/网络与在线服务/实时同步/实体生命周期/合作解谜中途加入的关卡状态与旧提示.md)
