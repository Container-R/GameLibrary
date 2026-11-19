# HUD 安全区坐标：复现实验

[返回正文](../../../GameLibrary/界面与体验/界面编程/画布与布局/手机%20HUD%20安全区怎样换算到实际画布.md)

- `check_rect.py`：窗口坐标统一后求交集，按目标显示比例回到 HUD，并检查不相交和已裁窗口。
- `check_generation.py`：不对称纵边的反射、竖屏安全矩形混进横屏几何、父子误用同一边距。版本号是可测试的输入，不代表所有平台都提供一致版本。
- [Godot 本地布局试件](godot/README.md)：实际运行 Godot Control，窗口及边距均为模拟输入，不查询系统安全区、不接触手机。
- [比例示意图](diagrams/window-viewport-safe.png)按第一个测试的窗口坐标制作，用来解释几何，不是截图；[SVG 源](diagrams/window-viewport-safe.svg)。

```sh
set -e
python3 -B check_rect.py >/tmp/gl-safe-rect.json
cmp /tmp/gl-safe-rect.json observed.json
python3 -B check_generation.py >/tmp/gl-safe-generation.json
cmp /tmp/gl-safe-generation.json generation-observed.json
```
