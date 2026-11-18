# Godot 4.6.3 暂停与时间倍率的双因素检查

执行环境：Linux x86_64，无界面，`4.6.3.stable.official.7d41c59c4`（可执行文件 SHA-256 `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`，它只是本次实际二进制身份，不声称匹配固定源码提交）。在本目录使用同版 Godot：

```sh
godot --headless --path . --max-fps 60
godot --headless --path . --max-fps 120
```

把 `XDG_CACHE_HOME`、`XDG_CONFIG_HOME`、`XDG_DATA_HOME` 指向自己的可写临时目录可隔离环境。两次退出码都是 0，stderr 都是空，保留 stdout。日志的毫秒数可能因调度或帧差不同；不要用逐字节相等当成通过。应看到全部六个检查为 true，短暂停组只有 always_unscaled，长暂停后 always_scaled 也到期，解除暂停但倍率仍为 0.05 时只有 pause_unscaled 新到期，恢复到 1.0 才有 pause_scaled；每种计数一次。节点在活动期确实收到每帧处理调用，暂停期间没有，但暂停组外的信号仍执行。

所有被测计时器都用普通帧更新；`--max-fps` 是上限，不是测出的持续帧率。脚本以另一个不受暂停或倍率影响的计时器触发检查点，目的在于对照回调阶段；未保证计时精度、实际键鼠输入、图形、物理帧语义、硬挂起和服务器时钟。
