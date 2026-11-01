# Present-wait semaphore：独立来源门复核

2026-11-01。**接受有限正常循环增量；未发现阻断前提。** 本次未参与选题或来源门起草，独立重新打开决定性原文；未执行 Vulkan、GPU、验证层或模型，也未读取关联运行档案。此结论不等于最终新增正文已经审查。

## 实际读取与身份

- Khronos Vulkan-Guide 固定提交 `82887e8444045655cc4578827e4183be9de593ff`，[swapchain_semaphore_reuse.adoc](https://github.com/KhronosGroup/Vulkan-Guide/blob/82887e8444045655cc4578827e4183be9de593ff/chapters/swapchain_semaphore_reuse.adoc)全文。独立计算 Git blob 为 `5095b0045018083433571a5e7aae7177295c9fb9`，UTF-8 SHA-256 为 `a8ad3b760da078f4da89648c5d086d5e24c182877cf3222e6364b1286acc8a62`。
- Vulkan-Docs 固定提交 `486e4b289053a7d64784e7ce791711843c60c235`，[swapchain/wsi.adoc 1065–1091](https://github.com/KhronosGroup/Vulkan-Docs/blob/486e4b289053a7d64784e7ce791711843c60c235/chapters/VK_KHR_swapchain/wsi.adoc#L1065-L1091)。读取 acquire 的同步与返回限制。
- 同时检查当前目标文章全文，SHA-256 `fb64436a50de8f68c65bbb2f06855c9348ded4e387fc3cbccb92cd167ad687fe`：当前已有容量/工作/呈现计数区分，但没有这一具体二值信号量复用选择。新增内容可独立补充正确性，不需修改旧假设延迟表。

## 决定性判断

接受来源门对指南 **Problem Statement / Discussion of Solution / 正常循环示例**与上述规范 acquire 段的有限引用；事实说明集中于最终文章，本记录仅保留定位与独立范围审查，不重复来源摘要。

## 两帧槽、三图像假设的审查

门中先前槽0使用图像A、后来槽0可能取得C，逻辑上可以说明 frame 身份与 image 身份不同。它只是一个**允许考虑的身份序列与缺少保证的论证**，不是指定驱动必须给出的获取顺序、已发生的并发重用或观测到的 validation 错误。

接收正文时仍须保留：必要 acquire 同步、正常成功循环、二值信号量、此前 present 所使用的同一图像。数组大小差异不是错误的唯一成因；即使数量相同，也不能把两个索引自动视为同一身份。对某个具体实现“这次确实仍在使用”的判断需要额外证据，本来源门没有提供。

## 明确不扩张

- 不把指南省略参数的伪代码变成完整循环；不替获取失败后 fence 状态、present 错误、重建或退出提供修复。
- 不推广到多交换链、队列族转移、所有等待 stage 配置或扩展呈现 fence 路径；具体可执行提交仍需完整有效的同步设置。
- 不声称 WaitIdle 解决所有回收问题，不将本正确性选择计作延迟优化或显示完成测量。

批准下一步编写有限 source-backed 补充。最终正文若删除 acquire 等待条件、把索引改动本身当作充分条件，或将假设升级为实际驱动故障，应重新拒收。当前没有代码、运行或性能结果可以继承。

## 最终正文限定复核

已读取暂存 `solutions/rendering/presentation-queue-latency-boundary.md`，SHA-256 `00e190d5737b3533a7996775f78b14439319f42aaed112f748ac189e30eb5023`。接受新增 1.1 节及其元数据范围：普通、同步设置有效的 `vkQueueSubmit` 限定已加入，明确不推广到任意 `vkQueueSubmit2` stage mask；旧假设时间线没有升级为运行证据。本次仅做文稿复核，没有新增执行。
