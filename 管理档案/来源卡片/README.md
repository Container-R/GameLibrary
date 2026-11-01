# 来源索引

> Godot 执行版本为本地程序自报；文件摘要、官方文档和公开源码标签不能互相替代身份认证。[共享来源取证](../../research/source-notes/godot-runtime-provenance.md)说明未解决对应关系及早期固定步摘要缺口。

来源记录就近保存在各知识条目的“来源”部分：原始 URL、组织/作者、可确认的版本或日期、读取日期、章节与用途。这里提供跨专题入口，不重复复制厂商正文。公开可访问不等于允许再分发。

## 精选来源分析：按接收问题进入

以下是少量问题入口，不是全量分类，也不提升证据等级。当前书目请查[学科导览](../../GameLibrary/README.md)。原有专题来源仍保留在下方；具体版本与限制以正文为准。

| 接收问题 | 阅读入口 | 不应外推的结论 |
|---|---|---|
| 两张 Steam Total Visits 相减，能否称为自然流量？ | [流量报表对账](../../research/source-notes/steam-report-reconciliation.md) | 文档与有限集合推导，不是真实后台测量 |
| piece 名称仍对应，合并分组为何还需重审？ | [模型烘焙的追踪集合](../../research/source-notes/model-bake-piece-visibility.md) | 节点文档与分组反例，没有实际烘焙结果 |
| 关键姿势相同，逐键四元数取负能否保留动画？ | [四元数符号与立方动画](../../research/source-notes/quaternion-sign-and-cubic-animation.md) | 固定规范与实数代数反例，没有播放器执行 |
| 通用 done 能否授权不同资源释放或复用？ | [释放与复用合同路由](../../research/source-notes/resource-release-and-reuse-routing.md) | 有限合同比较，不是统一关闭算法或新的 SDK 运行 |

## 专题与岗位来源

| 研究问题 | 来源记录入口 | 证据边界 |
|---|---|---|
| 固定时间步与输入流 | [专用来源档案](fixed-step-primary-sources.md)、[知识条目](../../solutions/programming/fixed-step-simulation-boundary.md) | 原作者时间步讨论、Unity版本文档；分开的本地Godot回调、合成输入与有限kinematic接触夹具各有独立范围，不能互相迁移证据或外推真实设备/完整物理政策 |
| 转身脚滑与运动责任 | [知识条目来源S1–S6](../../solutions/animation/turn-in-place-foot-sliding.md) | Unity6000.0、UE5.6；平面接触模型不验证IK实现 |
| 玩法程序工作接口 | [岗位档案](../../GameLibrary/玩法程序/玩法系统/岗位与协作/玩法程序员如何实现和验证设计规则.md) | 行业组织、雇主和教学项目的公开样本，不推定全行业组织结构 |
| 技术美术资产交接 | [岗位档案来源S1–S5](../../GameLibrary/技术美术/美术管线/岗位与协作/技术美术如何连接美术制作与引擎.md) | ScreenSkills、Ubisoft历史/岗位样本、UE5.6 FBX；不外推所有导入器 |
| 交互音乐状态契约 | [知识条目](../../solutions/audio/music-state-transition-contract.md) | FMOD2.04手册为主；Wwise历史案例和旧公开头文件明确标年，不假定当前SDK等价 |
| 客户端预测与确认 | [知识条目](../../solutions/programming/client-prediction-authority-boundary.md) | Gambetta原作者与Unity指定版本；离散模型不验证网络/物理/反作弊 |
| Niagara预算与测量 | [知识条目](../../solutions/vfx/niagara-performance-budget.md) | UE5.6为主，5.8补充单独标记；没有硬件性能实测 |
| 单机经济事件账本 | [知识条目](../../solutions/design/single-player-economy-ledger.md) | 设计作者与Unity资源映射；原创整数模型及实际 SQLite 事务/写锁证据，不预测真实玩家 |
| 交互音频职责交付 | [岗位档案](../历史正文/roles/audio/interactive-audio-designer.md) | 中英法雇主/机构样本；不由名称推断全行业分工 |
| 模态焦点恢复 | [知识条目](../../solutions/ux/modal-focus-recovery.md) | XAG113/112与Unity6000.0，状态模型及 Godot 实例/焦点无头证据，不证明真实渲染和认证 |
| 伪本地化与格式契约 | [知识条目](../../solutions/localization/pseudo-localization-contract.md) | Unity1.5.13、官方问题记录、ICU/W3C；已执行有限 ICU 格式化，未执行 Unity |
| Steam恢复与存档写隔离 | [知识条目](../../solutions/platform/cloud-save-resume-boundary.md) | Valve滚动中英文文档同源；串行模型与实际 tmpfs 路径替换反例，不证明 Steam 平台时序或持久介质断电恢复 |

## 更新规则

1. 新增结论必须能定位到实际读取的来源或已执行实验；搜索结果摘要不代替正文。
2. 版本化 URL 仍可能变动。维护时检查正文版本；可变分支不能伪装固定修订。
3. 资料受限或读取失败时记录缺口，换合法可读来源，不绕过访问控制。
4. 原创契约、建议实验和实际执行结果分别标明；无法观察的状态保持未知。

Godot暂停/合成输入的4.6官方资料和二进制哈希见[夹具档案](../../research/experiments/godot-pause-input/README.md)；Python3.12路径替换契约及实际tmpfs反例见[文件系统档案](../../research/experiments/filesystem-save-publication/README.md)。

焦点条目的Godot4.6官方API及4.6.3实际无头证据见[实例身份档案](../../research/experiments/godot-focus-boundary/README.md)，不替代Unity/UI可访问性验收。

[ink固定提交取证清单](../../research/source-notes/ink-v1.2.1-receipt.json)与[原创源码审计](../../research/source-notes/ink-v1.2.1-host-boundary.md)：仅代码阅读，不声称运行时验证。

[资产导入意图契约](../../solutions/engine/asset-import-intent-contract.md)与[原始夹具](../../research/experiments/godot-import-boundary/README.md)保存Godot4.6官方来源、4.6.3工具版本及独立复跑证据。

[导航就绪边界](../../solutions/ai/navigation-readiness-and-partial-path.md)记录Godot4.6 Experimental API来源、4.6.3实际查询及默认region诊断。[TA岗位](../../GameLibrary/技术美术/美术管线/岗位与协作/技术美术如何连接美术制作与引擎.md)另加入万代南梦宫工作室日语职责说明，属于工作室自述而非事故/效率量化证据。

[关键非语音声音来源档案](accessibility-critical-sound-sources.md)区分 Microsoft XAG103/104、Game Accessibility Guidelines 和 Naughty Dog 2020 年功能披露；[工程合同](../../solutions/accessibility/critical-sound-information-contract.md)的具体信息粒度和时序策略是原创提案，不是用户研究结果。

[试玩介入来源档案](playtest-intervention-sources.md)对照 Valve 居家模拟试玩条件与 GDS 服务可用性研究的救场目的；[工程方案](../历史正文/solutions/production/playtest-intervention-evidence.md)区分额外解题提示、预定参与支持、观察、解释和改后验证。没有真实参与者或改版收益数据。

[Steam 胶囊素材来源记录](../../research/source-notes/steam-capsule-handoff.md)的官方规则、当前规格与覆盖工作流分别定位；尺寸通过不等于文案、可用内容、语言及排期通过。没有平台上传或审核结果。

[动画方法事件来源与实测](../../research/experiments/godot-animation-events/README.md)区分官方 4.6 文档、固定公开提交的语义参照与本地二进制观察；[共享身份取证](../../research/source-notes/godot-runtime-provenance.md)禁止把三者合并为已认证精确源码。

[游戏质量保证职责来源](../../GameLibrary/项目管理与测试/质量保证/岗位与协作/游戏测试如何复现缺陷和评估版本风险.md)核对 ScreenSkills、SIE、Riot 与万代南梦宫工作室日语原始岗位；GDS 方法指南仅用于证据边界。公开职责不证明实际质量成果或当前招聘有效。

[关卡策划职责与交接](../历史正文/roles/design/level-designer.md)对照 ORCA 日语职责、Ubisoft 特定负责人岗位、Double Fine 移动度量制作案例和历史 NEXT 挑战；原创建议不冒充工作室内部规程。

[ICU 固定接口与运行观察](../../research/experiments/icu-message-boundary/README.md)区分公开源码、已安装库文件摘要和有限格式化证据，不以版本相同认证构建来源。

[SQLite 事务边界](../../research/experiments/sqlite-ledger-boundary/README.md)及[写锁序列](../../research/experiments/sqlite-writer-contention/README.md)分别保留官方接口依据、运行时自报身份与有限实际证据；不以本地事务代替远程权益或玩家经济研究。

[BC纹理预算](../../solutions/rendering/block-compressed-mip-budget.md)对照Microsoft/Khronos官方文档和固定DirectXTex源码；离线payload、上传布局、分配与驻留证据分层。未执行GPU资源创建。

[网格属性契约](../../solutions/modeling/gltf-interleaved-attribute-contract.md)固定Khronos glTF规范与schema版本；同项目多文件不冒充独立厂商验证，CPU字面oracle是另一证据层。

[遥测尝试分母](../../solutions/data/attempt-completion-denominator-contract.md)分别记录Unity事件身份与GameAnalytics指标人口定义，不把原创模型策略当作供应商服务实现。

[ink保存内容兼容性](../../research/source-notes/ink-save-content-compatibility.md)沿固定源码区分入口返回、近似路径诊断、延迟回调及作者批准的叙事延续；能力门槛限制了实测，未用抽象模型冒充运行。

[Bungie2020事故案例](../../GameLibrary/网络与在线服务/在线运维/配置与回退/Destiny2配置回退事故中的数据恢复问题.md)使用紧凑事实概述与原创分析，不转载整篇复盘；Kubernetes文档只提供概念对照，不充当历史技术栈证据。

[音乐帧端点来源记录](../../research/experiments/music-loop-frame-contract/source-receipt.json)区分固定 FFmpeg 上游文档、FMOD 2.04 API 约定和本地工具自报身份；不认证二进制供应链。

[Cygames 日语原始来源记录](../../research/audits/cygames-scenario-handoff/source-receipt.json)保留发布/活动日期和访问边界；Excel 兼容仅按原文示例处理，不扩写内部系统规格。

[Alpha 表示来源门槛](../../research/experiments/art2d-alpha-contract/source-gate.md)使用固定 W3C 文档与 Pillow 源码；明确区分历史 PNG 文件规定和实际数值 buffer 运行范围。

[Godot actor 调度来源门槛](../../research/experiments/godot-combat-policy/source-gate.md)记录 Node 物理优先级及固定官方比较源码；本地已安装二进制的未认证来源身份沿用共享取证说明，不因观察符合文档而升级认证。

[资源加载来源门槛](../../research/experiments/godot-resource-candidate/source-gate.md)区分 ResourceLoader CacheMode、外部依赖传播与同路径请求 token；当前实验仅验证一个原生资源图，ObjectID 比较源码不认证本地程序。

[同路径请求登记证据](../../research/experiments/godot-resource-broker/README.md)将第二次请求策略与首个未收取 token 的复用分开；登记失效不等于已持有资源失效。固定官方源码是语义参照，不是已安装二进制身份认证。

[矩阵接口来源与编译证据](../../solutions/rendering/matrix-major-interface-contract.md)对照固定 GLSL/Vulkan 规范及 shaderc API；实际 assembly decoration 与 CPU 字节解释分层，不称为 GPU 执行。

[导航体型交接](../../research/experiments/godot-navigation-radius/README.md)区分烘焙半径、避让配置与独立静止物理重叠；原生地面三角形和墙体不属于同一烘焙输入，未执行角色运动。

[预测依赖时间合同](../../research/source-notes/prediction-dependency-time-contract.md)重新核对 Unity Netcode for Entities 1.4.1 与 Gambetta 原文；跨实体反例为原创未执行手算，不是 ECS 复现，也不否定现有单角色模型范围。

[Factorio 派生缓存案例](../../GameLibrary/引擎与工具/运行时系统/缓存与存档/Factorio缓存失效与读档后的重算.md)与[来源回执](../../research/source-notes/factorio-derived-cache-sources.md)区分 FFF 340 当时报告的通知/重算修复、FFF 415 的历史后续版本计划与本库未执行验收工作表；没有私有源码或游戏复现证据。

[SQLite 提交恢复边界](../../research/experiments/sqlite-commit-busy/README.md)将滚动 Transaction/lockingv3 文档与本地 DELETE journal 实测区分；BEGIN 入口拒绝和仍活动事务内的 COMMIT BUSY 不共用重试假设。旧本地证据丢失后以新 UUID 重跑，不冒充恢复。

[原生 glTF 导入阶段](../../research/experiments/godot-gltf-import-boundary/source-gate.md)保留固定规范、Godot API 与公开比较源码的边界；原生逻辑数组观察不等于编辑器/GPU证据。首轮额外AABB断言失败与修正过程公开保留，未调整冻结几何意图。

[Rig 求值交接来源](../../research/source-notes/rig-evaluation-handoff.md)将 Square Enix 的2015年日文项目材料、Unity Animation Rigging 1.2.1 的版本化规则与 Capcom 雇主职责例子分开。原创接收矩阵尚未执行；原根运动证据仍是 Python 几何模型，不因其他 Godot 实验存在而升级为引擎证据。

[新增原生根运动观察](../../research/experiments/godot-root-motion-boundary/README.md)独立于之前四项几何模型：两份新运行各包含普通骨姿态/根运动提取配置，重复读取不消费delta，显式重复应用才重复移动；不验证真实角色、IK或Unity Rig表。固定比较源码不认证安装构建。

[图形程序职责与案例来源](../../research/source-notes/graphics-programmer-role.md)区分加拿大/日本/波兰雇主责任样本与 Wube 2018 树/阴影制作进展；职责材料不等于功能效果测试，原创接收工作表尚未试用。

[碰撞回调变更边界](../../research/source-notes/physics-callback-mutation-boundary.md)把官方deferred规范、固定比较源码、本机有限事件轨迹与原创业务交接建议分层；三个旧失败不因后续kinematic对照通过而获得重新解释。

[构建工程职责与候选交接来源](../../research/source-notes/build-engineer-role.md)区分日本共享引擎、美国高级发布架构、Cygames历史生成任务与SLSA概念参照；原创候选工作表未执行，不建立厂商实践或供应链认证。

[未来运行器五位置合同](../../research/source-notes/runner-environment-contract.md)使用Python版本化API和XDG0.8规范作范围参照；有限合成子进程不等于引擎或完整隔离验证。

[Addressables内容更新来源](../../research/source-notes/addressables-content-update-baseline.md)明确1.21.21文档版本、远端state缺失时已有本地缓存的精确条件和措辞差异；不声称执行Unity或验证读取观测接口。

[内建LookAt修正顺序](../../research/source-notes/skeleton-modifier-order.md)分开阶段信号、最终姿态与延后恢复；保留首轮Boolean附加判据失败，不把这个双骨证据转移给Unity Rig或通用IK。

[Vulkan能力门来源](../../research/source-notes/vulkan-capability-gate.md)区分固定ABI/发现规则与单次instance创建失败；库存在、设备枚举和shader执行不是同一证据。

[在线服务职责与平台压测来源](../../research/source-notes/online-services-engineer-role.md)将日本团队实际责任、Riot历史替身范围和原创未执行交接工作表分开；不从平台请求链推断真实玩法容量。

[League服务器分配来源](../../research/source-notes/league-server-allocation-observation-age.md)区分观测更新延迟、年轻对局未来需求和机器就绪；历史报告不证明普适策略或收益。

[ICU目标locale分支来源](../../research/source-notes/icu-locale-plural-coverage.md)核对固定CLDR派生规则、默认数字格式与other回退；格式化成功不等于完整消息意图或语言呈现验收。

[Ogg Opus 计数来源](../../research/source-notes/ogg-opus-frame-boundary.md)区分容器位置、pre-skip、尾裁与呈现 PCM；固定完整解码不证明随机访问循环。

[制作管理岗位来源](../../research/source-notes/production-manager-role.md)以英日第一方样本区分组织职称、历史经历及原创未执行依赖交接；不推断统一放行权或管理效果。

[游戏动画师岗位来源](../../research/source-notes/game-animator-role.md)区分历史项目经历、雇主职责与原创未执行的角色组合交接。

[实时特效美术岗位来源](../../research/source-notes/real-time-vfx-artist-role.md)保留日英历史项目材料、实际文字阅读范围与未进行的视觉/玩家验证。

[Killzone 3 行动执行来源](../../research/source-notes/killzone3-plan-execution-continuation.md)定位开发者历史章节，避免把原创取消与迟到结果审查表归为原作实现。

[NavigationAgent 路径结束来源](../../research/source-notes/navigation-agent-completion.md)区分原始文档、固定比较源码与受控位置更新下的实际状态。

[游戏 UX 岗位来源](../../research/source-notes/game-ux-designer-role.md)以英日实践者资料定位交互流程交接，保留未知与历史日期。

[角色实际移动来源](../../research/source-notes/character-motion-obstruction.md)区分位移请求、静止占用与实际碰撞位移；不使用slide状态冒充继承方法结果。

[环境概念美术来源](../../research/source-notes/environment-concept-artist-role.md)定位PlatinumGames与Bungie历史实践者资料；不把概念图当作制作或玩家结果。

[Left 4 Dead Director 来源](../../research/source-notes/left4dead-director-pacing.md)定位历史 AIIDE 演讲文字，不把代理强度量或阶段名当作玩家体验验证。

[游戏数据分析岗位来源](../../research/source-notes/game-data-analyst-role.md)定位 Nexus 与 Riot 历史实践者文字；不把描述性比较升级为因果实验。

[标量惯性化来源](../../research/source-notes/scalar-inertialization-continuity.md)区分弹簧残差、有限时间多项式及数值近似。

[glTF稀疏accessor来源](../来源笔记/gltf-sparse-accessor.md)定位基底、替换和元数据子集边界。

[叙事设计与写作职责来源](../../research/source-notes/narrative-designer-writer-role.md)区分日英实践者角色与任务图历史样本。

[GGPO重放与表现边界](../来源笔记/rollback-presentation-boundary.md)固定源码中的宿主责任，不将追赶结束解释为外部提交确认。

[Resource 复制图](../../research/source-notes/resource-duplication-policy.md)将浅/内部/全部深复制与容器、子资源和副本内部别名分开，保留固定源码与实际安装程序的身份界限。

[本地化协调职责来源](../来源笔记/localization-coordinator-role.md)核对两份历史实践者说明，区分语义沟通与原创未执行的变更接收表。

[离线 stem 混音来源](../../research/source-notes/silent-stem-normalization.md)定位固定 FFmpeg 的输入归一化与 EOF/FIFO 机制；程序自报与源码身份分列。

[游戏光照美术职责来源](../../research/source-notes/game-lighting-artist-role.md)定位两篇具名第一手访谈；独立出版者承载的实践说明不等于工作室技术规范。

[历史 TiDi 时钟与饱和边界](../../research/source-notes/time-dilation-overload-clocks.md)：区分提案、部署说明和回顾，不推断当前服务。

[游戏 UI 美术来源](../../research/source-notes/game-ui-artist-role.md)以日英工作室原始说明定位受限视觉语言；组合状态方案为原创未执行建议。

[游戏作曲的原始来源](../../research/source-notes/game-composer-role.md)定位具名创作者的声部分合与写作重点；意图不等于玩家效果。

[呈现队列的固定来源](../../research/source-notes/presentation-queue-latency-boundary.md)区分 Vulkan 请求政策与独立 DXGI 等待样例。

[FMOD 虚拟化观察边界](../../research/source-notes/fmod-virtualization-observation-boundary.md)区分事件层状态与实际承载提示的 Core Channel，保留2.04.00文档范围。

[Unreal 5.6 Notify 资格与权威请求](../../research/source-notes/unreal-notify-eligibility-authority.md)核对版本化官方文档，不把生成 API 当作已读实现。

[可靠信道与实体就绪](../../research/source-notes/reliable-channel-entity-readiness.md)定位固定 ENet 实现与独立 Godot 文档，不把协议确认当应用就绪。

[网格简化的请求与结果](../../research/source-notes/mesh-simplification-request-result.md)定位 meshoptimizer 固定源码、实际返回计数和相对误差尺度。

[PSO 预缓存首显验收](../../research/source-notes/pso-precache-first-use-acceptance.md)定位 UE 5.6 官方手册与组件收集、完整绘制状态和退化策略边界。

[输入禁用的同步取消边界](../../research/source-notes/input-disable-teardown-callback.md)核对 Unity Input System 1.11.2 固定源码与应用清理所有权。

[切线 handedness 与方向变换](../来源笔记/tangent-handedness-normal-transform.md)核对固定 glTF 规范与示例实现，区分局部属性、顶点基和最终画面。

[等功率淡化与素材相关性](../../research/source-notes/equal-power-crossfade-correlation.md)核对固定 SuperCollider 源码与增益机制，严格区分理想手推和实际实现输出。

[Rocket League 输入缓冲节奏](../../research/source-notes/rocket-league-input-buffer-cadence.md)定位 Jared Cone / Psyonix 2018 原始幻灯片物理第 135–138 页，区分历史陈述与原创接收提案。

[Noita 活跃区域与更新所有权](../../research/source-notes/noita-dirty-region-update-ownership.md)依据 Petri Purho 2019 年具名原始访谈，明确开发者陈述与实现证明的区别。

[Herringbone 片段内容合同](../../research/source-notes/herringbone-tile-content-contract.md)连接 Sean Barrett 原始制作分析与固定 stb 模板枚举、标签赋值、选择路径；不据此证明地图可达。

[Riot 分歧诊断与干预身份](../../research/source-notes/riot-divergence-diagnostic-interventions.md)采用 2018 年原始技术文章的构造阈值定位案例，区分历史成功与一般二分条件。

[Box2D 传感器步末与扫掠](../../research/source-notes/box2d-sensor-step-and-sweep.md)定位 v3.1.1 与固定 main 快照的文档和实现，避免把旧版限制传播成当前普遍结论。

[Detour 同步路径状态与容量](../../research/source-notes/detour-findpath-status-and-capacity.md)定位官方 v1.6.0 固定状态位、搜索、父链输出与节点池实现；不借既有引擎导航实验作验证。

[NativeArray 值副本与延迟释放](../../research/source-notes/nativearray-copy-and-disposal-ownership.md)依据固定 Unity 6000.0.0f1 C# reference source，并分别标示 Collections 2.1.4 和 6000.0 API 文档；未认证安装组合或执行作业。

[释放与复用合同路由](../../research/source-notes/resource-release-and-reuse-routing.md)区分分配完成、操作引用放弃、音频 bank 政策与正常呈现同步复用；原创 adapter 审查不把不同证据压成通用 done 布尔值，无新增 SDK 执行。

[四元数符号与立方动画](../../research/source-notes/quaternion-sign-and-cubic-animation.md)给出逐键符号变化保持关键姿势却改变中间旋转的原创反例；保留非零曲线证明、工具交接范围与未执行边界。

[Valve 情境对白的历史条件与排名](../../research/source-notes/valve-contextual-dialogue-rule-selection.md)区分规则资格和条件计数竞争；原创两规则轨迹说明一次防重复编辑为何会改变首次排名，未执行引擎或音频测试。

[Steam 流量报表对账](../../research/source-notes/steam-report-reconciliation.md)用两个有限集合反例区分总数差、观察集合差、实际未标记访问与自然来源；提供市场到分析的接收条件，未访问真实报表。

[模型烘焙 piece 可见集合](../../research/source-notes/model-bake-piece-visibility.md)区分跨输入名称对应与追踪分组不变；原创组件合并反例及接收步骤不预填实际命中或纹理结果。

[均匀网格最近命中的停止边界](../../knowledge/rendering/uniform-grid-nearest-hit-termination.md)以固定 PBRT 源码、作者书文和原创双三角形手推区分有序格子访问、最近命中与任意命中；有限验收计划未执行。

[最后生还者第二部如何结合顶点与探针照明](../../GameLibrary/图形渲染/场景光照/间接光照/最后生还者第二部如何结合顶点与探针照明.md)核对原始演讲及作者注释，区分顶点亮度、探针色度与方向依赖；长墙接收问题及有限比较为原创未执行设计。

[Vulkan present fence 的退役覆盖](../../research/source-notes/vulkan-present-fence-retirement-coverage.md)区分一次操作的 wait semaphore 与交换链全部过去请求的凭据；固定 KHR maintenance1 来源及原创未执行接收例，不是完整关闭流程。

[For Honor 动作事件标记与请求时刻](../../GameLibrary/角色动画/动画运行时/动作选择/ForHonor动作匹配中的事件与请求时机.md)根据原始 GDC2016 演讲区分作者约定、逻辑请求和候选源起点；原创时间算例未执行，不预测搜索胜者或战斗命中。

[FFXV 预结束段与同步窗口](../../research/source-notes/ffxv-pre-end-music-window.md)补强既有音乐时间交接：原始会议资料区分准备阶段与最终固定/可变编排；没有新增运行或听感结果。

[Horizon 流送的依赖初始化许可](../../GameLibrary/引擎与工具/世界加载/资源流送/Horizon如何组织资源读取与依赖初始化.md)核对原始项目资料中的异步读取与对象工作图，并用原创有限 DAG 区分完成通知、依赖许可和共享持有；没有新运行或性能结论。

[Warlander 取消类别与输入预约](../../GameLibrary/游戏设计/战斗设计/操作响应/Warlander如何区分招式取消与输入缓存.md)依据开发者原始日语文章区分行动许可和命令有效期；原创分开试次明确半开边界及共同计时前提，没有推定实际队列、hitstop或执行结果。

[FFXV 越障的片段后继候选](../../GameLibrary/角色动画/动画运行时/动作选择/FFXV如何组织越障动画的后续片段.md)以原始会议图和讲稿核对状态归并后的候选供给；原创A/B例区分结构简化与内容政策变化，不推导排序、无候选回退或已实现足相位精修。
