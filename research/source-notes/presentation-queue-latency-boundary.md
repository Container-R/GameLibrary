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
