# 技能预警的预算与恢复：逻辑与离屏读回

[返回正文](../../../GameLibrary/视觉特效/特效制作/性能分析/特效预算降低时，怎样保住技能预警.md)。

```sh
node warning.js
python3 -B probe.py ./rerun
```

- [warning.js](warning.js) / [离散状态输出](warning.observed.json)：Node v24.22.3。一维例子按游戏提供的披露资格、危险范围、半开时间换算画面内状态；有 4 名额 / 20 装饰的候选选择、错误原点剔除和合并时间的反例。没有做引擎或毫秒测量。
- [probe.py](probe.py) / [后台及读回结果](raster.observed.json)：Python 3、Pillow、Mesa EGL surfaceless 与桌面 OpenGL llvmpipe。命令生成 [timeline.png](timeline.png)、[controls.png](controls.png)、[outline.png](outline.png)，并向 stdout 写入实际像素数与图像摘要。目标 144×80 和 72×40，单采样，低档读回最近邻放到同等展示尺寸。每格图是实际像素，接触表、标签和布局由 Pillow 整理。
- 上下示意带共用世界横轴，不把示意画成实际二维重叠几何。时间数字在外围标签，不代表实机 UI 测量。亦不测 Niagara、TAA、真实 GPU 成本、复杂底图或玩家理解。正确配置不披露 C，只在故意错误的对照中显示。

以与固定输出相同的 backend 比较时，`warning.js` 的 stdout 与 `warning.observed.json` 一致，`probe.py` 的 stdout 与 `raster.observed.json` 一致，三张 PNG 与固定文件逐字一致。其他实现或字体版本需记录差异及其来源，不把像素个数当事实上的可见性阈值。
