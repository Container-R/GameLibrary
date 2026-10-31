# 启动寻路：空路径不是不可达证明，非空路径也不是到达证明

原创CPU/headless Godot4.6.3夹具。目标是给AI导航决策建立明确的三种状态：导航数据尚未就绪、已完成查询且到达目标、已完成查询但只得到部分路径。没有角色移动、RVO、碰撞、渲染或资产烘焙。

## 运行与证据

```sh
python run.py
```

运行器分别启动naive和guarded两个真实引擎进程，独立Python判据读取实际`NavigationServer2D.map_get_path`结果。版本、平台、Python版本、引擎/四份源文件SHA-256记录在`results/summary.json`；每次调用命令与隔离HOME/XDG记录在`*-command.json`。stdout/stderr分开完整归档。

实测2026-10-31，Godot`4.6.3.stable.official.7d41c59c4`，Linux x86_64，Python3.12.14。禁止-O；已保存实际拒绝记录。每次先删除旧成功summary，超时、非零退出、stderr、ERROR或oracle不匹配均失败。**本安装版本的过早查询没有产生stderr诊断**；不虚构预期错误，也没有任何吞错白名单。

## 一个地图、两个区域、三个查询

手工构造凸多边形，不调用烘焙：

- 主矩形`[0,30]×[0,10]`，起点S=(5,5)，可达目标R=(25,5)。
- 断开矩形`[100,110]×[0,10]`，目标D=(105,5)。间隔70，明确连接margin0.1，没有NavigationLink。
- 地图及region的异步iteration明确关闭；region明确enabled、层1，查询掩码1。直接用RID建立独立地图，不误用场景默认地图。map及region是不同同步对象，不能只配置map就假定region也同步。

同一deferred setup中连接目标地图更新观察、提交一次初始化批次；没有其他地图写者、后续拓扑修改或后台烘焙。naive同段立即查S→R。guarded等待自己的ready predicate后查S→R和S→D。

## Ready predicate实际检查了什么

1. 接收到`map_changed`，且信号RID等于本实验创建的map；其他地图信号不能解锁。
2. map iteration非0、不同于提交前的initial iteration；不使用严格大于，以免把通用代码写成永不回绕。
3. 已登记两个region，各region iteration也非0。最终记录再核对region所属map、enabled、层、async标志及区域间连接数。

回调只记录事件，查询在后续主回调完成；没有`map_force_update`，没有固定sleep，也没有“等任意一帧就ready”。看门狗200主回调仅是故障退出：若未就绪，则报同步失败/超时而不是宣布不可达。

这些条件足够解释本实验的**显式同步region+map、单写者、单批初始化**，不是多线程、连续更新或任意异步烘焙的事务确认协议。API iteration变化表示某次对象同步，不携带应用事务ID。首次地图iteration>0也不能证明某个未来变更已提交。

## 实际结果

| 查询 | 实际状态 | 实际路径 | 正确含义 |
|---|---|---|---|
| naive启动S→R | map iteration0，登记region为空 | `[]` | pending_navigation；不可据此缓存永久不可达 |
| guarded S→R | map iteration1，region已同步 | `(5,5)→(25,5)` | 末点到达R |
| guarded S→D | 同一就绪图，D位于第二region | `(5,5)→(30,5)` | 路径非空，但未到达D；是部分路径 |

naive进程中设置async=false/margin0.1之后立即读取getter，仍观察到async=true/margin1.0；guarded同步后为false/约0.1。日志同时保留`requested_config`和实际getter结果。这是实际排队尚未应用的证据，不把请求值冒充服务器已生效值。

独立oracle要求：实际路径坐标有限；起点误差小于1e-4；可达目标末点误差小于1e-4。断开目标不强行要求空数组，本次明确要求已观察到的非空部分路径末点距离D大于1，并且路径仍在主矩形内。`map_get_closest_point`确认D确实在第二区域表面，最近点接近D，owner与起点owner不同；两个region间连接数均0、links0，几何与margin独立支持断开的控制条件。不会把目标根本不在导航图上的情况混进来。

## 初版失败保留：map已更新不保证region几何可查

`results/initial-map-only-predicate/`保留首次探测的源码快照和两个进程日志：只显式设置map同步方式、未显式设置region async/enabled时，map iteration1且登记两个region，但可达查询仍为空，最近点owner为0。该版本尚无最终独立断言runner，不得列为成功实验。

之后显式设置region async=false、enabled=true并在最终版本检查region iteration，得到上表结果。**这次修改涉及多个条件，不能据此宣称已经隔离证明初版失败由某一个默认值造成，也不能称为引擎bug**。它证明原先以map计数/iteration作为唯一验收的设计不够强；最终就绪合同必须声明region配置和阶段。历史证据不是最终来源hash，单独标识以免混淆。

## 有界诊断：保留默认region配置，等待region就绪

为解释真实发现而非只靠关异步绕过，另运行 `python run_diagnostic.py`。它从冻结主夹具复制出临时变体，移除两条region配置setter，保留region iteration就绪检查，并逐次记录实际getter。源快照、基线hash、生成源码hash、独立runner hash、命令和原始日志在`results/default-region-readiness/`，不覆盖主案例。

实际观察到：region enabled=true、async=true；map iteration已非0时，region iteration仍0。等待后region iteration变为1，map到2，可达路径到R，断开控制仍只有部分路径。因此此运行直接显示“地图已登记/同步一次”和“区域几何已同步”存在分离阶段；不再仅靠两条配置修改猜原因。

中间等待次数由调度决定，诊断runner记录`map_ready_region_pending_observations`，不要求每次重跑都捕获同样次数甚至一定捕获该瞬间；若任务很快完成，不能人为延迟来制造通用结论。最终就绪与路径判据必须满足。本诊断也不证明“region非0+任意map非0”在持续多批异步更新中足够：其前提仍是单写者的一次初始化批次，生产仍要建立版本归属。

## 适用于工程的决策合同

推荐应用层状态（原创建议，不是引擎枚举）：

- `pending_navigation`：输入几何/烘焙/上传/同步尚未满足本轮就绪合同。不创建长期不可达缓存；维持等待/可回退行为。
- `query_complete_reachable`：使用匹配数据版本完成查询，末点符合游戏允许的到达阈值。
- `query_complete_target_not_reached`：在已知数据版本下得到部分/无有效到达路线。选择停在可达边缘、换目标或反馈失败需由玩法决定，不应继续把原目标当作已到达。
- `navigation_error`：无效RID、引擎错误、数据错误或同步超时。它不是几何不可达。

缓存否定结果时关联地图/区域数据版本与查询条件（目标、层、代理尺寸等适用项）；真正拓扑改变后标dirty，旧否定结论不能继续当作当前事实。生产多写者场景需要应用事务/版本归属：任意map_changed或iteration!=old不是“我的变更全完成”的保证。无变化的重复setter也不保证生成新iteration，不能盲等它。

`path.size()>0`仅说明有路径点，不保证末点是原目标；终点容差要匹配玩法需求，不能照抄本例1e-4当作所有游戏的到达半径。若目标会投影到导航表面，应分别记录原目标、投影目标和路径终点。

## 版本和范围限制

官方4.6将NavigationServer2D和NavigationPolygon标为Experimental。`map_force_update`已deprecated且不兼容异步更新，不建议以它修复启动时序。map和region iteration都可能回绕到1；本例实际只有0→1，代码的!=不等于完成了回绕实测。

未覆盖多写者、异步烘焙、流式多批变更、动态避障、寻路预算/限制、角色半径侵蚀、移动碰撞、3D、跨版本/平台、路径性能或最终游戏行为。手工已完成多边形避免烘焙阶段混入；没有把后台烘焙完成信号当地图就绪。

## 官方来源

访问2026-10-31，文档4.6，实际二进制4.6.3另有hash：

- [NavigationServer2D](https://docs.godotengine.org/en/4.6/classes/class_navigationserver2d.html)：map_changed、map/region iteration、同步getter/setter边界、async配置、路径查询、最近点、区域连接及force_update弃用说明。
- [Using NavigationServer](https://docs.godotengine.org/en/4.6/tutorials/navigation/navigation_using_navigationservers.html)，Threading and Synchronization / Waiting for synchronization：初始化查询边界。
- [NavigationPolygon](https://docs.godotengine.org/en/4.6/classes/class_navigationpolygon.html)：直接添加顶点和凸多边形索引。
- [Using NavigationPaths](https://docs.godotengine.org/en/4.6/tutorials/navigation/navigation_using_navigationpaths.html)：地图RID、导航层和实际路径查询。部分路径的具体坐标为本实验观察，不冒充文档对所有查询的固定输出承诺。

## 独立复核

[独立审查](review/README.md)在相同机器和二进制复制冻结源文件，重跑主对照两进程及默认region诊断一进程；四份主源文件、诊断runner和二进制哈希一致。原始复核输出在review/fixture/results，作者结果未被覆盖。两组重复不是六种场景，更不是跨平台同步协议证明。
