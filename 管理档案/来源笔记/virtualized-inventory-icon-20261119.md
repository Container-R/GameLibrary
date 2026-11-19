# 虚拟背包图标绑定：来源与验证范围

读取日期：2026-11-19。

## 一手资料：来源陈述与本文推导分开

S1 Unity 6000.0 ListView API
https://docs.unity3d.com/6000.0/Documentation/ScriptReference/UIElements.ListView.html
正常重定向至 https://docs.unity.com/en-us/engine/6000.0/script-reference/unityengine/uielements/listview
读取示例中 makeItem 创建、滚动复用、bindItem 使用 index 关联数据及属性说明。网页行定位约 760–772、841–844、869–873。
支持：视觉元素复用及回调职责。不给出本文图标加载算法。

S2 Unity 6000.0 bindItem / unbindItem
https://docs.unity3d.com/6000.0/Documentation/ScriptReference/UIElements.ListView-bindItem.html
https://docs.unity3d.com/6000.0/Documentation/ScriptReference/UIElements.ListView-unbindItem.html
对应重定向页面 Remarks，约 768–775 / 768–773：参数为视觉元素与索引，自定义一端而不配置另一端可能产生意外行为。
支持：绑定入口参数及成对接入。没有从这里推断每次自定义刷新必然以某个完全固定顺序回调，正文要求实际接入记录。

S3 Unity 6000.0 Manual ListView
https://docs.unity3d.com/6000.0/Documentation/Manual/UIE-uxml-element-ListView.html
对应重定向：https://docs.unity.com/en-us/engine/6000.0/manual/uitoolkits/uielements/uie-element-ref/uie-uxml-element-list-view
读取 ListView versus ScrollView、Refresh the collection view（约 371–420）。支持视觉元素回收、RefreshItem(s)与Rebuild区别；不提供本例性能数据。

S4 Microsoft Cancellation in Managed Threads
https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads
读取概述 33–55 与 Operation Cancellation Versus Object Cancellation 171–174。
支持协作取消由接收方响应、取消请求不强制停止；不据此断言某个 Unity 加载器可取消或一定回调。

补充阅读（正文未引用）：Unity 6000.0 Create a complex list view，确认其示例是 EditorWindow，并演示 bind 时更新数据关系。未复制代码，未将此编辑器例子当作运行时图标实验。
https://docs.unity3d.com/6000.0/Documentation/Manual/UIE-create-list-view-complex.html

以上均为2026-11-19读取的版本化网页，非固定发行源码快照。网页导航列出其他 Unity 版本不改变所读 6000.0 路径；内容仍可能后续更新。

## 原创推导与真实执行

原创方案：每次绑定票据，捕获不可变业务/资源目标，解绑先撤销资格，加载完成串行提交；模型变更须同步失效/刷新绑定；占位清除与过期回调拒绝是两项不同条件。

实际执行：Node v24.22.1，运行 `node fixture.mjs > output.json`，9组断言通过；坏变体得到预定错误（A覆盖B、旧失败污染同键新绑定、索引重排串图、等待期间旧图未撤）。输出是应用状态，不是Unity运行或可见帧。

加载替身主动忽略取消请求以检验结果归属。成功结果附带独立字符串资产租用；所有创建租用在关闭测试单元格后恰好释放一次。没有真实纹理、共享缓存引用计数、下载、线程或事件订阅实现。

本轮可用执行环境未找到 Unity 编辑器，没有安装引擎；有限检查不能证明所有机器上均不存在。没有以其他引擎的运行代替 Unity 验证。


## 正文与材料

[正文](../../GameLibrary/界面与体验/界面编程/列表与数据绑定/背包列表滚动后串图：虚拟单元格与异步图标的绑定.md)；[复现实验](../实验/虚拟背包图标绑定/README.md)。
