# 消耗钥匙关卡的软锁检查：取证记录

## 原始来源

- Joris Dormans, *Adventures in Level Design: Generating Missions and Spaces for Action Adventure Games* (PCG Workshop 2010)，[PDF](https://pcgworkshop.com/archive/dormans2010adventures.pdf)，§2 分别说明任务图与空间图；§6 讨论任务、空间等不同层级。论文中的能力／可复用道具关系不是本文的可消耗钥匙模型。
- Christopher Durham、Chris Alvin, *Shortest Walk in a Dungeon Graph* (37th FLAIRS, 2024)，[DOI](https://doi.org/10.32473/flairs.37.1.135299)、[PDF](https://journals.flvc.org/FLAIRS/article/download/135299/139628/259510)，§2–3。原文由地牢图样例引入一次性拾取与消耗钥匙的锁门，搜索状态区分库存、拾取和已开锁；它求最短行走，不检验所有可达状态是否存在完成延续。

## 本文推导与实验

本文算法从初态展开完整可达图，再从成功终态沿保留的入边反向标记，差集提供无成功延续的状态。首次发现路径只用于见证；保留非树边才不漏掉合法恢复。成功谓词必须表示本次挑战结束；原路继续与进度丢失后重试是不同验收口径。

[实验及复现](../实验/消耗钥匙关卡的软锁检查/README.md)。用 `python3 -B check.py | cmp - observed.json` 重放五个离散、确定性的小图。可达／坏状态分别为 4／2、7／0、5／0、10／3、6／2。坑里的三个状态来自同一位置、不同库存及门／拾取组合。另一配置直接对比同在大堂且都零把钥匙，却因已开门不同而一可完成、一不可完成。开锁与进门在试件里原子发生，完成房间为终点，主动拾取至多一次；没有碰撞、引擎或外部关卡输入。原创 DOT 与 PNG 只画基线，虚线不进入转移。

输出 SHA256：`f534c8528bb0f593938d7946d254b813554725ca7b4ba7e2be2fae7450722298`。图 SHA256：`7538a6d6093998b133c6842e9f22266acb50704aa6a429e4b5d95815caaf4428`。失败样例的界限是指定有限规则下的穷举，不是对任何商用关卡或玩家策略的覆盖。
