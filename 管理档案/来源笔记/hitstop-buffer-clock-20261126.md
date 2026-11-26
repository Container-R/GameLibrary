# 命中停顿中输入缓冲的来源与证据

- [Unity Input System 1.14 CallbackContext.time](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.14/api/UnityEngine.InputSystem.InputAction.CallbackContext.html#UnityEngine_InputSystem_InputAction_CallbackContext_time)：动作时间与 realtimeSinceStartup 同基准，通常来自控制信号事件；不是应用回调这一刻。回调上下文作用期不得外延。未运行 Unity。
- [SDL3 SDL_KeyboardEvent](https://wiki.libsdl.org/SDL3/SDL_KeyboardEvent)：字段 timestamp 的纳秒单位及 SDL_GetTicksNS 时基。未运行 SDL3，也不把 API 时间戳当作微观实体按键时间。
- [Godot 4.6 Input.flush_buffered_events](https://docs.godotengine.org/en/4.6/classes/class_input.html#class-input-method-flush-buffered-events)：区分输入缓冲与主动交付。配套试件使用 4.7.2，保留版本输出；0/50 ms 对照只测试带人为时间的合成键事件进入应用回调，未测设备与自动冲刷。
- [实验、脚本与记录](../实验/hitstop-buffer-clock/README.md)：Python 夹具验证三种应用时钟政策在固定窗口的可见差异；Godot 验证交付延迟可在主动路径中与夹具戳分离。选择何种寿命、如何清理旧动作、回滚是否重分配是项目规则，不由引擎接口决定。
