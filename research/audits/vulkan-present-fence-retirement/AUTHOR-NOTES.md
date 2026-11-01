# 作者说明：Vulkan present fence 退役覆盖

2026-11-01。拟发布正文：`research/source-notes/vulkan-present-fence-retirement-coverage.md`；本说明拟置于 `research/audits/vulkan-present-fence-retirement/AUTHOR-NOTES.md`。当前仅候选，等待独立技术审查。

## 来源身份与实际范围

Khronos Vulkan-Docs 固定提交 `b94f8bd2d004d2949469d8a5071ee10eb7d23566`，提交说明标识2026-10-30的Vulkan1.4.367文档更新。实际通过只读 GitHub 接口取得并定向阅读：

- [chapters/VK_KHR_surface/wsi.adoc](https://github.com/KhronosGroup/Vulkan-Docs/blob/b94f8bd2d004d2949469d8a5071ee10eb7d23566/chapters/VK_KHR_surface/wsi.adoc)：`VkSwapchainPresentFenceInfoKHR` 8677起、共用信号条件7493起、`vkDestroySwapchainKHR` 6801起、`VkPresentInfoKHR` 的feature门7688起。只使用选定段落，不声称通读该大文件。
- [KHR maintenance1 固定附录](https://github.com/KhronosGroup/Vulkan-Docs/blob/b94f8bd2d004d2949469d8a5071ee10eb7d23566/appendices/VK_KHR_swapchain_maintenance1.adoc)：扩展定位与revision1的2025-03-31元数据。这个日期不是全部条款的最后修改日，也不代表任一驱动实现版本。

另于2026-11-01直接阅读官方 rolling refpages：

- [VkSwapchainPresentFenceInfoKHR](https://docs.vulkan.org/refpages/latest/refpages/source/VkSwapchainPresentFenceInfoKHR.html)
- [vkDestroySwapchainKHR](https://docs.vulkan.org/refpages/latest/refpages/source/vkDestroySwapchainKHR.html)
- [VkPresentInfoKHR](https://docs.vulkan.org/refpages/latest/refpages/source/VkPresentInfoKHR.html)
- [VK_KHR_swapchain_maintenance1](https://docs.vulkan.org/refpages/latest/refpages/source/VK_KHR_swapchain_maintenance1.html)
- [VkPhysicalDeviceSwapchainMaintenance1FeaturesKHR](https://docs.vulkan.org/refpages/latest/refpages/source/VkPhysicalDeviceSwapchainMaintenance1FeaturesKHR.html)

这些是同一 Khronos 规范体系的源文与生成页面，不是独立实现验证。能力查询和启用的描述来自官方 feature 页；本次没有实际查询或启用设备。来源发现阶段还读过 present-wait 页用于排除不当替代，但其行为、错误处理与其他扩展不纳入正文结论。

## 原创部分及边界

P(A,B)、S、FA/FB 是原创未执行情景。只从成功入队、合法feature与同步设置、完整请求记录和无其他S使用等前提出发；“FB未知”不伪装成实际未signal观察。有限结论按 semaphore 与 swapchain 分别接收，没有把任一 fence 变成所有资源已关闭的标记。

请求/交换链/fence本次使用的记录建议为原创。末项简化只在同一queue、同一swapchain、完整覆盖且身份未丢失时讨论；不补造跨队列顺序，不要求或推荐具体容器实现。

正文不描述旧 wait-idle 行为，也不借新快照改写旧Vulkan1.3.296文章。没有任何驱动、验证层、图像、声音或计时执行；不转载上游完整章节、代码或图表。没有更改既有文章、来源索引、实验或远端内容。

## 候选精确绑定

`article.md` 完整UTF-8 SHA-256：`ed63f32a206e95e62a1e999c889f4dae2b64b9143c3adf8dc54c28a839558725`。
