# 来源索引

> Godot 执行版本为本地程序自报；文件摘要、官方文档和公开源码标签不能互相替代身份认证。[共享来源取证](../research/source-notes/godot-runtime-provenance.md)说明未解决对应关系及早期固定步摘要缺口。

来源记录就近保存在各知识条目的“来源”部分：原始 URL、组织/作者、可确认的版本或日期、读取日期、章节与用途。这里提供跨专题入口，不重复复制厂商正文。公开可访问不等于允许再分发。

| 研究问题 | 来源记录入口 | 证据边界 |
|---|---|---|
| 固定时间步与输入流 | [专用来源档案](fixed-step-primary-sources.md)、[知识条目](../solutions/programming/fixed-step-simulation-boundary.md) | 原作者时间步讨论、Unity版本文档；分开的本地Godot回调、合成输入与有限kinematic接触夹具各有独立范围，不能互相迁移证据或外推真实设备/完整物理政策 |
| 转身脚滑与运动责任 | [知识条目来源S1–S6](../solutions/animation/turn-in-place-foot-sliding.md) | Unity6000.0、UE5.6；平面接触模型不验证IK实现 |
| 玩法程序工作接口 | [岗位档案](../roles/programming/gameplay-programmer.md) | 行业组织、雇主和教学项目的公开样本，不推定全行业组织结构 |
| 技术美术资产交接 | [岗位档案来源S1–S5](../roles/technical-art/technical-artist.md) | ScreenSkills、Ubisoft历史/岗位样本、UE5.6 FBX；不外推所有导入器 |
| 交互音乐状态契约 | [知识条目](../solutions/audio/music-state-transition-contract.md) | FMOD2.04手册为主；Wwise历史案例和旧公开头文件明确标年，不假定当前SDK等价 |
| 客户端预测与确认 | [知识条目](../solutions/programming/client-prediction-authority-boundary.md) | Gambetta原作者与Unity指定版本；离散模型不验证网络/物理/反作弊 |
| Niagara预算与测量 | [知识条目](../solutions/vfx/niagara-performance-budget.md) | UE5.6为主，5.8补充单独标记；没有硬件性能实测 |
| 单机经济事件账本 | [知识条目](../solutions/design/single-player-economy-ledger.md) | 设计作者与Unity资源映射；原创整数模型及实际 SQLite 事务/写锁证据，不预测真实玩家 |
| 交互音频职责交付 | [岗位档案](../roles/audio/interactive-audio-designer.md) | 中英法雇主/机构样本；不由名称推断全行业分工 |
| 模态焦点恢复 | [知识条目](../solutions/ux/modal-focus-recovery.md) | XAG113/112与Unity6000.0，状态模型及 Godot 实例/焦点无头证据，不证明真实渲染和认证 |
| 伪本地化与格式契约 | [知识条目](../solutions/localization/pseudo-localization-contract.md) | Unity1.5.13、官方问题记录、ICU/W3C；已执行有限 ICU 格式化，未执行 Unity |
| Steam恢复与存档写隔离 | [知识条目](../solutions/platform/cloud-save-resume-boundary.md) | Valve滚动中英文文档同源；串行模型与实际 tmpfs 路径替换反例，不证明 Steam 平台时序或持久介质断电恢复 |

## 更新规则

1. 新增结论必须能定位到实际读取的来源或已执行实验；搜索结果摘要不代替正文。
2. 版本化 URL 仍可能变动。维护时检查正文版本；可变分支不能伪装固定修订。
3. 资料受限或读取失败时记录缺口，换合法可读来源，不绕过访问控制。
4. 原创契约、建议实验和实际执行结果分别标明；无法观察的状态保持未知。

Godot暂停/合成输入的4.6官方资料和二进制哈希见[夹具档案](../research/experiments/godot-pause-input/README.md)；Python3.12路径替换契约及实际tmpfs反例见[文件系统档案](../research/experiments/filesystem-save-publication/README.md)。

焦点条目的Godot4.6官方API及4.6.3实际无头证据见[实例身份档案](../research/experiments/godot-focus-boundary/README.md)，不替代Unity/UI可访问性验收。

[ink固定提交取证清单](../research/source-notes/ink-v1.2.1-receipt.json)与[原创源码审计](../research/source-notes/ink-v1.2.1-host-boundary.md)：仅代码阅读，不声称运行时验证。

[资产导入意图契约](../solutions/engine/asset-import-intent-contract.md)与[原始夹具](../research/experiments/godot-import-boundary/README.md)保存Godot4.6官方来源、4.6.3工具版本及独立复跑证据。

[导航就绪边界](../solutions/ai/navigation-readiness-and-partial-path.md)记录Godot4.6 Experimental API来源、4.6.3实际查询及默认region诊断。[TA岗位](../roles/technical-art/technical-artist.md)另加入万代南梦宫工作室日语职责说明，属于工作室自述而非事故/效率量化证据。

[关键非语音声音来源档案](accessibility-critical-sound-sources.md)区分 Microsoft XAG103/104、Game Accessibility Guidelines 和 Naughty Dog 2020 年功能披露；[工程合同](../solutions/accessibility/critical-sound-information-contract.md)的具体信息粒度和时序策略是原创提案，不是用户研究结果。

[试玩介入来源档案](playtest-intervention-sources.md)对照 Valve 居家模拟试玩条件与 GDS 服务可用性研究的救场目的；[工程方案](../solutions/production/playtest-intervention-evidence.md)区分额外解题提示、预定参与支持、观察、解释和改后验证。没有真实参与者或改版收益数据。

[Steam 胶囊素材来源记录](../research/source-notes/steam-capsule-handoff.md)的官方规则、当前规格与覆盖工作流分别定位；尺寸通过不等于文案、可用内容、语言及排期通过。没有平台上传或审核结果。

[动画方法事件来源与实测](../research/experiments/godot-animation-events/README.md)区分官方 4.6 文档、固定公开提交的语义参照与本地二进制观察；[共享身份取证](../research/source-notes/godot-runtime-provenance.md)禁止把三者合并为已认证精确源码。

[游戏质量保证职责来源](../roles/qa/game-quality-assurance.md)核对 ScreenSkills、SIE、Riot 与万代南梦宫工作室日语原始岗位；GDS 方法指南仅用于证据边界。公开职责不证明实际质量成果或当前招聘有效。

[关卡策划职责与交接](../roles/design/level-designer.md)对照 ORCA 日语职责、Ubisoft 特定负责人岗位、Double Fine 移动度量制作案例和历史 NEXT 挑战；原创建议不冒充工作室内部规程。

[ICU 固定接口与运行观察](../research/experiments/icu-message-boundary/README.md)区分公开源码、已安装库文件摘要和有限格式化证据，不以版本相同认证构建来源。

[SQLite 事务边界](../research/experiments/sqlite-ledger-boundary/README.md)及[写锁序列](../research/experiments/sqlite-writer-contention/README.md)分别保留官方接口依据、运行时自报身份与有限实际证据；不以本地事务代替远程权益或玩家经济研究。

[BC纹理预算](../solutions/rendering/block-compressed-mip-budget.md)对照Microsoft/Khronos官方文档和固定DirectXTex源码；离线payload、上传布局、分配与驻留证据分层。未执行GPU资源创建。

[网格属性契约](../solutions/modeling/gltf-interleaved-attribute-contract.md)固定Khronos glTF规范与schema版本；同项目多文件不冒充独立厂商验证，CPU字面oracle是另一证据层。

[遥测尝试分母](../solutions/data/attempt-completion-denominator-contract.md)分别记录Unity事件身份与GameAnalytics指标人口定义，不把原创模型策略当作供应商服务实现。

[ink保存内容兼容性](../research/source-notes/ink-save-content-compatibility.md)沿固定源码区分入口返回、近似路径诊断、延迟回调及作者批准的叙事延续；能力门槛限制了实测，未用抽象模型冒充运行。

[Bungie2020事故案例](../case-studies/liveops/destiny-config-admission-rollback.md)使用紧凑事实概述与原创分析，不转载整篇复盘；Kubernetes文档只提供概念对照，不充当历史技术栈证据。

[音乐帧端点来源记录](../research/experiments/music-loop-frame-contract/source-receipt.json)区分固定 FFmpeg 上游文档、FMOD 2.04 API 约定和本地工具自报身份；不认证二进制供应链。

[Cygames 日语原始来源记录](../research/audits/cygames-scenario-handoff/source-receipt.json)保留发布/活动日期和访问边界；Excel 兼容仅按原文示例处理，不扩写内部系统规格。

[Alpha 表示来源门槛](../research/experiments/art2d-alpha-contract/source-gate.md)使用固定 W3C 文档与 Pillow 源码；明确区分历史 PNG 文件规定和实际数值 buffer 运行范围。

[Godot actor 调度来源门槛](../research/experiments/godot-combat-policy/source-gate.md)记录 Node 物理优先级及固定官方比较源码；本地已安装二进制的未认证来源身份沿用共享取证说明，不因观察符合文档而升级认证。

[资源加载来源门槛](../research/experiments/godot-resource-candidate/source-gate.md)区分 ResourceLoader CacheMode、外部依赖传播与同路径请求 token；当前实验仅验证一个原生资源图，ObjectID 比较源码不认证本地程序。

[同路径请求登记证据](../research/experiments/godot-resource-broker/README.md)将第二次请求策略与首个未收取 token 的复用分开；登记失效不等于已持有资源失效。固定官方源码是语义参照，不是已安装二进制身份认证。

[矩阵接口来源与编译证据](../solutions/rendering/matrix-major-interface-contract.md)对照固定 GLSL/Vulkan 规范及 shaderc API；实际 assembly decoration 与 CPU 字节解释分层，不称为 GPU 执行。

[导航体型交接](../research/experiments/godot-navigation-radius/README.md)区分烘焙半径、避让配置与独立静止物理重叠；原生地面三角形和墙体不属于同一烘焙输入，未执行角色运动。

[预测依赖时间合同](../research/source-notes/prediction-dependency-time-contract.md)重新核对 Unity Netcode for Entities 1.4.1 与 Gambetta 原文；跨实体反例为原创未执行手算，不是 ECS 复现，也不否定现有单角色模型范围。

[Factorio 派生缓存案例](../case-studies/engine/factorio-derived-cache-load-equivalence.md)与[来源回执](../research/source-notes/factorio-derived-cache-sources.md)区分 FFF 340 当时报告的通知/重算修复、FFF 415 的历史后续版本计划与本库未执行验收工作表；没有私有源码或游戏复现证据。

[SQLite 提交恢复边界](../research/experiments/sqlite-commit-busy/README.md)将滚动 Transaction/lockingv3 文档与本地 DELETE journal 实测区分；BEGIN 入口拒绝和仍活动事务内的 COMMIT BUSY 不共用重试假设。旧本地证据丢失后以新 UUID 重跑，不冒充恢复。

[原生 glTF 导入阶段](../research/experiments/godot-gltf-import-boundary/source-gate.md)保留固定规范、Godot API 与公开比较源码的边界；原生逻辑数组观察不等于编辑器/GPU证据。首轮额外AABB断言失败与修正过程公开保留，未调整冻结几何意图。

[Rig 求值交接来源](../research/source-notes/rig-evaluation-handoff.md)将 Square Enix 的2015年日文项目材料、Unity Animation Rigging 1.2.1 的版本化规则与 Capcom 雇主职责例子分开。原创接收矩阵尚未执行；原根运动证据仍是 Python 几何模型，不因其他 Godot 实验存在而升级为引擎证据。

[新增原生根运动观察](../research/experiments/godot-root-motion-boundary/README.md)独立于之前四项几何模型：两份新运行各包含普通骨姿态/根运动提取配置，重复读取不消费delta，显式重复应用才重复移动；不验证真实角色、IK或Unity Rig表。固定比较源码不认证安装构建。

[图形程序职责与案例来源](../research/source-notes/graphics-programmer-role.md)区分加拿大/日本/波兰雇主责任样本与 Wube 2018 树/阴影制作进展；职责材料不等于功能效果测试，原创接收工作表尚未试用。

[碰撞回调变更边界](../research/source-notes/physics-callback-mutation-boundary.md)把官方deferred规范、固定比较源码、本机有限事件轨迹与原创业务交接建议分层；三个旧失败不因后续kinematic对照通过而获得重新解释。

[构建工程职责与候选交接来源](../research/source-notes/build-engineer-role.md)区分日本共享引擎、美国高级发布架构、Cygames历史生成任务与SLSA概念参照；原创候选工作表未执行，不建立厂商实践或供应链认证。

[未来运行器五位置合同](../research/source-notes/runner-environment-contract.md)使用Python版本化API和XDG0.8规范作范围参照；有限合成子进程不等于引擎或完整隔离验证。

[Addressables内容更新来源](../research/source-notes/addressables-content-update-baseline.md)明确1.21.21文档版本、远端state缺失时已有本地缓存的精确条件和措辞差异；不声称执行Unity或验证读取观测接口。

[内建LookAt修正顺序](../research/source-notes/skeleton-modifier-order.md)分开阶段信号、最终姿态与延后恢复；保留首轮Boolean附加判据失败，不把这个双骨证据转移给Unity Rig或通用IK。

[Vulkan能力门来源](../research/source-notes/vulkan-capability-gate.md)区分固定ABI/发现规则与单次instance创建失败；库存在、设备枚举和shader执行不是同一证据。

[在线服务职责与平台压测来源](../research/source-notes/online-services-engineer-role.md)将日本团队实际责任、Riot历史替身范围和原创未执行交接工作表分开；不从平台请求链推断真实玩法容量。

[League服务器分配来源](../research/source-notes/league-server-allocation-observation-age.md)区分观测更新延迟、年轻对局未来需求和机器就绪；历史报告不证明普适策略或收益。

[ICU目标locale分支来源](../research/source-notes/icu-locale-plural-coverage.md)核对固定CLDR派生规则、默认数字格式与other回退；格式化成功不等于完整消息意图或语言呈现验收。

[Ogg Opus 计数来源](../research/source-notes/ogg-opus-frame-boundary.md)区分容器位置、pre-skip、尾裁与呈现 PCM；固定完整解码不证明随机访问循环。
