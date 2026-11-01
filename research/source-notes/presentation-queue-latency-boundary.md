# 呈现队列与输入时效：来源定位

关联[呈现队列与输入时效](../../solutions/rendering/presentation-queue-latency-boundary.md)。访问日期2026-11-01。仅有原文核对与原创推演；没有呈现链、渲染或物理延迟实验。

## 固定 Khronos 范围

Vulkan-Docs `v1.3.296` 的 annotated tag `7353f6ced118815d61852a739b9eae6f0055d77a` 指向提交 `486e4b289053a7d64784e7ce791711843c60c235`，更新日期2024-09-26。选择历史固定文本，不以移动 latest 页面中的新增枚举补充其承诺。

- [surface/wsi.adoc](https://github.com/KhronosGroup/Vulkan-Docs/blob/486e4b289053a7d64784e7ce791711843c60c235/chapters/VK_KHR_surface/wsi.adoc#L1545-L1563)：`VkPresentModeKHR` 的 MAILBOX/FIFO 定义。
- [swapchain/wsi.adoc](https://github.com/KhronosGroup/Vulkan-Docs/blob/486e4b289053a7d64784e7ce791711843c60c235/chapters/VK_KHR_swapchain/wsi.adoc)：`VkSwapchainCreateInfoKHR` 267–270；`vkAcquireNextImageKHR` 1065–1091；`vkQueuePresentKHR` 1368–1389。回查时优先按命名章节定位，行号用于固定提交。

正文区分的是这些接口的保证边界，不是对全部平台、扩展或实现的断言。上游工作取消、时钟相关性和物理显示响应均未由这些段落得到验证。

## Microsoft 独立平台例子

[Reduce latency with DXGI 1.3 swap chains](https://learn.microsoft.com/en-us/windows/uwp/gaming/reduce-latency-with-dxgi-1-3-swap-chains)，Microsoft Learn，页面最后更新2022-10-20。读取动机、Step 2 与 Step 4 的正文及顺序；技术范围为其说明的 DXGI 1.3 / Direct3D 11.2 waitable swapchain。没有执行样例，不将其条件套到 Vulkan。

## 原创分析范围

16/32 毫秒时间线、串行占用、下一更新机会和有限评审表均是本文假设/建议，不是规范给出的数字或实测记录。只在假设内比较采样状态年龄，不称为 input-to-photon。没有来源图表、长代码或硬件测量资料复制；事实短述集中在正文。

## 2026-11-01 增补：present-wait semaphore 的正常循环复用

既有 Vulkan 1.3.296 与 Microsoft 来源记录及时间线假设保留不变。本次补充一个同步对象选择机制，不把指南当作独立驱动验证。

- **S4** Khronos Vulkan Guide，*Swapchain Semaphore Reuse*，固定提交 `82887e8444045655cc4578827e4183be9de593ff`（快照提交日期 2026-10-23，不据此推定本章最后修改日期），访问 2026-11-01。[固定原文](https://github.com/KhronosGroup/Vulkan-Guide/blob/82887e8444045655cc4578827e4183be9de593ff/chapters/swapchain_semaphore_reuse.adoc)。定向依据 *Problem Statement*、*Discussion of Solution* 及正常循环示例；按章节标题定位。复用事实短述集中于正文 §1.1，不复制上游伪代码。
- 与既有 **S2** 的 [acquire 返回与同步区分](https://github.com/KhronosGroup/Vulkan-Docs/blob/486e4b289053a7d64784e7ce791711843c60c235/chapters/VK_KHR_swapchain/wsi.adoc#L1065-L1091) 联读。Guide 的固定提交与历史规范版本分别标示，不以指南日期推定规则首次生效时间。
- 两个帧槽、三张图像与 S0 的身份反例是原创假设，不是上游示例的执行结果，也未证明某次实际 present 尚未完成。新片段没有变更原 16/32 毫秒时间线的数值、串行条件或显示机会假设。
- 未创建交换链、运行驱动／验证层或模型，未测量延迟；未据指南末尾扩展讨论制定重建、关闭或错误恢复方案。
