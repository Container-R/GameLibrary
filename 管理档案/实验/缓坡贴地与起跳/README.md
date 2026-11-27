# 缓坡贴地、跨低落差和手动贴地

在本目录执行 `python3 -B native/run.py`，或用 `python3 -B native/run.py | cmp - native/observed.jsonl` 对比。本次使用 Godot 4.7.2.stable.official.ed1daf0bf 和 Python 3.12.14；如程序不叫 godot，可用 GODOT 环境变量指定可执行程序。脚本每个场景用独立无头 Godot 进程、临时数据路径和超时，检查每次的物理步长、支撑状态、起跳前后两种速度、落差末端是否越过边缘。

斜坡长度按水平投影 400 px，右侧每 4 px 降 1 px；上、下层两平台以 x=200 为分界，顶面相差 8 px。角色碰撞矩形宽 4、高 8 px，safe_margin 0.08 px；引擎报告上次支撑后固定采样下一物理步。输入速度在不跳时为 (360, 0)，起跳为 (360, −90) px/s。不施加额外重力、恒速坡面或平台运输，不引入接缝、单向面或后处理。

[八组观测](native/observed.jsonl)中，start 是步前位置，moved 是 move_and_slide 返回后的取样，final 是在相同返回点或再调用手动贴地后取样。p 是实际位置，delta 是位置差 API，velocity 是 CharacterBody2D 的速度属性，real 是 get_real_velocity 的读数。数值取到方便复核的精度；法线用于核对当前报告的方向，不能拿地面标志为假时的法线当有效支撑。两次完整试跑的 JSONL 完全一致。

[回到正文](../../../GameLibrary/玩法程序/玩法系统/角色移动/角色沿缓坡下跑，为什么会短暂离地.md)。
