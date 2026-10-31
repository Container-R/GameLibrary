---
id: AUDIT-TAX-001
title: 初始七篇知识的覆盖审计与 ACCESS 兼容拆分建议
type: research
status: source-backed
primary_discipline: PROD
related_disciplines: [ACCESS, UX, QA, PLATFORM, ENGINE]
updated_at: 2026-10-31
verification_method: 本地七篇已集成正文的元数据与章节检查；行业组织及平台原始资料核对；分类调整仍为提案
sources:
  - https://www.screenskills.com/job-profiles/browse/games/
  - https://igda.org/sigs/localization/
  - https://igda.org/sigs/game-accessibility/
  - https://learn.microsoft.com/en-us/xbox/accessibility/guidelines
---

# 初始七篇知识的覆盖审计与 ACCESS 兼容拆分建议

## 审计范围与事实

检查时点：2026-10-31 13:14 UTC 的集成工作副本，对应知识内容提交 `cbcc02054265388f7d0d7481a17fe85ac45e99b4`；非自动随仓库更新的实时统计。后续新增文章不追写这个历史快照。检查 `roles/`、`solutions/` 等正文的 frontmatter 和章节，不把模板、来源索引、实验脚本与运行记录算作知识覆盖。

| 主分类 | 文档数 | 实际边界 |
|---|---:|---|
| PROG | 2 | 玩法程序岗位、固定步长模拟 |
| TA | 1 | 技术美术资产交接岗位 |
| ANIM | 1 | 原地转身脚滑诊断 |
| SFX | 1 | 交互音乐状态交接，非完整音频岗位体系 |
| NET | 1 | 移动预测/确认协议，非完整网络工程 |
| VFX | 1 | Niagara 预算测量方案，非实测跨平台性能结论 |

共七篇、涉及六个**主分类标签**，不意味着六个学科已完成。16 个候选主分类没有主归属正文；`related_disciplines` 中出现 QA、DESIGN 等，只说明有关联，不能计算成独立覆盖。当前程序、实时表现与资产管线较集中；可访问性、本地化、平台数据安全和生产验证仍缺可执行专题。

被检查文件：
- `roles/programming/gameplay-programmer.md`
- `roles/technical-art/technical-artist.md`
- `solutions/programming/fixed-step-simulation-boundary.md`
- `solutions/programming/client-prediction-authority-boundary.md`
- `solutions/animation/turn-in-place-foot-sliding.md`
- `solutions/audio/music-state-transition-contract.md`
- `solutions/vfx/niagara-performance-budget.md`

分类文件 `taxonomy/disciplines.json` 当时 SHA-256：`01ee5d65417e086b980d01eb58c68538c62fda03137d4eb25bea324f8fb43449`。这是内容指纹，**不是 Git 提交 SHA**。

## 行业资料支持哪些判断

ScreenSkills 的 games 岗位入口按 Production、Design、Art、Animation、Technical art、Audio、Programming、Quality assurance 导航。这证明职业导航可以采用较粗的组别，不证明本库 22 个候选节点是行业统一标准。[S1] IGDA 的 SIG 页面又混合学科、倡议与兴趣群体，因此也不能直接当作互斥完整学科树。[S2]

本库应维持“主分类 + 多角色/任务关联”的模型。主分类用于查找与编辑责任，岗位是交付职责，技术是可跨岗位复用的问题；不要为了与任何单一目录一致而改写已经稳定的文档 ID。

## ACCESS 是否合并了不同专业？

**是：目前节点将无障碍与本地化混为一个主类，检索和覆盖计数会丢失差异。** IGDA 独立设有 Localization 与 Game Accessibility；前者聚集翻译、本地化制作和项目管理，后者聚焦残障玩家的可玩性。[S3][S4] XAG 的输入、UI 焦点、音频替代等问题也不限于语言转换；其自身明确是设计/开发/测试最佳实践，而不是法律合规认证清单。[S5]

两者可交叉但不能互相代替：字幕既涉及语言版本与翻译上下文，也涉及声音信息、说话者和可读性；完成字幕翻译不等于通过听觉无障碍验收。反之，允许放大文字不能证明翻译正确。[S6；后句为分类推论]

### 向后兼容提案（尚未应用）

1. 保留 `ACCESS` 原 ID、旧显示名和历史范围，标为 `legacy-umbrella`；不要直接把它改名成纯“无障碍”，否则旧本地化引用会被悄悄改义。
2. 增加候选节点 `A11Y`（游戏无障碍/可访问性）和 `LOC`（国际化与本地化）。给 `ACCESS` 添加 `split_into: [A11Y, LOC]`、生效版本和说明。**一对多拆分不能伪装成单目标 alias/redirect。** 旧入口继续展示两分支。
3. 文档逐篇复核：主要验收目标决定 primary；交叉内容使用 related，保留历史分类变更记录。当前七篇没有 primary ACCESS，无需重写其 ID 或路径。
4. 更新 schema 兼容读取、索引器和验证测试，再增加新条目。旧消费者仍能读到 ACCESS；新统计分别输出“已审核主分类覆盖”和“遗留待归类”，避免拆分后误增完成率。
5. A11Y 与 LOC 同样先是候选分类；只有具体岗位/工程专题有证据才提高该部分置信，不把机构目录当作所有团队分工的最终答案。

## 三个可直接进入研究队列的问题

以下是下一步研究建议，非已经完成的方案，不替代正在进行的经济与音频任务。

| 问题与建议归属 | 可验收交付 | 初始证据与测试边界 |
|---|---|---|
| **模态菜单关闭、控件失效后，如何恢复手柄/键盘焦点而不落入隐藏节点？** A11Y/UX/QA；拆分前仍可登记 ACCESS | 焦点栈、默认恢复规则、禁用/卸载目标兜底，以及开关对话框/断开手柄/页面切换测试矩阵 | [XAG 113](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/113) 支持始终可见焦点及模态约束；恢复算法须原创设计并实际验证，不把本文建议称平台认证 |
| **如何在翻译前发现硬编码、文本扩展和占位符被破坏，而不把伪本地化当语言质量测试？** LOC/ENGINE/QA | 字符串 ID/参数契约、伪语言生成与截图检查方案；区分布局测试、真实语言 LQA 与 RTL/字体能力 | 已读 [Unity Localization 1.5.13 Pseudo-Localization](https://docs.unity3d.com/Packages/com.unity.localization@1.5/manual/Pseudo-Localization.html) 的问题列表和 Pseudo-Locale 流程；下一步选定版本样例，不外推引擎集成已测 |
| **Steam Deck 休眠后另一设备更新存档，恢复时怎样避免内存旧状态覆盖新文件？** PLATFORM/LIVE/QA | 文件更改通知→暂停写入→校验版本→加载/冲突决策的状态机，配中断与恢复测试；区分本地一致性和云同步 | 已读 [Steam Cloud](https://partner.steamgames.com/doc/features/cloud) Dynamic Cloud Sync：恢复可下载改动并通知应用；其预发布测试段警告未处理新回调的旧版本可能丢数据。先做本地模型，不擅自配置真实 Steam 应用 |

## 来源与限制

访问日期均为 2026-10-31；只保留短述、原创分类推论与链接，不复制机构目录全文或截图。

- **S1** ScreenSkills，[Careers in games](https://www.screenskills.com/job-profiles/browse/games/)，页面岗位组导航；英国行业技能组织，地域与用途边界明确。
- **S2** IGDA，[Special Interest Groups](https://igda.org/sigs/)，Types of Interest Groups；是社区组织结构，不是完整职业本体。
- **S3** IGDA，[Localization](https://igda.org/sigs/localization/)，Overview / Focus and actions。
- **S4** IGDA，[Game Accessibility](https://igda.org/sigs/game-accessibility/)，Overview。其外链独立站访问超时，未据该站补写事实。
- **S5** Microsoft，[Xbox Accessibility Guidelines V3.2](https://learn.microsoft.com/en-us/xbox/accessibility/guidelines)，Introduction 与 guideline 列表；页面标注 V3.2 于 2023-06-08 发布，访问页更新日期为 2026-08-14。
- **S6** Microsoft，[XAG 104: Subtitles and captions](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/104)，Implementation guidelines 中说话者、重要声音和字幕配置要求。仅用于确认交叉面，不在此复述完整标准。

本审计只说明当前内容缺口与可兼容的分类改进，不宣称已验证全球所有岗位、专业或团队组织方式。
