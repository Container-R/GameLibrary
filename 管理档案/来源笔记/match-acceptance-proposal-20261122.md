# 匹配确认与提案代次：证据范围

| 主张 | 证据 | 边界 |
| --- | --- | --- |
| 接受流程和整张票重排 | [AcceptMatch API](https://docs.aws.amazon.com/gameliftservers/latest/apireference/API_AcceptMatch.html) 枚举和请求栏；[Ticket schema](https://docs.aws.amazon.com/gameliftservers/latest/apireference/API_MatchmakingTicket.html)。 | API 记 CANCELLED/SEARCHING；[指南](https://docs.aws.amazon.com/gameliftservers/latest/flexmatchguide/match-client-accept.html) 用 FAILURE 概述，并非本文采用的编程状态枚举。 |
| 有事件提案 ID，不等于存在按它的条件写入 | 官方 [PotentialMatchCreated](https://docs.aws.amazon.com/gameliftservers/latest/flexmatchguide/match-events-potentialmatchcreated.html)、[AcceptMatch](https://docs.aws.amazon.com/gameliftservers/latest/flexmatchguide/match-events-acceptmatch.html)、[AcceptMatchCompleted](https://docs.aws.amazon.com/gameliftservers/latest/flexmatchguide/match-events-acceptmatchcompleted.html) 的 detail.matchId；[AcceptMatch 请求](https://docs.aws.amazon.com/gameliftservers/latest/apireference/API_AcceptMatch.html#API_AcceptMatch_RequestSyntax) 与 [Describe 响应](https://docs.aws.amazon.com/gameliftservers/latest/apireference/API_DescribeMatchmaking.html#API_DescribeMatchmaking_ResponseSyntax)。 | API 没有公开“当前提案必须仍是 P1”的请求参数。无生产实现证据，不推断服务内部或 AWS 重试会错写。 |
| 通知不是完整状态库 | [FlexMatch notifications](https://docs.aws.amazon.com/gameliftservers/latest/flexmatchguide/match-notification.html)，通知可能丢失；[EventBridge for GameLift Servers](https://docs.aws.amazon.com/eventbridge/latest/ref/events-ref-gamelift.html) 的尽力投递。 | 不能用确切事件次序和可靠性替代自有状态归并。 |
| 原子记录、外部消费去重和权威时刻 | AWS [idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)、[transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)、[SQLite transaction](https://www.sqlite.org/lang_transaction.html)；[两份实际运行材料](../实验/匹配确认与提案代次/README.md)。 | 时间、提案代次和显示修订规则是应用示例。SQLite 的单写者结果不外推其他数据库；没有执行外部分配。 |

调阅日期：2026-11-21。
