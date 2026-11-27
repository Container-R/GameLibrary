# 窄文本框的换行边界

[回到正文](../../../GameLibrary/本地化与无障碍/本地化制作/文字排版/窄文本框换行，为什么不能按字符数硬切.md)

- [ICU 实验](boundary_probe.py) · [实际输出](boundary-output.txt)：`python3 boundary_probe.py`。使用 ICU4C 76 的动态库，以 UTF-16 交给 BreakIterator，检测行/字素锚点和状态区间 100–199 的硬断点。测试 zh、en 两种 locale；不调用字体或排版。
- [Pango 实验](width_probe.py) · [实际输出](width-output.txt)：`python3 width_probe.py`。使用 Pango、PangoCairo、GObject 动态库和 DejaVu Sans。字号设为 16px；观察不限制宽度、54px 的词边界、54px 的词内退让。若字体缓存不可写，可为 `XDG_CACHE_HOME` 设可写的临时目录。Pango 行索引在此是 UTF-8 字节偏移，不能与 ICU 位置互换。
- 版本、配置和具体字宽只绑定这次运行；没有 GPU 渲染或屏幕像素评价。PDF、游戏引擎或其他系统的布局还应按各自字体链核实。
