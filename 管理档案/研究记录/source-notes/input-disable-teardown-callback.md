# Unity 输入禁用与清理：先进入停止态，再跨越回调边界

访问与核对日期：2026-11-01。证据状态：**source-backed**。这里只读取官方历史版本文档和固定源码，并给出原创、未执行的应用示例；没有启动 Unity、模拟设备、复现崩溃或验证生产清理代码。

## 固定版本与源码边界

Unity Input System 官方仓库 tag **1.11.2** 对应提交 `c8518694c7fdd2c755755e028e2ec19cdceda19b`，[package.json](https://github.com/Unity-Technologies/InputSystem/blob/c8518694c7fdd2c755755e028e2ec19cdceda19b/Packages/com.unity.inputsystem/package.json#L4) 声明同一版本；这不是“当前最新版”声明。

[官方 InputAction.Disable 文档](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.11/api/UnityEngine.InputSystem.InputAction.html#UnityEngine_InputSystem_InputAction_Disable)页面标注 1.11.2：Started 动作的取消回调发生在 Disable 调用之内。固定源码也能沿下列路径核对，而不必推测下一帧才通知：

| 固定源码定位 | 本说明采用的有限事实 |
|---|---|
| [InputAction.Disable](https://github.com/Unity-Technologies/InputSystem/blob/c8518694c7fdd2c755755e028e2ec19cdceda19b/Packages/com.unity.inputsystem/InputSystem/Actions/InputAction.cs#L916-L935)；[DisableSingleAction / ResetActionState](https://github.com/Unity-Technologies/InputSystem/blob/c8518694c7fdd2c755755e028e2ec19cdceda19b/Packages/com.unity.inputsystem/InputSystem/Actions/InputActionState.cs#L824-L881)（另见同文件 1071–1082） | 禁用路径进入取消，再完成重置 |
| [状态切换与监听器调用](https://github.com/Unity-Technologies/InputSystem/blob/c8518694c7fdd2c755755e028e2ec19cdceda19b/Packages/com.unity.inputsystem/InputSystem/Actions/InputActionState.cs#L2491-L2569) | canceled 监听器在调用栈内执行 |
| [默认 Value 动作分支](https://github.com/Unity-Technologies/InputSystem/blob/c8518694c7fdd2c755755e028e2ec19cdceda19b/Packages/com.unity.inputsystem/InputSystem/Actions/InputActionState.cs#L1958-L1967) | 达到激活条件后，performed 后续阶段设为 Started |

下面选 **无显式 interaction 的 Value 动作驱动预览**，假定它当前处于 Started。它不是 HoldInteraction 示例，也不扩展到任意动作类型、交互或重入组合。

## 一个能由代码顺序看出的重复清理机会

以下是原创应用伪代码，不是 Unity 源码或执行日志。固定假设：单线程；所有者初态 Active；预览已创建；`ReleasePreview` 是非幂等操作；两条路径都针对同一预览；没有其他处理器修改所有者；回调不重新启用或 Dispose 动作；这些操作均正常返回。

```text
BadStop():
    if ownerState != Active: return
    action.Disable()
    ReleasePreview()
    ownerState = Stopped

OnCanceled():
    if ownerState == Active:
        ReleasePreview()
```

按已核对的调用顺序，BadStop 进入 Disable；取消处理器仍看到 Active，释放预览；Disable 返回后，BadStop 又释放一次。**这里展示的是这些应用假设下的重复调用，不是已观察到的引擎错误，也不是所有清理实现都会出错。** 若释放本来幂等，具体损害可能不存在。

问题不在于固定 tick 不够精确，而在于所有者在跨越一个会执行外部代码的调用之前，尚未建立安全的中间状态。把清理后的状态赋值放在 Disable 后面，不能让回调提前看见它。

## 有限修正：停止意图先可见，清理由一个所有者完成

仍使用上述单线程、正常返回和无其他状态修改假设：

```text
Stop():
    if ownerState != Active: return
    ownerState = Stopping
    stopReason = Shutdown
    action.Disable()
    ReleasePreview()
    ownerState = Stopped

OnCanceled():
    NeutralizeInputState()
    if ownerState == Stopping: return
    HandleOrdinaryCancellation()
```

其中 `NeutralizeInputState` 只清除应用输入持有态，不释放预览、不触发伤害、不改变 ownerState；普通取消路径也不是本例的停用清理所有者。在这条有限路径上，取消处理器看见 Stopping，外层 Stop 独自释放一次；停止期间的重复 Stop 请求被入口条件合并。

这是**原创责任划分建议**，不是通用生产实现：异常、中途销毁、异步完成和后续重新激活需要另订合同；不能据此宣称异常时一定达到 Stopped。实际项目还应让资源交接/释放具备幂等保护。`canceled` 事件本身不提供本应用定义的 Shutdown 原因；不要不加区分地把它解释成玩家松手，从而在关闭输入时提交一次蓄力攻击。

在本例无其他监听器修改动作的前提下，回调期间阶段先为 Canceled，之后才写入 Disabled；而 [`enabled` 的定义](https://github.com/Unity-Technologies/InputSystem/blob/c8518694c7fdd2c755755e028e2ec19cdceda19b/Packages/com.unity.inputsystem/InputSystem/Actions/InputAction.cs#L532)只排除 Disabled。因此 `!action.enabled` 不能替代关闭原因判断。这是[固定源码顺序](https://github.com/Unity-Technologies/InputSystem/blob/c8518694c7fdd2c755755e028e2ec19cdceda19b/Packages/com.unity.inputsystem/InputSystem/Actions/InputActionState.cs#L2408-L2416)推导，不是运行观察。

## 不把借用、移除监听器和销毁混成一件事

[Dispose 说明与实现](https://github.com/Unity-Technologies/InputSystem/blob/c8518694c7fdd2c755755e028e2ec19cdceda19b/Packages/com.unity.inputsystem/InputSystem/Actions/InputAction.cs#L789-L802)涉及 map/asset 共享状态；[Destroy](https://github.com/Unity-Technologies/InputSystem/blob/c8518694c7fdd2c755755e028e2ec19cdceda19b/Packages/com.unity.inputsystem/InputSystem/Actions/InputActionState.cs#L227-L265)含处理期断言。它们不构成“回调内销毁总会被安全拒绝”的保证。应用可以规定：借用动作的监听器只提出销毁请求，实际所有者在已退出相关输入操作/回调后处理；不在此指定“必定下一帧”或声称已验证安全销毁。

[CallbackArray.RemoveCallback / UnlockForChanges](https://github.com/Unity-Technologies/InputSystem/blob/c8518694c7fdd2c755755e028e2ec19cdceda19b/Packages/com.unity.inputsystem/InputSystem/Utilities/CallbackArray.cs#L41-L75)在锁定分发期间延后移除。因此，仅在回调里退订不能替代业务停止态。另见 [DelegateHelpers](https://github.com/Unity-Technologies/InputSystem/blob/c8518694c7fdd2c755755e028e2ec19cdceda19b/Packages/com.unity.inputsystem/InputSystem/Utilities/DelegateHelpers.cs#L36-L59)：监听器异常有捕获路径，不能把“Disable 没向调用者抛异常”当作每个处理器都成功的回执。

## 后续验收问题，不是已通过测试

- 停用调用尚未返回时，取消处理器是否已观察到 Stopping？
- 同一预览由谁释放，普通取消和关闭输入是否走了不同的业务分支？
- map 中其他监听器是否仍只借用状态，而没有擅自销毁共享所有者？
- 若正常返回假设不成立，谁记录未完成的清理，如何避免重复释放？

本说明不提供运行结果、设备行为、跨线程保证或所有动作之间的回调顺序；没有把固定步、暂停队列或 Godot 物理回调实验迁移成 Unity 证据。文中伪代码为独立原创；只保留来源定位和短述，不转载厂商实现。
