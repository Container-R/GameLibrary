# 来源笔记：服务器历史目标与门的时间域

对应正文：[延迟补偿查的是旧目标，门也用旧状态吗](../../GameLibrary/网络与在线服务/实时同步/延迟补偿/延迟补偿查的是旧目标，门也用旧状态吗.md)。

| 要证实的内容 | 查读的原始资料 | 不延伸至 |
| --- | --- | --- |
| Valve 示例里，命令 tick 的换算目标可以被重新选择；相邻有效记录可插值，部分无插值路径复制记录 | Valve Source SDK 2013 固定 be57e3d01ac7d7aa6a2cacbfef187c0b46616db0，[目标](https://github.com/ValveSoftware/source-sdk-2013/blob/be57e3d01ac7d7aa6a2cacbfef187c0b46616db0/src/game/server/player_lagcompensation.cpp#L379-L412)、[仅在模拟时间推进时新增记录](https://github.com/ValveSoftware/source-sdk-2013/blob/be57e3d01ac7d7aa6a2cacbfef187c0b46616db0/src/game/server/player_lagcompensation.cpp#L290-L315)、[记录](https://github.com/ValveSoftware/source-sdk-2013/blob/be57e3d01ac7d7aa6a2cacbfef187c0b46616db0/src/game/server/player_lagcompensation.cpp#L450-L538)。项目 [2026-11-01 早期研究笔记](https://github.com/Container-R/GameLibrary/blob/a280f1b2f0b7e781f93f50e56e1ece35c6588e66/research/source-notes/lag-compensation-target-and-history-sample.md) 保留范围及更细分支 | RTT/2、完整姿态放置或动态门判定；样本计算是手算，不是 SDK 执行 |
| Fusion Hitbox 可取历史；SubtickAccuracy 使用插值；IncludePhysX 同次取当前普通 Unity 3D collider | Photon Fusion 2 [Lag Compensation，Queries](https://doc.photonengine.com/fusion/v2/manual/advanced/lag-compensation#queries) | 2D 物理、其他 SDK、线上性能 |
| 应在姿态正确后捕获；服务器 / 宿主 AfterTick | Photon Fusion 2 [Animation，Animations and Lag Compensation](https://doc.photonengine.com/fusion/v2/concepts-and-patterns/animation#animations-and-lag-compensation) | 自定义程序覆写了执行顺序后仍然成立 |
| 固定历史靶与线段时，先遇到的门取样时刻可以翻转规则结果 | [复现材料](../实验/延迟补偿的动态阻挡/README.md) | 层过滤和实际阻挡是项目规则；未运行 SDK |
