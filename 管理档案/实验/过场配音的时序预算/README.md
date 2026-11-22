# 过场配音的时序预算：合成对照

[正文](../../../GameLibrary/叙事设计/运行时叙事/过场演出/过场换了配音，怎样给长台词让出时间.md)

```sh
node model.js > model.observed.json
python3 -B plot.py
```

- [model.js](model.js) 与 [实际输出](model.observed.json)：Node 24.22.3，毫秒整数，三组假设的语音占用长和最后音素时间。相同硬锚，先缩句后等待再缩反应，最短停顿仍装不下就失败。不模拟已授权的声音尾部与视觉反应重叠方案，不约束最大持镜时长。
- [plot.py](plot.py) 用 Pillow 和 Noto Sans CJK SC 绘制 [timeline.png](timeline.png)，同一时钟，红块为最短方案仍跨越锚点的部分。不是 REDkit 界面或实机声音，也不测试口型、解码、帧舍入或可听性。
