---
id: ROLE-DATA-001
title: 游戏数据分析师：从指标请求到可解释的设计决定
type: role
status: source-backed
primary_discipline: DATA
related_disciplines: [DESIGN, PROG, QA, PROD, LIVE, UX]
related_roles: [game-data-analyst, data-engineer, game-designer, gameplay-programmer, producer, user-researcher]
related_topics: [metric-definition, analysis-question, cohort-eligibility, interpretation, decision-handoff, counterfactual-logging, triggered-analysis]
engines: [engine-agnostic]
platforms: [cross-platform-responsibility-not-validation]
versions: ["Bandai Namco Nexus 实践者文章2021-12-07", "Riot Insights介绍2015-11-16", "Microsoft ExP 方法文2020-07-31与2021-12-24"]
updated_at: 2026-11-01
review_after: 2027-02-01
verification_method: 日英第一方实践者及 Microsoft ExP 方法原文所列章节核对；教程比较与资格设计为原创未执行建议；未收集玩家数据、执行实验或测量改版效果
sources:
  - https://www.wantedly.com/companies/bandainamco-nexus/post_articles/362598
  - https://www.riotgames.com/en/work-with-us/disciplines/insights/get-data-informed-on-the-insights-blog
  - https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-pre-experiment-stage/
  - https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-post-experiment-stage/
---

# 游戏数据分析师：从指标请求到可解释的设计决定

> **历史技术补充（迁移衍生），不是当前读者书。** 当前阅读请见[《游戏数据分析师如何支持设计决策》](../../../../GameLibrary/数据分析/指标设计/岗位与协作/游戏数据分析师如何支持设计决策.md)。以下保留旧正文的完整技术上下文、来源和未执行范围；此次只增加历史标记并调整链接，没有重新运行或重新认证历史主张。原路径与前后文件绑定见[迁移记录](../../迁移记录-source-group.json)。


## 定位与责任边界

本文限定一个工作单元：**把设计或运营提出的问题转为有定义的观察，再把观察连同解释边界交回决定者。** 分析师不是只接收“算一个完成率”的报表执行者，也不能因为拥有数据就替设计决定目标、替制作授权发布。

测量定义正确、数据足以回答问题、解释成立、建议值得采纳，是不同判断。数据工程、玩法埋点、QA、用户研究与分析可以由不同人员负责，也可以兼任；岗位名称不能消除这些证据接口。这里不把分析师、数据科学家、数据工程师和研究员规定为同义词或固定层级。

## 第一方实践样本

- **Bandai Namco Nexus，中村一哉，2021-12-07。** 其企业实践文章介绍与运营讨论分析请求背后的问题，并在报告中区分事实、考察和提案；一个最初被称作“抽卡分析”的请求，在讨论后转向既有用户减少的问题。[S1] 原文没有将该例明确归属于文中列举的某款游戏，也没有公开可复算数据或随机实验。
- **Riot Insights，2015-11-16。** 文中引用 Davin Pavlas 与负责分析的 Rudi Bonaparte，说明数据参与而不独占决策；历史 Yasuo 例子结合使用经验解释胜率，而非只看总体值。[S2] 这是开发方的历史说明，不证明经验分组之间存在因果学习效应，也不能把后续平衡结果全部归因于某一改动。

两者支持“问题与解释需要协作”的角色范围，不提供通用组织结构、当前招聘状态或实验统计规范。本文没有检查其中图片、图表或游戏界面。

## 常见任务与接收产物

下表为原创、未执行的责任建议，不是来源公司的内部表单。

| 工作 | 分析侧推动明确的产物 | 不能偷换的判断 |
|---|---|---|
| 接到指标或报表请求 | 要决定什么、有哪些可选行动、何种答案会改变行动 | 请求的图表不一定对应真实问题 |
| 定义可观察对象 | 事件含义、观察单位、资格条件、时间窗口、版本与数据截止点 | 事件名称相同不保证语义相同 |
| 核对数据是否适用 | 字段来源、缺失/冲突与已知采集变化、无法辨认的对象 | 查得到数据不等于覆盖目标人群 |
| 组织比较 | 可比较部分、不可比较条件、替代解释及尚需证据 | 差异存在不自动证明改动造成差异 |
| 向设计/制作交接 | 事实、解释、建议、限制、下一判断所需输入 | 建议不是已获授权的上线决定 |

关键能力包括与设计人员澄清问题、把玩法行为转换为测量定义、检查查询和数据语义、解释不确定性并清楚沟通。SQL、脚本、可视化或统计工具服务于这些任务；工具执行成功不证明分析问题选对了。

## 原创有限工作表：教程改版后的完成率

**完全假设，未取得任何结果：**团队改了教程提示，要求分析师回答“改版是否帮助玩家完成教程”。这里没有玩家记录、样本数、百分比、提升量或真实实验。

| 交接层 | 应先回答的问题 | 接收边界 |
|---|---|---|
| 决定问题 | 是考虑继续投入、撤回提示，还是定位卡点？“帮助”指完成、独立理解还是其他目标？ | 由目标责任人与分析侧共同确认，不让指标代替目标 |
| 测量定义 | 一次尝试如何开始和结束？重试算几次？分母是尝试还是主体？ | 先定义再算，不能事后挑选较好看的口径 |
| 数据资格 | 哪些对象实际接触了哪个版本/提示？新手和回流者如何辨认？不可辨认者怎么保留？ | 安装了版本不必然等于看过该提示；未知不能默认为暴露 |
| 时间与质量 | 数据窗口和报告截止是什么？是否存在迟到、缺失、重复或采集改动？ | 旧快照与新增信息分开；修订报表不是游戏已经改善 |
| 比较解释 | 两组或两个时期还有哪些条件不同？当前记录能排除什么，不能排除什么？ | 单纯前后变化不能直接宣称改版因果效果 |
| 实验声明 | 是否真的有分配、暴露和比较方案及对应记录？ | 没有证据就保留因果问题未回答；本文不提供随机化或显著性检验配方 |
| 建议与决定 | 哪项结论支持哪项建议？谁接受风险、补证或决定后续动作？ | 分析师解释证据，不从报表推导发布权限 |

例如，发现完成率变化时，可以先问两个时期的开始资格或事件记录是否变化；但没有实际记录，不能宣称“原因就是玩家构成变了”。也不能为了追求可比性随意剔除不利对象：排除规则及其影响必须可解释。以上只是需要回答的问题，不是已验证的清洗策略。

### 一个可直接交回请求者的结论结构

建议分别写出：**已观察事实 → 在哪些条件下可解释 → 仍不能回答什么 → 建议取得什么证据或作出什么决定。** 若数据不足，可交付明确缺口，而不是生成一个貌似精确的结论。若原问题已从完成变成理解，需重新评估方法；重复计算同一完成率并不能回答新的问题。

这不要求每次分析都成为大规模实验。描述性报告也能定位后续问题；关键是报告实际支持的结论，而非给所有分析贴上“因果”或“优化成功”。本工作表未在团队试用，不声称提高效率或降低错误率。

### 方法补充：控制组没有新提示时，怎样定义可比较的资格？

这是将 **Microsoft ExP 的跨领域方法迁移到教程问题的原创建议**，不是游戏实验结果。其 2020 年方法文介绍反事实记录：控制组不提供新功能，但记录在相应条件下是否本会触发；2021 年后续文讨论按触发资格分析及检查未触发补集。这里的“反事实”是功能触发条件的记录，**不是知道某个玩家接受另一种处理后的真实结果**。[实验前方法](https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-pre-experiment-stage/) [实验后方法](https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-post-experiment-stage/)

延续教程假设：设以玩家为随机分配单位，两组到达相同检查点后，才有首次显示新提示的机会。拟议资格在显示前按两组相同规则评估；控制组只记资格，不显示提示。**这要求资格及此前到达路径尚未被本次处理影响**，不能仅因字段名称相同就假定成立。若处理已改变更早导航、预加载或耗时，就需要重新设计资格，而不是继续套用此例。

| 分析选择 | 能回答什么、付出什么代价 |
|---|---|
| 保留全部已分配对象 | 对准总体问题；大量没有机会受影响的对象可能降低检测灵敏度，但不能无数据就断言功效不足 |
| 只筛点击新提示者 | 控制组没有同一点击机会，点击又可能由提示设计改变；这不是两组对称的资格条件 |
| 两组共同记录首次提示资格 | 可聚焦潜在受影响者；需要核对覆盖、日志完整性和处理前条件。额外计算可能增加成本或延迟；较宽资格可降低实现负担，但会纳入更多未受影响者 |

**资格不是完整的估计方案。** Microsoft 后文所述用户触发分析还排除首次触发前的日志。迁移到教程完成率时，必须另外规定观察单位、起点与窗口：不能删掉触发前的教程开始事件，却继续沿用原来的尝试分母；也不能把“有资格的玩家”与“该玩家之后的尝试”默认为同一单位。若改问“从首次资格机会起，指定窗口内是否完成”，就应明确这是怎样的新指标，而不是悄悄改变原完成率。

实际交接至少包括：**两组共用的资格谓词及评估时点、排除对象为何不应受影响、指标单位与窗口如何衔接**。触发样本的分配比例检查（SRM）和未触发补集分析可以暴露问题，但未发现异常不证明无偏或遗漏影响为零。子群结果也不自动代表全体；教程完成率是比例指标，不能未经推导就把子群变化乘以触发比例作为总体收益。

这段方法补充没有提供样本量、显著性阈值或实施保证。分析师应先把上述取舍交给玩法、埋点与研究接收者，再决定是否具备实施条件；没有实际数据时，不填写改版有效或无效的结论。

## 与既有工程证据的关系

- [玩家分配与逐场实际暴露](../../../../research/source-notes/game-experiment-assignment-and-session-exposure.md)用原始预印本机制和原创未执行情景，区分原分配、共享规则预测与实际启用证据；记录关系不构成估计器或因果识别验证。
- [事件、尝试与玩家分母](https://github.com/Container-R/GameLibrary/blob/1a7bf18b24ba56395892c4c0cdb3b2acecc16985/solutions/data/attempt-completion-denominator-contract.md)已用18行原创合成输入检查有限快照与排列，帮助约束身份、窗口和未知状态。它没有真实玩家或服务调用，更不是上述教程改版实验；本角色不重写其算法，也不把纯模型升级为线上采集可靠性。
- [游戏 QA](../../../../GameLibrary/项目管理与测试/质量保证/岗位与协作/游戏测试如何复现缺陷和评估版本风险.md)可提供版本、复现与数据检查证据；检查通过不替代分析解释，分析师也不能把不利观察简单标为测试错误。
- [制作管理](../../../../GameLibrary/项目管理与测试/制作管理/岗位与协作/制作人如何协调任务依赖与交付.md)协调接收、依赖和决定权限；指标成为决策输入不等于已经调整了范围或发布承诺。
- [试玩干预与证据边界](../../solutions/production/playtest-intervention-evidence.md)帮助区分辅助完成与无提示理解；遥测和玩家研究可以互补，但不能互相冒名。

## 限制与后续工作

下一步应在获准的问题和数据范围内先建立定义与接收关系，再选择合适方法。本文没有生产查询、埋点部署、真实玩家数据、A/B实验或收益测量；没有给出样本量、显著性阈值、实验停止规则、隐私合规或全行业岗位权限表。

此档案只补 DATA 岗位的一项接口，不表示全学科岗位矩阵完成。

## 来源

访问2026-11-01，正文阅读，未查看图像；详见[来源记录](../../../../research/source-notes/game-data-analyst-role.md)。

- **S1** 中村一哉，Bandai Namco Nexus 企业 Wantedly 文章，日语，2021-12-07：[组织与分析流程介绍](https://www.wantedly.com/companies/bandainamco-nexus/post_articles/362598)。定位：課題設定フェーズ、分析報告フェーズ。
- **S2** Riot Games 企业编辑，英语，2015-11-16：[Get Data Informed on the Insights Blog](https://www.riotgames.com/en/work-with-us/disciplines/insights/get-data-informed-on-the-insights-blog)。定位：开头、READY YOUR SPREADSHEETS、研究方法区分。

- **方法补充** Microsoft ExP [Pre-Experiment Stage](https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-pre-experiment-stage/)（2020-07-31）与 [Post-Experiment Stage](https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-post-experiment-stage/)（2021-12-24）；采用反事实记录、用户触发分析与解释范围章节，不作为游戏效果证据。
