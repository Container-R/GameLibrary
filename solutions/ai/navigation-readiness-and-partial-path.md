---
id: SOL-AI-001
title: 导航查询的就绪边界：空路径不等于不可达，非空路径不等于到达
type: solution
status: source-backed
primary_discipline: AI
related_disciplines: [PROG, ENGINE, QA]
related_roles: [ai-programmer, gameplay-programmer, engine-programmer, qa-engineer]
related_topics: [navigation, synchronization, partial-path, negative-cache, initialization, navigation-clearance, agent-radius, physics-overlap, path-consumption, target-arrival]
engines: [Godot]
versions: ["Godot 4.6 文档：NavigationServer2D 为 Experimental", "Godot 4.6.3.stable.official.7d41c59c4 本地程序自报；发行与源码对应未确认"]
platforms: [PC]
updated_at: 2026-11-01
verification_method: 官方资料与固定源码核对；既有导航同步、烘焙半径及静止重叠证据；新增作者与独立各一次两agent受控Node3D位置赋值、实际路径结束与目标到达信号观察；未测试角色碰撞移动或持续并发更新
sources:
  - https://docs.godotengine.org/en/4.6/classes/class_navigationmesh.html
  - https://docs.godotengine.org/en/4.6/classes/class_navigationagent3d.html
  - https://docs.godotengine.org/en/4.6/classes/class_physicsdirectspacestate3d.html
  - https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/navigation_3d/3d/nav_mesh_generator_3d.cpp
  - https://docs.godotengine.org/en/4.6/classes/class_navigationserver2d.html
  - https://docs.godotengine.org/en/4.6/tutorials/navigation/navigation_using_navigationservers.html
  - https://docs.godotengine.org/en/4.6/classes/class_navigationpolygon.html
  - https://docs.godotengine.org/en/4.6/tutorials/navigation/navigation_using_navigationpaths.html
---

# 导航查询的就绪边界：空路径不等于不可达，非空路径不等于到达

> **运行身份说明（2026-10-31）：** 下述 Godot 版本为已安装程序自报，不代表已认证官方发行包或精确源码身份。[共享取证与缺口](../../research/source-notes/godot-runtime-provenance.md)保留原始版本、文件摘要及公共标签查询差异；各次有限行为观察仍按实际归档字段解释。

## 一个常见的错误决策链

AI生成后立即查询路径，拿到空数组，于是缓存“目标不可达”并永久换状态。几帧后导航数据实际可用了，AI却不再重试。另一个方向的错误是：只要路径非空就宣布目标可达，结果角色停在断开区域的边缘，却仍执行远处目标的到达逻辑。

这两个问题分别混淆了**数据就绪与几何结论**、**有可走路径与到达原目标**。本文用Godot4.6.3的实际NavigationServer2D查询建立有限证据，给出应用层决策契约。不是完整导航AI、通用并发屏障或角色运动方案。

## 1. 先明确哪个对象同步了

Godot4.6官方说明导航服务器的多数变更在后续物理帧同步而非立即生效；map与region各有iteration ID，0表示该对象从未同步，ID达到范围上限会回到1。[S1] `map_changed`只报告对应地图变化，不携带项目的业务事务标识。

因此不能把以下概念混为一谈：提交了设置调用、getter已经显示新值、地图登记了region、region几何已同步、本次查询使用了自己期望的完整数据批次。API使用异步内部工作时，某个map iteration非0不足以证明全部相关region已准备好。

[实际夹具](../../research/experiments/godot-navigation-sync/README.md)采用一个独立RID地图、单写者、一次初始化批次、手工已完成的凸多边形，不引入烘焙。主对照明确关闭map与region的异步iteration，并启用region及层1。就绪谓词核对本map的信号、非0且已变化的map iteration、两个登记region及各自非0 iteration；最终另核对所属map、enabled、layers与async实际值。它不是“随便等一帧”。

该谓词只在声明的单批前提下使用。持续多写者、后台烘焙或流式更新时，需要应用层数据版本/批次归属；收到任意信号或iteration发生变化不等于“我的更新全部可查”。重复设置相同值也不保证产生新iteration，不能盲目等待。

## 2. 可复现的三种实际结果

原始几何：主区域为`[0,30]×[0,10]`，断开区域为`[100,110]×[0,10]`，边连接margin0.1，无NavigationLink。起点S=(5,5)，同区目标R=(25,5)，断开目标D=(105,5)。查询层掩码1。

| 实际查询 | 已观察的数据状态 | 实际路径 | 能推出什么 |
|---|---|---|---|
| 初始化同段立即S→R | map iteration0，region尚未登记到读视图 | 空 | 本次数据未就绪，不能永久缓存几何不可达 |
| 主对照就绪后S→R | map和region均已同步 | `(5,5)→(25,5)` | 路径末点到达该目标 |
| 同一就绪图S→D | D在另一实际region表面 | `(5,5)→(30,5)` | 非空部分路径，未到达D |

独立Python判据读取实际`map_get_path`坐标，检查有限数值、起点、可达终点和部分路径末点；通过最近点及所属region确认D确实位于第二块导航表面，不把“目标在图外”混入断开控制。region连接数与link数量也实际记录。没有用自制A*或Python期望数组冒充引擎返回值。

过早查询没有在这份二进制上产生stderr诊断；不能虚构一条引擎错误来证明它发生。更直接的观察是：同段提交async=false和margin0.1后，getter仍显示true和1.0；就绪后才显示指定值。日志区分`requested_config`与实际getter，证明发出请求不等于设置已经可见。

## 3. 一次真实失败使就绪条件变得更严格

初版仅等待map信号/iteration和两个region登记，却得到空的“可达路径”；没有把这次探测当作成功验证。最初修正同时增加region配置与iteration检查，涉及多个条件，不能直接归因于某一个默认值。

随后增加单独的默认region诊断：保留默认region配置，只补充实际getter与region就绪观察。此次真实记录出现 **map iteration=1而region iteration=0**；region enabled=true、async=true。继续按条件等待后，map到2、region到1，可达与部分路径均出现。这样才有证据区分“地图已同步一次”与“相关region几何已同步”，而不是靠关异步掩盖问题。

这个中间状态出现次数依赖调度。诊断runner不要求每次重跑都观察同样次数，甚至不要求一定抓住该短暂阶段；最终就绪及路径判据仍必须成立。历史初版源码/结果、主对照和诊断分别归档，不能把不同版本结果拼成同一运行。

## 4. 应用层状态与缓存契约

下面是原创建议，不是引擎内置枚举：

| 状态 | 进入条件 | 应做的事 |
|---|---|---|
| `pending_navigation` | 相关输入、烘焙或同步未满足本轮就绪条件 | 等待/回退；不创建长期不可达缓存 |
| `query_complete_reachable` | 匹配数据版本的查询完成，末点满足目标容差 | 允许进入路径跟随；仍未证明角色实际已到达 |
| `query_complete_target_not_reached` | 查询完成，但没有符合原目标的末点 | 根据玩法选择换目标、停在可达边缘或反馈失败 |
| `navigation_error` | 无效句柄、数据错误、引擎异常或同步超时 | 诊断并恢复；不能解释成几何不可达 |

“路径规划可达”和“角色移动已到达”也要分开：此前查询夹具没有移动任何角色。目标可能投影到导航表面时，分别记录原目标、投影目标和最终路径末点。1e-4是本微型几何的数值判据，不是所有游戏应采用的到达半径。

否定缓存应关联数据身份/版本与查询条件；拓扑、层或相关代理配置改变后使旧结论失效。iteration可能回绕，也不是跨进程稳定身份，不宜直接作为永远递增的持久版本。何时重试需要预算和玩法策略；本夹具没有测量查询性能，不能由“可以重查”推出每帧对所有AI无上限重查。

## 5. 不用强制更新掩盖生命周期问题

在4.6文档中`map_force_update`已标Deprecated，并说明与异步更新不兼容；不应把旧版示例中的强制更新当作默认启动补丁。[S1] 本实验没有调用它，也没有固定sleep来保证时序。

本轮同步超时看门狗只判“未能建立就绪条件”，不会返回“目标不可达”。生产应明确谁提交导航数据、谁确认本轮完成、查询绑定哪个快照，以及变更期间AI保持什么安全状态。图形化场景节点、直接服务器RID与后台烘焙的生命周期不应凭名字相似而互换。

## 6. 体型交接补充：路径可查，不等于碰撞形状放得下

就绪之后仍有另一道边界：**导航图为多大的身体留出了空间？** `NavigationMesh.agent_radius`、`NavigationAgent3D.radius` 与实际物理形状不是同一个参数的三个别名。

| 契约 | 控制什么 | 不能替代什么 |
|---|---|---|
| 烘焙半径 | 生成导航网格时侵蚀可行走区域 | 运行时碰撞形状、动态避让输出 |
| NavigationAgent3D.radius | 避让代理的体积参数 | 重新烘焙、普通路径查询的体型筛选 |
| Shape3D 与变换/层 | 物理查询或碰撞中的实际形状 | 可行走拓扑、角色运动与到达逻辑 |

Godot 4.6 [NavigationMesh 文档](https://docs.godotengine.org/en/4.6/classes/class_navigationmesh.html#class-navigationmesh-property-agent-radius)明确烘焙半径用于侵蚀，并向上取整到 cell_size 的倍数；[NavigationAgent3D 文档](https://docs.godotengine.org/en/4.6/classes/class_navigationagent3d.html#class-navigationagent3d-property-radius)明确 agent radius 不改变普通寻路，支持不同体型应使用相应烘焙数据/地图。[固定源码](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/navigation/navigation_agent_3d.cpp#L607-L615)的 setter 转发到 agent_set_radius，而[烘焙器](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/navigation_3d/3d/nav_mesh_generator_3d.cpp#L353-L372)将另一项 agent_radius 转成体素半径，再用于[侵蚀](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/navigation_3d/3d/nav_mesh_generator_3d.cpp#L461-L482)。这是来源分析，不认证本地二进制来源。

### 两次实际烘焙，四条实际 agent 路径

[原创 3D 无头夹具](../../research/experiments/godot-navigation-radius/README.md)使用 y=0 的六个地面三角形：两个宽房间通过 x∈[-2,2]、z∈[-1,1] 的窄桥相连。输入为 Godot 要求的 clockwise 面序；`add_faces` 的[固定实现](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/resources/3d/navigation_mesh_source_geometry_data_3d.cpp#L180-L193)反转索引，原始解析数组实际核对为 +Y 法线。这一约定在运行前已明确，不是失败后倒置面序来凑结果。

两个新进程只改变烘焙半径，其余几何和显式烘焙参数相同，cell_size / cell_height 均为 0.1。每个进程创建两个不同 radius 的 NavigationAgent3D；**avoidance_enabled 都为 false**。父节点不移动，通过 agent 自己的路径更新/getter 获取结果，不把直接 map 查询冒充 agent 行为。

| 实际烘焙半径 | Agent radius | 实际路径末点 | 解释 |
|---:|---:|---|---|
| 0.2 | 0.2 | 到达右房间目标 x≈4 | 此图提供通路 |
| 0.2 | 1.2 | 与上一条路径相同 | 只扩大避让半径未收窄此图 |
| 1.2 | 0.2 | 非空部分路径，x=-2.5 | 本次路径未通向右房间 |
| 1.2 | 1.2 | 与上一条部分路径相同 | 决定通路的是本次烘焙结果 |

起点/目标实际投影到 `(-4,≈0.2,0)` / `(4,≈0.2,0)`；体素化后的 Y 没有被重写成输入的 0。大半径案例的目标仍投影在保留下来的右房间，不能把结果误解为目标落在所有导航数据之外。两份生成网格在 agent 创建/设置前后均保持相同顶点和多边形记录。多边形数量是观察值，不是通用验收常数。

每轮先确认烘焙回调与非空网格，再等待本地图信号、非零且变化的 map iteration、非零 region iteration，并核对所属地图/层/启用状态。两者使用显式同步 iteration、单写者的一次初始化；240 个物理回调的看门狗只用于失败退出，不意味着等待固定帧数总能就绪。没有 force_update 或 sleep。路径末点容差 0.01 是此样例判据，不是通用角色到达阈值。

### 另一个实际系统给出不同答案：静止形状重叠

物理场景另建两面墙，位于窄桥两侧 z∈[1,4] 与 [-4,-1]、x∈[-2,2]、y∈[0,4]。**烘焙输入只有地面三角形，墙的 collider 没有被解析进烘焙；桥边的自由边界侵蚀形成导航间隙。** 两套输入的 XZ 边界对齐，但来源不同，不能说本实验验证了 collider 自动参与烘焙。

实际 `intersect_shape` 在 `(0,1.5,0)` 查询：半径 0.2 的球不与墙重叠，半径 1.2 的球与两面墙都重叠。另把小球放在正侧墙内作为正对照，确实命中该墙，避免把尚未同步的空物理空间当作“没有碰撞”。日志保留实际 collider 身份、shape index、墙尺寸/变换/层；查询代码显式设置 margin=0，但没有另记运行时 margin getter。

球心 Y=1.5 是显式的身体形状中心，不等于导航表面 Y≈0.2；比较的是同一通道的 XZ 容纳关系。没有角色真正沿路径走到这里，也没有执行碰撞响应。依据 [PhysicsDirectSpaceState3D 文档](https://docs.godotengine.org/en/4.6/classes/class_physicsdirectspacestate3d.html#class-physicsdirectspacestate3d-method-intersect-shape)，此 API 检查静止重叠且忽略 motion。因此这证明大球在所查位置与墙相交，不证明小球整条路线安全，也不是 capsule、台阶、旋转、地板接触或移动 sweep 的测试。

### 应用验收应按体型与阶段分账

以下为原创工程建议：

1. 为角色配置记录烘焙档位、导航地图/层、避让 radius、真实碰撞形状及缩放/中心偏移，不把一个编辑器字段当作全部体型信息。
2. 在地图制作/体型调整后，用代表性的狭窄连接做实际烘焙与路径末点验收；数据未就绪与图上无通路仍按前文分开处理。
3. 对同一空间另做真实物理形状查询或角色运动测试；静止重叠、连续运动、地形跟随和实际到达是不同验收层级。
4. 若启用避让，另记录请求 velocity 与实际 `velocity_computed`，并验证应用怎样移动身体；本例未运行 RVO，不能据此声称调大 radius 会自动避免墙体碰撞或改变通路。
5. 多体型导航图增加烘焙、存储和版本一致性成本；共享图或分档必须显式接受其取舍。本例没有测量这些成本，不推荐无限细分，也不提供“一次烘焙适合所有身体”的承诺。

[独立复验](../../research/experiments/godot-navigation-radius/review/REVIEW.md)重跑两次实际烘焙/四条路径，另用独立字面判据核对输入几何、绕序、就绪状态及真实重叠结果。三个合成启动失败案例均拒绝旧 PASS，它们启动了零个 Godot 进程，不是新增导航案例。runner 记录启动时源码摘要，不强制匹配预存冻结摘要，也不在结束时再次哈希；审查仍须关联保存的源码、运行记录与当前 invocation。

本次仍使用既有字节身份的已安装 Godot 程序，官方标签与自报源码身份的对应仍[未认证](../../research/source-notes/godot-runtime-provenance.md)。上述 4.6 文档访问于 2026-10-31，导航类标为 Experimental。有限证据覆盖实际烘焙、agent 路径及静止重叠，不覆盖 RVO 输出、角色移动、并发更新、GPU、跨构建或性能；不能把本节有限新增覆盖扩写成通用导航/物理一致性保证。

## 验证范围与来源

实际环境：2026-10-31，Godot`4.6.3.stable.official.7d41c59c4`，Linux x86_64，Python3.12.14；源码/二进制摘要、几何、调用命令、完整stdout/stderr、主对照与诊断见夹具档案。官方4.6将NavigationServer2D和NavigationPolygon标为Experimental；不保证未来版本接口不变。

前文第 1–5 节的 2D 手工凸多边形实验消除了烘焙变量，不覆盖 3D、半径侵蚀或物理形状。第 6 节另有实际 3D 烘焙、agent 路径和静止形状重叠证据；两组均未覆盖持续多批并发、异步烘焙、流式地图、RVO 输出、角色移动/碰撞响应、跨平台/版本、寻路预算或运行性能，也不等于验证完整地图制作流程。文章保留`source-backed`，只有明确记录的有限引擎结果实际执行。

- [S1] [NavigationServer2D](https://docs.godotengine.org/en/4.6/classes/class_navigationserver2d.html)：同步说明、map/region iteration、查询、最近点、连接与force_update状态。
- [S2] [Using NavigationServer](https://docs.godotengine.org/en/4.6/tutorials/navigation/navigation_using_navigationservers.html)：Threading and Synchronization / Waiting for synchronization。
- [S3] [NavigationPolygon](https://docs.godotengine.org/en/4.6/classes/class_navigationpolygon.html)：顶点与凸多边形输入。
- [S4] [Using NavigationPaths](https://docs.godotengine.org/en/4.6/tutorials/navigation/navigation_using_navigationpaths.html)：地图与路径查询。具体部分路径坐标来自本实验，不是文档对任意地图的输出承诺。

来源访问2026-10-31；代码和几何原创，无第三方实现复制。关联[固定规则与表现边界](../programming/fixed-step-simulation-boundary.md)：不同系统的“下一次更新”不能自动合并成同一个业务就绪时刻。

## 7. 跟随阶段补充：navigation_finished 不等于原目标已经到达

前面的两组实验检验了查询结果、烘焙间隙与静止重叠，父节点没有沿路径前进。这里另用本机自报 Godot 4.6.3 的程序，实际推进两个 NavigationAgent3D 的路径跟随状态，检验**耗尽当前可走路径**和**到达请求目标**之间的区别。新增结果不把旧查询实验升级成角色移动测试。

Godot 4.6 [navigation_finished / target_reached 文档](https://docs.godotengine.org/en/4.6/classes/class_navigationagent3d.html#class-navigationagent3d-signal-navigation-finished)区分这两个信号。[固定比较源码](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/navigation/navigation_agent_3d.cpp#L866-L879)先检查父节点是否进入目标距离，否则推进路径点，并允许在不可达路线的最后一点结束导航。因此，业务把所有 `navigation_finished` 都接到“任务成功”，在部分路径场景中可能作出错误决定；有些玩法有意允许停在可达边缘，则应明确记录这种成功语义，而不是混用信号名称。

### 同一地图，两种真正完成的路径状态

[新夹具](../../research/experiments/godot-navigation-completion/README.md)建立两块原始平面凸区域：XZ `[0,10]×[0,4]` 与 `[20,30]×[0,4]`，没有连接、烘焙或碰撞体。两个独立 Node3D 父节点都从 `(2,0,2)` 开始，各带一个关闭避让的 agent；目标分别为 `(8,0,2)` 与 `(22,0,2)`。查询前核对地图/区域就绪、配置和目标所属区域，确认第二个目标确实在断开的导航表面上。

驱动器按实际 `get_next_path_position()` 返回点，每次把父节点向前赋值最多 0.5 单位，直到 agent 发出结束信号。它没有直接把父节点放到请求目标，也没有用自制路径代替引擎路径。实际结果如下：

| 路线 | 实际路径末点 / 最终父节点位置 | 位置赋值次数 | 到达与结束信号 | 最终 getter |
|---|---|---:|---|---|
| 同区域目标 x=8 | `(8,0,2)` | 12 | 第 13 次驱动回调先 target_reached，后 navigation_finished | reached=true，finished=true，reachable=true |
| 断开目标 x=22 | `(10,0,2)` | 16 | 第 17 次驱动回调只有 navigation_finished；窗口内没有 target_reached | reached=false，finished=true，reachable=false |

第二个父节点距原目标仍有 12 单位，但导航确实已结束。一个仅监听 finish 的应用会把两个结果都当成到达；保留目标语义的应用可把第二个结果交给换目标、等待通路或“已到可达边缘”的分支。这是从实际结果导出的原创建议，不是额外执行了游戏任务逻辑。

路径起点的实际坐标约为 `(1.99999988079071,0,1.99999988079071)`，并非理想输入的精确 `(2,0,2)`；它通过预先冻结的 1e-5 几何容差，原始值未被吸附后重写。两项距离阈值都显式为 0.1。具体步数来自本次固定步长驱动，不能换算为真实角色速度、网络时延或导航性能。

### 观察顺序也是合同的一部分

这次使用 `SceneTree.physics_frame` 信号回调，发生于节点物理处理之前；它不是“物理步骤已经完成”的证据。每个活动 agent 依次调用 `get_next_path_position`、`is_navigation_finished`、`is_target_reachable`、`get_final_position`，**四个都可能更新内部导航状态**。两者所有查询完成后才赋值父节点位置；移动后直到下一回调都不再查询。

信号处理器只记录身份、位置、阶段和顺序，不调用这些更新方法，也不改目标或位置。结束信号形成锁存后，驱动不再移动该父节点。这样可以分清“哪个位置被本次查询采样”与“下一步即将写入的位置”，不依赖“同帧重复 getter 一定无操作”的假设。正式游戏不必照搬四次调用；这是本夹具为了可核对证据而声明的有限调用序列。

### 应用交接应保留三个结果

以下是原创验收建议：

1. **规划结果**：原目标、路径最终点、可达判定和所用地图版本，不能只交一个非空路径数组。
2. **跟随结束原因**：目标距离满足、当前路径耗尽，或由应用取消/失败；后两类不能冒充前一类。本次只验证前两种，不验证取消竞态。
3. **真实身体与业务到达**：如果角色由 CharacterBody3D、根运动或网络状态推进，再单独验证碰撞、被阻挡、动画及业务触发条件。这里没有碰撞移动，不能声称整条路线物理安全或已经完成任务。

项目还要付出保存目标身份、阶段记录与独立运动验收的成本。若产品明确接受部分完成，应把它作为可审查的规则，而不是靠放大到达距离把断开的目标“吞进去”。

### 新证据边界

作者与独立审阅者分别重复同一有限序列：合计 **2 个行为进程 + 2 个版本查询，共 4 个 Godot 进程**，不是 4 种不同条件；每轮都是上述 2 条路线。独立重复同样观察到 337 个事件、17 次驱动回调与 12/16 次位置赋值。静态 consumer 从原始事件重建步进、信号与数组关联，不只信任子进程结论。运行前的合成记录曾暴露帧顺序及嵌套 bool/int 验收漏洞，已保留初稿与修正；它们不是导航引擎失败或新的移动场景。

新结果仅覆盖受控 Node3D 位置更新下的 agent 状态/信号，不覆盖 CharacterBody3D、碰撞响应、RVO、取消/重规划、动态地图、性能或跨构建稳定性。安装字节与官方源码的对应仍[未认证](../../research/source-notes/godot-runtime-provenance.md)。[来源说明](../../research/source-notes/navigation-agent-completion.md)分开记录文档、源码预期与实际有限观察。
