# 移动单向平台：来源记录

- Unity Technologies，[Platform Effector 2D reference](https://docs.unity.com/en-us/engine/6000.0/manual/unity2d/2d-physics/effectors-2d/platform-effector-2d-reference)，Unity 6.0，Surface Arc、Use One Way Grouping。只用于界定有效表面方向和多碰撞体分组的公开选项，不推断其求解、相对运动或容差实现。
- Godot Engine，[CollisionShape2D](https://docs.godotengine.org/en/4.7/classes/class_collisionshape2d.html)，4.7。one_way_collision 和 one_way_collision_margin 是形状属性；文档未在此定义本文的持续支撑和下穿状态机。
- Godot Engine，[CharacterBody2D](https://docs.godotengine.org/en/4.7/classes/class_characterbody2d.html)，4.7。platform_floor_layers、platform_on_leave 和 move_and_slide 用于区分平台跟随、脱离与实际移动。文章不把引擎的默认规则当作通用设计。
- [复现材料](../实验/移动单向平台的相对穿越/README.md)包含原创精确分数点足/横段扫掠，以及 Godot 4.7.2 静态矩形控制。只后者运行原生引擎，不能用它验证移动平台的具体内部逻辑。
