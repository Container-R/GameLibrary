# Detour findPath：成功搜索与完整输出，是两项接收条件

> 以下保留初次发表的来源分析；其中“未执行”指该原始分析形成时。后续三矩形容量观察另见末节，不把其结果扩展到全部政策与预算情形。

本文只核对官方 Detour **v1.6.0** 固定提交 `6dc1667f580357e8a2154c28b7867bea7e8ad3a7`，不称为最新版。访问日期：2026-11-01。下文是源代码推导与原创调用者政策，**没有编译、调用 Detour 或构建导航网格**。

## 一个不能只靠 PARTIAL_RESULT 检出的缺尾结果

固定实现中，`dtStatusSucceed` 只检查成功位；`dtStatusDetail(status, mask)` 检查掩码内**任一位**是否存在，不是要求全部存在。[状态定义与辅助函数](https://github.com/recastnavigation/recastnavigation/blob/6dc1667f580357e8a2154c28b7867bea7e8ad3a7/Detour/Include/DetourStatus.h#L22-L63)

`findPath` 依据搜索所得末节点是否为 `endRef` 添加 `DT_PARTIAL_RESULT`；父链输出超过 `maxPath` 时，`getPathToNode` 写入起点侧前缀，返回 `DT_SUCCESS | DT_BUFFER_TOO_SMALL`，并不因此添加 `DT_PARTIAL_RESULT`。[结果组装与父链回写](https://github.com/recastnavigation/recastnavigation/blob/6dc1667f580357e8a2154c28b7867bea7e8ad3a7/Detour/Source/DetourNavMeshQuery.cpp#L1147-L1204)

**原创、未执行的构造：** 假设搜索确已找到 A→B→C，目标引用为 C，期间没有节点池不足，而调用者只提供 `maxPath=2`。按上述控制流，写出的 corridor 为 A、B，状态为 `SUCCESS | BUFFER_TOO_SMALL`，没有 `PARTIAL_RESULT`。这不是观察到的返回数组，也不需要虚构一个游戏中的导航失败。

因此，“成功且没有 partial”仍可能批准一份缺少目标 polygon 的数组。搜索内部已经找到 C，与调用者实际取得 C，是不同的事实。反例针对的是输出容量，不是角色距离容差。

## 两种容量，对应两种处理方向

节点分配失败会记录 `OUT_OF_NODES` 并跳过该邻居；它与末节点是否到达目标分别判定。输出的 `pathCount` 则是已写数量，不提供完整所需长度。[邻居扩展](https://github.com/recastnavigation/recastnavigation/blob/6dc1667f580357e8a2154c28b7867bea7e8ad3a7/Detour/Source/DetourNavMeshQuery.cpp#L1064-L1078)、[结果组装](https://github.com/recastnavigation/recastnavigation/blob/6dc1667f580357e8a2154c28b7867bea7e8ad3a7/Detour/Source/DetourNavMeshQuery.cpp#L1147-L1204)

以下是**项目可选择的处理政策，不是 API 强制拒绝规则**：

| 本次记录 | 先决定什么 | 不要作出的替代判断 |
|---|---|---|
| `BUFFER_TOO_SMALL` | 本轮是否允许前缀；若不允许，按输出预算增加容量并重新取得结果 | 把 `pathCount` 当作下一次必定足够的精确容量，或把截断记成拓扑不可达 |
| `OUT_OF_NODES` | 是否允许资源受限的搜索结果；按搜索预算调整节点资源或降级 | 只增加输出数组就认为恢复了未探索的邻居；或认定此位必然伴随 partial |
| `PARTIAL_RESULT`，无上述容量位 | 是否保留部分路线供玩法使用，并关联本次过滤器、数据与目标 | 把一次查询结论缓存成真实世界永久不可达 |

这些位可能共存，表格不是互斥的 `else-if` 顺序。预算不足可以成为拒收或降级的理由，不应自动变成对几何的判决；增加预算也不承诺必定找到目标或改善性能。

## 一项明确而保守的完整 corridor 政策

先限定前提：同步 `findPath`；以有效容量 `0 < maxNodes <= 65535` 初始化且成功，不能只靠初始化返回值替代容量前提；起终位置分别位于所给起终 polygon 内，引用与过滤器有效；`maxPath >= 1`，实际分配的数组至少能容纳该数量。前两项容量与位置要求见[接口契约](https://github.com/recastnavigation/recastnavigation/blob/6dc1667f580357e8a2154c28b7867bea7e8ad3a7/Detour/Include/DetourNavMeshQuery.h#L162-L201)。导航数据及查询对象的生命周期还须有效，查询期间没有不受支持的并发变更。

若业务选择“本轮只接收无这三种降级标志的完整 corridor”，可以采用以下**原创逻辑表达，不是完整可编译包装器**：

```text
拒绝 failure 或非 success；保留原始 status 供诊断。
若 statusDetail(status, PARTIAL_RESULT | BUFFER_TOO_SMALL | OUT_OF_NODES)：转入降级决策。
否则，只有 0 < pathCount <= 提供的容量 且 path[pathCount-1] == endRef，才接收该 corridor。
```

合并掩码在这里有意表示“任一项出现就转出”，并非声称三项同时出现。另一项目可以允许前缀或资源受限结果，但应为其定义不同用途；不能把一个严格政策冒充所有 Detour 调用者的义务。

节点预算也应核对实际对象：固定 `init` 可复用已有较大池，传入较小 `maxNodes` 不保证缩小。[初始化分配／复用](https://github.com/recastnavigation/recastnavigation/blob/6dc1667f580357e8a2154c28b7867bea7e8ad3a7/Detour/Source/DetourNavMeshQuery.cpp#L171-L223) 本文不提供自动扩容循环或统一预算。

即使以上接收通过，也仅是该政策下的 polygon corridor：不会替调用者验证坐标位于对应 polygon 的前提，也不证明直线路径输出完整、身体碰撞可通行或玩法已到达。不涵盖 sliced 查询、Crowd、引擎分叉、动态 tile 更新或自定义成本最优性。

[既有导航证据](https://github.com/Container-R/GameLibrary/blob/1a7bf18b24ba56395892c4c0cdb3b2acecc16985/solutions/ai/navigation-readiness-and-partial-path.md)讨论不同的准备、路径与运动边界，不能替本篇提供 Detour 执行证据。本篇也不回写或升级那些实验的覆盖范围。


## 后续有限原生观察

2026-11-01，使用同一固定上游源码及手工三矩形A→B→C、默认过滤器、节点池16，仅比较maxPath2/3。实际前缀A/B对应成功与输出不足位、无partial；上限3得到A/B/C。另建副本重复相同条件；首次未审诊断构建门槛停止的记录保留。详见[输入、原始观察与回执](../../支持资料/Detour路径输出容量观察/README.md)。这里只增加该固定合法链的输出容量观察，没有运行本篇节点耗尽、动态地图、费用最优性或全部调用者政策。
