# 消耗钥匙关卡的状态图检查

正文：[地牢明明有通关路线，玩家为什么还能被一把钥匙卡死](../../../GameLibrary/游戏设计/关卡设计/关卡推进/地牢明明有通关路线，玩家为什么还能被一把钥匙卡死.md)。

- [check.py](check.py)：Python 3 标准库，内置五种布局和断言。
- [observed.json](observed.json)：标准输出，包含状态数量、成功序列和最短失败前缀。
- [doors.dot](doors.dot)、[doors.png](doors.png)：原创基线示意图。红色带叉线仅标示不可通行，图也不用于生成规则。

在本目录运行：

```sh
python3 -B check.py | cmp - observed.json
dot -Tpng doors.dot -o /tmp/gamelibrary-dungeon-doors.png
```

第一条命令无输出且退出码为 0 表示结果逐字一致。图源中用到中文字体；不同字体可能改变 PNG 的渲染。试件不读取任何引擎地图或存档。
