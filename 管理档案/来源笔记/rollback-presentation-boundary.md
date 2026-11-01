# GGPO重放与表现输出：来源定位

补充[客户端预测与权威边界](../../GameLibrary/网络与在线服务/实时同步/移动预测/客户端移动预测与服务器纠正.md)。读取2026-11-01；仅源码/文档，不运行SDK。

统一固定提交：`7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a`，GitHub commit时间2019-11-07T17:39:58Z。以下初始三个文件属于同一作者项目，不构成三个独立厂商交叉验证；未建立任何安装二进制对应关系。

| 原始文件 | 已读定位 |
|---|---|
| [DeveloperGuide.md](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/doc/DeveloperGuide.md) | Game State and Inputs；save/load/free callbacks；frame-delay警示；Separate Updating Game State from Rendering；RNG及external time章节 |
| [ggponet.h](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/include/ggponet.h) | GGPOSessionCallbacks中的save/load/free/advance注释；flags保留字段不能当作确认令牌 |
| [sync.cpp](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/lib/ggpo/sync.cpp) | AdjustSimulation、LoadFrame、SaveCurrentFrame，另核对SetLastConfirmedFrame |

指南短闪烁例子在同段混用frames/seconds，本库只采用其定性风险，不自行修正数字后当成规范。文档要求、应用回调责任和代码实际调用路径分开理解；所读路径的推进/保存/恢复回调返回值未构成外部效果投递确认。不能把这项局部检查扩展为全SDK或所有集成的缺失证明。Sync中确有SetLastConfirmedFrame等内部确认帧机制；这里没有把它解释为外部输出或经济事务的确认保证。网页抽取行号与源码视图可能不同，定位采用固定提交、方法和章节名称。

正文五行情形及验收条件为原创未执行建议，不是GGPO公开内部表单或已经验证的事件协调器。原权威服务器模型与P2P回滚语境不同；原有16项模型测试保持原范围。本次未进行安装、编译、网络、音频、渲染或持久交易验证；未复制完整指南、源码或第三方案例图像。

## 2026-11-01 新增阅读：正常前进的预测屏障

仍固定于上游 `pond3r/ggpo` 提交 `7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a`。这是同一项目的新增调用链阅读，不增加独立厂商证据或运行验证。

- [main.cpp](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/lib/ggpo/main.cpp)：ggpo_start_session 创建 Peer2PeerBackend；ggpo_add_local_input、ggpo_synchronize_input、ggpo_advance_frame 检查非空 session 后委托对应方法，所读包装层没有另一道预测屏障。
- [sync.cpp 57–141](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/lib/ggpo/sync.cpp#L57-L141)：AddLocalInput 的双条件拒绝、SynchronizeInputs、IncrementFrame。
- [backends/p2p.cpp 263–338](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/lib/ggpo/backends/p2p.cpp#L263-L338)：提交错误映射、同步正常返回与单独推进。
- [input_queue.cpp 116–181](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/lib/ggpo/input_queue.cpp#L116-L181)：GetInput 的已有／预测输入分支及内部断言前提，不能省略为“同步总成功”。
- [VectorWar 329–439](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/apps/vectorwar/vectorwar.cpp#L329-L439)：AdvanceFrame、RunFrame、Idle，区分正常更新、绘制及服务。
- [ggponet.h 419–500](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/include/ggponet.h#L419-L500)：输入、同步与 idle 使用说明。另据其中 frame delay 须在首次同步输入前设置的前提，**未采用运行中动态调延迟建议**；内部队列分支不替代公开调用约束。

条件例与正常步控制流为原创未执行推导；没有展示可达网络轨迹、恢复时间或输入保留保证。仅限单本地玩家、初始化完成后的 P2P 正常前进，不套在回滚回调上。内部确认帧不被重命名为原服务器模型的 ack；idle 可涉及回滚，故不把分支拒绝写成全状态冻结。原始源码、示例及接口注释各自支持有限结论，没有新增 SDK、网络或模型执行。

## 正常步不能用后一次成功覆盖提交失败

只看最后一个返回码，会把两个不同决定混在一起。在上述固定P2P实现中，设当前帧为F、内部最后确认帧为C、预测上限为M，`AddLocalInput` 在 `F >= M` 且 `F-C >= M` 时拒绝，发生在本次输入进入队列之前。随后调用 `SyncInput` 并不会重新执行这道预测上限检查；它正常返回成功，不能补发先前遭拒的输入。[提交分支](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/lib/ggpo/sync.cpp#L57-L77)、[P2P两入口](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/lib/ggpo/backends/p2p.cpp#L263-L338)。

因此正常前进要保留每一步的结果：本地提交失败便停止本次正常推进；提交成功后才取同步输入，取成功后才推进玩法并通知完成该帧。网络服务和绘制仍有各自路径，不能一并停掉；服务可能触发回滚，所以这里也不是“整个游戏状态冻结”。此说明只针对初始化完成、单个有效本地玩家的正常P2P路径；不覆盖多个本地玩家部分提交或回滚回调。短按如何保留、重采样或消费仍由应用决定。

这是旧源分析的可读承接，2026-11-01再次核对固定sync/P2P分支；未运行GGPO，也未把条件式当成已构造的网络历史。旧条件例与完整适用限制见[固定历史支持](https://github.com/Container-R/GameLibrary/blob/1a7bf18b24ba56395892c4c0cdb3b2acecc16985/solutions/programming/client-prediction-authority-boundary.md#正常推进还有一道门预测上限拒绝不能被后续成功覆盖)。
