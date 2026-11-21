# 教程分支与尝试漏斗：来源与验证

| 正文结论 | 原始材料与定位 | 证据边界 |
| --- | --- | --- |
| 保序、精确保序和中间事件的处理不同 | Amplitude，[How Amplitude computes funnels](https://amplitude.com/docs/analytics/charts/funnel-analysis/funnel-analysis-how-amplitude-computes)，Order；[Funnel Analysis FAQ](https://amplitude.com/docs/analytics/charts/funnel-analysis/faq)，同秒和属性保持。 | Exact order 的同秒自定义选项和容忍不能替代真实序号；不对其他工具类推。 |
| 固定属性必须在各漏斗步骤有值，不自动等于一个业务尝试 | Amplitude，同文 Holding a property constant；另见[转换计数选择规则](https://amplitude.com/docs/analytics/charts/funnel-analysis/funnel-analysis-how-amplitude-computes-conversions)。 | 用户×属性值是该产品的一种计量，尝试 ID、日期和合法分支要由项目定义，不把 Totals、Uniques 或 Sessions 当相同量。 |
| 开／闭入口、直／间接相邻独立，GA4 默认每用户只报告首序列 | Google Analytics，[Funnel exploration](https://support.google.com/analytics/answer/9327974?hl=en)，开闭入口、Edit funnel steps、Funnel behavior。 | 无产品配置实测；只复述文档合同。不宣称一般漏斗都有相同规则。 |
| 同为三人可能选中不同账号；迟到跳过改变错误的完成结论 | [SQLite 原创实验](../实验/教程分支与尝试漏斗/README.md)，试件验证 A–I。 | 右观察边界、事件 ID 去重和多端写入不是实际演练的系统行为。由教学规则明示连续序号与合法分支；生产先核合同。 |

调阅日期：2026-11-21。正文另链接本库相邻“关卡完成率”与“七天解锁率”，前者处理通用尝试单位，后者处理不同观察长度；本文只解有分支的阶段与终态还原。
