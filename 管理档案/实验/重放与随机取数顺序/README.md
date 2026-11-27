# 重放与随机取数顺序

[回到正文](../../../GameLibrary/玩法程序/玩法系统/时间与模拟/同一个随机种子，为什么重放还是抽到了不同奖励.md) · [试件脚本](probe/rng_probe.gd) · [Godot 项目配置](probe/project.godot) · [实际运行记录](engine-output.txt)

用 Godot 4.7.2，从本目录运行：

```sh
godot --headless --path probe --script rng_probe.gd
```

命令名可按本机安装替换。Linux 若默认数据和缓存目录不可写，用可写位置设置 `XDG_DATA_HOME`、`XDG_CACHE_HOME` 与 `XDG_CONFIG_HOME`。成功退出码为 0。每条 JSON 行记录同一个模拟步内试件唯一事件，状态用十进制字符串。对比时先按 `stream` 隔离，再在该流内按顺序列出事件；观察共享版本的 `sparkle` 推进 `reward`，隔离版仅推进 `visual`。最后一行对照仅种子、部分状态与全状态恢复。

此试件的 tick 是用来标识顺序的固定编号，并未驱动真实重放、渲染或物理。取原始数字用于同一引擎版本诊断，不当成跨版本标准测试向量。
