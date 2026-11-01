---
id: CASE-NARR-002
title: Valve 情境对白：新增历史条件为何也会改变候选排名
type: case-study
status: source-backed
primary_discipline: NARR
related_disciplines: [AI, PROG, SFX, QA]
related_roles: [narrative-designer-writer, interactive-audio-designer]
related_topics: [contextual-dialogue, rule-selection, narrative-history, response-variation]
engines: []
versions: ["Elan Ruskin，GDC 2012；历史机制说明，非当前 Source API 保证"]
platforms: [engine-agnostic]
updated_at: 2026-11-01
review_after: 2027-01-31
verification_method: Valve 官方演讲 PDF 选定页文字核对；规则资格与计数排名的原创手推例，未执行规则模型、引擎或听觉测试，未观看演讲视频
sources:
  - https://www.valvesoftware.com/en/publications
  - https://cdn.fastly.steamstatic.com/apps/valve/2012/GDC2012_Ruskin_Elan_DynamicDialog.pdf
---

# Valve 情境对白：新增历史条件为何也会改变候选排名

## 历史案例中的具体机制

Valve 的 Elan Ruskin 在 **2012 年 3 月 GDC** 的 [Rule Databases for Contextual Dialog and Game Logic](https://cdn.fastly.steamstatic.com/apps/valve/2012/GDC2012_Ruskin_Elan_DynamicDialog.pdf) 中介绍：query 汇集当前及角色历史事实；规则全部条件满足才有资格，条件为假或引用的事实缺失均拒绝。其团队采用的简单评分是条件数，在已匹配规则中比较；同一 response 内另可放随机表达变体。示例用“未说过”条件及历史写回限制重复。（物理页 54–65、67–69；页码与读取范围见[来源记录](../../research/source-notes/valve-contextual-dialogue-rule-selection.md)。）

这是开发者对历史系统的说明，不是当前引擎源码审计，也不表明条件多就更紧急或更重要。下面讨论一个具体内容编辑后果，**不报告 Valve 的真实故障**。

## 原创手推：防重复条件同时改变两件事

设一个虚构营地仅有两条候选规则，使用上述“全部满足后按条件数比较”的模型。以下名字与事实均为本文定义，不是游戏台词或实际规则文件：

- `concept=idle`：本次询问闲置对白；`who=scout`：说话者为侦察员。
- `area=camp`：位于营地；`supplies_low=true`：物资不足。
- 规则 **A（营地观察）**：要求 concept、who、area 三项。
- 规则 **B（物资提醒）**：要求 concept、who、supplies_low 三项。
- 新增 `said_A` 是明确提供的布尔历史事实。给 A 增加条件 `said_A=false`，意图是说过后不再选 A。

固定前四项事实均满足各自条件，无其他候选；只改变规则编辑状态与历史：

| 阶段 | A：先检查资格，再计分 | B：先检查资格，再计分 | 手推选择关系 |
|---|---|---|---|
| 加条件前 | 有资格，3 | 有资格，3 | 同分；不指定实际胜者 |
| 已加条件，`said_A=false` | 有资格，4 | 有资格，3 | A 排在 B 前 |
| 已加条件，`said_A=true` | 无资格，不参与评分 | 有资格，3 | 仅 B 留在候选中 |

第二行的变化发生在**第一次说 A 之前**：一次防重复编辑也把原有同分改成了 A 优先。第三行不能解释成“4 分仍胜过 3 分”，因为资格已经失败。这里的历史变化是人为给定的下一次 query，不假定写回时机、音频完成或玩家已经听到。

另一个必须分开的输入是 **query 根本没有 `said_A`**：按所述缺失事实规则，A 被拒绝，而不是自动获得“从未说过”的值。内容方若希望新角色可说 A，应约定首次历史如何进入 query；不能靠未声明的默认值填补设计。

## 接收这次内容编辑时，究竟作什么决定？

**原创建议，未执行。** 内容作者交付的应不只是“给 A 加防重复”，还应说明首次竞争的预期：营地观察是否应先于物资提醒？若答案是否定的，第二行就是需要重审的选择结果，而不是继续只检查第三行能否抑制重复。

接收者保留这两条竞争规则及上述事实，分别记录资格集合和排序。这样可区分三类改动：

1. **语义只说一次**：需要历史条件及明确初始事实，并接收它对首次排名的影响。
2. **同一语义换表达**：可以考虑 response 内变体；声音不同不等于这件事没有重复说。
3. **确有优先级需求**：显式决定如何表达优先级，不把条件数当作业务重要性的天然单位。修改评分政策也会影响别的候选，需要另行检查，本文不主张一律改用权重。

这种计数办法便于用更具体的条件覆盖一般情况，代价是资格编辑与排名耦合。可扩充规则数据库，不等于追加内容会保持旧的选择行为。接收重点因此是**新条件在哪些仍然有效的竞争情境中改变了顺序**，而非只核对规则能否解析或台词是否存在。

## 证据与迁移边界

两规则轨迹是有限的原创推导，没有运行结果、成功率或玩家反馈。它不重建实际同分策略、历史存档、过期时钟、并发说话仲裁或完整音频中断协议；记录“已说”也不能证明完整听见。若项目使用其他评分或缺失值政策，应重新推导，不能照搬这张表。

[叙事设计／编剧职责](../../roles/narrative/narrative-designer-writer.md)中的语义与宿主效果问题仍需另行处理；[Cygames 对白与录音制作交接案例](cygames-scenario-voice-handoff.md)关注上游工作流，不提供本例的运行时选择证据。
