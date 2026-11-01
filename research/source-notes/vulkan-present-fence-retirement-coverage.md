# Vulkan present fence：先按对象核对退役凭据的覆盖范围

2026-11-01。依据 Khronos Vulkan-Docs 固定提交 `b94f8bd2d004d2949469d8a5071ee10eb7d23566`（Vulkan 1.4.367 文档更新），限定**支持并合法启用 `VK_KHR_swapchain_maintenance1` 的成功 present 路径**。以下是规范阅读与原创未执行推演，没有创建交换链、运行驱动或验证层。

## 新问题不是正常循环中的 semaphore 复用

[既有呈现说明 §1.1](https://github.com/Container-R/GameLibrary/blob/1a7bf18b24ba56395892c4c0cdb3b2acecc16985/solutions/rendering/presentation-queue-latency-boundary.md)讨论重新取得同一图像并满足 acquire 同步之后的正常循环复用，明确没有提供关闭方案。本篇问另一件事：有了扩展提供的 present fence，**哪一份 signal 证据能支持哪一个对象退役？**

这里的 present fence 是通过 `VkSwapchainPresentFenceInfoKHR` 附到 `VkPresentInfoKHR` 的 fence，不是渲染提交 fence。其数组按本次 present 的交换链条目对应；非空 fence 还须满足未 signal、没有关联其他未完成队列命令等有效使用条件。[固定规范：present fence](https://github.com/KhronosGroup/Vulkan-Docs/blob/b94f8bd2d004d2949469d8a5071ee10eb7d23566/chapters/VK_KHR_surface/wsi.adoc#L8677-L8745)

## 同一组凭据，有两个不同覆盖要求

规范对本问题给出两个不同量词：

| 要结束的责任 | present fence 所需覆盖 | 不能替代的判断 |
|---|---|---|
| 某次 present 操作关联的 wait semaphores | 该操作至少一个关联 fence 已 signal | 这不是所有交换链、所有历史请求均可销毁的证明 |
| 某个 swapchain 的过去 present 请求 | 指向该 swapchain 的全部过去请求所关联 fences 已 signal | 仍须满足其 acquired images 的其他使用完成及 host 同步等独立销毁条件 |

这是规范的对象范围区别，不是建议把所有资源放进同一队列后等一个通用 done。fence 的信号点可能早于呈现操作实际完成；它提供这里规定的资源退役条件，不提供“用户已经看见”的回执。[固定信号条件](https://github.com/KhronosGroup/Vulkan-Docs/blob/b94f8bd2d004d2949469d8a5071ee10eb7d23566/chapters/VK_KHR_surface/wsi.adoc#L7493-L7527)

另外，`vkDestroySwapchainKHR` 销毁相关句柄，并不保证呈现引擎立刻释放图像内存；所有 acquired image 使用完成的要求也没有被上述表格取消。[固定销毁条款](https://github.com/KhronosGroup/Vulkan-Docs/blob/b94f8bd2d004d2949469d8a5071ee10eb7d23566/chapters/VK_KHR_surface/wsi.adoc#L6801-L6868)

## 原创接收例：P 同时呈现 A 与 B

**未执行假设：**成功入队的 present 请求 P 同时提交交换链 A、B 的图像，等待二值 semaphore S，分别关联合法 fence FA、FB。应用不再把 S 用于其他工作，并为待退役对象收束新使用；不存在未记账的请求。其他图像使用和 host 同步仍各自核对。

现在只收到 **FA 已 signal** 的证据，FB 状态未知：

1. **S：**对于 P 对 S 的使用，已经满足“至少一个关联 fence”的条件。若 S 没有其他未完成使用，就不必仅因 FB 未确认而继续把 P 视为阻止 S 销毁的责任。
2. **B：**FA 不能借给 B 充当其全部历史请求的退役凭据。FB 未确认，不能按这条规则批准 B 销毁；“未知”也不意味着 FB 必定仍未 signal。
3. **A：**FA 证明的是关联请求的条件。只有 A 的其他过去请求也已被覆盖，且其他独立销毁前提满足，才能批准 A；不能把“当前这一项通过”改名为“A 的所有责任结束”。

因此接收记录至少应关联**请求 P、交换链条目、fence 本次使用及所保护对象**。在把完成证据记入相应责任之前，不应重置或重新分配该 fence 并丢失其原对应关系。这是原创跟踪建议，不是规范提供的现成资源管理器。

规范保证同一 swapchain、同一 `VkQueue` 上的 present fences 按呈现操作顺序 signal。因此，若完整账目确认所覆盖请求都满足这两个条件，且保留了 fence 本次使用的身份，最后一项 signal 可支持前序项已 signal 的判断。**不能跨队列、跨交换链，或越过未附 fence／未登记请求套用这一简化。** 本例的 FA 不因与 FB 来自同一调用，就变成 B 的末项凭据。

## 能力前提与停止边界

KHR maintenance1 是扩展能力，不由头文件有结构体或设备支持某个核心 Vulkan 版本自动成立。其依赖、支持查询与 device 创建时的 feature 启用须另行满足；未启用 `swapchainMaintenance1` 时，不能在 present 信息中附该 fence 结构。[扩展及依赖](https://docs.vulkan.org/refpages/latest/refpages/source/VK_KHR_swapchain_maintenance1.html)、[feature 查询与启用](https://docs.vulkan.org/refpages/latest/refpages/source/VkPhysicalDeviceSwapchainMaintenance1FeaturesKHR.html)、[固定有效使用条件](https://github.com/KhronosGroup/Vulkan-Docs/blob/b94f8bd2d004d2949469d8a5071ee10eb7d23566/chapters/VK_KHR_surface/wsi.adoc#L7688-L7692)

这些官方 refpages 是读取日的滚动页面；核心退役条款以上述固定源文为准。本篇不把 KHR 条件倒推为旧 Vulkan 1.3.296 或全部历史 EXT 修订的保证，也没有查询任何平台的实际支持。

这里不覆盖失败入队、OUT_OF_DATE、device lost、未附 fence 的历史工作、无扩展回退、未呈现的已获取图像、完整交换链替换或 surface/device 销毁。也不比较 wait-idle 或 present-wait 扩展，不给出显示时刻、释放耗时或性能承诺。这是一份**对象与请求覆盖的有限审查**，不是完整关闭配方。[读取范围与原创部分](../audits/vulkan-present-fence-retirement/AUTHOR-NOTES.md)另列。
