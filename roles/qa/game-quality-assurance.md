---
id: ROLE-QA-001
title: 游戏质量保证：缺陷复现、版本风险与体验研究的责任边界
type: role
status: source-backed
primary_discipline: QA
related_disciplines: [PROG, ENGINE, PROD, UX, DATA, PLATFORM]
related_roles: [qa-tester, qa-engineer, performance-qa, build-engineer, gameplay-programmer, producer, ux-researcher]
related_topics: [defect-reproduction, regression-testing, build-risk, test-automation, evidence-boundary]
engines: [engine-agnostic]
platforms: [cross-platform]
versions: ["公开岗位职责于2026-10-31读取；不表示当前招聘有效", "GDS研究方法页更新2017-10-03"]
updated_at: 2026-10-31
review_after: 2027-01-31
verification_method: 行业职业资料、三个独立雇主原文及方法指南核对；交付矩阵与模板为原创建议，未进行招聘访谈、组织试用或玩家研究
sources:
  - https://www.screenskills.com/job-profiles/browse/games/quality-assurance/games-tester/
  - https://careers.playstation.com/qa-tester/job/6237361004
  - https://www.riotgames.com/en/work-with-us/job/8302722?gh_jid=8302722
  - https://hrmos.co/pages/bandainamcostudios/jobs/050_0080_qa010_0500_0010
  - https://www.screenskills.com/job-profiles/browse/games/quality-assurance/quality-assurance-qa-build-engineer/
  - https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing
---

# 游戏质量保证：缺陷复现、版本风险与体验研究的责任边界

## 岗位定位：交付可决策的证据，而不是一张“全部通过”截图

开发者需要知道：哪个构建、哪种条件下出了什么问题，修复改变了什么，还有什么没测。本文把“游戏QA”作为一组质量工作责任的入口，不假定所有公司有同名岗位、固定汇报线或统一放行权限。`qa-tester`、`qa-engineer`、`performance-qa` 在本库仍是不同检索标签；关联到本篇**不建立同义词、重定向或一岗包办关系**。

QA可以提供体验反馈，也可以参与组织试玩；区别不在“某职位有没有资格关心体验”，而在证据能回答什么。测试员按熟悉流程通关、自动化全部绿灯、合适玩家无提示完成，是三种不同观察，不能互相替代。

## 公开职责样本：不同组织确实把重点放在不同位置

以下是有限原始样本，不是对公司内部实际运作或招聘有效性的调查：

| 来源 | 已读取的职责重点 | 本文如何使用 |
|---|---|---|
| ScreenSkills Games tester [Q1] | 对特定方面测试、详细记录问题、修复后复测 | 支持“报告—修复—复测”工作接口，不将列出的tester/technician称谓扩展到所有QA岗位 |
| SIE，Liverpool QA Tester，R-126089 [Q2] | 发现、调查、复现与报告缺陷，执行预发布测试计划、对照质量标准，也提供用户反馈；该样本为临时用工安排 | 具体执行责任样本；未取得SIE非公开标准，不把提供反馈写成代表性玩家研究 |
| Riot，VALORANT QA Manager，REQ-0010434 [Q3] | 跨引擎、TA及发布工程的策略与风险沟通；综合测试、遥测、缺陷和playtest；提及性能工具/自动化 | 说明某管理岗覆盖广且跨团队，不据此赋予所有QA最终发布裁决权 |
| 万代南梦宫工作室，日语QAエンジニア [Q4] | 自动测试脚本、测试环境、CI/CD、结果可视化/通知、支援工具与跨项目协作 | 技术型QA工程样本；Jenkins/Azure/Git等是该样本工具，不是行业必需栈 |
| ScreenSkills QA build engineer [Q5] | 构建可得性、自动化与工具、发布流程障碍，与程序/QA/制作协作 | 说明构建工程与测试执行存在接口，不把两种工作自动合并 |

日语样本由工作室[官网职业页](https://www.bandainamcostudios.com/recruit/career)“エンジニア職（サーバ／ビルド／QA）”直接链接至HRMOS雇主页面，是日语原始职责资料，不是英译文档或招聘聚合摘要。所有岗位页未提供可确认发布日期（SIE的Date Posted栏为空）；访问日期为2026-10-31。页面可读不等于岗位仍在招聘。以上公开职责也不证明实际质量、覆盖率或效率提升。

## 原创交付矩阵：谁需要拿到什么才能继续工作

下表是项目可采用的接口设计，**不是上述雇主披露的内部模板**。一个人可以承担多列工作，但应保留对应责任与证据。

| 工作问题 | 上游输入/主要接口 | QA侧交付 | 接收方可检查的完成条件 |
|---|---|---|---|
| “修复了没有？” | 程序提供修复构建及变更范围；设计提供期望规则 | 关联原缺陷的复测记录与邻近回归结果 | 明确复测构建/环境/步骤；区分已验证、未复现、受阻；不能仅凭开发状态标记关闭 |
| “这个反馈能定位吗？” | 玩家支持/内部测试的症状、存档或日志 | 最小复现包、观察与推测分开、未复现条件 | 接收者无需猜前置状态；无法稳定复现时仍保留原材料和尝试记录，不伪造必现 |
| “新构建能进入后续测试吗？” | 构建工程提供可定位产物、配置与依赖 | 冒烟检查结果、阻断项及已知环境问题 | 测试对象唯一可识别，运行器失败与产品失败分开；受阻不能算通过 |
| “自动化绿灯意味着什么？” | 工程/工具侧提供输入、断言、环境、日志 | 检查范围说明、故障注入/负例、失败分类与原始结果 | 预期错误可被捕获；失败不会复用旧成功结果；统计有明确对象/分母 |
| “这次改动值得冒什么风险？” | 变更清单、目标平台/配置、上线目标 | 风险—证据—未测范围清单及缓解建议 | 每项结论能追到构建与证据；谁接受残余风险由项目明确，不由职位名称推断 |
| “玩家是否理解下一步？” | 设计/UX研究问题与合适参与者安排 | 分离提示前后行为、方法条件与观察 | 不用熟练测试员的通关替代目标玩家理解；参与者/任务/干预条件写清 [Q6] |

关键技术不只是一种工具：状态前提重建、输入/配置隔离、日志关联、差异定位、可执行判据、数据留存和清晰沟通决定证据能否被消费。自动化与构建型职责还需要相应脚本、版本控制、CI和环境维护能力；不是要求每个执行测试员都写引擎代码。

## 一张能交给开发的缺陷包

建议最小结构如下；没有数值的字段写“未知/未测”，不要补成看起来完整的证据：

```text
标题：可观察的行为差异，而不是先认定根因
对象：产品构建ID/提交、内容版本、配置、平台/设备、相关工具版本
前提：账户/存档状态、关卡、网络条件、输入设备及权限（避免真实私密数据）
期望：指向已确认规则/验收条款；若规则有争议，标“待设计确认”
步骤：最小操作序列；需要等待哪个可观察事件，不只写“等一会儿”
实际：具体状态/日志/画面与发生时间
复现：观察次数/尝试次数及条件；未复现的对照条件
附件：最小必要日志、可分享录屏/截图、存档或配置；标脱敏及访问范围
影响：阻断/数据损失/体验后果的已知范围，与推测分开
复测：目标修复构建、原步骤结果、邻近回归、剩余限制
```

**假设交接示例，非新实验：**“暂停恢复后角色执行旧攻击”。报告若只写“暂停失效”，开发无法判断是玩法节点仍推进、常驻输入适配器继续收命令，还是恢复后设备迟到输入被当新事件。应分别要求记录暂停边界、玩法tick、输入接收与应用消费时点，并注明合成输入还是物理设备。已有[固定步与暂停输入条目](../../solutions/programming/fixed-step-simulation-boundary.md)演示了其中一种本地程序行为，但不覆盖全部原因，也不能作为新产品已复现的凭据。

附件中的文件摘要用于区分被测字节，不认证官方发行来源；参见[本地Godot身份限制](../../research/source-notes/godot-runtime-provenance.md)。缺陷报告应分别记录版本自报、文件标识和已知取得来源，不把它们合成一个未经验证的“官方版本”字段。

## 从单项缺陷到版本风险：避免两种假成功

### 1. 用“检查通过”替代产品结论

自动化应说明输入域、判据和运行条件。例如证据一致性工具能证明当前源文件与声明摘要匹配，但不能证明运行真实发生，更不能证明游戏好玩。检查数增加，可能只是同一条轨迹反复验证；不应没有需求/风险分母就声称覆盖率。

偶发失败需要保留第一次失败、每次重跑及环境差异。允许重试的目的、上限、归类规则应事先明确；“重跑到绿”为原始失败的诊断增加了证据，不能抹掉它。隔离不稳定测试时应记录未覆盖风险和恢复负责人，不能让移除断言变成产品修复。

### 2. 用“没收到新bug”替代版本可交付

建议制作人与QA共同维护一个有界清单：变更影响范围、最低验收、已执行环境、未测/受阻、已知问题、缓解/回滚条件及接受风险的责任人。严重程度描述影响，处理优先级还受发布目标、影响人数和替代路径等项目因素制约；不要在模板中预置全行业唯一排名。

示例判读：构建打不开导致十项后续检查没执行，应报告“一项阻断、十项未执行”，而非“十项未发现缺陷”。对某旧存档未能复现问题，应保存尝试条件；这并不自动否定另一平台原始数据损失报告。

## 与体验研究相邻，但不混淆证据

SIE样本包含用户反馈，Riot QA管理岗包含playtest。[Q2][Q3] 因此本篇不画一条“QA只找bug，UX才管体验”的职业禁区。真正要分清的是：

- 功能检查：是否满足可指向的规则，哪里发生偏差。
- 性能/稳定性检查：在声明环境与工作负载下，测量如何；阈值由产品目标和平台条件决定。
- 体验研究：特定参与者在任务和干预条件下如何理解、选择与受阻。

GDS方法要求研究问题、实际/潜在用户、合适任务与中立指引，并允许在特定情况下帮助受阻参与者继续研究。[Q6] 本库据此采用的工程边界是：帮助后的完成不能当作无帮助成功。参见[主持人干预与试玩证据](../../solutions/production/playtest-intervention-evidence.md)。这不意味着有帮助的观察无价值，而是它回答了不同问题。没有执行玩家试验时，不写“玩家已理解”“可访问性已达标”。

## 组织规模与协作：建议而非统一标准

小团队可由同一人执行测试、维护脚本和整理风险，但最好明确不同工作记录：作者自测、另一人复核、设计反馈分别是什么。没有独立测试人员时，不能把同一人的第二次运行称为独立组织审查。

多团队项目可以把测试执行、技术QA/构建、领域质量负责人、UX研究分工，但接口比职位名称更重要：谁提供构建与规则，谁维护测试环境，谁解释玩家观察，谁承担放行决定，都应写入项目协议。现有雇主样本支持职责会跨团队，不足以证明所有大团队如此安排。

常见瓶颈及可交接缓解：

- **构建身份不清**：先追溯测试产物，不能拿另一构建的通过记录抵消失败。
- **测试环境坏了**：明确基础设施故障与产品缺陷，保留受阻状态。
- **规则本身有争议**：转交设计决策，QA保留已观察行为，不擅自发明期望。
- **平台/设备资源有限**：显式列出未测组合，采用风险优先而非虚构全面覆盖。
- **复现附件不能公开**：保留访问控制和脱敏；不为“证据完整”泄露用户存档、凭据或未公开平台材料。

## 本篇验收与未研究部分

完成的是公开来源对照与原创交付契约，不是团队绩效研究或职业认证。未进行访谈、招聘联系、实际bug重现、玩家研究或组织试用；无虚构通过率/改善量。`performance-qa`这里只是相邻专门工作方向，尚无足够独立样本建立完整岗位档案。本篇也不把ScreenSkills的近义称谓自动扩展成库内全局alias。

适合交给团队讨论的产物是：缺陷包是否足以让接收者重建条件、风险清单是否暴露未测项、自动化与玩家结论是否被分开。后续应在真实项目中验收这些交接成本，而不是以文章或工单数量宣称质量提升。

## 来源记录

均于2026-10-31实际读取；仅原创概括，不转载招聘全文或隐藏平台标准。

- **Q1** ScreenSkills, [Games tester](https://www.screenskills.com/job-profiles/browse/games/quality-assurance/games-tester/)；What does a games tester do / What's a games tester good at；发布日期未标。
- **Q2** Sony Interactive Entertainment, [QA Tester](https://careers.playstation.com/qa-tester/job/6237361004)，职位ID R-126089；Role Overview / What you'll be doing；Date Posted栏空白。
- **Q3** Riot Games, [Manager, Quality Assurance — VALORANT](https://www.riotgames.com/en/work-with-us/job/8302722?gh_jid=8302722)，REQ-0010434；概述、Responsibilities及Required Qualifications；发布日期未标。不把招聘页面话语当项目成果。
- **Q4** バンダイナムコスタジオ，[QAエンジニア](https://hrmos.co/pages/bandainamcostudios/jobs/050_0080_qa010_0500_0010)；仕事内容/担当業務，日语原文；雇主官网链接来源已核验，发布日期未标。招聘系统承载不改变其雇主一手性质。
- **Q5** ScreenSkills, [Quality assurance (QA) build engineer](https://www.screenskills.com/job-profiles/browse/games/quality-assurance/quality-assurance-qa-build-engineer/)；What does / Who works with；发布日期未标。仅作为邻接构建责任背景。
- **Q6** GOV.UK Service Manual / User research community, [Using moderated usability testing](https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing)；Plan sessions / Design tasks / Run a session；发布2017-02-21，更新2017-10-03。是服务研究方法，不是游戏行业岗位标准。
