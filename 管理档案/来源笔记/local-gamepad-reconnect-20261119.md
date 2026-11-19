# 本地合作手柄重连：来源和证据

- SDL2 [JoystickID](https://wiki.libsdl.org/SDL2/SDL_JoystickID)、[JoystickGetDeviceInstanceID](https://wiki.libsdl.org/SDL2/SDL_JoystickGetDeviceInstanceID)、[JoyDeviceEvent](https://wiki.libsdl.org/SDL2/SDL_JoyDeviceEvent) 说明 0 是可用连接实例、重连换号及加入与移除使用不同身份。[ControllerDeviceEvent](https://wiki.libsdl.org/SDL2/SDL_ControllerDeviceEvent) 说明同一兼容设备可能收到两种事件。Linux SDL2 2.32.4 的虚拟实验用实际 PollEvent 与枚举查询来区别同一数值何时仅代表索引；观察数据按值排序，不外推回调顺序。
- SDL3 [JoystickID](https://wiki.libsdl.org/SDL3/SDL_JoystickID)、[JoyDeviceEvent](https://wiki.libsdl.org/SDL3/SDL_JoyDeviceEvent)（类型自 SDL 3.2.0）：0 无效，加入和移除事件的 which 都是实例。本例未运行 SDL3。
- Unity [InputSystem.disconnectedDevices](https://docs.unity3d.com/ja/Packages/com.unity.inputsystem@1.4/api/UnityEngine.InputSystem.InputSystem.html#disconnecteddevices) Input System 1.4.3：会对比 InputDeviceDescription，文档明确同款不同设备可能被归类为 Reconnected；具备序列号的设备按该版本描述另论。未用此页面作为额外物理身份保证，也未运行 Unity。
- SDL2 [JoystickGetAxis](https://wiki.libsdl.org/SDL2/SDL_JoystickGetAxis)：失败返回 0，真实中立也可能是 0。不建议用标量判断有效性；采样有效性和设备能力由项目核对。
- [复现实验](../实验/本地合作手柄重连/README.md)区分原生虚拟设备、合成游戏输入隔离、合成认领冲突。合成冲突和门控策略是游戏层的设计，不是平台接口保证，物理 USB、蓝牙和无障碍体验仍由项目验证。
