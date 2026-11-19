# 程序化随机流：复现实验

[返回正文](../../../GameLibrary/游戏设计/关卡设计/程序化布局/同一个种子，加一点装饰为什么关卡也变了.md)

- `check_chunk_order.py`：用实际 Python 3.12.14 伪随机实例和合成三块地图，对照增加抽样、调整加载顺序和候选顺序。记录 SHA-256 种子派生的固定字节向量；只涉及有限输入和明确格式，不做通用序列统计。
- [Godot 原生抽取](godot/README.md)：同一 4.6.3 构建共享/独立实例与状态恢复。未生成实际游戏关卡，未测试并发调度或跨版本。

```sh
set -e
python3 -B check_chunk_order.py >/tmp/gl-chunk-order.json
cmp /tmp/gl-chunk-order.json chunk-observed.json
```

Godot 运行方法见子目录。
