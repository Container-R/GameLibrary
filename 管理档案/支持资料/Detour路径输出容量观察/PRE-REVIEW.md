# Detour 输出容量：独立执行前审查

2026-11-01。结论：**三 quad 数组与 oracle 接受；协议须先明确初始化失败退出策略，再进入实现审查。不授权构建或执行。** 两行 oracle 有固定源码支持。权重六 quad 已明确排除，不能把本单元用于其费用解释。下面的失败退出要求须在实现中落实；尚不存在可接受的 fixture/runner 结果。

## 实际阅读与绑定

完整读 GATE、PROTOCOL 及当前已发表支持《Detour findPath：成功搜索与完整输出，是两项接收条件》。审查绑定：

- `GATE.md`：`12414846159aed496841162e3a351dcb9cc1960598ec61dc932105f9a93aa6a6`。
- 同目录 `PROTOCOL.md`：`a653bdbc9a885cc4017856003b0d263908ed2d7a2509f8f14ebe2cbf1e4e664c`。第一次读后作者明确补齐 links 有界遍历和未执行 case 表示；本结论绑定该最终文本，不是先前 a8813 版本。
- stage `管理档案/研究记录/source-notes/detour-findpath-status-and-capacity.md`：`9bdb2a4659b2c34fd2a87bb04f5a2e6c075b3340415cc0e57e5efd54f69044af`。
- `SOURCE-MANIFEST.json`：`0cfadaf8b16ebfc537259734b752f75a3baeac2186245d30191c6fe35d76c9ea`。独立以文件字节重算 16 项 SHA256 和 Git blob SHA1，全部与清单相符。这是本地身份核对，不是假称另行下载验证官方树。

实际读固定官方提交 `6dc1667f580357e8a2154c28b7867bea7e8ad3a7` 的本地原样源码：

- `DetourNavMeshBuilder.h` 创建参数与接口说明；`DetourNavMeshBuilder.cpp` 268–315、350–450、480–560、590–630：输入、分配、坐标、邻接及缺省 detail。
- `DetourNavMesh.cpp` 180–287、524–558、900–1040：构造/析构、初始化、内部链接、addTile 所有权。
- `DetourNavMeshQuery.h` 162–203；`DetourNavMeshQuery.cpp` 35–90、150–223、973–1204、2330–2365：默认 filter、初始化、搜索与父链回写、门户中点。
- `DetourStatus.h` 全文。

以上为源代码阅读和纸面分析；仅额外执行文件哈希核对，没有编译器调用、原生查询、模拟模型或网络运行。

## 几何、邻接与字面预期

A 的 XZ 投影顺序 (0,0)→(0,1)→(1,1)→(1,0)，B/C 为相同平移；三个凸单位 quad 均非退化，从 +Y 法线看方向一致。A 的边 2 是 5→1，与 B 的边 0（1→5）反向共边；B 的边 2（6→2）与 C 的边 0（2→6）同理。start/end 在各自 polygon 内部，不依赖最近点投影。

输入邻接 0/1/2 是零基索引；builder 对内部边加 1，0xffff 的低位方向 0xf 成为墙。由此 neis 正是 A[0,0,2,0]、B[1,0,3,0]、C[2,0,0,0]。内部链接再减 1 组装 ref。12 条总边、无 portal/offmesh，源码分配的 link 容量足以承载四条有向链接；实际生成后仍须核完整内容，不能仅靠这项推导跳过 setup。

独立纸面 oracle（不是运行结果）：

| 顺序 | maxPath | pathCount | 三槽符号值 | 精确 status |
|---|---:|---:|---|---|
| 1 | 2 | 2 | A、B、0 | 0x40000010 |
| 2 | 3 | 3 | A、B、C | 0x40000000 |

两次均无 FAILURE、IN_PROGRESS、PARTIAL_RESULT、OUT_OF_NODES；第一次有 BUFFER_TOO_SMALL。搜索节点仅需要 A/B/C，首次新建的 maxNodes=16 足够；单链没有路线选择平局。目标出堆后 lastBestNode 为 C，父链长度 3；maxPath2 回退至 B 后按起点方向写两槽，仅设置输出不足位。不能把 `dtStatusSucceed` 或合并 detail 掩码的“任一位”检查代替精确状态。

返回引用必须绑定本次实际 mesh 的有效、互异、非零 A/B/C。协议不预设平台 ref 编码数值。第三槽零哨兵仅观察该槽未被改写，不证明数组外绝无写入。两 case 是两次实际 findPath，不是两次 query.init，也不等于两张网格或节点预算实验。

## 生命周期与必须落实的失败约束

正常路径可接受：builder 分配 data；单 tile init 成功后由 mesh 持有 DT_TILE_FREE_DATA；query 的生命周期短于 mesh；两次 findPath 自行清空内部节点池和 open list；最终不得手动重复释放 tile data。

**实现审查必须特别检查初始化失败退出，而不是笼统套用 RAII。** 当前源码 `dtNavMesh::init(params)` 先设置 m_maxTiles，之后分配 m_tiles/m_posLookup，再 memset；析构按 m_maxTiles 访问 m_tiles[i]。若第一分配失败，或第二分配失败发生于 tiles 清零前，不能据成功路径推出失败对象可安全析构。query 初始化的 placement-new 分配同样不是本单元认证的 OOM 安全保证。

因此若初始化失败或所有权/对象状态不确定，须先输出并刷新首错，采用不会继续访问或析构不确定对象的非零进程终止路径；不能返回时隐式触发同样危险的栈对象析构。具体实现待代码审查，不在这里提供未经检查的包装器。此要求不是新增 OOM 注入测试，也不授权改上游分配器或源码。协议现有“保留观察、所有权不确定停止”方向正确，但须在协议中先明确上述具体退出策略，不能只留待实现自行解释。

runner/consumer 后续还须核：实际调用计数不是写死成功摘要；第一 case 不符不执行第二 case；计数或 setup 缺失不能补预期；未执行 case 不得伪装成零状态；有界 links 读取得先检查索引再解引用。构建非零、未审查诊断、超时、输出缺失/损坏均停止并保存首错，不自动换旗标/地图/oracle 重跑。

## 接受范围与下一门槛

认可的只是一个合法固定网格、一次 query.init(16)、最多两次同步 findPath 的预期和记录协议。当前已确认原生查询数为零。后续先冻结 fixture、consumer、独立字面预期、runner 及完整编译 argv，审查失败退出和纯合成拒绝用例，之后由主编单独授权。没有节点耗尽、动态拓扑、真实烘焙、身体移动、性能、并发或所有缓冲安全的保证。

## 有限修订闭合

随后实际比较 `history/PROTOCOL-before-failure-policy.md` 与新 `PROTOCOL.md`，后者 SHA256 为 `a9a385b58b3adc60ccc8f460e937083ee34348c142c6f7f5c9d4409f157c1406`。变化仅为正常成功清理与初始化/不确定失败的退出策略，以及对应修订记录；几何数组、邻接、两查询顺序和 oracle 未变。

新协议明确 builder/任一 init 失败或对象状态不确定时先记录并 flush、非零结束隔离进程、不让返回路径自动析构可疑部分对象；正常全部成功才 query→nav 释放。它同时排除了 OOM 注入及生产修复保证。**前述必要协议修正已闭合，接受该版本进入 fixture/consumer/runner 实现审查。** 未授权或执行构建、查询；本报告不能替代下一轮代码与执行授权。


公开归档说明：已将早期研究副本的目录前缀归一化；这些历史定位不表示本归档附带原执行目录。可复现输入与实际观察以README映射为准，技术结果未改，本文件不是原审查原字节副本。
