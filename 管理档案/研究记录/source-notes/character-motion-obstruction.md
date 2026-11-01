# CharacterBody3D 位移与阻挡：来源和证据适用范围

读取日期2026-11-01。关联[现有导航文章](https://github.com/Container-R/GameLibrary/blob/1a7bf18b24ba56395892c4c0cdb3b2acecc16985/solutions/ai/navigation-readiness-and-partial-path.md)与[新增原生运动夹具](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/research/experiments/godot-character-motion/README.md)。此前静止重叠与 Node3D 路径跟随是不同实验，未被改写成物理移动证据。

## 原始资料

- [Godot4.6 PhysicsBody3D](https://docs.godotengine.org/en/4.6/classes/class_physicsbody3d.html#class-physicsbody3d-method-move-and-collide)：位移参数、test_only、恢复 margin 和 collision 返回合同。没有从文档推导本例精确停止位置。
- [Godot4.6 CharacterBody3D](https://docs.godotengine.org/en/4.6/classes/class_characterbody3d.html)：velocity / safe_margin / move_and_slide 与相关实际运动 getter。用于区分两套接口；本例没有执行 slide。
- [Godot4.6 KinematicCollision3D](https://docs.godotengine.org/en/4.6/classes/class_kinematiccollision3d.html)：travel、remainder、碰撞对象/索引、接触点与法线。记录值不自动证明运动后零重叠。
- [Godot4.6 PhysicsDirectSpaceState3D](https://docs.godotengine.org/en/4.6/classes/class_physicsdirectspacestate3d.html#class-physicsdirectspacestate3d-method-intersect-shape)：intersect_shape 是静止相交查询，不处理 motion；本例将其用于可见性与起点/期望终点控制，不能替代实际 body move。

## 固定实现定位

公共比较提交 `35e80b3a8822a9df9be390814b62f44c0a9c69e8`，不认证为本机二进制来源。

- [physics_body_3d.cpp87–162](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/physics/physics_body_3d.cpp#L87-L162)：把方法实参装入 MotionParameters、测试运动、处理恢复/轴锁并写入 travel。具体停止分数的内部机制未在本次审计中确立。
- [character_body_3d.cpp40–134](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/physics/character_body_3d.cpp#L40-L134)、[399–454](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/physics/character_body_3d.cpp#L399-L454)、[684–693](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/physics/character_body_3d.cpp#L684-L693)：slide 速度积分/多段运动与它自己的运动状态。仅作 API 边界比较。
- [kinematic_collision_3d.cpp67–112](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/physics/kinematic_collision_3d.cpp#L67-L112)结合[collision_shape_3d.cpp82–90](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/physics/collision_shape_3d.cpp#L82-L90)：在本场景注册方式下，local/collider shape 返回的是 shape-owner 节点，资源通过另一路映射核对。

原创部分是两条通道、相同位移、分开的静止查询与实际运动、冻结的宽接触区间，以及逐条原始记录验收。没有导入第三方场景或照抄角色控制器。

## 实际观察与未证明事项

作者观察到阻挡位移0.9765625、剩余3.0234375，开放位移4；数值来自真实输出，不以理想1−margin替换。协议在运行前接受 `[0.95,1.05]`，不是后拟合。没有运行后重叠查询或诊断精确停止分数的算法，因此不能补写这两项结论。

源码/二进制前后摘要、参数、raw输出和静态 reader 支持档案核对；不是执行真实性签名、官方构建认证或不同物理实现一致性。配置读取为GodotPhysics3D，通用singleton类名不额外识别 provider。运行前有限数值门槛与 subtype cast 加强属于代码审查，无真实 parser 失败或 native NaN 注入测试。
