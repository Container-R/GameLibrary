# NPC 最后目击与有限搜索：复现实验

[正文](../../../GameLibrary/游戏人工智能/行为决策/感知与搜索/游戏%20NPC%20丢失视线后，怎样用最后目击点搜索.md)

在本目录使用 Python 3.10+ 标准库：

```sh
python3 check_evidence.py | cmp - observed.json
python3 check_batch_order.py | cmp - batch-observed.json
python3 check_search_epistemic.py | cmp - search-observed.json
python3 check_search_lifecycle.py | cmp - lifecycle-observed.json
```

- 旧点保留，声音线索有独立时效，迟到旧丢失不覆盖新的当前目击。
- 单传感器、单对象、单批次，用可信世代与顺序比较全部六种送达排列，并区分同 tick 先确认后丢失、以及下一批仅有旧记录的结果。
- 同一证据回放的隐藏路线对照，以及当前可见区域随时间的排除、连通区域重新可达。
- 用给定的导航返回、搜索和命令编号检查迟到结果、部分路径、真实可见半区和两次预算后的停止，以及唯一导航不返回时的本地截止。

输出来自四个合成对照。没有运行 Unreal、真实导航网格、视线射线、真实多人共享或商业游戏代码。
