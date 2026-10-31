# 音乐适配器生命周期：纯状态模型

这是原创、标准库 Python 小模型，不导入或调用 FMOD、Wwise、Unity，不模拟音乐量化、线程调度、资源流式读取或设备输出。用于检验设计不变量，不能宣称中间件接入正确。

## 执行

```sh
cd research/experiments/audio-lifecycle
python -m unittest -v
```

2026-10-31 实际执行：7 个测试通过；其中一个枚举 8 种动作、长度 4 的全部 4096 条序列。精确调用列表断言覆盖关键路径，枚举检查重复命令、所有权、释放后使用等安全属性。结果见 `test-results.txt`。这是有界检查，不是无限状态证明；守卫不满足时动作是 no-op，因此不代表4096条互异有效产品场景。

## 模型 API 与假设

单线程串行调用，无锁、无真实回调。所有异步完成被外部测试驱动为一次原子调用。`generation` 是 begin 分配的正整数；handle 是不重复使用的非空字符串，重复 ready 表示同一完成的重投递，不是新分配。Ticket 是本模块生成或等价构造的不可变 generation/revision 对；输入可信，不作为安全边界或通用 API 校验器。

| 调用 | 语义 |
|---|---|
| begin(mode) | 只从 Stopped 开始；增加 generation/revision；等待 loader |
| ready(generation, handle) | loader 转移句柄所有权；取消/旧会话或冗余分配立即归原 owner 释放；重复完成不重复释放 |
| intent(mode) | 更新最新意图；不同值增加 revision；只在可用句柄上提交 |
| retry(ticket) | 仅当前 generation/revision 且仍存活时执行；旧请求丢弃 |
| invalidate_external_write() | 显式使成功缓存失效、增加 revision，并重新提交当前目标 |
| outcome(generation, handle, kind) | started 使本地 Starting→Active；start_failed 独立回收，不等 STOPPED；stopped 回收；旧通知忽略 |
| exit() | 逻辑取消；若已发 start 则发 stop；释放当前所有权；迟到 loader 仍可交付，但只能清理 |

FakePort 的有序 `calls` 记录每次 `mode/start/stop/release`，包括失败 mode 调用；测试使用列表或 Counter 断言，不通过集合去重掩盖重复副作用。`owned/started/released` 是模型状态，历史记录不回收，不能直接复制为长期产品实现。

### 明确简化

- FakePort 的 mode 可注入一次失败，返回 False；只成功才更新 submitted。start/stop/release 命令在本模型总是被接受，其自身同步错误和队列满未建模。
- 本模型在 mode 成功提交之后才发 start；这是自选适配策略，不声称所有中间件都必须或允许完全相同的 API 顺序。
- start 接受不变成 Active；后续 outcome 决定结果。START_FAILED 对应一个独立终止路径；不等待 STOPPED，也不自动重试复音拒绝。
- release 表示模型所有权移交/结束，而非证明底层立即释放内存。真实运行时释放时序、销毁回调、cookie/GCHandle 寿命与停止失败仍须另验。
- 同一会话只使用一个启动句柄；内部重启必须显式退出并新开会话。多实例淡入淡出不在范围。
- 正常情况下适配器是参数唯一写入者；若有外部写入，调用者必须主动 invalidate。未通知的外部变化不可由缓存模型发现，也不声称当前参数值等于 submitted。
- 句柄不复用使身份比较简化；真实句柄复用应另用实例 token/cookie 与 generation 绑定。
- 不同 generation、旧 revision 被过滤；并不模拟来自 SDK 的时间乱序概率。互相矛盾的迟到 start_failed 在 Active 时忽略。

## 已执行的关键场景

1. start_failed 独立完成，不依赖 stopped；随后 stopped 不能重复清理。
2. Starting 在资源就绪前取消，迟到 ready 只释放，重复 ready 不重复释放。
3. 新会话启动后收到旧会话 ready/outcome，旧 handle 清理不影响新 handle。
4. mode 首次失败未写成功缓存；同值 retry 能恢复且不重复 start。
5. 旧 revision retry 不覆盖新目标；成功同值请求去重；外部写入显式失效后重新提交。
6. Active 退出只 stop/release 一次，重复 exit/迟到 stopped 不增加调用。
7. 4096 条有界动作序列逐步检查：同 handle 的 start/stop/release 各不超过一次；调用 owner 与所有权表一致；释放后无 mode/start/stop；存活句柄属于当前 generation。

## 依据与验收限界

配套知识条目：`solutions/audio/music-state-transition-contract.md`。FMOD2.04官方 `EventInstance` 的 callback type 文档描述 START_FAILED（复音拒绝）不产生 STARTING/STARTED/STOPPED：
https://www.fmod.com/docs/2.04/api/studio-api-eventinstance.html

模型用该事实选择必须覆盖的失败路径；其余适配器政策是原创设计，不是 FMOD API 的仿真实现。量化、音频线程、尾音、播放声音、性能和 SDK 回调顺序均未验证。

独立附加检查见[对抗审查](../deep-model-qa/README.md)：200个固定种子各150次动作，审查4568条FakePort调用；最终退出由测试施加，不证明无需外部条件的活性。
