# 七天首次解锁：来源与验证

- Kaplan & Meier，1958，JASA 53(282) 457–481，[原论文扫描](https://jhanley.biostat.mcgill.ca/bios601/SurvivalAnalysis/KaplanMeier1958.pdf)。§1.2 中从共同定义的起点观察事件或测量上限；§3.2 说明人群或条件改变会使观察长度与结果有关。不是游戏数据采集规范。
- Aalen & Johansen，1978，Scandinavian Journal of Statistics 5(3) 141–150，[原论文扫描](https://gwern.net/doc/statistics/survival-analysis/1978-aalen.pdf)。§I 有限状态与乘积积分；本文用两互斥终点的特例，不复现一般多状态估计。
- Therneau 等，[Competing Risks and Multistate Models](https://cran.r-project.org/web/packages/survivalVignettes/vignettes/tutorial.html)，§1.1 对照普通 KM 和正确 Aalen–Johansen。原文疾病案例仅用于方法核对，没有挪用其数据。
- 本库[关卡完成率](../../GameLibrary/数据分析/指标设计/玩家行为/如何计算关卡完成率.md)讨论事件身份、重报和两个时间；本篇从不同年龄的随访切入。SQLite 只接受给定的可信覆盖值，不实现对账服务。

[复现实验](../实验/解锁时长与观察窗口/README.md)的数值均为原创合成。
