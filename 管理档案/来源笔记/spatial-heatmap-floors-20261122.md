# 叠层关卡热力图：来源与边界

| 主张 | 一手资料及具体位置 | 边界 |
| --- | --- | --- |
| 公开的开发实践曾用平面格查找死亡事件密度 | Brent Nash（Amazon Game Studios），[Building an Event-Based Analytics Pipeline for Amazon Game Studios’ Breakaway](https://aws.amazon.com/blogs/big-data/building-an-event-based-analytics-pipeline-for-amazon-game-studios-breakaway/)，Transmitting gameplay events 与 Analyzing gameplay data。前者给事发位置、ID、时间、竞技场；后者 SQL 对 El Dorado 的 player_death 在一米格内 COUNT(*)。 | 构建时的开发案例。该查询不含区域层、路线分母或楼层风险；不推断引擎剩余遥测字段，也不暗示正式发售。 |
| 复杂空间应保留三维及路径方向，二维概率图不能替代轨迹 | C. Bauckhage 等，[Beyond Heatmaps: Spatio-Temporal Clustering using Behavior-Based Partitioning of Game Levels](https://andersdrachen.com/wp-content/uploads/2014/07/beyondheatmapsspatiotemporalclusteringusingbehaviorbasedpartionioningofgamelevels_ieeecig2014.pdf)，IEEE CIG 2014，物理第 1–2 页 §II–III 与图 1；物理第 6–7 页 §V.A、图 4–5。作者从 Quake III 和 UT 2003 demo 提取三维位置，向量聚类得路点，相邻不同时序路点形成有向边；下跳与上返不必对称。 | 所谓 mesh 是聚合轨迹的 Voronoi 划分，不是烘焙导航网格。论文不是本示例楼层归因、低计数门槛、分母或缺失范围的来源。 |
| 路线覆盖图可定位从哪条非预期路绕道，再交设计师复查关卡 | Ubisoft 的 Jonathan Dankoff，[Game Telemetry with DNA Tracking on Assassin’s Creed](https://www.gamedeveloper.com/design/game-telemetry-with-dna-tracking-on-assassin-s-creed)，原 2012 文作者重刊，Part 3 的 Geographic representation。降落伞教学示例 8 名测试玩家，6 人按预期、2 人改走非预期路径；DNA Viewer 支持二维底图与生产建模资料导出的三维图。 | 不与文中另一张 138 人的上线后轨迹图混用；不评估做改动后的效果量，亦非楼层失败率。 |
| 同一世界投影可能导致数量与分层比例排序相反；已知尝试的区域和末端位置不同仍需区分 | 本文合成固定构建示例及 Node 输出。下层 10/200、上层 4/10，双层合图 14/210；刻意把连接器和未归类从双层对照剥离。 | 观测到结局的穿越比例，不是实际玩家表现或因果结论。已知开始但结局未知的情况可做简单的极端范围，不能替代漏采的开始事件或不对称观察窗。 |

调阅日期：2026-11-22。
