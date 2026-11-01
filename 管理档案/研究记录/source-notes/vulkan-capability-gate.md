# Vulkan 能力门：loader、instance、枚举和 shader 执行是不同证据

本记录服务于已有矩阵接口专题的一个明确缺口：实际 shaderc 编译与 CPU 字节解释之后，当前环境是否足以开始另一个 shader 执行方案？**即使枚举到设备，也不能据此声称矩阵 shader 已经执行。**

## 源码与 ABI 边界

固定 Vulkan-Headers `b379292b2ab6df5771ba9870d53cf8b2c9295daf` 的 [vulkan_core.h](https://github.com/KhronosGroup/Vulkan-Headers/blob/b379292b2ab6df5771ba9870d53cf8b2c9295daf/include/vulkan/vulkan_core.h) 定义 dispatchable handles 为不透明指针，并声明创建 instance、枚举 physical devices 和销毁 instance 三个函数。固定 [vk_platform.h](https://github.com/KhronosGroup/Vulkan-Headers/blob/b379292b2ab6df5771ba9870d53cf8b2c9295daf/include/vulkan/vk_platform.h) 在普通 Linux 分支使用默认 C 调用约定。本夹具只接受 Linux x86_64 LP64：自然对齐的 VkInstanceCreateInfo 为 64 bytes，成员 offset 为 0、8、16、24、32、40、48、56。这里的结构大小不是跨平台规范常量；ABI 不匹配就应在加载库前停止。

官方 [VkApplicationInfo](https://docs.vulkan.org/refpages/latest/refpages/source/VkApplicationInfo.html) 与 [VkInstanceCreateInfo](https://docs.vulkan.org/refpages/latest/refpages/source/VkInstanceCreateInfo.html) 允许本请求使用 NULL application info 的 Vulkan 1.0 语义；不请求扩展或显式层。显式声明 VkResult 的有符号返回值、void 返回及 handle 输出参数，避免依赖 ctypes 默认签名或把输出 handle 当作返回值。NULL allocator 在 [销毁 instance](https://docs.vulkan.org/refpages/latest/refpages/source/vkDestroyInstance.html) 时保持匹配。

[枚举规范](https://docs.vulkan.org/refpages/latest/refpages/source/vkEnumeratePhysicalDevices.html) 区分获取数量和填充数组。数组容量是输入，实际写入数量是输出；VK_INCOMPLETE 是部分结果，不是完整清单。此探针自定上限 64，仅允许一次查询和一次有界填充，既不是 Vulkan 设备数上限，也不是生产环境面对动态枚举的通用策略。对 SUCCESS 和 INCOMPLETE 都必须检查返回数量没有超过容量且返回范围内 handles 非空。错误输出不能当成有效数量继续消费。

## 为什么限定环境，而不宣称“没有 GPU”

固定 [Vulkan-Loader Linux discovery 文档](https://github.com/KhronosGroup/Vulkan-Loader/blob/aa6dee8385afe4b2cc0152d086af2184743e16fd/docs/LoaderDriverInterface.md#driver-discovery-on-linux) 说明 XDG/system roots、编译期目录与 driver manifests 的关系；覆盖变量还可能替换或过滤发现过程。检查有限标准目录没有 manifest，并不排除所有构建路径、其他运行环境或物理硬件。manifest 存在也不保证它引用的共享库能够加载。

探针使用新建 HOME/XDG 五目录、固定系统 XDG_DIRS 和最小环境；不继承 VK 或 LD 注入/搜索覆盖变量，不读取私人 manifest，也不把 VK_DRIVER_FILES 指向空目录制造失败。这是 **system-path-only** 的明确请求环境，并非用户完整桌面环境；隐式系统层和 loader 编译期路径仍可能参与。环境 helper 不是安全沙箱。

实际已安装 loader 的路径/哈希只标识被观察的字节，不认证发行版本或源码来源。官方头文件与 loader 文档用于接口比较，不能当成本地二进制构建证明。Refpages 使用 moving latest，访问于 2026-10-31；两份 GitHub 源码/文档使用固定 commit。

## 证据与停止条件

协议在实现前冻结，执行前已完成作者以外的独立源码复核及协调者复核。每次原生调用记录 entry 前的 attempt 和返回后的 returned；父进程保存原始 stdout/stderr、退出码和超时事实。超时可以限制等待，不能保证已崩溃进程完成 destructor。合法创建且非空的 instance 才进入 finally 销毁；未创建 instance 不得伪造 cleanup 调用。

2026-10-31 的唯一原生子进程在此记为描述别名 `历史执行记录-01`：`vkCreateInstance` 实际 attempt 1 次、returned 1 次，返回 `-9`（`VK_ERROR_INCOMPATIBLE_DRIVER`）；枚举调用 0 次、销毁调用 0 次，因为没有成功创建 instance。Python 子进程退出码 0、无超时、stderr 为空，只说明负面结果成功归档，不是 Vulkan/GPU PASS。该请求在上述隔离环境下未能创建 instance；不推断物理 GPU 不存在，也不诊断 loader 缺陷。

实际 loader 的安装路径及文件摘要已从本公开衍生说明省略；原记录中调用前后的安装摘要相同，源文件前后摘要也相同，本轮没有重新检查这些历史相等关系。文件名不是可信构建版本声明。[夹具与原始记录](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/research/experiments/vulkan-capability-probe/README.md) 保存冻结协议、源码、进程元数据、调用 trace 与原始 stdout/stderr。独立评审只做源码和归档一致性检查，**没有独立原生复跑**。作者 6 个纯测试以及评审 normal/optimized 两种模式各 8 个合成记录检查，不是额外原生调用或设备测试。

第一次实现的归档检查器在执行前被发现类别/阶段和 ABI 记录验证不充分；原始源码与纯测试保留为 pre-native review history，修正后才运行唯一子进程。它不是曾经失败的 Vulkan 原生实验，也不与本次负面 API 结果混为一谈。

本单元已在能力门停止：不重试、不安装驱动、不切换 API、不创建逻辑 device、队列、pipeline、buffer，不运行 shader。矩阵接口文章仍只有 shaderc 实际编译与 CPU 解释证据。归档校验成功只表示固定字段、哈希与调用记录相互一致，不认证执行真实性，也不证明枚举成功、GPU 可用或矩阵计算正确。

> 公开衍生说明：本次仅省略安装位置、安装指纹或执行记录标识，并调整现址/固定历史链接；技术观察、失败、计数与原有证据范围保留。正文中的“本次”及身份相等陈述均属于原记录时点，本轮未重新检验，未运行旧实验，原始摘要声明不改写为新字节。文中描述性记录别名不是可执行目录名。
