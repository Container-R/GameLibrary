# Godot 场景树计时的暂停政策与时间倍率

核读：2026-11-19（北京时间）。既有固定步战斗正文讨论输入分配和步进；既有系统挂起期限正文讨论操作系统挂起与本地时钟。这里聚焦在 Godot 进程中的 SceneTreeTimer 政策及普通帧和信号。

1. Godot 4.6 [SceneTree.create_timer](https://docs.godotengine.org/en/4.6/classes/class_scenetree.html#class-scenetree-method-create-timer)：process_always 默认 true，暂停时是否继续；process_in_physics 决定帧选项；ignore_time_scale 默认 false，设 true 使用不受 time_scale 的经过时间。此路径为一次性。
2. Godot 4.6 [Pausing games and process mode](https://docs.godotengine.org/en/4.6/tutorials/scripting/pausing_games.html)：设定节点处理模式后对应的 _process 等停止，但 signal 连接仍可执行。建议核对业务所有权属于本文工程建议，不是运行库自动保证。
3. [Godot 4.6 SceneTreeTimer](https://docs.godotengine.org/en/4.6/classes/class_scenetreetimer.html)：timeout 和帧末处理。未将 Timer 节点、Tween 等同一 API。
4. [原创原生工程](../实验/Godot暂停时间与计时器/README.md)：同一 4.6.3 Linux 二进制、60／120 两个 FPS 上限，四种组合和活动期／暂停期节点处理的对照；恢复仍慢时额外检查时间倍率的区别，并断言每类一次。时间日志用于标识顺序，不外推秒表精度或源码相等。
