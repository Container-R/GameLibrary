# 解锁时长与观察窗口

[返回正文](../../../GameLibrary/数据分析/指标设计/玩家行为/七天解锁率：新玩家只观察两天时，怎样比较.md)

从本目录执行：

```bash
python3 -B time_to_unlock.py | diff -u observed.json -
python3 -B run_snapshot.py | diff -u snapshot-observed.json -
```

第一组用 Python 有理数计算固定批次已知比例和区间、Kaplan–Meier 补数与简单竞争终点的累积发生率。它只执行给定的确定性数据，不计算置信区间或检验独立删失。第二组执行 SQLite 查询：同一预定事件窗口，第 168 小时尚未对账与已经对账得到不同的可观察分母。它把账本覆盖当作外部输入，不能据此证明任意生产管线的投递完整性。没有使用真实玩家数据。
