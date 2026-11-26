# 增量快照基准：来源与验证范围

1. Glenn Fiedler，[Snapshot Compression，Delta Compression](https://gafferongames.com/post/snapshot_compression/#delta-compression)：作者方案只对已确认收到的旧快照作增量，并讨论初始已知状态或独立数据块。本文进一步区分收到、应用成功及缓存留存；保留边界不是作者报告中的实验结果。
2. Quake III Arena，[固定源码 dbe4ddb](https://github.com/id-Software/Quake-III-Arena/tree/dbe4ddb10315479fc00086f08e25d968b4b43c49)：`code/client/cl_input.c:666–707` 为消息 ACK/有效快照门控；`code/server/sv_client.c:1247–1258, 1425–1429` 为 delta 形式分流；`code/server/sv_snapshot.c` 的 `SV_WriteSnapshotToClient` 另验旧帧与实体保留；`code/client/cl_parse.c` 的 `CL_ParseSnapshot` 检验有效、精确编号和实体记录范围，拒绝把无效新快照提交为当前快照。`CL_ParsePacketEntities` 可使用共享初始实体基线；没有声称解码中完全没有副作用，或非 delta 帧是整个世界的裸状态。
3. [实际 Python 模型和输出](../实验/snapshot-retained-baseline/README.md)。推导假设同流同代、已展开序号、上限 D、接收晚窗 R、不会早于合约回收。环的大小覆盖可能引用的编号，不填补未成功收到或未解码的历史空洞。

查阅时间：2026-11-26（北京时间）。
