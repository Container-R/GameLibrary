# 程序化关卡的空间与任务可达性：出处

核读日期 2026-11-18。当前邻近《瓦片生成遇到矛盾，为什么不一定要放宽规则》处理 WFC 的局部约束分支、回溯及规则无解区分，并提醒不能把拼接合法当可玩。本稿深化最终含状态的地图验收，不复刻旧文约束例。

1. [Spelunky World 原版页面](https://spelunkyworld.com/original.html)区分 Classic 与 2012 HD，含原版源文件入口。没有自行构建或运行官方源码。
2. Darius Kazemi，[Part 1: The Solution Path](https://tinysubversions.com/spelunkyGen/) 和 [Part 2: Generating the Rooms](https://tinysubversions.com/spelunkyGen2/)，读两篇文字说明，4×4 网格，从位置路线决定包含下落口的房型，模板在要求的房型里变化。是原作的教学改版，文档自述只演示较早生成阶段；未以它宣称真实原版所有种子、后填危险物或平台运动都安全。
3. Joris Dormans、Sander Bakkes，2011，[论文作者存档](https://pure.hva.nl/ws/files/149264/453867_Dormans_Bakkes_-_Generating_Missions_and_Spaces_for_Adaptable_Play_Experiences.pdf)，第 III 节区分 mission 与 space；第 V 节印刷页 221、图 7–11 周边解释任务里的锁和钥匙、其前后位置交换。用原先任务次序与落到空间的区别支持流程；本文状态搜索是原创验证组件，不是论文算法的复刻。
4. 本文固定五房间测试见 [试件](../实验/程序化关卡的有状态通路/README.md)。把房间与钥匙合为状态，区分两次进大厅；只在完整枚举此有限模型时，无路线是模型结论。
