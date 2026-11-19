# 越障接触约束试件

本例自造两个原始样本，不加载动画或角色控制器。

- `python3 check_alignment.py` 比较原样、仅根末端修正、以及在两个指定时刻分别修正。输出 [observed.json](observed.json)。用有理数计算，距离误差按前进方向的厘米给出；没有求连续路径。
- `python3 check_moving_anchor.py` 比较冻结世界点、只更新障碍平移、以及把局部点按该帧整体变换。输出 [moving-observed.json](moving-observed.json)。XY 平面使用整数厘米和 90° 旋转；这是锚点计算，不是手骨的 IK 或播放采样。

运行于 Python 3.12.14；所有断言均通过。文件夹中的输出可逐字复跑，不用于判断穿模或画面自然程度。

[返回正文](../../../GameLibrary/角色动画/角色移动/根运动与动作对齐/越障动画的根运动扭曲：落点对了，手为什么还没贴住.md)
