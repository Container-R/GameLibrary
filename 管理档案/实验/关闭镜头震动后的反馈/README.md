# Godot：表现镜头偏移、实际命中与提示坐标

需要 Godot 4 的命令行程序 `godot`。本夹具在 Godot
`4.7.2.stable.official.ed1daf0bf`（Linux x86_64）无头模式执行。

```sh
sh run.sh > /tmp/camera-observed.txt
cmp native-observed.txt /tmp/camera-observed.txt
```

脚本在原生 `SubViewport` 内放置两台透视 `Camera3D`，横向视场
90°、视口 1920×1080。控制视角始终为原点看 −Z。两个小盒子的正面恰在
5 m 与 20 m；盒子分属独立碰撞层，每次屏蔽另一层，以免近目标遮住远目标。
`PhysicsDirectSpaceState3D.intersect_ray` 查询确认控制射线在三次采样中
命中相同的面；表现镜头平移 0.20 m 时，`Camera3D.unproject_position`
把命中点投影到横坐标 921.6 和 950.4（中心 960，分别相差 −38.4 与
−9.6 像素）。如果误用表现镜头中心发射射线，此处会打空；改从再投影
的坐标反求射线，则命中同一个盒子上的同一点。最后保持原始偏移采样
0.20 m 不变，仅让表现强度归零，确认投影回到中心。

两条另外注入的游戏结果 `19/tick=100/HIT` 与 `20/tick=101/BLOCK`
方向均为左。输入字典标记只读；呈现路由分别在震动、音频、触觉均开和
均关下处理相同记录，核对 ID、逻辑帧、方向、文字标签不变，只有三个
可选输出开关改变。这不是从射线推导命中/格挡，也未播放音效或触觉反馈。
该流程没有截图、实际 UI 或感知测试；这里的像素是 Godot 投影返回的
坐标，而非帧缓冲像素读取。未测试持续震动曲线、生产游戏时序或瞄准策略。

- [项目](project.godot)、[测试脚本](probe.gd)、[运行器](run.sh)、[实测输出](native-observed.txt)。
- [返回正文](../../../GameLibrary/本地化与无障碍/无障碍设计/视觉信息/关闭镜头震动后，怎样保留命中反馈.md)。
