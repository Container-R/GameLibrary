---
id: SOL-GFX-003
title: 呈现队列与输入时效：为何 MAILBOX 和图像数量不能单独给出延迟
type: solution
status: source-backed
primary_discipline: GFX
related_disciplines: [ENGINE, PROG, PLATFORM, UX, QA]
related_roles: [rendering-programmer, engine-programmer, gameplay-programmer, qa-engineer]
related_topics: [presentation-queue, swapchain, input-sampling, frame-pacing, latency-boundary, present-wait-semaphore-reuse]
engines: []
platforms: [Vulkan-WSI-documentation, Windows-DXGI-documentation]
versions: ["Vulkan 1.3.296，2024-09-26，486e4b289053a7d64784e7ce791711843c60c235", "Microsoft DXGI 1.3 / Direct3D 11.2 指南，页面更新2022-10-20", "Khronos Vulkan Guide 固定快照 82887e8444045655cc4578827e4183be9de593ff，2026-10-23"]
updated_at: 2026-11-01
review_after: 2027-02-01
verification_method: 固定 Khronos 规范、同步指南与 Microsoft 平台指南正文核对；有限时间线及同步对象身份反例为原创未执行推演；未创建呈现链、运行渲染或验证层、测量输入到光子延迟
sources:
  - https://github.com/KhronosGroup/Vulkan-Docs/blob/486e4b289053a7d64784e7ce791711843c60c235/chapters/VK_KHR_surface/wsi.adoc
  - https://github.com/KhronosGroup/Vulkan-Docs/blob/486e4b289053a7d64784e7ce791711843c60c235/chapters/VK_KHR_swapchain/wsi.adoc
  - https://learn.microsoft.com/en-us/windows/uwp/gaming/reduce-latency-with-dxgi-1-3-swap-chains
  - https://github.com/KhronosGroup/Vulkan-Guide/blob/82887e8444045655cc4578827e4183be9de593ff/chapters/swapchain_semaphore_reuse.adoc
---

# 呈现队列与输入时效：为何 MAILBOX 和图像数量不能单独给出延迟

## 问题：替换的是哪一处等待

“改成 MAILBOX”“把交换链改成两张图”是配置选择，不是输入延迟的测量结果。若旧工作还在应用或 GPU 端等待，呈现端替换一个待显示请求，并不自动撤销那些工作；若帧早已采样了旧输入，最后显示的是较新的提交，也不保证包含较新的输入。

本文提出一套**定位干预点的诊断方法**，而不是推荐统一呈现模式。适用于审查呈现/帧节奏改动的理由与验收范围；不涵盖可变刷新、特定合成器调优、多显示器策略或具体引擎接入。没有运行可执行模型或渲染实验。

## 1. 官方机制支持到哪里

以 Vulkan 1.3.296 固定文本为准：MAILBOX 在呈现端保留单个待处理请求，新请求可替换该项；FIFO 按顺序处理，并是必须支持的模式。MAILBOX 是否可用仍需查询，不能从枚举存在推断支持。[S1]

`minImageCount` 是创建时要求的最小图像数，不是实际图像数或延迟。规范提醒不要依赖 `vkAcquireNextImageKHR` 必然阻塞来控制生成节奏；获取返回不等于可安全访问图像数据；访问前须等待相应 semaphore 或 fence 发出信号。`vkQueuePresentKHR` 的队列操作范围不含呈现引擎对图像的实际处理，具体呈现时机依平台而定。[S2]

因此下面这些数量必须分开：图像存储容量、应用已准入的帧工作、GPU 待处理工作、呈现端待处理请求。它们可能相互约束，但不是同一个计数。由上述机制不能推出“有三张图就固定多两帧延迟”，也不能推出“MAILBOX 会取消此前的 GPU 渲染”。

### 1.1 正常循环中的同步对象：帧槽结束，不是 present 等待结束

这里有一项独立于延迟优化的正确性决定。Khronos 固定指南说明：等待渲染提交的 fence，不能保证 `vkQueuePresentKHR` 对 `pWaitSemaphores` 的使用已经结束；重新获取同一交换链图像并等待相应 acquire 同步对象，才建立其方案所需的复用条件。指南因此按**实际交换链图像数**分配这些二值信号量，再按取得的 `image_index` 选择。[S4]

**原创未执行反例：** 假设有两个在途帧槽、三张交换链图像 A、B、C。帧槽 0 渲染 A，提交 signal S0，随后 present 等待 S0。槽 0 再次轮到时，CPU 已等到该槽的提交 fence；这次获取的是 C。如果仅凭槽号再次 signal S0，就把“槽 0 的渲染提交结束”误当成“A 的 present 已不再使用 S0”。这里不是声称观察到了冲突，而是指出现有等待不足以证明这次复用安全。两个计数不同只是让身份错配更明显，并不意味着计数相同就能免除同步要求。

正常成功路径的接收重点是：**数组容量、图像索引、acquire 等待三者一起核对**。若取得 C，就选与 C 对应的 present-wait semaphore，并保留 acquire 的同步关系；不能把 CPU 得到索引的返回时刻当作等待完成。在指南所示、同步设置有效的普通 `vkQueueSubmit` 路径中，可由 GPU 提交等待 acquire semaphore，再 signal 对应的 present-wait semaphore，不必为此额外增加一次 CPU 阻塞；这里不推广到任意 `vkQueueSubmit2` stage mask 配置。帧 fence、命令缓冲和 acquire semaphore 仍可按各自的帧槽寿命管理，不是把所有数组一律改为图像索引。[S4]

这个片段只讨论持续呈现的正常循环，不提供完整可运行实现，也不覆盖获取失败、交换链重建、关闭、队列族或扩展路径。先前 presentation 操作及其 semaphore 等待结束，也不等于那张图像实际显示给了用户：请求可能被替换或丢弃。本文没有运行驱动或验证层，不给后面的假设时间线增加任何实测依据。

## 2. 有限反例：相同模式，相同图像数，不同上游等待

以下全部数字是**原创假设，未执行、未测量**。只用于反驳“模式和图像数唯一决定结果”，不是 FIFO 与 MAILBOX 的性能比较。

共同前提：

- 两次假设运行均使用受支持的 MAILBOX，实际图像数相同，且本例有可用图像。
- 只考虑一个新的呈现请求，没有其他待呈现请求与它竞争；本例不触发 MAILBOX 替换。
- 时间单位为毫秒。输入状态在 `0` 被采样，CPU 准备在 `2` 完成，选定帧的 GPU 工作需要 `4`。
- 约定显示更新机会在 `16`、`32`；同步与平台处理均允许就绪帧赶上随后第一个机会。这是额外假设，不由“GPU 已完成”自动保证。
- B 中已有工作占用所需执行路径至 `18`，**选定帧不能与之重叠或绕过它**。仅称“另有 GPU 工作”不足以推出这一串行关系。

| 假设运行 | 应用阶段 | GPU 等待与执行 | 就绪时刻 | 假设更新时刻 | 采样到假设更新的年龄 |
|---|---|---|---:|---:|---:|
| A | `0` 采样；CPU `0–2` | 无此前等待；执行 `2–6` | 6 | 16 | 16 |
| B | 与 A 相同 | 等待 `2–18`；执行 `18–22` | 22 | 32 | 32 |

配置相同，额外的上游等待使选定帧错过本例第一个机会。单个呈现请求没有可替换的旧请求，不能借 MAILBOX 名称消去这段等待。若真实系统允许并行或提前完成，B 的前提就不成立，不能拿此表诊断它。

最后一列是**采样到假设图像更新的年龄，不是物理输入到光子的延迟**。真实设备输入发生/到达、采样相位、状态如何进入画面、扫描位置和像素响应都未包含。反过来，保持更新时刻不变而改变采样时刻，也会改变此年龄；这不授权随意重排玩法模拟或网络权威状态。

## 3. 先写干预点，再决定参数

下表是原创建议的变更评审单，尚未执行。接收方应能说明“我改变了什么等待”，而不只提供一个设置截图。

| 拟议改动 | 先明确的量与边界 | 需要区分的证据 | 不能凭设置推出 |
|---|---|---|---|
| 减少交换链图像 | 请求的最小数、实际数、图像可用性 | 实际容量与获取/同步等待，不把容量当占用 | 固定减少若干毫秒或若干帧 |
| 限制应用在途帧 | 工作准入点、允许领先多少、输入何时采样 | 相关输入/状态身份与提交工作关联；哪里发生等待 | 限制一定免费，或必然不损失 CPU–GPU 重叠 |
| 改变呈现模式 | 目标模式支持情况、请求保留/替换与刷新条件 | 呈现请求和实际显示的帧身份；丢弃的请求不是完成显示 | 上游工作也被取消；最新提交一定含最新输入 |
| 改变等待与采样顺序 | 等待发生在何处，采样的是哪一份状态 | 同一显示帧对应的采样时间，而非仅看 Present 调用时间 | 可不顾游戏模拟语义随意晚采样 |
| 验收端到端目标 | 起点是物理动作、应用收到事件还是状态采样；终点是什么 | 同一事件与显示变化的关联、所用时钟/同步方法及误差 | CPU 返回、GPU 完成或软件呈现标记等于光子变化 |

若缺少一段观察，应保留“未知”，而不是把其他时间戳相减填满延迟预算。若只观察到呈现端积压，本文 B 的上游等待并非既定原因；若显示端额外处理尚未知，不能把剩余时间一律归给 GPU。

## 4. DXGI 的独立例子：等待位置也属于设计

Microsoft 的 DXGI 1.3 指南介绍从 Direct3D 11.2 起可用的 waitable swapchain 技术：样例先等待，再处理事件、更新、渲染和呈现；并讨论较低帧延迟设置与 CPU–GPU 并行程度的取舍。[S3] 这提供一个具体平台上的问题切入点：不能只调队列容量而忽略生成新状态的时机。

**不要把这个 Windows 技术映射成 Vulkan 获取图像的保证。** 本文没有移植其样例、执行其 API，或证明该循环适合某个引擎。设置的 frame latency 数字也不是物理输入到光子的测量。选择更多并行、较少领先或不同呈现策略，必须结合该产品的吞吐、时效和平台条件；不是数值越小越正确。

## 5. 成本、替代与可证伪范围

限制领先可能减少陈旧工作，也可能减少重叠；更多可用图像可能缓解等待，但不能替代工作准入政策。不同呈现策略还有刷新与撕裂方面的条件。本文不提供统一最优值，不要求安装驱动或新测量工具，也不把理论图当成基准测试。

一项有界后续应先挑明目标：例如验证当前产品的等待主要位于 GPU 工作之前，还是呈现请求之后；关联同一帧的输入状态与各阶段观察。若实际记录否定串行假设、显示机会假设或帧身份关系，应修改诊断，而非以配置名称维护原结论。关于物理端到端目标，没有合适起止观测就不能验收。

## 来源及关联

主研究与独立来源审查均核对原文；[来源定位](../../research/source-notes/presentation-queue-latency-boundary.md)保留固定版本与 API 适用范围。本条是 source-backed，时间表和决策单都是未执行分析。

- **S1** Khronos，Vulkan 1.3.296，2024-09-26，固定提交 `486e4b289053a7d64784e7ce791711843c60c235`：[VkPresentModeKHR](https://github.com/KhronosGroup/Vulkan-Docs/blob/486e4b289053a7d64784e7ce791711843c60c235/chapters/VK_KHR_surface/wsi.adoc#L1545-L1563)。
- **S2** 同版本，[最小图像数](https://github.com/KhronosGroup/Vulkan-Docs/blob/486e4b289053a7d64784e7ce791711843c60c235/chapters/VK_KHR_swapchain/wsi.adoc#L267-L270)、[获取与节奏](https://github.com/KhronosGroup/Vulkan-Docs/blob/486e4b289053a7d64784e7ce791711843c60c235/chapters/VK_KHR_swapchain/wsi.adoc#L1065-L1091)、[呈现操作范围](https://github.com/KhronosGroup/Vulkan-Docs/blob/486e4b289053a7d64784e7ce791711843c60c235/chapters/VK_KHR_swapchain/wsi.adoc#L1368-L1389)。
- **S3** Microsoft，[Reduce latency with DXGI 1.3 swap chains](https://learn.microsoft.com/en-us/windows/uwp/gaming/reduce-latency-with-dxgi-1-3-swap-chains)，页面更新2022-10-20；动机说明、Steps 2/4。

- **S4** Khronos Vulkan Guide，[Swapchain Semaphore Reuse](https://github.com/KhronosGroup/Vulkan-Guide/blob/82887e8444045655cc4578827e4183be9de593ff/chapters/swapchain_semaphore_reuse.adoc)，快照提交 `82887e8444045655cc4578827e4183be9de593ff`，2026-10-23；Problem Statement、Discussion of Solution 与正常循环示例。快照日期不是章节最后修改日。访问2026-11-01。

关联：[图形程序职责](../../管理档案/历史正文/roles/rendering/graphics-programmer.md)负责将视觉需求与可观察成本/行为交接；[矩阵接口合同](matrix-major-interface-contract.md)讨论另一种数据边界，其证据不验证本条的呈现或延迟；[固定 Tick](../programming/fixed-step-simulation-boundary.md)的模拟时间规则也不等于显示时效。
