# 叠层效果到期与周期：来源与边界

| 主张 | 原始依据 | 范围 |
| --- | --- | --- |
| 效果资产与运行时数据分开，叠加分组独立 | Epic UE 5.8 [Gameplay Effects](https://dev.epicgames.com/documentation/unreal-engine/gameplay-effects-for-the-gameplay-ability-system-in-unreal-engine?application_version=5.8) 的 Lifecycle、Spec；[Stacking Type](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Plugins/GameplayAbilities/EGameplayEffectStackingType)。 | 同定义的非瞬时效果；本文的简化组键不是引擎序列化定义。 |
| 重加时长、到期动作和周期进度不同 | Epic [Duration Policy](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Plugins/GameplayAbilities/EGameplayEffectStackingDurationP-)、[Expiration Policy](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/GameplayAbilities/EGameplayEffectStackingExpiratio-) 和 [Period Policy](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Plugins/GameplayAbilities/EGameplayEffectStackingPeriodPol-?lang=en-US) 的 Values 表。 | 文档检索结果标为 UE 5.8；演示的每层独立和同一步优先级均非 GAS 结构或实现保证。 |
| 明确拒绝溢出时文档说明不刷新时长或上下文 | Epic UE 5.8 [UGameplayEffect](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/GameplayAbilities/UGameplayEffect?application_version=5.8) Variables 中的 bDenyOverflowApplication、bClearStackOnOverflow、bExecutePeriodicEffectOnApplication。 | 没有运行引擎组合；“仅刷新”是试件另一种项目规则，非读取 UE 默认行为。 |
| 层数相同也可能伤害记录不同 | [本库 Node 合成对照](../实验/叠层效果到期与周期/README.md)。 | 分类和边界场景实跑，不支持任何产品的平衡值或实际引擎调度。 |

调阅日期：2026-11-22。
