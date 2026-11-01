# Present fence 退役范围：主审原始来源记录

2026-11-01。范围仅为成功、合法启用 KHR maintenance1 路径的有限对象退役依据；不制定通用关闭流程。

## 直接读取与身份

固定 Khronos Vulkan-Docs 提交 `b94f8bd2d004d2949469d8a5071ee10eb7d23566`：

- `chapters/VK_KHR_surface/wsi.adoc` blob `003f12904c94dd7e791d0a6f2e59b5a8259f68a0`。读取7480–7545，包括被引用的 `common_present_fence`；8670–8755，包括 `VkSwapchainPresentFenceInfoKHR` 的对象范围、销毁条款、顺序和有效使用条件；6801–6868，包括 `vkDestroySwapchainKHR` 独立图像使用条件及图像内存寿命。
- `appendices/VK_KHR_swapchain_maintenance1.adoc` blob `3ff7648b1d6e33626a4d3af8c076a7657aa91a34`，全文。revision 1 /2025-03-31 是扩展记录，不是运行驱动身份。
- 官方当前 refpages：`VkSwapchainPresentFenceInfoKHR`、`vkDestroySwapchainKHR`、`VkPhysicalDeviceSwapchainMaintenance1FeaturesKHR`、`VkPresentInfoKHR` 和 `VK_KHR_swapchain_maintenance1`，直接读取正文、功能启用及相应有效使用条件。它们是访问时的生成页面，不能冒充旧 Vulkan 1.3.296 快照。
- 既有 `solutions/rendering/presentation-queue-latency-boundary.md` 前置元数据与 §1/§1.1、相关来源记录和 `research/source-notes/resource-release-and-reuse-routing.md`。仅使用 source-only 范围；未读取运行归档。

## 独立接受的区分

规范明确将一次 present 的等待信号量与特定交换链的全部过去请求分开。一个与该操作关联且已发信号的 present fence 可以提供前者的 present 使用退役证据；不能据此忽略其他使用或把另一交换链的历史请求自动结清。交换链还受 acquired image 使用完成、有效对象和 host 同步等独立条件约束。

同一队列、同一交换链的 fence 信号顺序是有限保证，不可跨对象或跨队列扩大。fence 状态必须结合其对应请求的身份读取；重置并复用后的裸句柄状态不能保留旧请求身份。没有测试实际 fence 时序或实现管理器。

该规范段还提醒 fence 不必等实际呈现完成。销毁句柄与展示完成或内部图像内存立即回收不能合并。这些是来源边界，不是已测平台行为。

新快照包含与旧章节不同的排布和条件文本；本次不外推无扩展路径或改变旧文献的历史结论。未研究完整失败恢复、未附 fence 的历史请求或 present_wait 替代方案。最终正文和独立评审待核对。

最终全文验收对象：`article.md` SHA-256 `ed63f32a206e95e62a1e999c889f4dae2b64b9143c3adf8dc54c28a839558725`。另直接核对固定 WSI 7670–7700 的 feature 条件，以及提交元数据所列2026-10-30 /Vulkan 1.4.367 文档更新。S/B/A 三项决定没有混用凭据；同队列同交换链的末项推论保留完整账目和本次 fence 身份前提。接受为有限来源说明，不改变旧呈现文章的历史版本及正常循环范围。
