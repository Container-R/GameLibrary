---
id: SOL-AI-001
title: 导航查询的就绪边界：空路径不等于不可达，非空路径不等于到达
type: solution
status: source-backed
primary_discipline: AI
related_disciplines: [PROG, ENGINE, QA]
related_roles: [ai-programmer, gameplay-programmer, engine-programmer, qa-engineer]
related_topics: [navigation, synchronization, partial-path, negative-cache, initialization]
engines: [Godot]
versions: ["Godot 4.6 文档：NavigationServer2D 为 Experimental", "Godot 4.6.3.stable.official.7d41c59c4 实际运行"]
platforms: [PC]
updated_at: 2026-10-31
verification_method: 官方同步与API资料核对；原创CPU无头导航图实际查询及默认异步region诊断；未测试角色移动或持续并发更新
sources:
  - https://docs.godotengine.org/en/4.6/classes/class_navigationserver2d.html
  - https://docs.godotengine.org/en/4.6/tutorials/navigation/navigation_using_navigationservers.html
  - https://docs.godotengine.org/en/4.6/classes/class_navigationpolygon.html
  - https://docs.godotengine.org/en/4.6/tutorials/navigation/navigation_using_navigationpaths.html
---

# 导航查询的就绪边界：空路径不等于不可达，非空路径不等于到达

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

“路径规划可达”和“角色移动已到达”也要分开：本研究没有移动任何角色。目标可能投影到导航表面时，分别记录原目标、投影目标和最终路径末点。1e-4是本微型几何的数值判据，不是所有游戏应采用的到达半径。

否定缓存应关联数据身份/版本与查询条件；拓扑、层或相关代理配置改变后使旧结论失效。iteration可能回绕，也不是跨进程稳定身份，不宜直接作为永远递增的持久版本。何时重试需要预算和玩法策略；本夹具没有测量查询性能，不能由“可以重查”推出每帧对所有AI无上限重查。

## 5. 不用强制更新掩盖生命周期问题

在4.6文档中`map_force_update`已标Deprecated，并说明与异步更新不兼容；不应把旧版示例中的强制更新当作默认启动补丁。[S1] 本实验没有调用它，也没有固定sleep来保证时序。

本轮同步超时看门狗只判“未能建立就绪条件”，不会返回“目标不可达”。生产应明确谁提交导航数据、谁确认本轮完成、查询绑定哪个快照，以及变更期间AI保持什么安全状态。图形化场景节点、直接服务器RID与后台烘焙的生命周期不应凭名字相似而互换。

## 验证范围与来源

实际环境：2026-10-31，Godot`4.6.3.stable.official.7d41c59c4`，Linux x86_64，Python3.12.14；源码/二进制摘要、几何、调用命令、完整stdout/stderr、主对照与诊断见夹具档案。官方4.6将NavigationServer2D和NavigationPolygon标为Experimental；不保证未来版本接口不变。

未覆盖持续多批并发、异步烘焙、流式地图、RVO、角色碰撞/半径侵蚀、3D、跨平台/版本、寻路预算或运行性能。手工凸多边形消除了烘焙变量，不等于验证了完整地图制作流程。文章保留`source-backed`，只有明确记录的有限引擎结果实际执行。

- [S1] [NavigationServer2D](https://docs.godotengine.org/en/4.6/classes/class_navigationserver2d.html)：同步说明、map/region iteration、查询、最近点、连接与force_update状态。
- [S2] [Using NavigationServer](https://docs.godotengine.org/en/4.6/tutorials/navigation/navigation_using_navigationservers.html)：Threading and Synchronization / Waiting for synchronization。
- [S3] [NavigationPolygon](https://docs.godotengine.org/en/4.6/classes/class_navigationpolygon.html)：顶点与凸多边形输入。
- [S4] [Using NavigationPaths](https://docs.godotengine.org/en/4.6/tutorials/navigation/navigation_using_navigationpaths.html)：地图与路径查询。具体部分路径坐标来自本实验，不是文档对任意地图的输出承诺。

来源访问2026-10-31；代码和几何原创，无第三方实现复制。关联[固定规则与表现边界](../programming/fixed-step-simulation-boundary.md)：不同系统的“下一次更新”不能自动合并成同一个业务就绪时刻。
