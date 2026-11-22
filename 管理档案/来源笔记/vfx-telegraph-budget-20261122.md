# 技能预警的预算与恢复：来源

| 主张 | 一手材料 | 边界 |
| --- | --- | --- |
| Effect Type 可定义全局预算下的距离与数量裁剪 | Epic 公开滚动 [Effect Type Budgeting](https://dev.epicgames.com/documentation/en-us/unreal-engine/performance-budgeting-using-effect-types-in-niagara-for-unreal-engine)，读取时标 5.9；固定 [5.8 Global Budget Scaling](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/Niagara/FNiagaraGlobalBudgetScaling?application_version=5.8)、[5.8 System Scalability](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/Niagara/FNiagaraSystemScalabilitySetting-?application_version=5.8)。 | 引用配置能力，不用系统可见性来推断有权可见的玩法范围。没有运行 UE。 |
| 恢复可能保留停止时的粒子状态，不能替代玩法时间 | Epic [5.8 Cull Reaction](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/Niagara/ENiagaraCullReaction?application_version=5.8) 与 [5.8 Visibility Settings](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/Niagara/FNiagaraSystemVisibilityCullingS-?application_version=5.8)。 | Cull Reaction 与 Age Update Mode 是不同参数；不推定所有 Resume 用法衔接粒子年龄或可见性。 |
| 危险范围、重要程度、颜色以外的识别线索 | Riot Games [Clarity in League](https://www.leagueoflegends.com/en-us/news/dev/clarity-in-league/)，Unbreakable Vows、Abilities；Microsoft [XAG 103](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/103)。 | 不是 Riot 的性能算法或读者无障碍测量；有限原始原则。 |
| 正确并集也可以传错时间；瘦边线遇到内部缩放会在指定采样路径消失 | [复现说明](../实验/技能预警的预算与恢复/README.md) 中 Node 离散试件及实际 software GL 读回。 | 逻辑测试不代表画面／理解；GL 没有多样本/时间性抗锯齿、不测生产 draw time、压力预算或玩家指标。 |

调阅日期：2026-11-22。
