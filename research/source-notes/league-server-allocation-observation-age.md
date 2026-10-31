# League 服务器分配：来源定位与证据边界

对应 [CASE-NET-001](../../case-studies/network/league-server-allocation-observation-age.md)。访问日期 2026-10-31。

原始来源：[Riot Tech Blog: Improving Performance by Streamlining League’s Server Selection](https://www.riotgames.com/en/news/tech-blog-cpu-usage)，作者 Tomasz Mozolewski，页面日期 **2025-01-16**，英语，第一方历史技术报告。正文介绍作者与 Robin Maddock 的技术负责人身份；不据此推断当前职务。版本无代码提交或运行环境可供本次独立验证。

实际阅读正文：
- The Old and the New / The Goals：当次文本视图 23–49 行。
- Building a Simulation / Game Cost / Game Duration / Game Starts：50–98 行。
- Auto Scaling / Solution Criteria：115–162 行。
- Results / Scoring：163–246 行。
- Live Results / Learnings：251–287 行。

行号为本次网页文本定位，不是不可变源码锚点；优先用章节标题回查。未读取评分公式图片、附录算法解码图片或图表像素数据。没有下载数据、运行算法或推算图形坐标。正文的算法名称也不构成完整实现说明。

证据分层：历史模拟报告、历史线上比较、原创建议分别标明。源文 40%→50% 的目标变化不能写成不加说明的“提高 10%”；本文不需要这个数字及成本比例。来源的输入采集粒度、策略刷新周期、机器准入约束和未来需求是不同概念。未根据“排名不依赖指标”推导整套系统不需要遥测或容量约束。

完整原始数据、精确线上比较日期与因果控制未核实；不能据此给出新的收益预测。来源所述同类硬件的简化与不同大小的场景变化，不被改写为混合硬件实现保证。正文五方工作表与验收问题均为原创未执行分析，不是 Riot 内部制度。

既有岗位与配置事故案例不构成本次分配策略的运行证据。本文不创建模拟 benchmark，不使用虚构玩家数据，不声称某策略普遍最优。
