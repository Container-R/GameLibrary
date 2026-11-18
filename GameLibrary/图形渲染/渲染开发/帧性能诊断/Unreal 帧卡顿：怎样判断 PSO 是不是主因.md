# Unreal 帧卡顿：怎样判断 PSO 是不是主因

第一次转进走廊，画面卡了一下。Unreal Insights 里，同一个尖峰附近恰好有一条 PSO Missed。先别把任务派给负责管线缓存的人：这条记录说明绘制或派发计算时发现了准备问题，却不直接回答「把这个 PSO 提前做好，这帧会不会更快」。本文给有基本 Unreal 性能分析经验的渲染开发者一条排查路线：先找到哪一步不能继续，再查它在等什么。

## 先区分两张记录

PSO（管线状态对象）包含图形 API 执行绘制或计算所需的一组状态。用 UE 5.9 的术语来说，未预缓存但本应覆盖的组合记作 **Missed**；已有预缓存请求、却没赶上使用时刻的是 **Too Late**。**Untracked** 则表示不在该验证的跟踪范围内；Shipping 构建缺少某些调试信息时，可能把它记作 Missed。[1] 这些是准备侧的分类。不要用不同构建的 Missed 数直接比较覆盖率，也不要从计数推算帧耗时。单独的运行时 PSO 创建卡顿计数还有自己的阈值，不能替代项目的帧预算。[1]

帧侧要问的不同：**哪个必须完成的工作，把关注的帧端点推迟了？** 端点可以是你在排查的 CPU 帧结束或提交，也可能是之后的 GPU 执行、呈现。先选定观察目标，不要把同编号的 Game、Render 和 GPU 区间假定为同一次画面提交。PSO 编译花了多久、某个消费者等了多久、这次等待对观察端点增加了多久，通常是三个不同的数字。

## 在时间线上从消费点向前查

1. **先定位可以重现的那次尖峰。** 固定引擎版本、打包配置、RHI（渲染硬件接口）、设备与驱动、画质和首次进入的路线。按 Epic 的建议，在同一组冷驱动缓存测试中一致使用 `-clearPSODriverCache`；热缓存复测另立一组。记录验证档位；排查时可用 `r.PSOPrecache.Validation=2` 取得详细记录，开销不能假装不存在。[1] 若需要衡量玩家最终看到的停顿，另保留对应的呈现测量，不能只报诊断构建里的 CPU 数。
2. **打开尖峰附近的线程和 GPU 轨道。** 在 Timing Insights 选择明确的帧范围，先找显著的串行工作、等待或空档，必要时扩大到尖峰前后的帧。按实际轨道展开 Game、Render、RHI 和 GPU 的相关工作，利用 Timers 与 Callers/Callees 找事件上下文，不要把不同线程或同线程嵌套计时器的耗时相加。[2] 若开始排查的是一条 PSO 日志，拿它记录的组合来对照实际消费点；对图形 PSO 可参考材质、pass、vertex factory 和着色器哈希等字段，计算 PSO 则按其可用标识找 dispatch。只靠相邻时间戳或只匹配材质名，还不能确认是同一工作。
3. **找到连接这两条记录的依赖。** 若能识别出画面提交必须等待的绘制或计算，再查它是否等同一个 PSO 的完成；区分请求提出、编译（或取回）、首次需要和继续执行。启用了任务追踪且事件确实属于可追踪任务时，可以用 Task Connections 查看已记录的前置、后续任务。[3] 工具中的任务关键路径只对该任务图按已记录执行时间计算，不会替你证明任意驱动等待、线程空档或整帧呈现的原因。没有看见消费或等待关系时，记为「尚不能归因」，不要把空档自动算给 PSO。
4. **选择能验证假设的下一次比较。** 已排队但消费点在完成之前，优先试把那批请求提前到场景切换或内容确定时；真正未收集的组合则先比对收集和实际绘制或计算的输入。若已准备但实际首次使用仍慢，继续区分驱动取回和其他同时发生的工作，不要复用漏收的结论。[1] 如果主线索指向资源销毁或另一同步链，先查那条路径，PSO 缺口可以单独登记。只改变跟假设相应的一项，在相同缓存条件下重走路线；同时看 PSO 事件和帧端点是否一起变化。即使游戏中少了一项等待，也要看成本是否只是移到加载页，或换成了首次不可见等画面差异。

## 同一条编译，为什么可能不延长这一帧

用一个纸面例子说明。假设一个提交步骤要等两个分支：A 是首次绘制，最早到第 26 ms 才会用到 PSO；B 是与它独立且提交前必须结束的工作。原来 PSO 在第 4 ms 开始编译、第 29 ms 才完成。按这个例子的假设，A 要等 3 ms，不是编译总共用掉的 25 ms。把 PSO 提前到第 26 ms 可用，只去掉这段等候。

| 另一路 B 结束时刻 | 原先最早可提交 | PSO 提前后最早可提交 |
| --- | --- | --- |
| 第 36 ms | 第 36 ms | 第 36 ms |
| 第 21 ms | 第 29 ms | 第 26 ms |

表格按两个前置分支中较晚完成的一支计算，忽略 A 获得 PSO 后的剩余工作，提交后工作不变；假定独立分支之间没有争抢资源。第一行里 PSO 的确拖住 A，但 A 不是最后等到的工作。第二行才真的把提交提前了 3 ms。实际线程可能同核争抢、有别的等待或跨帧排队；不是从任何两条事件的长短做减法就能套出这个表。

公开案例也能看出这种区别。一份 UE 5.7.3、D3D12 SM6 的项目支持讨论中，审阅 trace 的 KTerelst（署名 Kenzo） 把第 569 帧主要归于 RHI 资源删除，虽然同处还发现一项 37 ms 的计算 PSO miss；他把另一处第 967 帧的大尖峰归于迟到的 Nanite 计算管线。[4] 这是对该项目捕获的诊断记录，原始 trace 未供本文复核，不能据此算两类工作的重叠毫秒数，也不能把帖子提到的候选修补认作已证明的解决方案。遇到类似问题，最有用的缺陷说明不是「这帧有 Missed」，而是「哪个消费者在等哪个管线；若没有看到这层依赖，还看到哪些更可能推迟这帧的工作」。

## 参考资料

1. Epic Games，[PSO Precaching](https://dev.epicgames.com/documentation/unreal-engine/pso-precaching-for-unreal-engine)，UE 5.9；Testing、Validation and Tracking、Collect Information on PSO Precaching，以及驱动缓存取回段落。
2. Epic Games，[Timing Insights](https://dev.epicgames.com/documentation/unreal-engine/timing-insights-in-unreal-engine)，UE 5.9 在线文档；Frames、Timing Panel、Timers and Counters、Callers and Callees。涉及的界面以目标版本所见为准。
3. Epic Games，[Task Graph Insights](https://dev.epicgames.com/documentation/unreal-engine/task-graph-insights-in-unreal-engine-5?lang=en-US)，UE 5.9 在线文档；CPU task trace、Task Connections 和 Task Dependencies 段。该页给出任务追踪示例 `-trace=default,task`。
4. Epic Developer Community，[UE 5.7.3 D3D12 SM6: PSO cache pipeline, compute PSO bundling, and late PSO hitches on PC](https://forums.unrealengine.com/t/ue-5-7-3-d3d12-sm6-pso-cache-pipeline-compute-pso-bundling-and-late-pso-hitches-on-pc/2745197)，定位 KTerelst（署名 Kenzo） 对 Frame 569、967 的直接回复。未据回复外推其他游戏或驱动。
