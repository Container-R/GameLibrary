# 固定步与显示位置：来源核对

核对日期 2026-11-25。原始运行与命令见[复现实验](../实验/固定物理步与画面位置/README.md)。

| 正文主张 | 已核对的来源与边界 |
| --- | --- |
| 累加器余量决定前后两状态之间的显示位置 | [Glenn Fiedler，Fix Your Timestep!](https://gafferongames.com/post/fix_your_timestep/)，The final touch 的 previous/current 和 `accumulator/dt`。采用该模型，不照搬文中对 50/60 步数的文字，具体序列以实测为准：50 低于 60，这里是 0 或 1 步。 |
| 插值有一步取样滞后；外推可能穿过碰撞界限 | [Unity 6000.0 手册](https://docs.unity.com/en-us/engine/6000.0/manual/physics-section/physics-overview/rigidbody/rigidbody-interpolation)，Interpolate、Extrapolate。未运行 Unity，不把一步延迟当端到端测量。 |
| 手动镜头读目标插值变换，位置跟随与鼠标朝向可分开 | [Godot 4.7 高级插值指南](https://docs.godotengine.org/en/4.7/tutorials/physics/interpolation/advanced_physics_interpolation.html)，Cameras、get_global_transform_interpolated、Mouse look。正文镜头距离是单轴模型而非完整镜头集成。 |
| 无窗口人工步进；传送后截断历史 | [Godot 4.7 命令行](https://docs.godotengine.org/en/4.7/tutorials/editor/command_line_tutorial.html)的 `--headless` 和 `--fixed-fps`；[Godot 4.7 使用插值](https://docs.godotengine.org/en/4.7/tutorials/physics/interpolation/using_physics_interpolation.html#call-reset-physics-interpolation-when-teleporting-objects)的 Standing start。用固定坐标和 API 读回，未测显示器、设备或物理接触。 |
| 补充挂点实验的世界坐标混合为手写对照 | [Godot 4.7 高级指南](https://docs.godotengine.org/en/4.7/tutorials/physics/interpolation/advanced_physics_interpolation.html#exceptions-to-automatic-physics-interpolation)描述局部插值和向孩子传递，[迁移到 SceneTree 的合并 PR #104269](https://github.com/godotengine/godot/pull/104269)也以保住旋转枢轴为目标。[4.6 概览](https://docs.godotengine.org/en/4.6/tutorials/physics/interpolation/2d_and_3d_physics_interpolation.html#global-versus-local-interpolation)关于 3D 独立插值世界变换的段落和[同版本源码](https://github.com/godotengine/godot/blob/4.6-stable/scene/main/scene_tree_fti.cpp#L545-L574)冲突，不作为当前行为依据。 |
