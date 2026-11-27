# 脚步素材选择：来源和证据

- Godot，[4.7 AudioStreamRandomizer 类文档](https://docs.godotengine.org/en/4.7/classes/class_audiostreamrandomizer.html)，播放模式枚举与权重入口。
- Godot 4.7.2 固定提交 ed1daf0bf001b61586d9930840f2f1394092c079，[audio_stream.cpp 第 629–669 行](https://github.com/godotengine/godot/blob/ed1daf0bf001b61586d9930840f2f1394092c079/servers/audio/audio_stream.cpp#L629-L669) 与 [audio_stream.h 第 272–304 行](https://github.com/godotengine/godot/blob/ed1daf0bf001b61586d9930840f2f1394092c079/servers/audio/audio_stream.h#L272-L304)：比较子资源引用、过滤失效与非正权重、候选为空时回到普通随机、创建播放对象时写资源上的 last_playback。不是可听时回调，也不保证不同资源对应不同录音。
- 固定提交的 [get_length](https://github.com/godotengine/godot/blob/ed1daf0bf001b61586d9930840f2f1394092c079/servers/audio/audio_stream.cpp#L727-L732) 回传已选资源的时长，故试件可在不启动播放的情况下读出选项。
- [运行材料](../实验/脚步素材的防重复历史/README.md)为合成输入、真实引擎选择调用，不测试驱动、混音、方向感或听感。
