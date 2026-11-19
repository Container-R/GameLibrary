# 复制实体重新接入：来源与证据

- Epic Games，[Actor Relevancy](https://dev.epicgames.com/documentation/en-us/unreal-engine/actor-relevancy-in-unreal-engine)，UE 5.9。开头与 Obtain an Actor’s Relevancy：判断针对连接，动态生成复制 Actor 失去相关性时从客户端移除；不据此推断服务器销毁。
- Epic Games，[Actor Network Dormancy](https://dev.epicgames.com/documentation/en-us/unreal-engine/actor-network-dormancy-in-unreal-engine)，UE 5.9。休眠期间两端可仍保有 Actor；休眠对象通常不检查相关性，文档列出特定 Replication Graph 配置例外。
- Unity，[Optimizing your game](https://docs.unity.cn/Packages/com.unity.netcode@1.4/manual/optimizations.html)，Netcode for Entities 1.4.0，Relevancy 说明按连接标记及退出与角色死亡不同。Limiting Snapshot Size / Importance Scaling 说明每份消息没列到某个实体也可能只是预算问题。
- Unity，[Ghost snapshots and synchronization](https://docs.unity.cn/Packages/com.unity.netcode@1.4/manual/ghost-snapshots)，Netcode for Entities 1.4.0，Should you use ghosts or RPCs?：宝箱状态应能随实体同步，不以一次 RPC 代替当前事实。

副本期、退出水位、初始快照确认策略及实验数据都是原创设计示例，不是这些引擎的内部字段、线上的实际协议或兼容保证。试件见[复现实验](../实验/实体副本期与首份快照/README.md)。两个试件只固定一个会话和实体生成代。
