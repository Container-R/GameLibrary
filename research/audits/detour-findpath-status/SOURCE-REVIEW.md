# TASK129 独立固定源码审查

2026-11-01。**接受同步 findPath 的状态/容量机制，未发现阻断项。** 门稿 SHA256：`90a0b458a4da523e6e2126268ec6491015ed7d89109c9704db49d1db444fdaec`。目标仅新增 `research/source-notes/detour-findpath-status-and-capacity.md`，不改已有导航文件。

## 独立打开的来源

官方 `recastnavigation/recastnavigation` 的 annotated tag `v1.6.0`，tag 对象 `b4554541b658630816dba41466eb1cefb624519e`，解引用到固定提交 `6dc1667f580357e8a2154c28b7867bea7e8ad3a7`。不称当前最新版。

- [DetourStatus.h](https://github.com/recastnavigation/recastnavigation/blob/6dc1667f580357e8a2154c28b7867bea7e8ad3a7/Detour/Include/DetourStatus.h#L22-L63)：22–63。
- [DetourNavMeshQuery.cpp](https://github.com/recastnavigation/recastnavigation/blob/6dc1667f580357e8a2154c28b7867bea7e8ad3a7/Detour/Source/DetourNavMeshQuery.cpp#L973-L1204)：完整同步 `findPath` 与 `getPathToNode` 973–1204；另读 `init` 171–223。
- [DetourNode.cpp](https://github.com/recastnavigation/recastnavigation/blob/6dc1667f580357e8a2154c28b7867bea7e8ad3a7/Detour/Source/DetourNode.cpp#L121-L151)：`getNode` 121–151。此处是 Source 下的 cpp，不是同名 Include 头文件的相同行号。

## 决定性检查

1. **A→B→C、maxPath=2 的手工追踪正确。** 父链长度3，从 C 沿父链先退至 B，随后写 `path[1]=B`、`path[0]=A`，`pathCount=2`。输出不是 B,C。若最佳节点已是 endRef=C，截断带来 BUFFER_TOO_SMALL，却不由此产生 PARTIAL_RESULT。以上是条件明确的源码推演，不是网格或返回值观测。
2. 成功位与细节位共存；成功检测只查成功位。细节掩码判断是任一命中，不是所列位全部同时存在。正文若采用三个排除位的组合，应写清“任一存在即不满足该保守政策”。
3. OUT_OF_NODES 与最佳节点是否到达 endRef 分别判断；前者不是 partial 的同义词。已有节点仍可在池满时返回，失败针对需要新分配的节点。不能把资源受限标记改写为永久几何不可达，也不能用扩大输出数组替代扩展搜索资源。
4. `pathCount` 是实际写出数量，不是完整所需容量；`init` 可复用较大池，较小参数不证明缩池。追加重试只是有预算的应用选择，不保证下一次成功或性能改进。

## 接收政策边界

建议的“成功、无三种降级位、非空、末 ref 等于 endRef”可作为应用要求完整且未受这些容量限制的保守政策，不是所有 Detour 用途的强制规则。它不证明最佳成本、具体坐标合法归属、角色体积/物理通行、straight-path 结果或业务到达。应保留初始化使用文档允许的节点容量且成功、有效引用/位置配对、过滤器和导航数据寿命，以及无不受支持并发变更的前提。

政策可以拒绝一个已找到 endRef 但出现 OUT_OF_NODES 的结果；这属于有意的保守取舍，不能误报为引擎失败。反之，缺少 PARTIAL_RESULT 并不足以接收完整输出，正是本项相对既有部分路径讨论的新机制。

本轮没有编译、调用查询、制作网格或读取运行档案。没有独立审查 sliced 查询、Crowd、引擎分叉或动态 tile 协议；不能继承其他导航材料的运行结果。无远端或既有导航正文改动。

补充独立读取同提交 `DetourNavMeshQuery.h` 162–201：初始化节点容量要求 `0 < maxNodes <= 65535`，位置须在对应 polygon 内，输出容量至少1。不能仅凭 init 中出现的上界检查，把任意零容量视为有效前提。
