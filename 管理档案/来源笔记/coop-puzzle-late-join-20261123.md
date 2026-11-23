# 合作解谜晚加入：声明与证据

核对日期：2026-11-23。

| 正文位置与主张 | 原始资料和定位 | 观察与适用前提 |
| --- | --- | --- |
| 初次看到门：关联网络实体生成时，迟加入者收 NetworkVariable 当前值；过去的一次性 RPC 不做此事 | Unity Technologies，[NetworkVariables · NGO 2.7.0](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.7/manual/basics/networkvariable.html#networkvariables)，开篇、Initializing a NetworkVariable 及 Door 示例 | 网络物体已生成、字段可读；这是版本文档，不是本文运行过的引擎测试，也没有推断多对象一起取得快照。 |
| 初次看到门：服务器 NetMulticast 当时只对已经连接且 actor 相关的客户端 | Epic Games，[Remote Procedure Calls · UE 5.7](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-procedure-calls-in-unreal-engine?application_version=5.7#types-of-rpc)，Types of RPC 表 | 区分服务器调用与客户端调用。RPC 不提供本文所需的历史基线和后续连接同步。 |
| 快照交界、按收件人排序及恢复 | 同附录 `late_join_model.py`，`exercise` 三组对照 | 作者推导并实跑指定模型，并非引用某引擎默认协议。 |
| 一库内原子发放及重试 | SQLite，[Isolation In SQLite](https://www.sqlite.org/isolation.html)，Isolation Between Database Connections；附录 `reward_sqlite.py` | 原文说明独立连接只读到完整提交和写入串行化。试件约束收据唯一，只有首次记账，与收据同事务。SQLite 的观察不外推其它数据库。 |
