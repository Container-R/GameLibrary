# 本地知识可发现性审查：岗位入口与恢复类问题路线

审查时间：2026-10-31。只读检查 `gamelibrary-work`，未查询/修改远端，未修改主暂存树。检查时本地 CATALOG 含16篇候选（3岗位、13方案）；不能据此声称16篇已在远端发表。第三篇 Steam 稿未纳入本次快照。发布因受众澄清暂停，本文件仅供决策。

## 结论

开发者能够从标题列表找到已知术语，却很难从岗位或跨学科故障稳定进入相关方案。已有文章间内链提供部分路线，不是完全无导航。最小有用改进应是**一个受控、ID驱动的阅读路线索引**，而非复制正文、补空目录或把任意标签自动变成行业知识图谱。

## 实际检查与具体缺口

- `CATALOG.md` 实际仅按 type 分为岗位/方案，按路径排序；每项显示主学科，但**没有按主学科另行分组**。未展示 canonical document ID、岗位关联、主题、引擎/版本边界。
- skill 的 `scripts/build_catalog.py` 是当前生成器来源；仓库 `scripts/` 本身有分类/模型/证据校验，没有岗位或主题反向索引生成器。该生成器解析顶层字段，不消费 `related_roles`/`related_topics`。
- 16篇均有稳定文章 ID及 `related_roles`。5篇无 `related_topics`：ROLE-SFX-001、ROLE-PROG-001、SOL-DESIGN-001、SOL-LOC-001、SOL-SFX-001。因此自动主题云会漏掉经济、本地化和交互音乐等实际内容，不能把缺标签解释为无关。
- 岗位标识是关系标签，不是已建立的统一岗位实体表。玩法档案 ROLE-PROG-001 的 `related_roles` **不含自己** gameplay-programmer；TA档案也不含 technical-artist；交互音频档案标签中亦无 interactive-audio-designer。仅按标签反查会漏掉入口岗位本身。应显式建立 route 的 subject_profile_id，不自动把相关岗位误认作文章主体。
- QA相关标记有 qa-engineer（8篇）、qa-tester（3篇）、performance-qa（1篇）。这些是不同范围的检索标签，尚无来源支持将它们当同义词合并；也没有 QA 岗位档案。可提供“测试验收视角”而不能据此宣称已完成 QA 职业研究。本次建议不新增该入口，避免超出最小范围。
- gameplay-programmer 反向标签命中8篇，其中1篇是音频岗位档案、7篇是方案（经济、导航、云恢复、音乐、固定步长、预测、脚滑）。只看 PROG 主类会错过多数实际关联。
- technical-artist 标签精确命中2方案（Niagara、导入）；技术美术档案已有到玩法、脚滑、导入的正文链接，说明标签集合也不等于完整关系。
- 当前实际内链有价值：玩法→固定步长/脚滑；TA→玩法/脚滑/导入；交互音频→音乐交接/声音信息等价。这些应保留，不由新索引取代。

## 一个有界改进：四条受控阅读路线

建议未来新增一份小型路线注册表（如 `taxonomy/reading-routes.json`）及其生成展示（如 `DISCOVERY.md`），README与CATALOG只增加入口。此为一个导航功能，不改变文章目录、ID、证据状态或现有 CATALOG 生成规则。

首批仅4条路线，以下均是**拟议编者关联**，不是已经写入的元数据或统一职业标准：

| 稳定路线ID建议 | 起点与已经存在的岗位档案 | 问题式下一跳（实际文章ID） |
|---|---|---|
| role-gameplay | 玩法程序，ROLE-PROG-001 | 战斗规则与表现谁负责→SOL-PROG-001；联网确认与重放→SOL-NET-001；查询结果何时有意义→SOL-AI-001；运动交接→SOL-ANIM-001 |
| role-technical-art | 技术美术，ROLE-TA-001 | 换机干净检出资产变样→SOL-ENGINE-001；特效预算归因→SOL-VFX-001；角色脚滑职责→SOL-ANIM-001 |
| role-interactive-audio | 交互音频，ROLE-SFX-001 | 玩法状态与可听切换不同步→SOL-SFX-001；关键信息不能只靠声音→SOL-A11Y-001 |
| problem-stale-intent-after-transition | 问题路线，无岗位档案/不生成职业完成项 | 暂停恢复命令归属→SOL-PROG-001；关闭界面后旧焦点恢复→SOL-UX-001；存档恢复旧写覆盖→SOL-PLATFORM-001；音乐生命周期与迟到回调→SOL-SFX-001 |

最后一条必须注明：这是“检查状态切换边界”的阅读路线，**不是一套跨系统可直接复用的算法**。暂停输入、焦点节点身份、存档在途I/O、音乐意图各自有不同权威边界和验收条件；不能用 generation/token 术语相同就推断同一修复成立。路线按问题链接，不复制或夸大实验结果。

### 最小注册契约

每条：`id, title, kind(role|problem), subject_profile_id(optional), entries:[{document_id, question, rationale}]`。subject_profile_id 必须指向现有 role 文档；问题路线无该字段。document_id 通过实际文章 frontmatter 唯一解析成路径。rationale 是可审查的编者关联理由，不冒称外部证据。初版只维护4条路线，不预填22/24个候选学科，不生成缺失岗位占位页。

显示时读取原文 title/status/primary_discipline；原样保留证据状态，必要时附现有 engines/versions简短信息。不得从存在实验目录推断 verified。当前候选在本地只显示“本地候选预览”，待实际提交核实后才进入发表导航；不能通过原生成器的“状态非needs-research”规则推断远端已发表。

### 有限验收标准（拟议，未实现/未运行）

1. 四条路线每个 ID 唯一；每个目标ID在允许知识目录中恰好对应一个文件。重复ID、缺文件、未知status、needs-research目标均报错，不静默丢项。
2. role入口须解析到 `type: role`；problem入口不得被计为岗位成果。canonical文章ID不更名，旧路径和ACCESS→A11Y/LOC兼容关系不变。
3. 路线只声明编者阅读关系；不自动合并 qa-engineer/qa-tester/performance-qa 或由文件名猜主体岗位。后续确需别名时独立审查记录。
4. 生成必须确定性、提供只读 `--check`；相同输入不变，文章移动但ID保留后链接更新；错误时不覆盖已生成索引。
5. 当前示例验收：玩法起点能定位跨NET/AI/ANIM文章；TA能定位ENGINE/VFX；音频能定位A11Y；恢复问题能定位4篇不同主学科并保留各自限制。
6. 保留CATALOG为完整清单，新路线只做精选导航；不把“路线没收录”解释为文章不存在或岗位无关。缺related_topics不阻止已人工核实的路线收录。

## 应暂缓的扩大范围

暂不做全文搜索服务、网站、嵌入索引、自动语义标签、全职业同义词库或大批空白路线。这些都不能先解决主体岗位标签缺失和证据边界展示问题，且在16篇候选规模上维护成本高于收益。先验收这四条路线是否能减少读者跨类翻找，再决定扩展。

## 审查依据及限制

已读取研究skill `01-taxonomy-and-roles.md`（多轴关联、稳定ID、勿复制正文）与 `05-repository-contract.md`（实际存在方可列入、元数据与兼容）；当前README/CATALOG、16篇frontmatter、三份岗位正文内链、taxonomy说明、test_taxonomy.py、skill build_catalog.py。统计来自本地只读扫描。未做真实开发者寻路测试，因此“改进有效”是待验收设计判断，而不是用户研究结果。未修改代码、未生成路线、未提交或改变任何发布状态。
