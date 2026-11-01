# NativeArray：值副本的 IsCreated，不是全局存活或释放完成通知

本文限定普通、非空、成功分配的 `Allocator.Persistent` 数组。依据 Unity 官方 C# reference source **6000.0.0f1** 固定提交 `0d0e6a11923ed73f1e8481eb5a6b2e67fe5ddc09`，并分别参考 Collections **2.1.4** 与引擎 **6000.0** 文档。没有运行 Unity，也没有认证这几个版本在某个安装环境中的组合。

## 同一个字段，两种不能据此作出的决定

固定代码的 `NativeArray` 是 struct，`IsCreated` 只检查该副本的 buffer 指针。普通值赋值复制字段，不复制底层元素；分配者的同步 `Dispose()` 释放内存并清空接收者字段，不会遍历其他副本。[字段定义](https://github.com/Unity-Technologies/UnityCsReference/blob/0d0e6a11923ed73f1e8481eb5a6b2e67fe5ddc09/Runtime/Export/NativeArray/NativeArray.cs#L34-L67)、[查询与同步释放](https://github.com/Unity-Technologies/UnityCsReference/blob/0d0e6a11923ed73f1e8481eb5a6b2e67fe5ddc09/Runtime/Export/NativeArray/NativeArray.cs#L194-L231)

由此构造两个**未执行、遵守合法调用前提**的情景：

| 情景 | 能从机制推出什么 | 不能作出的决定 |
|---|---|---|
| `b = a`，所有使用者完成后，负责人成功调用 `a.Dispose()` | a 已清空；b 的指针字段未被同步改写，其 `IsCreated` 仍为 true | 因 b 为 true 就访问内存，或让 b 再释放同一分配 |
| 负责人成功调用 `release = a.Dispose(lastUse)` | a 在调用返回前已清空，释放 job 不必已经完成 | 因 a 为 false 就宣称底层内存已经释放 |

第二行依据拥有分配的分支：它按 `inputDeps` 调度释放 job、清空接收者，再返回 job handle；实际 free 位于释放 job 的执行路径。job 也可能很快结束，因此这里**不声称每次都存在可观测的“false 但尚未 free”窗口**。[延迟释放](https://github.com/Unity-Technologies/UnityCsReference/blob/0d0e6a11923ed73f1e8481eb5a6b2e67fe5ddc09/Runtime/Export/NativeArray/NativeArray.cs#L233-L270)、[释放 job](https://github.com/Unity-Technologies/UnityCsReference/blob/0d0e6a11923ed73f1e8481eb5a6b2e67fe5ddc09/Runtime/Export/NativeArray/NativeArray.cs#L924-L947)

普通 `b = a` 还保留 allocator 字段。把 b 在设计上称为“借用”，不会自动将它变成非拥有视图；不能外推某种 view 的释放规则，称普通副本的 `Dispose` 一律是 no-op。本文不尝试访问或再次释放失效副本来制造演示。

## 原创接收协议：先收齐消费者，再保存释放的依赖

以下是应用可以采用的协议，不是 Unity 自动赋予的借用检查，也不是完整生产管理器。

1. **一份分配，一名释放负责人。** 记录谁负责同步或延迟释放；其他值副本仅按约定使用，不能凭自己的 `IsCreated` 获得释放权。
2. **关闭新借用，再收齐已调度使用者。** 假设两个独立读作业 J1、J2 使用同一分配，`lastUse` 必须覆盖二者，不能只挑最后拿到的一个 handle。官方 `CombineDependencies` 可把多项依赖合成一项；其示例的后继作业等待两项前驱完成。[6000.0 API](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Unity.Jobs.JobHandle.CombineDependencies.html) 选择哪些依赖仍是调用者责任，不是自动发现所有副本。主线程等非作业的同步借用也应先结束，不能假定 job handle 自动登记了这些使用。
3. **成功安排释放后，保留返回的 release。** 将它用于依赖于释放完成的后续工作；需要同步确认时，对这个返回 handle 调用 `Complete()`，而不是仅等输入 `lastUse`。官方契约是确保该 job 已完成。[6000.0 Complete API](https://docs.unity.com/en-us/engine/6000.0/script-reference/unity/jobs/jobhandle/complete)

关闭新借用不意味着取消既有作业。已正确包含在释放依赖中的消费者仍按原依赖完成；不能因为 owner 字段清空，就断言它们立即变成非法访问。同步释放则应等使用者完成后由负责人执行。清空 owner 也没有物理撤回其他变量里的副本，协议需要约束这些变量后续的用途。

这里没有解决异常中途发生、漏记消费者、调度失败或并发修改 owner 的恢复过程。没有通过包装器测试、安全检查配置矩阵或性能测量来证明完整内存安全。

## 来源与适用边界

访问日期为 **2026-11-01**。上述固定 C# 代码解释字段与调度入口，不包含 native 调度器实现；[JobHandle 托管绑定](https://github.com/Unity-Technologies/UnityCsReference/blob/0d0e6a11923ed73f1e8481eb5a6b2e67fe5ddc09/Runtime/Jobs/ScriptBindings/JobHandle.bindings.cs#L22-L100) 不代替公开 API 契约或实际执行。

辅助来源 [Collections 2.1.4 — Allocator overview](https://docs.unity3d.com/Packages/com.unity.collections@2.1/manual/allocator-overview.html)，*Deallocating an allocator / IsCreated property*；页面元数据生成日期为 2024-04-02。它支持副本与延迟释放的区分，不把包版本当作引擎源码版本。6000.0 API 文档是可更新页面，固定源码提交则为另一种版本定位。

不覆盖 Temp / TempJob、自定义或 rewindable allocator、外部指针、各种 view 的完整释放政策、unsafe 绕过或结构体防御性复制；也不承诺错误访问在所有构建中都会被诊断拒绝。

[Addressables 操作所有权](../../历史正文/solutions/engine/addressables-content-update-baseline.md)处理的是另一类引用管理，不能据此把 NativeArray 普通值副本解释为新增一次引用计数。本篇没有执行失效访问、释放、作业或引擎实验。
