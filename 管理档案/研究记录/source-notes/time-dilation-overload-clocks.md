# Time Dilation：历史时钟政策与过载边界的来源定位

对应[固定 Tick 方案](https://github.com/Container-R/GameLibrary/blob/1a7bf18b24ba56395892c4c0cdb3b2acecc16985/solutions/programming/fixed-step-simulation-boundary.md)的来源补充。2026-11-01 实际读取下列三篇官方 EVE 原始开发日志英文正文；没有运行游戏、检查图像曲线或观看视频。以下日期是发表日期，不是精确软件构建版本。

| 来源 | 精确回查位置 | 用途与限制 |
|---|---|---|
| [CCP Veritas，Introducing Time Dilation (TiDi)](https://www.eveonline.com/news/view/introducing-time-dilation-tidi)，2011-04-22 | 游戏钟提案和长计时器段，正文返回行29–35；末段明确工作仍属初期 | 支持提案中的选择性时钟语义。例子与预期不作为上线结果，假想5%不作为已部署下限。 |
| [CCP Veritas，Time Dilation – How’s That Going?](https://www.eveonline.com/news/view/time-dilation-hows-that-going)，2012-02-10 | 开头行7；跳跃负载行18；node-level段行19 | 支持历史部署与影响范围说明。未核验当前拓扑；未从图像、外部战报或引述玩家评价推导结果。 |
| [CCP Veritas，HED-GP Technical Retrospective: What a HED-ache](https://www.eveonline.com/news/view/what-a-hed-ache)，2014-01-24 | 三种指标/下限/迟到量行9–13；原因不确定性行14–17 | 支持饱和后仍有积压及单位区分。可能原因不是被控制实验确认的结论，历史10%不是通用推荐。 |

以段落主题定位为准，网页行号可能变化。只采用原始开发者说明；搜索返回的百科、论坛镜像与外部战报没有作为独立证据。没有转载源图、长引文、任务调度器实现或完整原文。

文章的三类接收问题是原创解释，不是 CCP 的 API、运行手册或全量计时器清单。源码、反馈公式、采样周期、精确排队策略、当前服务状态和跨节点时钟同步都未由这些材料建立。来源补充没有改变已有 Python/Godot 夹具的验证对象，也没有增加一次实际过载测试。
