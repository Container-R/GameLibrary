# 步态混合落脚通知：来源记录

访问日期：2026-11-23。

| 正文位置 | 来源及定位 | 观察与范围 |
| --- | --- | --- |
| 换主导：同步组可随权重换主导；默认跟随者不触发 | Epic Games，[UE 5.7 Animation Sync Groups](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-sync-groups-in-unreal-engine?application_version=5.7#overview)，Overview、Sync Settings | 同组且采用默认分配；动画角色选项可改写。不能从文档推出自拟时间轴必然原生重现。 |
| 换主导：事件可设触发权重和跟随触发选项 | Epic Games，[UE 5.7 Animation Notifies](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-notifies-in-unreal-engine?application_version=5.7#common-notify-properties)，Common Notify Properties | 是各通知的过滤设置，不是保证每个物理接触发生一次。 |
| 原生分派：两个有权重的分支可分别调用 | Godot Engine，固定构建提交 [Blend2::_process](https://github.com/godotengine/godot/blob/ed1daf0bf001b61586d9930840f2f1394092c079/scene/animation/animation_blend_tree.cpp#L850-L859) 及 [方法轨](https://github.com/godotengine/godot/blob/ed1daf0bf001b61586d9930840f2f1394092c079/scene/animation/animation_mixer.cpp#L1593-L1618)，与附录原生试件 | Blend2 将二者交给混合器。普通非 seek 推进时，符合条件的方法轨查询跨过的键；静态测试不外推到显式 seek 或音频效果。 |
| 解决方法与反例 | 试件 `contact_model.py` | 作者推导，检查事件归属反例、按接触边界枚举及防抖误删；无原生 UE 验证。 |
