# NPC 双向窄门排队：来源记录

访问日期：2026-11-23。

| 正文主张 | 一手出处和定位 | 使用条件 |
| --- | --- | --- |
| 局部避让调整速度，不能由不相撞推出最终通行 | van den Berg、Guy、Lin、Manocha，[Reciprocal n-body Collision Avoidance](https://gamma.cs.unc.edu/ORCA/publications/ORCA.pdf)，Introduction、Problem Definition、§§5.2–5.4 | ORCA 有模型假设；论文所述的停滞不等于这次 Godot 物理试件跑了 ORCA。 |
| Godot NavigationAgent 避让、寻路和场景碰撞是不同环节 | Godot Engine，[Using NavigationAgents 4.7](https://docs.godotengine.org/en/4.7/tutorials/navigation/navigation_using_navigationagents.html#navigationagent-avoidance)，NavigationAgent Avoidance | API 给计算速度，由移动代码使用。避让优先级不能充当入口许可。 |
| 单列圆碰撞形状、有限批次、通道清空释放 | 原创几何算例和 [本地复现](../实验/NPC双向窄门排队/README.md) | 两侧净宽固定、没有中途避让凹位；离散模型检验调度，实际 Godot 试件用碰撞体移动而不是 NavigationAgent/RVO。 |
