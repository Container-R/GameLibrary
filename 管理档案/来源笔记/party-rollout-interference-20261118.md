# 组队 A/B 的分配与干扰：出处与范围

核查日期 2026-11-18。已读现有正式文章《按玩家分组的场次完成率比较》：它采用独立玩家、无玩家间干扰的比值大样本推断，并在读者自查中预告不能套用整队分配。本文解决的是实验前如何因队友结果依赖选择分配和解释目标；不重复既有比例方差公式。

1. Hudgens、Halloran，2008，JASA 103(482)，832–842。[文献页](https://pubmed.ncbi.nlm.nih.gov/19081744/)和[原论文](https://www.treatment-effects.com/Hudgens-Halloran-2008.pdf)。第 2.1 节中的个体结果允许依赖同组分配；跨组无干扰是明确假设。第 2.2 节的两阶段分配先分配组策略，然后按组策略分配个体。本文用等大固定双人队展示四种状态与三个不同对比，不复刻论文推断、方差或疫苗数据。
2. Saveski、Pouget-Abadie 等，KDD 2017，[会议摘要](https://www.kdd.org/kdd2017/papers/view/detecting-network-effects-randomizing-over-randomized-experiments)。作者报告在 LinkedIn 平台同时使用个体与簇级随机化并比较估计量，用于发现网络效应。这不是证明任意两个未协调的上线试验可直接相减，也不是游戏数据。
3. 原创确定性均值表和 Python 分数计算，见 [复算材料](../实验/组队功能的实验分配/README.md)。分配权重是设计输入；未模拟生产队伍、实际暴露、玩家行为、活跃后选择、聚类方差或全局规模效应。
