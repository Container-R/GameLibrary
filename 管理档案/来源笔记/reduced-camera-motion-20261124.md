# 关闭镜头震动后，怎样保留命中反馈：来源记录

| 主张 | 原始依据 | 范围 |
| --- | --- | --- |
| 非核心视觉运动可以由玩家关闭；镜头震动、起伏、模糊是例子 | Microsoft，[Xbox Accessibility Guideline 117](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/117#implementation-guidelines)，查阅于 2026-11-24 | 设计和验收建议；本文不报告健康结果，不把所有相机修正都分类为装饰。 |
| Godot Camera3D 的透视射线关联调整后的相机变换，世界点可以投到视口 | Godot Engine，[4.6 文档](https://docs.godotengine.org/en/4.6/classes/class_camera3d.html)，get_camera_transform、project_ray_origin/normal 与 unproject_position；4.6-stable 固定提交 [相机变换](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/scene/3d/camera_3d.cpp#L253-L265)、[透视射线](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/scene/3d/camera_3d.cpp#L393-L441)、[世界点投影](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/scene/3d/camera_3d.cpp#L469-L489) | 不从 4.6 源码推断 4.7.2 全部行为。投影输出不是遮挡测试；插值时若需要严格一致的裁剪判定，以当帧采样的展示变换为准。 |
| 重要提示有替代感知通道 | Microsoft，[Xbox Accessibility Guideline 103](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/103#implementation-guidelines)，查阅于 2026-11-24 | 命中和格挡的具体替代文字与分开验收是本文方案；不声称验证玩家识别效果。 |
| 横向偏移下近点偏差大于远点；原判定射线可以不变 | 本库[Godot 4.7.2 无头复现](../实验/关闭镜头震动后的反馈/README.md)，及正文针孔公式 | 两碰撞层分别查询；未读取渲染帧，也未测复杂场景碰撞、实际回放与生产 UI。 |
