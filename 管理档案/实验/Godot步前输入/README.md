# Godot 步前输入

这个试件用 Godot 4.6.3 对照同一次合成按键怎样被固定步接收，或怎样在步首清空时被丢掉。用可写的用户目录运行，本目录为项目根目录。

```sh
godot --headless --fixed-fps 60 --path . --script pre_step.gd
godot --headless --fixed-fps 60 --path . --script pre_step.gd -- --drop-inbox
```

[试件脚本](pre_step.gd)在 `_process` 注入动作 B 并显式提交。步号从 0 开始；两种运行都记录在步 0 完成后收到 B，而且收到时不在物理阶段。读日志时，`received` 的三个字段是步号、是否在物理阶段、动作 ID；`drained` 记录消费步号和动作 ID。

- [保留队列：实跑记录](pre-step-keep.txt)：步 1 消费 B 一次，退出码 0。
- [步首清空：实跑记录](pre-step-drop.txt)：仍收到 B，但步 1 和步 2 都未消费，故障变体按预期退出 1。

`--fixed-fps` 使用人工时间，不代表真实画面帧率。这个试件没有测设备输入、引擎自动提交或含多个并发生产者的队列。
