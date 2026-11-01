# 独立来源复核：present fence 的对象与请求覆盖

2026-11-01。**接受下列精确文稿，无实质修改要求。** 这是来源与未执行情景的审查，不是设备、呈现或关闭流程测试。

- `article.md` SHA256：`ed63f32a206e95e62a1e999c889f4dae2b64b9143c3adf8dc54c28a839558725`
- `gate.md` SHA256：`665944b99ac8429cd2b2906e0f212085645095dc428789a4c7e9ee04bd9f7b32`

## 独立原文读取

直接取得 Khronos Vulkan-Docs 固定提交 `b94f8bd2d004d2949469d8a5071ee10eb7d23566` 的 [chapters/VK_KHR_surface/wsi.adoc](https://github.com/KhronosGroup/Vulkan-Docs/blob/b94f8bd2d004d2949469d8a5071ee10eb7d23566/chapters/VK_KHR_surface/wsi.adoc)，检查：

- 6801–6855：`vkDestroySwapchainKHR` 及其有效使用条件。
- 7493–7527：被 present-fence 段包含的 `common_present_fence` 信号描述。
- 7688–7692：`swapchainMaintenance1-10158`。
- 8677–8736：`VkSwapchainPresentFenceInfoKHR` 的对象范围、量词、顺序与有效使用。

另读同提交 [KHR 扩展附录](https://github.com/KhronosGroup/Vulkan-Docs/blob/b94f8bd2d004d2949469d8a5071ee10eb7d23566/appendices/VK_KHR_swapchain_maintenance1.adoc)，以及官方生成页 [present fence](https://docs.vulkan.org/refpages/latest/refpages/source/VkSwapchainPresentFenceInfoKHR.html)、[feature](https://docs.vulkan.org/refpages/latest/refpages/source/VkPhysicalDeviceSwapchainMaintenance1FeaturesKHR.html)、[扩展](https://docs.vulkan.org/refpages/latest/refpages/source/VK_KHR_swapchain_maintenance1.html)。生成页只代表读取日页面；固定源文是本次核心身份，未推断驱动能力或历史 EXT 全版本等价。

## 对文稿的有限挑战与结论

1. “一次操作至少一个”与“指定交换链全部过去请求”没有混成同一个覆盖集合。P/A/B 例子中的 FA 可以支持 P 对 S 的责任结束，但不冒充 B 的请求凭据；S 的其他未完成使用被明确排除。
2. FB 未知被写为证据不足，而非断言未 signal；A 的历史请求和独立图像使用仍须检查。没有将扩展信号扩大成显示完成、内存立即释放或无条件销毁许可。
3. 最后一项信号所支持的前序推理明确限于同一队列、同一交换链、完整账目和本次 fence 身份。重置/复用前记录证据是原创跟踪要求，不是假定一个旧 signal 永远代表新请求。
4. 成功路径、合法启用、图像使用和 host 同步前提在正文保留。失败、缺失 fence、替换与完整关闭均明确排除，因此不是未经证明的多窗口资源管理器。

引用定位支持正文范围。原创情景没有被写成驱动观察，也没有从既有正常循环文章继承运行或平台保证。本审查不重复正文来源摘要，不编辑主研究记录或既有文章；未读取运行归档、执行程序或访问设备。
