# 来源核对：局部避让速度与通道进展

- [Reciprocal n-body Collision Avoidance](https://gamma.cs.unc.edu/ORCA/publications/ORCA.pdf)，van den Berg、Guy、Lin、Manocha，2011。§3 定义独立同时选择速度、有限前视与接近首选速度；§4 给出成对半平面约束；§5 把单对约束用于多代理选择。本文单轴 g/(2τ) 是原创算例，不是将论文的二维求解简化成该公式。
- [Using NavigationAgents 4.6](https://docs.godotengine.org/en/4.6/tutorials/navigation/navigation_using_navigationagents.html#navigationagent-avoidance)，Godot Engine。回调给避让输出，移动由用户代码负责；避让不从导航网格或物理碰撞自动取得墙体；邻居/层/时间/半径和优先级有不同作用；文档也提示理想化正面相遇可能找不到通过侧。不把较早版说明的每个参数细节推断到后续所有版本。
- [Using NavigationServer 4.7](https://docs.godotengine.org/en/4.7/tutorials/navigation/navigation_using_navigationservers.html)，Godot Engine。同步前后可见状态与 safe velocity 递送；原生试件用 4.7.2 的 Server 方法，实际输出与写回由脚本记录。
- [复现实验](../实验/NPC局部避让与实际进展/README.md)：分析控制和 4.7.2 的三个受控场景。只验证两圆，无寻路、物理墙或根运动；墙边距是对已走路径和假定边界的演算。实际分组以回调及同一步位移为准。上一条关于单列窄门的文章已经有真实物理碰撞与放行控制，不把本试件包装成再一次入口调度验证。

核读：2026-11-25（北京时间）。
