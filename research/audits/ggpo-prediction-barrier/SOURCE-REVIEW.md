# 独立源码门审查：预测屏障与宿主正常推进

2026-11-01。**接受窄的既有 GGPO 段落深化**。已读 gate，并核对当前预测文章的范围、验证方法和既有 GGPO 表现输出补充。前者为服务器权威模型，后者为 P2P 回滚源读；新内容不能合并两者的确认语义，也不能继承16项模型测试为 GGPO 实测。

## 独立重新读取的固定源码

全部固定于官方 `pond3r/ggpo` 提交 `7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a`，未运行。

- [Sync::AddLocalInput](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/lib/ggpo/sync.cpp#L57-L74)：拒绝条件确为 `F >= M && F-C >= M`，不是仅比较落后帧数；拒绝在本次输入的队列写入之前。
- [P2P AddLocalInput / SyncInput / IncrementFrame](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/lib/ggpo/backends/p2p.cpp#L263-L338)：本地提交先检查回滚、初始同步、玩家句柄；同步层拒绝映射为预测上限错误。SyncInput 检查初始同步后取输入，正常返回路径给出 OK，没有重复预测屏障。
- [SynchronizeInputs / IncrementFrame](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/lib/ggpo/sync.cpp#L105-L141)与[InputQueue::GetInput](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/lib/ggpo/input_queue.cpp#L116-L181)：输入可以来自已有队列或预测；有缓冲大小、预测错误状态、请求范围等断言前提。不能把不存在屏障检查改写成任意状态下调用必然成功。
- [VectorWar_RunFrame / Idle](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/apps/vectorwar/vectorwar.cpp#L395-L439)及同文件329–356：正常单本地玩家路径先检查提交结果，再检查同步结果，之后才更新游戏并通知 GGPO 前进。绘制在外层条件之后；idle 服务分开。
- [公开调用说明](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/include/ggponet.h#L419-L479)：同步输入也服务回滚帧；idle 涉及传输和回滚；frame delay 要在首次同步前设置，故不采用运行中调延迟建议。

## 有限推论与起草约束

取正 M、F=M、C=0，两个拒绝条件确实成立。这是手算条件例，不证明已构造一段达到该状态的真实网络历史。假设已完成初始同步、正常非回滚、有效单本地玩家提交与合法输入缓冲；若错误地继续调用 SyncInput，还须其内部队列/断言前提成立并正常返回，才能说后者会走到 OK。应写“该正常返回路径不重新实施此屏障”，而非“拒绝后同步必然成功”。

这个接口差异有独立价值：SyncInput 的成功不补接纳先前被拒绝的本地输入，也不替宿主决定这一正常模拟步可推进。上游示例保留外层提交结果，提供具体集成依据，不只是泛泛检查返回码。

停止的是**本次正常前进分支**，不能写成 SDK 冻结所有应用状态。尤其继续 idle 可能处理回滚；这与正常前进一步不同。绘制不必随该分支停掉，也不意味着输入短按一定保留。未接纳输入的保留、重采样或消费政策需另定。

排除多本地玩家部分成功恢复、其他后端、断连/恢复时长、最优预测窗口、确定性及服务端授权。`last_confirmed_frame` 不改称服务器 ack；不把正常分支的提交门套在回滚回调上。没有实际迟到、错误推进或成功恢复轨迹，没有读取运行档案或执行网络/程序。

结论：来源支持 gate 的受限机制，建议在写作中显式补出“内部前提成立且正常返回”的条件，并将失败不推进限定为正常前进分支。无需扩大场景或新增模型。
