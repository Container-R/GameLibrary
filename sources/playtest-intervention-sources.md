---
id: SRC-PROD-PLAYTEST-001
title: 试玩观察与主持人介入的原始来源记录
type: source
status: source-backed
primary_discipline: PROD
related_disciplines: [QA, DESIGN, UX]
related_roles: [producer,level-designer,ux-researcher]
related_topics: [playtesting,research-methods,label-granularity]
engines: [engine-agnostic]
platforms: [cross-platform]
versions: ["ValvePDF日期冲突未解决", "GDS更新2017-10-03", "Ostrovsky等论文2025-09-12"]
updated_at: 2026-11-01
verification_method: 原始PDF、机构方法页与非游戏记忆研究的论文正文定向核对；无新增参与者研究或模型运行
sources:
  - https://cdn.akamai.steamstatic.com/apps/valve/2006/GDC2006_HL2DesignProcess.pdf
  - https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing
  - https://link.springer.com/article/10.3758/s13428-025-02800-5
---

# 来源记录与主张边界

以下 Valve 与 GDS 两份来源的初始访问日期均为2026-10-31。两份来源来自不同机构，但都是方法说明，不是两个验证本文协议的独立实验。未复制整页幻灯片、图片或他人的研究数据。

## Valve PDF

- 原始URL：https://cdn.akamai.steamstatic.com/apps/valve/2006/GDC2006_HL2DesignProcess.pdf
- 标题：Valve’s Design Process for Creating Half-Life 2。
- 署名：David Speyrer、Brian Jacobson；28页。
- 页码规则：以下为PDF物理页，从1起计。检索接口的P编号从0起计，故第10页对应P9。
- 日期：目录2006及文件名GDC2006；PDF页脚©2007。版权年不必等于发表日期，两者都不足以单独确定实际演讲日。本稿保留该冲突，未追认具体会期。
- 第3页 *An Engineering Approach*：实验、想法及目标有分别评估的环节。
- 第10页 *Running a Good Playtest*：居家体验模拟与不提示的语境。
- 第11页 *Questioning Playtesters*：问题的局限与非诱导提问。
- 第19页 *Playtesting as Production*：趋势与避免过度纠正。
- 已通读文本层；相关页进行了网页PDF截图请求。没有对第9页照片及第14–15页视觉案例作任何玩家行为或定量结果推断。
- 不支持：本文干预分级来自Valve；救场后完成的具体成功率；本文工单协议已提升项目表现；任何通用样本/时长标准。

## GDS原始方法页

- 原始URL：https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing
- 标题：Using moderated usability testing；归属User research community / GOV.UK Service Manual。
- Published2017-02-21；Last updated2017-10-03（更新区）。
- *Design the tasks*：不在任务中泄露答案；抓取正文95–117行。
- *Run a session*：中性任务说明、观察、必要时救场继续学习；118–139行。
- *Plan the sessions / Researching with assistive technologies*：参与支持与实际设备条件；88–94、162–174行。正文行号可能随网页改变，以章节标题定位为准。
- 迁移边界：这是服务可用性研究的方法，不能当作关卡设计或游戏内提示的效果数据。本文采用它来区分研究目的与干预条件，不迁移服务特有的数据任务、会话长度或样本安排。

## 原创部分与未完成部分

五栏证据结构、介入分类、虚构E1–E5水泵房序列与生产决策卡是本研究原创。方法来源并不包含该场景。未招募、未运行游戏、未录制参与者、未修改关卡、未复测；不能从静态反例推出任何玩家群体的成功率或因果收益。

关联[工程方案](../管理档案/历史正文/solutions/production/playtest-intervention-evidence.md)。来源方法与原创假设保持分层，不以文档归档代替真实试玩。

## 2026-11-01 增补：标签粒度与生产决定

保留前述 2026-10-31 的两份来源记录；本增补引入第三份原始研究，不把旧资料改称自动编码实验。

- Tehilla Ostrovsky、Paul Ungermann、Chris Donkin，*Using machine learning to automate the collection, transcription, and analysis of verbal-report data*，Behavior Research Methods 57, 285；出版商标示发表于 2025-09-12，DOI 10.3758/s13428-025-02800-5。[原始开放全文](https://link.springer.com/article/10.3758/s13428-025-02800-5)。
- 本次定向阅读：Methods；Text analysis / Effectiveness test；Discussion / Evaluating the efficacy of the framework；Transcription & text analysis pipelines。正文定位以章节为准；未据图片推断结果。
- 采用的研究任务、评分过程与两种粒度的一致率集中记在关联方案的新增小节，本记录不再重复。人工评分是比较参照，不是对真实心理状态的直接测量；不把这项跨领域案例当成游戏模型基准。
- 新增的合并函数推导、“需要帮助”与不同工单的反例、按决定选择粒度的接收建议均为本稿原创。它们不是论文执行过的游戏任务，也不改变原水泵房记录的虚构身份。
- 未获取参与者音频或个体数据，未运行研究仓库或模型，未复算统计；未验证任何游戏分类、转录、派单或改版收益。未采用论文其他速度、成本或模型确定性主张。
