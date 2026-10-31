# GameLibrary 已发表知识索引

仅列出具备元数据、证据状态不是 `needs-research` 的实际知识文章。详见文档内来源和适用边界。

## 岗位档案

- [交互音频设计：从声音意图到游戏内验收的责任接口](roles/audio/interactive-audio-designer.md) — `source-backed` · `SFX`
- [关卡策划：从遭遇意图与白盒到可验收的空间交接](roles/design/level-designer.md) — `source-backed` · `DESIGN`
- [玩法程序：从设计规则到可验收系统的责任边界](roles/programming/gameplay-programmer.md) — `source-backed` · `PROG`
- [游戏质量保证：缺陷复现、版本风险与体验研究的责任边界](roles/qa/game-quality-assurance.md) — `source-backed` · `QA`
- [技术美术：把艺术意图变成可重复交付的资产管线](roles/technical-art/technical-artist.md) — `source-backed` · `TA`

## 工程解决方案

- [对白字幕齐全仍不够：关键非语音声音的信息等价验收](solutions/accessibility/critical-sound-information-contract.md) — `source-backed` · `A11Y`
- [导航查询的就绪边界：空路径不等于不可达，非空路径不等于到达](solutions/ai/navigation-readiness-and-partial-path.md) — `source-backed` · `AI`
- [大角度原地转身脚滑：先划分根运动与控制器职责，再处理足底接触](solutions/animation/turn-in-place-foot-sliding.md) — `source-backed` · `ANIM`
- [交互音乐状态交接契约：玩法意图不等于可听见的切换](solutions/audio/music-state-transition-contract.md) — `source-backed` · `SFX`
- [关卡完成率：事件、尝试与玩家分母不能混用](solutions/data/attempt-completion-denominator-contract.md) — `source-backed` · `DATA`
- [单机成长经济：用事件账本验证来源、消耗与升级可达性](solutions/design/single-player-economy-ledger.md) — `source-backed` · `DESIGN`
- [干净检出后的资产导入：保留导入意图，而不是依赖作者缓存](solutions/engine/asset-import-intent-contract.md) — `source-backed` · `ENGINE`
- [伪本地化与占位符契约：让布局失败暴露，而不是破坏字符串语法](solutions/localization/pseudo-localization-contract.md) — `source-backed` · `LOC`
- [有效字节不等于正确顶点：glTF 交错属性的偏移、步长与几何验收](solutions/modeling/gltf-interleaved-attribute-contract.md) — `source-backed` · `MODEL`
- [Steam 动态云同步恢复时的存档写入隔离与冲突契约](solutions/platform/cloud-save-resume-boundary.md) — `source-backed` · `PLATFORM`
- [主持人提示后的通关，不能验证无提示关卡引导](solutions/production/playtest-intervention-evidence.md) — `source-backed` · `PROD`
- [客户端移动预测的权威边界与确认重放契约](solutions/programming/client-prediction-authority-boundary.md) — `source-backed` · `NET`
- [用固定 Tick 划清战斗模拟与引擎表现边界](solutions/programming/fixed-step-simulation-boundary.md) — `source-backed` · `PROG`
- [BC 压缩纹理预算：逐 mip 计算 payload，不把 DDS 文件长度当作显存](solutions/rendering/block-compressed-mip-budget.md) — `source-backed` · `GFX`
- [模态菜单关闭后的焦点恢复：有效目标、嵌套作用域与失效回退](solutions/ux/modal-focus-recovery.md) — `source-backed` · `UX`
- [Niagara 特效预算：分离实例、模拟与像素成本的受控测量流程](solutions/vfx/niagara-performance-budget.md) — `source-backed` · `VFX`

## 真实案例

- [Destiny 2 配置回退事故：实例准入与角色数据恢复不是同一道验收](case-studies/liveops/destiny-config-admission-rollback.md) — `source-backed` · `LIVE`

