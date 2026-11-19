# 非付费掉落保底：来源与证据

- UC Berkeley CS70，Spring 2024 [Note 19](https://sp24.eecs70.org/assets/pdf/notes/n19.pdf) §1–1.2；MIT OpenCourseWare [18.05 Class 4 §3.4](https://ocw.mit.edu/courses/18-05-introduction-to-probability-and-statistics-spring-2022/mit18_05_s22_probability.pdf#page=36)。尾部是多次未取到的联合概率；相同概率且独立才可直接取幂。本文次数包含成功那次。
- Digital Extremes，[Warframe Update 32.3 历史原发布说明](https://www.warframe.com/en/patch-notes/switch/32-3-0)：“Tauforged Archon Shard Probability Change” 与 “New Resources: Belric & Rania Fragments”。前者证实成功结算普通碎片后按颜色和玩家提升概率，以及等待既有轮换结束来切换；后者证实完整成功防守后给定额碎片，允许兑换部分轮换奖励。未推断当前版本、数据库、去重实现或全部获取途径。
- [复现材料](../实验/非付费掉落保底/README.md)：精确概率、资格与重复结算、旧版本迟到回执和等价格式离线迁移三套独立场景；单玩家单写入者，实物背包与网络均未接入。
- 将原支持文的几何等待推导并入唯一正式正文，原链接作为迁移入口保留；相邻成长经济文章仍负责收支与升级预算，不改其论证。
