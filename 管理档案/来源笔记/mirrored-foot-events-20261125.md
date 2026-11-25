# 镜像落脚事件的足别：来源核对

核查日期 2026-11-25。[复现实验](../实验/镜像落脚事件的足别/README.md)。

- [Epic：Mirroring Animation](https://dev.epicgames.com/documentation/en-us/unreal-engine/mirroring-animation-in-unreal-engine)：Mirror Entry Type、Bone/Attributes 区分、Blueprint Notify 中检查是否来自镜像动画。支持不同种类需要各自检查的主张，不声称所有自定义属性都会或不会由任何版本自动转换。
- [Epic：GetNotifyEventName](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/FAnimNotifyEvent/GetNotifyEventName) 和 [FAnimNotifyEventReference](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/FAnimNotifyEventReference)：前者指定镜像命名，后者文档列出 MirrorTable 及其关联的通知名称映射。没有运行 Unreal。
- [Godot：Animation Track types，4.7](https://docs.godotengine.org/en/4.7/tutorials/animation/animation_track_types.html)，Call Method Track 记有方法和参数。Godot 运行验证的是主动创建的两种姿态及显式事件参数，证据范围见同目录。
