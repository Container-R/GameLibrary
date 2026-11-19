# 非颜色状态标记

[返回正文](../../../GameLibrary/本地化与无障碍/无障碍设计/视觉信息/游戏界面不用颜色也能辨认状态：门标记与操作焦点.md)

从本目录运行：

```bash
python3 -B check_signifiers.py | diff -u observed.json -
python3 -B check_mask_scale.py | diff -u mask-observed.json -
python3 -B draw_signifiers.py
```

最后一项在当前目录生成原创 SVG；可在临时目录复制脚本再执行。第一项是 sRGB 固定色值、均匀黑色背景和一个把明度编码成 8 位灰度的实验；对照符号编码与焦点组合，不是色觉差异的生理模拟。第二项是受控规范坐标的条带，按像素面积覆盖和 50% 二值阈值计算，不模拟全套 UI 栅格器。实验只测合成输入，不推断玩家能认清某一特定符号，也不评价目标设备或 HDR／动态图。
