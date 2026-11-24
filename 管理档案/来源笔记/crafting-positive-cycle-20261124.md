# 合成与拆解为什么能反复产出材料：来源记录

| 主张 | 来源及定位 | 适用范围 |
| --- | --- | --- |
| 每次转换需有足够输入库存，执行才消耗输入并产生输出 | Ákos Hajdu、Róbert Német、Szilvia Varró–Gyapay、András Vörös，2014，[Petri Net Based Trajectory Optimization](https://inf.mit.bme.hu/sites/default/files/publications/ASCONIKK2014_HajduEtAl.pdf)，§2.1 Dynamic behavior | 用有权值的输入和输出展示库存前提；游戏容量和站点电量另外建模。 |
| 发生次数满足状态方程只是可达性的必要条件 | 同文 §2.2 Reachability，状态方程定义及讨论 | 正文仅用状态方程做筛查；未运行或声称采用该论文的优化算法。 |
| 原创两配方在指定状态无上限时可反复增产，几个控制可阻断 | [六组整数状态搜索](../实验/合成与拆解材料循环/README.md)与正文的逐轮推导 | 八动作预算不证明无界；无上限基线的数学推导依赖无背包限制、无电量消耗和固定配方。 |
| 单轮收益要放回整体成长收支判断 | 本库[用收支记录检查单机游戏的成长经济](../../GameLibrary/游戏设计/系统设计/成长与经济/用收支记录检查单机游戏的成长经济.md) | 是设计校核方法，非本文夹具测量得到的玩家产出或虚拟市场预测。 |
