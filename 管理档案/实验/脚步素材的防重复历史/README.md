# 脚步素材的防重复历史

正文：[脚步声设了不重复，为什么同一个角色还是会重复](../../../GameLibrary/声音与音乐/游戏音效/播放管理/脚步声设了不重复，为什么同一个角色还是会重复.md)。

- `python3 -B model.py | cmp - observed.txt`：运行受控抽取记录，非引擎随机实现。
- 在 Godot 4.7.2 将本目录设为项目目录，运行 `godot --headless --path . --script probe.gd`。Linux 下可用独立可写的 XDG_DATA_HOME、XDG_CACHE_HOME 和 XDG_CONFIG_HOME；断言需要启用。原始执行见 [engine-observed.txt](engine-observed.txt)。

Godot 探针实例化 AudioStreamPlayback，不调用 start、不使用音频设备或产出可听声音。它以两个不同长度的空白 WAV 与随机器当前 get_length() 识别选项，验证共享与独立资源、同一子资源的重复条目、实例化后历史推进、两候选 9:1 权重时强制交替。脚本内 A/B 是调用者标签，未模拟角色节点或组件并发。没有测试任何 Wwise 版本。
