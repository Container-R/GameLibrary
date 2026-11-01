# 释放与复用合同：先选择责任单位，再设计 adapter

假设集成层准备让各系统统一提供 `isDone / release`，在 done 后回收或复用对象。下面是**原创、未执行的接口审查路由**：它不反对统一调度入口、消息传输或记录格式，前提是保留带类型的责任、证据与允许动作；拒绝的是让一个无这些限定的布尔值抹掉不同系统的责任。四行来自已有来源研究，不是一次跨 SDK 实验，也不提出通用关闭屏障。

## 四个入口，不是四种写法的 resourceDestroyed

| 你真正要决定什么 | 转去核对的责任与证据 | 应退回的 adapter 推断 |
|---|---|---|
| 一份 NativeArray 分配是否已完成释放 | [普通值副本与释放依赖](nativearray-copy-and-disposal-ownership.md)：负责人先收束同步借用，并覆盖所有已调度消费者；延迟释放时保存返回的 disposal handle，需同步确认时 Complete 它 | 将 owner 的 `IsCreated=false` 当作 free 完成；将另一值副本的 true 当作访问或再次释放权。输入 lastUse 不是返回的释放依赖 |
| 本方是否还持有 catalog 加载操作引用 | [Addressables §4.1](../../solutions/engine/addressables-content-update-baseline.md)：明确自动或手动释放的互斥所有权政策；更新前核对相关旧加载操作的持有者 | 将“操作完成”当作已放弃引用，或把释放本方引用等同卸载 catalog、清空 bundle 缓存、取得最新远端内容 |
| 场景退出时是否继续保有所需音频 bank | [FMOD 生命周期退出段](../../solutions/audio/music-state-transition-contract.md)及[来源范围](fmod-event-bank-teardown.md)：先决定保尾部还是允许中断；bank 管理方结合项目结束记录、其他使用者及卸载政策作决定 | 由一次 STOPPED / DESTROYED 通知直接批准所有 bank 卸载，或把实例 release 当作 bank 保留权、声学尾部完成证明 |
| 正常持续呈现中，某个 present-wait semaphore 能否再次使用 | [Vulkan §1.1](../../solutions/rendering/presentation-queue-latency-boundary.md)：沿固定指南的正常路径，以实际交换链图像数与 image index 对应资源，并满足重新获取该图像的 acquire 同步关系 | 将帧槽提交 fence，或 CPU 取得 image index 的返回，替代该同步条件；把复用许可当作图像已显示或关闭／重建回收许可 |

这里的四种输出分别是**分配释放完成、本方操作引用放弃、bank 持有政策决定、下一次同步对象复用许可**。若适配层把它们都改名为 `resourceDestroyed=true`，下游就可能采取并未被支持的动作。也不能反过来把每份 struct 或 handle 都当作新增一次拥有引用。

## 一个小型接收记录，而非公共生命周期枚举

对每个 adapter，要求设计者填写以下四项；字段用于评审，不是声称有一套现成跨平台 API：

1. **责任单位与负责人：** 哪一份分配、哪一份本方操作引用、哪些所需 bank，或哪张交换链图像对应的同步对象？普通值副本、共享使用者与帧槽不能暗中互换。
2. **当前路径与允许动作：** 是正常循环复用，还是场景退出中的资源政策？只允许下一次 signal 的证据，不能被关闭队列消费成“可销毁全部对象”。
3. **依赖覆盖与完成证据：** 谁仍可使用对象，哪些同步借用已结束，哪些 job 或 acquire 等待被覆盖，哪些其他持有者仍未知？事件通知还需携带所指实例与政策，不能假定延迟处理时原句柄仍可查询。
4. **明确不授权的动作：** 填入本行尚未证明的动作，例如继续借用、下载最新版、保证可听尾部或销毁交换链。未知项保留未知，不能由别的 adapter 的 done 补齐。

**原创反例审查：** 某 retire 队列收到“数组 owner 已清空”“catalog load 已完成”“事件已 STOPPED”“帧提交 fence 已 signal”四类消息。统一执行“release 后允许后继复用”并不是充分合同。它们应分别进入释放依赖核对、操作引用所有权处理、bank 使用者与产品政策审查、图像关联的 acquire 同步检查，而不是统一再等待一个固定时长。四条是假设的独立接入需求，不是同一产品中发生过的一段时间线。

收束新使用者也不等于取消已正确登记的工作；例如在合法释放依赖中的既有 job 仍须完成。此处没有实现取消、失败恢复、并发 owner 管理或自动依赖发现，不能作为生产级资源管理器的验收结果。

## 阅读与证据边界

2026-11-01 综合。各入口保留各自的固定源码或官方版本化文档及限制；本文只使用其 source-only 部分，不借音乐假端口模型或其他实验认证 SDK。没有执行 API、验证层、模型或声音检查，也没有性能与等待时长结论。具体版本和本次材料身份在[审查记录](../audits/resource-release-routing/AUTHOR-NOTES.md)中分开列示。
