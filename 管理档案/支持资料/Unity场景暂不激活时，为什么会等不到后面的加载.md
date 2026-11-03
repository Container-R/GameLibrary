# Unity场景暂不激活时，为什么会等不到后面的加载

一个加载界面先准备场景 A，但暂时不让它激活。程序又请求加载资源 B，打算等 B 完成后再放行 A。看起来只是多等一个资源，结果 A 一直没有激活，B 也一直没有完成。

这可能不是 B 太大，而是程序自己安排了一个循环等待：**A 的激活要等 B，B 的处理却要先等 A 放行。** 下文用 Unity 的文档约束解释这种接入风险，不把它说成所有异步加载系统都有的行为。

范围是 Unity 6000.0 的 `AsyncOperation.allowSceneActivation`，以及 Addressables 2.7.6 文档中的 `activateOnLoad`。这里没有运行 Unity、构建场景或复现卡住；A、B 是原创的条件示例，不是实际故障记录。

## 延迟激活，不只是少调用一次显示

用 `SceneManager.LoadSceneAsync` 得到的场景加载操作，可以通过 `allowSceneActivation=false` 延迟激活。Unity 6000.0 文档说明，在这个状态下，操作进度停在0.9，`isDone` 仍为false；更重要的是，`AsyncOperation` 队列会停住。文档直接举例：后续 `UnloadSceneAsync` 不会继续处理，直到前一操作允许激活。[1]

所以，不能只把它理解为“场景早就完全处理好了，只差把画面显示出来”。你延后的是引擎操作的一部分，它还会影响后续排队工作的推进。0.9也是这个场景操作的进度条件，不是所有资源加载的统一完成标记，更不能直接当作已经下载的字节比例。

Addressables 2.7.6 对 `activateOnLoad=false` 有对应警告：它会阻塞 `AsyncOperation` 队列，包括其他 Addressable 资产的加载，直到场景被激活。[2] 这是明确的范围，不能扩大成“全部线程、所有网络请求和任意异步任务都暂停”。

## 看清循环究竟在哪里

下面的三条是**假定应用满足的条件**，不是从某段日志猜出的事实：

1. A 已因延迟激活而挡住所述队列。
2. B 是此时排在后面、依赖该队列推进的加载工作。
3. 应用只会在 B 完成后才允许 A 激活，没有其他放行路径。

它们组成了这样的等待关系：

```text
A 的激活许可 ← 等待 B 完成
B 的加载推进 ← 等待 A 允许激活
```

在这些条件不变时，单纯再等一会儿不能消除这个环。把协程改成另一种等待写法，也不会自动改变谁先等谁。这是根据文档约束作出的依赖分析，不是本库测得某个固定时长后一定死锁。

反过来，不能只看到两个操作都未完成，就断言一定是这个原因。B 可能不经过受阻队列，可能早已完成，也可能因另一项错误而失败。排查需要核实际操作类型、启动次序、A 的激活许可，以及究竟哪条代码能改变这个许可，而不是仅看加载界面的百分比。

## 不要混淆引擎操作和Addressables句柄

普通 `SceneManager.LoadSceneAsync` 返回的是引擎的 `AsyncOperation`。Addressables 的场景加载则返回 `AsyncOperationHandle<SceneInstance>`；这不是同一种对象，不能把前者的 `isDone` 状态直接套给后者。[3][5]

对本文讨论的 Addressables 延迟激活路径，应通过成功取得的 `SceneInstance` 调用 `ActivateAsync()`；该方法返回引擎的场景加载 `AsyncOperation`。[2][4] “已拿到可用于激活的场景结果”与“场景已经激活完毕”仍须区分，不能把所有阶段统称成一个完成回调。

这也不是一段可直接复制的加载器。接入者还需要按所用包版本处理失败、句柄持有和释放，以及切换被取消时的收尾；不能对失败或已失效的句柄无条件读取结果，更不能将装备预览的 `LoadAssetsAsync` 释放策略直接套到场景卸载上。

## 把前置依赖移到等待环之外

要修的是依赖关系，而不是给进度条加一个更长的超时。对于上面的条件示例，可以考虑两种不同安排：

- **B 确实是激活 A 前必须完成的准备。** 先让 B 完成，再进入会挡住队列的延迟激活阶段。需要重新检查内存峰值与失败时保留什么，不能只改调用顺序就宣布整个加载流程安全。
- **A 可以先激活，B 并非激活前提。** 在项目允许的时刻放行 A，再让后续工作继续。是否接受提前进入该场景，是玩法与生命周期安排，不应为了疏通队列无条件强行激活。

这是编辑者给出的接入选择，不是 Unity 文档承诺的通用修复方案。若产品确实需要长时间把场景停在激活前，还要列出这段时间哪些工作不能依赖受阻队列，以及放行由谁负责。不要把激活放行责任交给一个随加载界面关闭就消失的临时对象，再期待另一个等待自然结束。

检查修改时，应记录每个操作自己的状态，而不只给整个流程保留一个“加载中”：A 何时开始延迟激活，B 何时提交，谁允许 A 激活，激活何时完成。本文没有执行这些检查，也没有证明缓存命中、不同加载模式或不同包版本的所有时序。

能迁移到其他引擎的，是先画清等待关系；这里的0.9、接口名称和队列限制，仍然属于所引用的 Unity 文档范围。

## 参考来源

2026-11-03读取以下官方文档。它们是版本目录中的文档，不是已编译验证的引擎／包组合；没有读取内部实现或运行例子。

[1] Unity，[*AsyncOperation.allowSceneActivation*，6000.0](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/AsyncOperation-allowSceneActivation.html)，Remarks及示例。页面正常重定向至同6000.0系列的新文档地址；用于延迟激活、0.9、isDone及后续Unload队列例。

[2] Unity，[*Load scenes*，Addressables 2.7.6](https://docs.unity3d.com/Packages/com.unity.addressables@2.7/manual/LoadingScenes.html)，参数与Warning。`@2.7`是系列地址，本次页面标2.7.6；其他Addressable加载受阻范围来自该警告，不推广为任意异步任务。

[3] Unity，[*Addressables.LoadSceneAsync*](https://docs.unity3d.com/Packages/com.unity.addressables@2.7/api/UnityEngine.AddressableAssets.Addressables.LoadSceneAsync.html)，`object, LoadSceneMode, bool, int, SceneReleaseMode`重载的声明与返回类型。本文没有核读全部重载。

[4] Unity，[*SceneInstance.ActivateAsync*](https://docs.unity3d.com/Packages/com.unity.addressables@2.7/api/UnityEngine.ResourceManagement.ResourceProviders.SceneInstance.ActivateAsync.html)，方法声明及返回说明。该方法专页与手册写作ActivateAsync；加载API参数描述仍有Activate()字样，本说明采用实际方法声明，不据残留描述编造另一个接口。

[5] Unity，[*SceneManager.LoadSceneAsync*，6000.0](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/SceneManagement.SceneManager.LoadSceneAsync.html)，首个 `int, LoadSceneMode` 重载的声明、返回说明及示例。用于核对普通引擎 API 返回 `AsyncOperation`，没有核读全部重载。

[返回异步资源收尾正文](../../GameLibrary/引擎与工具/运行时系统/异步资源/关闭装备预览后，未完成的资源加载怎样收尾.md)
