# 房间名额：来源核对

本轮为北京时间 2026-11-26 00:50。[复现实验](../实验/房间最后一席的预留与确认/README.md)。

- [Amazon GameLift Servers](https://docs.aws.amazon.com/gameliftservers/latest/developerguide/gamelift-sdk-interactions.html#adding-a-player-to-a-game)，Adding a player to a game / Removing a player：检查空位、Reserved/Active/TimedOut/Completed 转移。GameLift Server SDK 不会发来此类超时通知，本文的延迟清理是自建服务的试件，不归因于它。
- [Nakama Go Match Handler](https://heroiclabs.com/docs/nakama/server-framework/go-runtime/function-reference/match-handler/#matchjoinattempt)：MatchInit 的标签可筛选列表，MatchJoinAttempt 执行接纳判定，MatchJoin 得到已成功加入的 presences。不声称示例等同于 Nakama 默认名额账本。
- [SQLite Transaction](https://www.sqlite.org/lang_transaction.html#deferred_immediate_and_exclusive_transactions)：只能同时有一个写事务，BEGIN IMMEDIATE 在已有写者时可报忙。本试件用超时 0 与确定性顺序显式读到忙，不声称所有部署都即时返回或具有相同锁粒度。
