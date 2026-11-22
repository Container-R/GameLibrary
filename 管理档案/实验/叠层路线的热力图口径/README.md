# 叠层路线的热力图口径：合成对照

[正文](../../../GameLibrary/数据分析/指标设计/玩家行为/热力图把楼上楼下压成一层时，怎样找对问题地点.md)

```sh
node exposure.js > exposure.observed.json
python3 -B plot.py
```

- [exposure.js](exposure.js) 用 Node 24.22.3 取同一关卡版本、同一入口横向格与尝试类型，按假定已经在入口确定的支撑/连接区，聚合每个合格尝试的一份已整理记录。它不做实际坐标变换、支撑探测或事件流拼接。重复传输完全同一记录可以去重，冲突 payload 和同一次尝试的多份整理记录被拒绝，不能用它代替生成尝试表的上游流程。
- [exposure.observed.json](exposure.observed.json)：有二元结局的尝试，下层 10/200、上层 4/10，压平 14/210。上层另有一次未观察到结局和一次折返，均不混入该比率；连接区和无法归类另存。零分母的 null 不同于观测到一次且无失败。记录均为合成输入，不是玩家数据。
- [plot.py](plot.py) 用 Pillow 读取检查过的输出，使用 Noto Sans CJK SC 写 [overlay.png](overlay.png)。上、下层路径的投影重合是示意，柱图以各自的量纲显示失败数量和比例，不能跨面板直接比较条宽。
