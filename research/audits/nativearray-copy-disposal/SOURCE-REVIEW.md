# NativeArray 副本与释放：独立来源门复核

2026-11-01。**接受有限 source-only 机制；未发现阻断前提。** 本次独立重新读取固定源码和下列官方正文，未参与该来源门起草。没有执行 Unity、Jobs、Burst 或内存访问，未读取关联运行档案或执行环境资料。不是最终正文验收。

## 实际读取范围

固定 UnityCsReference `0d0e6a11923ed73f1e8481eb5a6b2e67fe5ddc09`，版本标签 6000.0.0f1：

- [NativeArray.cs](https://github.com/Unity-Technologies/UnityCsReference/blob/0d0e6a11923ed73f1e8481eb5a6b2e67fe5ddc09/Runtime/Export/NativeArray/NativeArray.cs)：34–67、156–270、924–947；字段、局部状态、两个释放入口和释放作业的执行位置。
- [JobHandle.bindings.cs](https://github.com/Unity-Technologies/UnityCsReference/blob/0d0e6a11923ed73f1e8481eb5a6b2e67fe5ddc09/Runtime/Jobs/ScriptBindings/JobHandle.bindings.cs)：22–28、74–100；托管绑定，不据此声称检查了 native 调度实现。
- Collections 2.1.4 [Allocator overview](https://docs.unity3d.com/Packages/com.unity.collections@2.1/manual/allocator-overview.html)：Deallocating an allocator / IsCreated property；[Aliasing allocators](https://docs.unity3d.com/Packages/com.unity.collections@2.1/manual/allocator-aliasing.html)：视图示例及 Array reinterpretation。页面元数据为 2.1.4，与引擎源码分开标识。
- Unity 6000.0 [CombineDependencies](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Unity.Jobs.JobHandle.CombineDependencies.html) 的 Description 和双依赖示例；[Complete](https://docs.unity.com/en-us/engine/6000.0/script-reference/unity/jobs/jobhandle/complete) 的定义及 Remarks。首次直接获取 Complete 超时；随后从旧官方地址重定向到同页成功读取，不把失败请求当证据。

这些定位支持门中有限机制，事实说明应集中在新说明正文，不在审查中再次展开整段来源摘要。未认证任何包与引擎安装组合。

## 独立推理与必要边界

1. 普通 `b=a` 不等同于通过特定 API 构造非拥有视图。前者复制 allocator 字段；应用称它“借用”不会改变字段。不能把 alias 文档的简化处置文字推广成所有值副本 Dispose 都是 no-op，也不在本次替全部 Reinterpret/视图 API 指定释放政策。
2. 在门中非空 Persistent 分配及成功调用的前提下，两方向反例成立：另一副本的局部非空字段不能授权再次访问/释放；负责人字段清空也不能证明释放作业已完成。后者只证明可能尚未执行，不声称总存在可测量时间窗口。
3. 原创协议应把“禁止新增借用”与“先前已正确纳入依赖的作业正常完成”分开。成功调度释放不是宣布所有既有消费者立刻非法；反过来，仅选一个读作业的 handle 不能覆盖另一个独立使用者。
4. 输入依赖完成与返回的释放作业完成不能互换。合并依赖 API 支持完整先行关系，Complete API 支持等待对应作业；这不是自动发现消费者或保证异常路径已处理。须保留返回 handle，并明确应用层关闭/回收时需要哪一个完成条件。

限定在成功拥有分配分支，不推广未创建接收者（`!IsCreated`）返回输入 handle 的分支、非拥有分支、自定义 allocator、并发 owner 或防御性复制。元素检查条件编译不足以承诺所有构建安全拒绝错误访问；不预测具体异常、崩溃或性能。源码与文档足以支持该有限公开说明，不足以升级为生产内存安全证明。
