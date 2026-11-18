# Unreal 帧卡顿与 PSO：原始依据

核读日期 2026-11-18。区分引擎手册、支持人员读 trace 的观察、本文的独立纸面计算。本文没有运转 Unreal、读取原始案例 trace 或实测帧改善。

1. [Epic PSO Precaching](https://dev.epicgames.com/documentation/unreal-engine/pso-precaching-for-unreal-engine)，UE 5.9。Testing：驱动缓存残留可能掩盖首次现象；同测试组使用清除参数。Validation and Tracking：Missing coverage 与 queued but too late 区分，Shipping 未跟踪情况可能并入 Missed，运行时创建卡顿另有阈值。Collect Information：验证需要启用，日志按材质、通道、顶点工厂、哈希等提供线索；官方示例中有较大但非 PSO 所致的卡顿。Memory：驱动第一次取回仍可能有开销。
2. [Epic Timing Insights](https://dev.epicgames.com/documentation/unreal-engine/timing-insights-in-unreal-engine) 和 [Task Graph Insights](https://dev.epicgames.com/documentation/unreal-engine/task-graph-insights-in-unreal-engine-5?lang=en-US)，直接重读时所见文档标为 UE 5.9。CPU/GPU 分轨、帧选区、调用关系；Task Connections 显示可观测任务依赖，关键路径计算以图内各任务的执行时间为准，不等于整帧分析。这里复用排查入口，不断言所有版本或构建的界面与跟踪数据一致。
3. [Epic Developer Community 论坛原讨论](https://forums.unrealengine.com/t/ue-5-7-3-d3d12-sm6-pso-cache-pipeline-compute-pso-bundling-and-late-pso-hitches-on-pc/2745197)，KTerelst（署名 Kenzo） 的回复，Frame 569 和 967。前者主因分析为删除 RHI 资源，且另有 37 ms 计算 PSO 缺失；后者归因为 Nanite 计算迟到。回复推测的修复没有作为已证结论；未取得原始附件。

纸面例的独立分支在共同提交点汇合。第 26 ms 消费 PSO，原完成 29 ms；比较 `max(29,B)` 与 `max(26,B)`，B 分别为 36、21，得到 36→36、29→26。数值与公开案例无关；无 CPU 争抢、其他依赖或变长提交后工作是模型假设。
