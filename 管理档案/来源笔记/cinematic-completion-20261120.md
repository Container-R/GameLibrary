# 过场完成与控制权：来源记录

- [Godot 4.7 AnimationPlayer.seek](https://docs.godotengine.org/en/4.7/classes/class_animationplayer.html#class-animationplayer-method-seek)：2026-11-20 定位 seek、update_only、animation_finished 与 advance。4.7.2 原生的第一试件只测列出的非循环轨。
- [Unreal 5.8 EUpdatePositionMethod](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/MovieScene/EUpdatePositionMethod)：2026-11-20 核对 Play 扫区间并可触发事件、Jump 不触发区间事件，不把节点和其他引擎的 seek 等同。
- [Unreal 5.8 Play Cinematics from Blueprints](https://dev.epicgames.com/documentation/en-us/unreal-engine/play-cinematics-from-blueprints-in-unreal-engine?lang=en-US)：2026-11-20 核对步骤 16–18，Keep State 与 Go to End and Stop 的灯光属性示例，不将它视为项目任务回调实证。
- [原创建模与试件](../实验/过场完成与控制权/README.md)：两个标识、入口与逐项释放的实现是本文示例；第二试件实际读取视口当前相机与延迟队列，不包含设备输入、事务或跨崩溃去重。
