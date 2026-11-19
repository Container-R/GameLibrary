# 过肩镜头换边：来源与两套试件

- Unity Cinemachine 3.1.0：[Third Person Follow](https://docs.unity.cn/Packages/com.unity.cinemachine@3.1/manual/CinemachineThirdPersonFollow.html)，三 pivot、Camera Side、碰撞半径和独立碰撞阻尼。[Third Person Aim](https://docs.unity.cn/Packages/com.unity.cinemachine@3.1/manual/CinemachineThirdPersonAim.html) 在位置噪声下重调观察方向，说明结构分工，不保证换肩时序或外部目标跨镜头状态。
- Godot 4.6：[SpringArm3D](https://docs.godotengine.org/en/4.6/classes/class_springarm3d.html)、[弹簧臂教程](https://docs.godotengine.org/en/4.6/tutorials/3d/spring_arm.html)，沿当前臂扫掠、直接子相机的近裁区形状、显式形状与回退射线；没有将这些配置全部跑一遍。
- Godot 4.6.3-stable 发布标签所指的公开提交 [35e80b3a8822a9df9be390814b62f44c0a9c69e8 的 spring_arm_3d.cpp](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/physics/spring_arm_3d.cpp#L128-L187)，`process_spring()` 沿当前轴变换的运动、形状查询与直接子节点应用；不是上一相机中心到期望肩位的横扫。二进制报告 4.6.3-stable (official)，CLI 打印 7d41c59c4；两份证据分别核对，不据此声称二进制可追溯到该公开提交。
- Godot 4.6 [PhysicsDirectSpaceState3D](https://docs.godotengine.org/en/4.6/classes/class_physicsdirectspacestate3d.html#class-physicsdirectspacestate3d-method-cast-motion)，已有重叠不由 `cast_motion` 报出；使用单独形状查询。场景实际比较了同一初始重叠状态的两种结果。

[复现实验](../实验/过肩镜头换边/README.md)含有理数二维几何和原生 headless 小场景。两者用途是隔离空间观察点、形状扫掠和瞬时可见性，不执行交互或玩家相机策略。图为原作者生成并经 Inkscape 栅格目检；不是产品截图。
