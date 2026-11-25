# 分屏视口的离屏箭头：复现

[正文](../../../GameLibrary/界面与体验/界面编程/画布与布局/分屏里目标绕到镜头背后，箭头为什么指反了.md) · [来源核对](../../来源笔记/split-screen-arrow-20261125.md)

```sh
godot --headless --path native --script probe.gd
```

[原始读数](native/observed.txt)来自 Godot 4.7.2.stable.official.ed1daf0bf。两个 640×720 SubViewport 内相机均在原点、无旋转或缩放，Godot 前向为本地负 Z。fixture 用引擎 API 测视口投影及近面判定；右侧在窗口中的位置由脚本加 (640,0)，没有渲染实际的分屏布局或箭头。箭头候选列只测试射线和内缩矩形的数学结果，前方有效且位于允许区域的点在产品策略中改用普通点标记；不把该候选列当成完整 UI 状态机。
