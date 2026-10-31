# 精选阅读路线（本地候选预览）

仅表示编者选择的阅读关系，未经用户寻路测试；不是远端发表凭证。完整清单仍见 [CATALOG](CATALOG.md)。链接以仓库根目录为基准。证据状态原样来自文章，不由路线推断。

## 从玩法程序出发
路线 ID：`role-gameplay`

岗位起点：[玩法程序：从设计规则到可验收系统的责任边界](roles/programming/gameplay-programmer.md) — `ROLE-PROG-001` · `source-backed` · `PROG`

- 战斗规则与表现由谁推进？ → [用固定 Tick 划清战斗模拟与引擎表现边界](solutions/programming/fixed-step-simulation-boundary.md) — `SOL-PROG-001` · `source-backed` · `PROG`
  - 关联理由：区分固定模拟、输入归属与表现侧职责。
- 联网预测如何确认与重放？ → [客户端移动预测的权威边界与确认重放契约](solutions/programming/client-prediction-authority-boundary.md) — `SOL-NET-001` · `source-backed` · `NET`
  - 关联理由：跨网络权威边界阅读，不把本地确定性当作协议正确性。
- 导航查询结果何时有意义？ → [导航查询的就绪边界：空路径不等于不可达，非空路径不等于到达](solutions/ai/navigation-readiness-and-partial-path.md) — `SOL-AI-001` · `source-backed` · `AI`
  - 关联理由：区分尚未就绪、部分路径与目标到达。
- 角色转身脚滑由谁处理？ → [大角度原地转身脚滑：先划分根运动与控制器职责，再处理足底接触](solutions/animation/turn-in-place-foot-sliding.md) — `SOL-ANIM-001` · `source-backed` · `ANIM`
  - 关联理由：检查控制器与动画运动职责交接。
- 派生值不保存，为何读档后规则会分叉？ → [Factorio 派生缓存失同步：读取前失效与读档后重算必须遵守同一语义](case-studies/engine/factorio-derived-cache-load-equivalence.md) — `CASE-ENGINE-001` · `source-backed` · `ENGINE`
  - 关联理由：以第一方历史案例区分可重建性、实时失效和合法检查点续跑等价；验收工作表未执行。

## 从技术美术出发
路线 ID：`role-technical-art`

岗位起点：[技术美术：把艺术意图变成可重复交付的资产管线](roles/technical-art/technical-artist.md) — `ROLE-TA-001` · `source-backed` · `TA`

- 换机干净检出后资产为何变样？ → [干净检出后的资产导入：保留导入意图，而不是依赖作者缓存](solutions/engine/asset-import-intent-contract.md) — `SOL-ENGINE-001` · `source-backed` · `ENGINE`
  - 关联理由：检查源文件、导入配置与生成缓存的边界。 补充运行时候选根与可变外部依赖的隔离检查，不能把新根身份当作整图独立。
- 如何定位特效预算来源？ → [Niagara 特效预算：分离实例、模拟与像素成本的受控测量流程](solutions/vfx/niagara-performance-budget.md) — `SOL-VFX-001` · `source-backed` · `VFX`
  - 关联理由：区分实例、模拟和像素成本，保留未运行UE的证据限制。
- 导入正确为何仍会脚滑？ → [大角度原地转身脚滑：先划分根运动与控制器职责，再处理足底接触](solutions/animation/turn-in-place-foot-sliding.md) — `SOL-ANIM-001` · `source-backed` · `ANIM`
  - 关联理由：资产正确不自动证明运行时运动责任正确。
- 纹理预算究竟量的是哪一层？ → [BC 压缩纹理预算：逐 mip 计算 payload，不把 DDS 文件长度当作显存](solutions/rendering/block-compressed-mip-budget.md) — `SOL-GFX-001` · `source-backed` · `GFX`
  - 关联理由：逐mip核算压缩payload，分开文件、上传、分配和驻留证据。
- 字节可读是否意味着几何正确？ → [有效字节不等于正确顶点：glTF 交错属性的偏移、步长与几何验收](solutions/modeling/gltf-interleaved-attribute-contract.md) — `SOL-MODEL-001` · `source-backed` · `MODEL`
  - 关联理由：区分属性跨度、步长解释与索引恢复的内容意图。
- 相同四通道字节为什么仍可能在消费者处重复乘 alpha？ → [精灵透明度交接：四通道字节不说明 RGB 是否已经乘过 alpha](solutions/art2d/alpha-association-contract.md) — `SOL-ART2D-001` · `source-backed` · `ART2D`
  - 关联理由：实际有限 CPU 反例区分模式转换与字节重标，不冒称渲染器或真实暗边修复。
- 矩阵大小和 stride 都相同，为何变换仍然错？ → [CPU 与 shader 矩阵交接：相同大小和 stride，不代表相同矩阵约定](solutions/rendering/matrix-major-interface-contract.md) — `SOL-GFX-002` · `source-backed` · `GFX`
  - 关联理由：把编译产物的 major 约定、主机字节编码与逻辑乘法分开验收；离线证据不替代 GPU 读回。

## 从交互音频出发
路线 ID：`role-interactive-audio`

岗位起点：[交互音频设计：从声音意图到游戏内验收的责任接口](roles/audio/interactive-audio-designer.md) — `ROLE-SFX-001` · `source-backed` · `SFX`

- 玩法状态改变为何不等于可听切换？ → [交互音乐状态交接契约：玩法意图不等于可听见的切换](solutions/audio/music-state-transition-contract.md) — `SOL-SFX-001` · `source-backed` · `SFX`
  - 关联理由：区分意图、提交、生命周期与实际声音观察。
- 关键信息如何不只依赖声音？ → [对白字幕齐全仍不够：关键非语音声音的信息等价验收](solutions/accessibility/critical-sound-information-contract.md) — `SOL-A11Y-001` · `source-backed` · `A11Y`
  - 关联理由：把声音设计交付延伸到跨模态信息验收。
- 带前置和尾部的素材，如何准确交接音乐主体与循环端点？ → [音乐循环素材交接：用 PCM 帧区间表达主体，不混淆文件尾部与循环终点](solutions/music/pcm-loop-frame-contract.md) — `SOL-MUSIC-001` · `source-backed` · `MUSIC`
  - 关联理由：用实际离线 PCM 帧证据核对单位和端点，避免把素材边界验收误当作中间件或听感验收。
- 对白、录音和审核结果怎样完整交给下一制作环节？ → [Cygames 叙事制作工具：对白、录音与上下游交接的验收边界](case-studies/narrative/cygames-scenario-voice-handoff.md) — `CASE-NARR-001` · `source-backed` · `NARR`
  - 关联理由：日本第一方制作案例与原创验收矩阵分层，避免把文件身份或可用界面当成声音和叙事正确性。

## 从游戏质量保证出发：按证据类型选择方法
路线 ID：`role-game-quality-assurance`

岗位起点：[游戏质量保证：缺陷复现、版本风险与体验研究的责任边界](roles/qa/game-quality-assurance.md) — `ROLE-QA-001` · `source-backed` · `QA`

- 提示后的完成能否证明独立引导成功？ → [主持人提示后的通关，不能验证无提示关卡引导](solutions/production/playtest-intervention-evidence.md) — `SOL-PROD-001` · `source-backed` · `PROD`
  - 关联理由：区分观察条件、主持人介入与改后复测；不是划定QA与UX的职业禁区。
- 可加载的资产是否仍可能违反交付意图？ → [干净检出后的资产导入：保留导入意图，而不是依赖作者缓存](solutions/engine/asset-import-intent-contract.md) — `SOL-ENGINE-001` · `source-backed` · `ENGINE`
  - 关联理由：用具体配置和干净检出对照定义验收，不以无报错替代语义一致。 补充运行时候选根与可变外部依赖的隔离检查，不能把新根身份当作整图独立。
- 对白字幕全覆盖是否已经保住关键行动信息？ → [对白字幕齐全仍不够：关键非语音声音的信息等价验收](solutions/accessibility/critical-sound-information-contract.md) — `SOL-A11Y-001` · `source-backed` · `A11Y`
  - 关联理由：把内容覆盖合同与真实玩家理解分开；假设矩阵不是可访问性认证。
- 完成事件证明了哪个分母的结果？ → [关卡完成率：事件、尝试与玩家分母不能混用](solutions/data/attempt-completion-denominator-contract.md) — `SOL-DATA-001` · `source-backed` · `DATA`
  - 关联理由：用固定人口与as-of验收报表，不把未知终态、重试或帮助上下文混成玩家失败。
- 登录测试通过是否覆盖所有实例的修改数据资格？ → [Destiny 2 配置回退事故：实例准入与角色数据恢复不是同一道验收](case-studies/liveops/destiny-config-admission-rollback.md) — `CASE-LIVE-001` · `source-backed` · `LIVE`
  - 关联理由：真实历史案例区分实例准入覆盖与数据恢复验收，建议不冒充已执行防护。
- 关闭触发功能后不再出错，算修复验收吗？ → [Factorio 派生缓存失同步：读取前失效与读档后重算必须遵守同一语义](case-studies/engine/factorio-derived-cache-load-equivalence.md) — `CASE-ENGINE-001` · `source-backed` · `ENGINE`
  - 关联理由：区分诊断消融与保留产品语义的修复，并定位缓存首次读取和读档续跑差异。

## 从关卡策划出发：区分空间意图、可行性与玩家理解
路线 ID：`role-level-design`

岗位起点：[关卡策划：从遭遇意图与白盒到可验收的空间交接](roles/design/level-designer.md) — `ROLE-DESIGN-001` · `source-backed` · `DESIGN`

- 提示后的通关能证明路线已被独立理解吗？ → [主持人提示后的通关，不能验证无提示关卡引导](solutions/production/playtest-intervention-evidence.md) — `SOL-PROD-001` · `source-backed` · `PROD`
  - 关联理由：先确定观察与干预条件，不以主持人援助替代空间引导证据。
- NPC没有走到目标，是空间不可达还是导航未就绪？ → [导航查询的就绪边界：空路径不等于不可达，非空路径不等于到达](solutions/ai/navigation-readiness-and-partial-path.md) — `SOL-AI-001` · `source-backed` · `AI`
  - 关联理由：区分数据状态、部分路径与实际到达；不把导航API结果当作玩家体验。
- 美术与导入改动后，旧白盒通过状态还能直接继承吗？ → [干净检出后的资产导入：保留导入意图，而不是依赖作者缓存](solutions/engine/asset-import-intent-contract.md) — `SOL-ENGINE-001` · `source-backed` · `ENGINE`
  - 关联理由：借资产意图契约建立版本与接收条件，仍需按关卡受影响点复查。 补充运行时候选根与可变外部依赖的隔离检查，不能把新根身份当作整图独立。

## 状态切换后，旧状态或迟到回调覆盖当前意图
路线 ID：`problem-stale-intent-after-transition`

问题入口，不代表新增岗位档案。相似的状态边界不意味着可直接共享算法；分别阅读各文适用条件。

- 暂停恢复后旧攻击为何仍被消费？ → [用固定 Tick 划清战斗模拟与引擎表现边界](solutions/programming/fixed-step-simulation-boundary.md) — `SOL-PROG-001` · `source-backed` · `PROG`
  - 关联理由：查看输入队列边界；不外推真实设备迟到事件识别。
- 关闭界面后为何恢复到错误焦点？ → [模态菜单关闭后的焦点恢复：有效目标、嵌套作用域与失效回退](solutions/ux/modal-focus-recovery.md) — `SOL-UX-001` · `source-backed` · `UX`
  - 关联理由：检查目标身份、作用域与延迟恢复动作。
- 恢复后旧存档为何覆盖新版本？ → [Steam 动态云同步恢复时的存档写入隔离与冲突契约](solutions/platform/cloud-save-resume-boundary.md) — `SOL-PLATFORM-001` · `source-backed` · `PLATFORM`
  - 关联理由：在途I/O不能仅靠拒绝旧完成通知撤销。
- 音乐迟到回调为何覆盖新意图？ → [交互音乐状态交接契约：玩法意图不等于可听见的切换](solutions/audio/music-state-transition-contract.md) — `SOL-SFX-001` · `source-backed` · `SFX`
  - 关联理由：生命周期、generation与revision需要联合检查。

## 从图形与渲染程序出发
路线 ID：`role-graphics-programmer`

岗位起点：[图形与渲染程序：从视觉需求到可维护渲染功能的交付责任](roles/rendering/graphics-programmer.md) — `ROLE-GFX-001` · `source-backed` · `GFX`

- CPU与shader的矩阵接口如何接受？ → [CPU 与 shader 矩阵交接：相同大小和 stride，不代表相同矩阵约定](solutions/rendering/matrix-major-interface-contract.md) — `SOL-GFX-002` · `source-backed` · `GFX`
  - 关联理由：区分编译反射、CPU字节解释与尚未执行的GPU行为。
- 纹理预算指的是payload还是实际驻留？ → [BC 压缩纹理预算：逐 mip 计算 payload，不把 DDS 文件长度当作显存](solutions/rendering/block-compressed-mip-budget.md) — `SOL-GFX-001` · `source-backed` · `GFX`
  - 关联理由：先定位资源成本口径，不从文件大小推断帧性能。
- 内容侧特效优化需要什么测量合同？ → [Niagara 特效预算：分离实例、模拟与像素成本的受控测量流程](solutions/vfx/niagara-performance-budget.md) — `SOL-VFX-001` · `source-backed` · `VFX`
  - 关联理由：阅读未执行的受控协议，保留UE版本与无硬件采集限制。
- 怎样让渲染功能成为可制作的内容接口？ → [技术美术：把艺术意图变成可重复交付的资产管线](roles/technical-art/technical-artist.md) — `ROLE-TA-001` · `source-backed` · `TA`
  - 关联理由：明确底层实现与资产制作/导入配置的交接责任。
- 缺陷证据何时足以支撑发布决定？ → [游戏质量保证：缺陷复现、版本风险与体验研究的责任边界](roles/qa/game-quality-assurance.md) — `ROLE-QA-001` · `source-backed` · `QA`
  - 关联理由：技术解释与风险签收分开，不把单项通过当整体验收。

