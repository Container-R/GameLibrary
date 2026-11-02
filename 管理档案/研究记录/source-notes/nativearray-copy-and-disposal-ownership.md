# 复制了 NativeArray 变量，为什么不能各自释放

一个采样任务需要一组数据。负责人创建数组，随后把数组变量分别交给两个消费者。任务结束时，三个地方都保存着一个变量，是否就应该各自释放一次？又或者，只要某个变量的 `IsCreated` 仍为 true，就说明数据还可以使用？

这两个判断都把**变量里的记录**和**记录所指向的存储**混在了一起。复制一个资源变量，不自动意味着复制了存储，也不自动意味着多取得一份拥有权；具体行为要看类型。下面限定 Unity 的 `NativeArray` 普通值赋值，不把结论套到所有语言、容器或句柄。

## 三个变量，仍可能只有一份元素

设负责人成功创建了一个普通、非空、使用 `Allocator.Persistent` 分配的采样数组 `a`，再进行 `b = a`、`c = a`，交给两个只读消费者。这个场景是虚构的来源分析，没有运行 Unity；以下释放都以调用合法且成功为前提。

在本文固定的 Unity 6000.0.0f1 C# reference source 中，`NativeArray` 是值类型 `struct`，其中保存指向元素的指针、长度、allocator 等字段。普通赋值复制这些字段，不为每个变量重新分配一份元素。[1] 因而，a、b、c 是三个变量，却仍指向同一份采样数据。

这也解释了为什么“我把 b 当借用”还不是一种自动保护。它可以是团队约定，却没有把 b 变成某种特殊的非拥有视图：普通副本仍保留 allocator 字段。不能假定所有副本的 `Dispose()` 都是无操作，也不能让每个使用者因为拿到变量就各自释放。

如果两个消费者需要各自独立修改的副本，应另行设计独立存储及内容复制。仅仅改变量名，不能得到独立数据；这里也不展开各复制 API 的选择。

## 同步释放后，别的副本为什么还能显示 true

先走一条简单的合法路径：两个消费者都已停止使用，负责人成功调用 `a.Dispose()`。

固定源码的同步释放路径归还底层内存，并清空接收者 a 的指针字段；它没有遍历所有地方，把 b、c 的字段一并改写。而 `IsCreated` 检查的只是当前这个副本的指针是否非空。[1] 所以 a 已经是 false，b、c 却仍可能保持 true。Collections 2.1.4 文档也明确提醒了这种副本区别。[2]

此时 b 的 true 不是继续访问数据的许可，更不是再次释放同一份分配的理由。不要为了验证这个解释而去读取或二次释放失效副本。应用应靠使用期与释放责任决定下一步，而不是让每个副本独自询问 `IsCreated` 后作决定。

`IsCreated` 并非没有用途；问题在于把一个变量的字段状态，当成了所有副本共享的存活通知。它既没有撤回其他变量，也没有替程序收齐使用者。

## 延迟释放时，false 又不等于已经释放完

如果两个消费者是已经调度的作业 J1、J2，负责人可能希望等它们完成后再释放，而不是立刻在主线程等待。此时需要先形成覆盖二者的依赖 `lastUse`；不能因为 J2 的 handle 最后拿到，就认为它自然包含 J1。`CombineDependencies` 可以把已知依赖合并，但选择哪些使用者必须被覆盖，仍是调用方的责任。[3]

随后，负责人成功调用 `release = a.Dispose(lastUse)`。对本文拥有分配的路径，固定代码会安排一个依赖于 lastUse 的释放作业，清空 a 的字段，再返回这个释放作业的 handle；真正归还内存发生在该作业执行时。[1]

因此，a 的 `IsCreated=false` 说明不了释放作业是否已经完成。作业也可能很快完成，所以这里不是承诺每次都能观察到一段“false 但内存未释放”的时间窗口。

把两个 handle 的用途说清楚更容易避免误用：**lastUse 覆盖释放前的消费者，release 则代表安排出来的释放工作。** 若后续工作依赖释放完成，应保留并使用返回的 release；需要同步确认时，对它调用 `Complete()`，而不是仅等待输入 lastUse。官方 API 的契约是确保所指作业完成。[3]

安排释放也不等于取消 J1、J2。它们若已正确纳入依赖，仍应按原安排完成。禁止的是再交出新的使用机会，或让旧副本在约定使用期外继续访问；不能因为 owner 字段清空，就说正确登记的消费者立即变成非法访问。

## 交出去之前，就决定由谁收尾

对这组采样数据，可以采用下面的应用安排。它是设计建议，不是 Unity 自动提供的借用检查器。

先指定一名释放负责人，并告诉两个消费者何时可以使用、怎样报告结束。准备收尾时，不再新增使用者；已有的主线程同步使用应先结束，作业使用则要全部纳入依赖。不要假定 job handle 会自动登记一段普通函数里的访问。

随后选择一种路径：使用者全部完成后同步释放，或让释放作业依赖完整的已有工作。若走延迟路径，把返回的释放 handle 保存到真正需要它的地方，不用 `IsCreated` 代替完成依据。其他副本即使仍存在，也只能遵守已经结束或收束的使用期，不能自行恢复访问或获得释放权。

这项安排与 Addressables 的引用管理不同。若你处理的是 catalog 加载操作，应回到[Addressables 内容更新书的操作持有说明](../../../GameLibrary/引擎与工具/构建发布/内容更新/Unity Addressables内容更新与旧客户端兼容.md#手动加载附加目录时别漏掉加载操作)；不要把 NativeArray 普通赋值理解为增加一次引用计数。

## 这里没有解决什么

本文只解释成功分配的普通非空 Persistent 数组，以及合法、成功的两种释放路径。它不推广未创建接收者返回输入 handle 的分支，也不把零长度数组等同于未创建。

Temp、TempJob、自定义或可重绕 allocator、外部指针、各种 view、unsafe 绕过及结构体防御性复制，需要分别核对。安全检查可能帮助发现错误，但本文没有验证各构建配置，更不保证错误访问总能被拒绝。

漏记消费者、调度失败、异常中途发生或多个线程并发修改负责人状态，都还需要具体恢复与同步设计。本文没有运行作业、测试包装器或测量性能，也没有认证源码版本、Collections 包与某个已安装编辑器的组合。它提供的判断起点是：**一份分配的使用关系和释放依据，不能由几个副本各自的布尔字段拼出来。**

## 参考来源

2026-11-02 重新定向读取以下公开原源；没有执行 Unity。

[1] Unity 官方 C# reference source，`6000.0.0f1`，固定提交 `0d0e6a11923ed73f1e8481eb5a6b2e67fe5ddc09`；本轮重新核对 tag 指向。实际读取 [NativeArray.cs](https://github.com/Unity-Technologies/UnityCsReference/blob/0d0e6a11923ed73f1e8481eb5a6b2e67fe5ddc09/Runtime/Export/NativeArray/NativeArray.cs) 第34–67、156–270、924–947行：字段、IsCreated、两种 Dispose 与释放 job。另读 [JobHandle.bindings.cs](https://github.com/Unity-Technologies/UnityCsReference/blob/0d0e6a11923ed73f1e8481eb5a6b2e67fe5ddc09/Runtime/Jobs/ScriptBindings/JobHandle.bindings.cs#L22-L100) 第22–100行；托管绑定不是 native 调度器实现。

[2] Unity Collections 2.1.4，[*Allocator overview*](https://docs.unity3d.com/Packages/com.unity.collections@2.1/manual/allocator-overview.html)，重点 Persistent、Deallocating an allocator、IsCreated property；页面生成日期2024-04-02。包文档版本与引擎源码版本分别记录，不能互相替代。

[3] Unity 6000.0 API：[*CombineDependencies*](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Unity.Jobs.JobHandle.CombineDependencies.html) 的说明与示例，以及 [*Complete*](https://docs.unity.com/en-us/engine/6000.0/script-reference/unity/jobs/jobhandle/complete) 的说明与 Remarks。它们是可更新文档，不是本例的执行记录。

---

[返回《关闭装备预览后，未完成的资源加载怎样收尾》](../../../GameLibrary/引擎与工具/运行时系统/异步资源/关闭装备预览后，未完成的资源加载怎样收尾.md)
