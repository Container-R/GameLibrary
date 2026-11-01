# GameLibrary 已发表知识索引

仅列出具备元数据、证据状态不是 `needs-research` 的实际知识文章。详见文档内来源和适用边界。

## 岗位档案

- [游戏动画师：从动作表演到运行时角色组合的验收交接](roles/animation/game-animator.md) — `source-backed` · `ANIM`
- [环境概念美术：从透视图中的意图到可解释的制作交接](roles/art2d/environment-concept-artist.md) — `source-backed` · `ART2D`
- [游戏 UI 美术：组合状态如何分配图形通道](roles/art2d/game-ui-artist.md) — `source-backed` · `ART2D`
- [交互音频设计：从声音意图到游戏内验收的责任接口](roles/audio/interactive-audio-designer.md) — `source-backed` · `SFX`
- [游戏数据分析师：从指标请求到可解释的设计决定](roles/data/game-data-analyst.md) — `source-backed` · `DATA`
- [关卡策划：从遭遇意图与白盒到可验收的空间交接](roles/design/level-designer.md) — `source-backed` · `DESIGN`
- [构建工程：把源与配置变成可验收、可交接的候选产物](roles/engine/build-engineer.md) — `source-backed` · `ENGINE`
- [游戏本地化协调：原文未变时，谁重新接收变化后的语境](roles/localization/localization-coordinator.md) — `source-backed` · `LOC`
- [游戏作曲：把完整乐曲变成有意图的交互编配](roles/music/game-composer.md) — `source-backed` · `MUSIC`
- [游戏叙事设计与写作：让对白意图、知识状态和实现条件一起交接](roles/narrative/narrative-designer-writer.md) — `source-backed` · `NARR`
- [在线服务工程师：把服务调用成功交接为可验证的游戏会话](roles/network/online-services-engineer.md) — `source-backed` · `NET`
- [制作管理：从局部完成到接收方可用的依赖交接](roles/production/production-manager.md) — `source-backed` · `PROD`
- [玩法程序：从设计规则到可验收系统的责任边界](roles/programming/gameplay-programmer.md) — `source-backed` · `PROG`
- [游戏质量保证：缺陷复现、版本风险与体验研究的责任边界](roles/qa/game-quality-assurance.md) — `source-backed` · `QA`
- [游戏光照美术：共享灯具交给别人摆放后，应该改哪一层](roles/rendering/game-lighting-artist.md) — `source-backed` · `GFX`
- [图形与渲染程序：从视觉需求到可维护渲染功能的交付责任](roles/rendering/graphics-programmer.md) — `source-backed` · `GFX`
- [技术美术：把艺术意图变成可重复交付的资产管线](roles/technical-art/technical-artist.md) — `source-backed` · `TA`
- [游戏 UX 设计师：从交互意图到可操作流程的接收责任](roles/ux/game-ux-designer.md) — `source-backed` · `UX`
- [实时特效美术：把视觉表现交接为有明确含义的游戏信号](roles/vfx/real-time-vfx-artist.md) — `source-backed` · `VFX`

## 技术机制

- [均匀网格最近命中：访问顺序为什么还需要停止边界](knowledge/rendering/uniform-grid-nearest-hit-termination.md) — `source-backed` · `GFX`

## 工程解决方案

- [对白字幕齐全仍不够：关键非语音声音的信息等价验收](solutions/accessibility/critical-sound-information-contract.md) — `source-backed` · `A11Y`
- [导航查询的就绪边界：空路径不等于不可达，非空路径不等于到达](solutions/ai/navigation-readiness-and-partial-path.md) — `source-backed` · `AI`
- [中断动画转场的标量惯性化：保留输出值与速度，而不是重用旧片段](solutions/animation/scalar-inertialization-continuity.md) — `source-backed` · `ANIM`
- [大角度原地转身脚滑：先划分根运动与控制器职责，再处理足底接触](solutions/animation/turn-in-place-foot-sliding.md) — `source-backed` · `ANIM`
- [精灵透明度交接：四通道字节不说明 RGB 是否已经乘过 alpha](solutions/art2d/alpha-association-contract.md) — `source-backed` · `ART2D`
- [交互音乐状态交接契约：玩法意图不等于可听见的切换](solutions/audio/music-state-transition-contract.md) — `source-backed` · `SFX`
- [离线 stem 混音：零值输入结束，为何可能改变另一轨增益](solutions/audio/silent-stem-normalization-boundary.md) — `source-backed` · `SFX`
- [关卡完成率：事件、尝试与玩家分母不能混用](solutions/data/attempt-completion-denominator-contract.md) — `source-backed` · `DATA`
- [单机成长经济：用事件账本验证来源、消耗与升级可达性](solutions/design/single-player-economy-ledger.md) — `source-backed` · `DESIGN`
- [Addressables 内容更新：先证明用了哪个已发布基线，再验证旧版客户端](solutions/engine/addressables-content-update-baseline.md) — `source-backed` · `ENGINE`
- [干净检出后的资产导入：保留导入意图，而不是依赖作者缓存](solutions/engine/asset-import-intent-contract.md) — `source-backed` · `ENGINE`
- [伪本地化与占位符契约：让布局失败暴露，而不是破坏字符串语法](solutions/localization/pseudo-localization-contract.md) — `source-backed` · `LOC`
- [有效字节不等于正确顶点：glTF 交错属性的偏移、步长与几何验收](solutions/modeling/gltf-interleaved-attribute-contract.md) — `source-backed` · `MODEL`
- [音乐循环素材交接：用 PCM 帧区间表达主体，不混淆文件尾部与循环终点](solutions/music/pcm-loop-frame-contract.md) — `source-backed` · `MUSIC`
- [Steam 动态云同步恢复时的存档写入隔离与冲突契约](solutions/platform/cloud-save-resume-boundary.md) — `source-backed` · `PLATFORM`
- [主持人提示后的通关，不能验证无提示关卡引导](solutions/production/playtest-intervention-evidence.md) — `source-backed` · `PROD`
- [客户端移动预测的权威边界与确认重放契约](solutions/programming/client-prediction-authority-boundary.md) — `source-backed` · `NET`
- [用固定 Tick 划清战斗模拟与引擎表现边界](solutions/programming/fixed-step-simulation-boundary.md) — `source-backed` · `PROG`
- [BC 压缩纹理预算：逐 mip 计算 payload，不把 DDS 文件长度当作显存](solutions/rendering/block-compressed-mip-budget.md) — `source-backed` · `GFX`
- [CPU 与 shader 矩阵交接：相同大小和 stride，不代表相同矩阵约定](solutions/rendering/matrix-major-interface-contract.md) — `source-backed` · `GFX`
- [呈现队列与输入时效：为何 MAILBOX 和图像数量不能单独给出延迟](solutions/rendering/presentation-queue-latency-boundary.md) — `source-backed` · `GFX`
- [模态菜单关闭后的焦点恢复：有效目标、嵌套作用域与失效回退](solutions/ux/modal-focus-recovery.md) — `source-backed` · `UX`
- [Niagara 特效预算：分离实例、模拟与像素成本的受控测量流程](solutions/vfx/niagara-performance-budget.md) — `source-backed` · `VFX`

## 真实案例

- [Killzone 3 行动执行：计划可继续、动作完成与优先级替换不是同一判断](case-studies/ai/killzone3-plan-execution-continuation.md) — `source-backed` · `AI`
- [Left 4 Dead Director：强度估计、节奏控制与实际体验的证据边界](case-studies/ai/left4dead-director-pacing-evidence.md) — `source-backed` · `AI`
- [Factorio 派生缓存失同步：读取前失效与读档后重算必须遵守同一语义](case-studies/engine/factorio-derived-cache-load-equivalence.md) — `source-backed` · `ENGINE`
- [Destiny 2 配置回退事故：实例准入与角色数据恢复不是同一道验收](case-studies/liveops/destiny-config-admission-rollback.md) — `source-backed` · `LIVE`
- [Cygames 叙事制作工具：对白、录音与上下游交接的验收边界](case-studies/narrative/cygames-scenario-voice-handoff.md) — `source-backed` · `NARR`
- [Valve 情境对白：新增历史条件为何也会改变候选排名](case-studies/narrative/valve-contextual-dialogue-rule-selection.md) — `source-backed` · `NARR`
- [League 服务器分配：观测到的低负载，不等于下一场对局的余量](case-studies/network/league-server-allocation-observation-age.md) — `source-backed` · `NET`
- [《The Last of Us Part II》混合探针光照：内容变化应由哪一层采样承载](case-studies/rendering/tlou2-hybrid-probe-content-frequency.md) — `source-backed` · `GFX`

