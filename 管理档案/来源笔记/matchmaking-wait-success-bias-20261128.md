# 匹配等待的成功者偏差：来源与验证

[正文](../../GameLibrary/数据分析/指标设计/玩家行为/匹配成功的人等得更少，排队真的变快了吗.md) · [SQLite 试件](../实验/匹配等待的成功者偏差/README.md)。查阅 2026-11-28。

- [AWS MatchmakingTicket](https://docs.aws.amazon.com/gameliftservers/latest/apireference/API_MatchmakingTicket.html)，StartTime、Status 及游戏会话字段。托管状态准备好不是已进服；CANCELLED 原因不统一；没有据此假定字段任意状态必有，也没有用文档示例推断日期单位。
- [AWS Searching](https://docs.aws.amazon.com/gameliftservers/latest/flexmatchguide/match-events-matchmakingsearching.html)、[Succeeded](https://docs.aws.amazon.com/gameliftservers/latest/flexmatchguide/match-events-matchmakingsucceeded.html)、[事件概览](https://docs.aws.amazon.com/gameliftservers/latest/flexmatchguide/match-events.html)：新票与回队、成功及 CloudWatch Events 投递边界。未试用服务或声称 AWS 给出完善历史台账。
- 教学比例、未知范围、nearest-rank 分位与到期分类是明示口径上的算术，用 Python 3.12.14/SQLite 3.53.1 执行。未证实生产字段、指标波动、真实样本、因果或分布拟合。覆盖证据在模型中独立供应，防止把无消息误作无事件。
