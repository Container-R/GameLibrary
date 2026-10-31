---
id: SOL-GFX-002
title: CPU 与 shader 矩阵交接：相同大小和 stride，不代表相同矩阵约定
type: solution
status: source-backed
primary_discipline: GFX
related_disciplines: [TA, ENGINE, PROG, QA, PLATFORM]
related_roles: [rendering-programmer, technical-artist]
related_topics: [shader-interface, uniform-buffer, matrix-layout, spir-v, host-packing]
engines: []
versions: ["GLSL 450", "Vulkan 1.0 / SPIR-V 1.0 compile target", "installed libshaderc byte identity, release unknown", "shaderc API comparison 3362e24c42ab5bf7ad32c0fec64b0a0ddeb2fda1", "Python 3.12.14"]
platforms: [offline-cpu-compilation]
updated_at: 2026-10-31
verification_method: 固定官方规范与 C API 核对；两个实际编译进程及独立同库复跑，字面 assembly/host bytes 判据，三个启动失败负例；CPU 数值解释；另一次隔离 Vulkan instance 请求返回 -9，不含 shader 执行
sources:
  - https://github.com/KhronosGroup/GLSL/blob/0099bf83b0288469917fc2e2972cb0a2b74d6711/chapters/variables.adoc
  - https://github.com/KhronosGroup/GLSL/blob/0099bf83b0288469917fc2e2972cb0a2b74d6711/chapters/operators.adoc
  - https://github.com/KhronosGroup/Vulkan-Docs/blob/b94f8bd2d004d2949469d8a5071ee10eb7d23566/chapters/interfaces.adoc
  - https://github.com/google/shaderc/blob/3362e24c42ab5bf7ad32c0fec64b0a0ddeb2fda1/libshaderc/include/shaderc/shaderc.h
---

# CPU 与 shader 矩阵交接：相同大小和 stride，不代表相同矩阵约定

## 问题：缓冲区没有越界，变换为什么仍然错？

CPU 上传工具与 shader 都接受一块 48-byte 的矩阵记录，成员 offset 为 0，MatrixStride 为 16，类型也都是 3×3 float32。这些检查全部相同，仍不足以说明两端解释的是同一个矩阵：**矩阵按行还是按列存储，属于独立的接口字段。**

本方案用实际编译器输出建立这一边界，而不是再写一个内存大小计算器。两个原创 GLSL shader 只有存储布局限定不同；实际生成的 SPIR-V assembly 分别含 RowMajor 与 ColMajor。相同的主机字节在两种解释下可以得到转置关系。本文没有执行 shader，数值结果是明确标注的 CPU 字节解释与代数判据，不是 GPU 读回。

## 1. 交接契约必须同时包含存储布局和代数语义

[固定 GLSL 规范](https://github.com/KhronosGroup/GLSL/blob/0099bf83b0288469917fc2e2972cb0a2b74d6711/chapters/variables.adoc#L5004-L5031)规定 row_major / column_major 对矩阵及其嵌套容器的内存布局生效，分别使行或列的元素在内存中连续。[Vulkan 内存布局定义](https://github.com/KhronosGroup/Vulkan-Docs/blob/b94f8bd2d004d2949469d8a5071ee10eb7d23566/chapters/interfaces.adoc#L1844-L1928)把两者分别对应为行向量数组、列向量数组，并定义相关对齐。

同一固定规范的[乘法规则](https://github.com/KhronosGroup/GLSL/blob/0099bf83b0288469917fc2e2972cb0a2b74d6711/chapters/operators.adoc#L812-L820)把右操作数向量视为列向量、左操作数向量视为行向量，按线性代数乘法解释。因此不能把“CPU 数学库使用行向量”直接翻译成“shader 必须 row_major”。至少需要分开记录：

| 契约层 | 必须交付的信息 | 本例 |
|---|---|---|
| 资源定位 | shader 阶段、descriptor set / binding、块与成员身份 | compute，set 0 / binding 0，Params.transform |
| 逻辑类型 | 标量类型、位宽、行数、列数 | float32，3 行、3 列 |
| 存储布局 | RowMajor / ColMajor、成员 Offset、MatrixStride | 两种 major，Offset 0，stride 16 |
| 主机编码 | 实际字节序、每项写入位置、padding 处理 | 有限 little-endian float32 记录；padding 写 99 |
| 代数含义 | 矩阵代表什么、向量乘法放哪一边、组合次序 | 此例仅验证 `M * vec3(1,2,3)` |
| 内容意图 | 非对称字面矩阵与期望逻辑结果 | 下节矩阵及 `(14,32,53)` |

前两种 major 使用的是同一个逻辑 GLSL 矩阵类型；改变存储限定符，不等于请求改变乘法方向或自动修正项目的坐标系。视图/投影矩阵、左右手坐标、行向量数学库及变换组合顺序需要项目另行约定，本例没有验证这些语义。

## 2. 一个大小和 stride 都无法区分的反例

实现前冻结的逻辑矩阵为：

```text
M = [ 1  2   3 ]      v = [1, 2, 3]^T
    [ 4  5   6 ]
    [ 7  8  10 ]      Mv = [14, 32, 53]^T
```

std140 下本例的每个行/列记录使用 16-byte stride。3 个 float32 分量占 12 bytes，记录中剩余位置不是第 4 个矩阵元素。下面是两份**不同但都正确**的主机记录；括号中的 99 为刻意可辨识的 padding：

| 与消费布局匹配的编码 | 连续的 12 个 float32 值 |
|---|---|
| RowMajor | `1,2,3,(99), 4,5,6,(99), 7,8,10,(99)` |
| ColMajor | `1,4,7,(99), 2,5,8,(99), 3,6,10,(99)` |

两份记录均为 48 bytes，均可由相同的 Offset 0 / MatrixStride 16 访问完毕。按照各自 major 解码，都恢复原矩阵，CPU 计算都得到 `(14,32,53)`。

若直接把第一份行分组字节交给 ColMajor 解释，得到的是转置矩阵，CPU 计算变成 `(30,36,45)`。没有越界、没有字节数变化，padding 也未参与运算，但内容意图已经错了。对称矩阵或单位矩阵会掩盖这一问题，所以验收样例不应只使用单位变换。

这里的 48 bytes 是有限矩阵记录的布局，不是 GPU 分配量，也不是任意 API 绑定范围/动态 offset 的对齐要求。其他标量类型、数组、矩阵维度与布局模式必须重新检查；[Vulkan Uniform 对齐规则](https://github.com/KhronosGroup/Vulkan-Docs/blob/b94f8bd2d004d2949469d8a5071ee10eb7d23566/chapters/interfaces.adoc#L1978-L2010)还包含特性条件，不能把本例 std140 推成所有 UBO 的唯一布局。

## 3. 实际编译证据到哪里为止？

[原创夹具与原始输出](../../research/experiments/shader-matrix-layout/README.md)在两个隔离 Python 进程中，分别调用已安装 libshaderc 的固定参数 C API。每个进程编译一个原创 GLSL compute 源码为 assembly：显式 Vulkan 1.0、SPIR-V 1.0、optimization zero；源码读取 Params.transform 并执行矩阵乘向量，把结果写入另一个 storage block。因此证据不是一个没有消费点的孤立声明。

实际输出中，目标命名块/成员都解析为 3 列、每列 3 个 float32 的逻辑矩阵类型，并包含 `OpMatrixTimesVector`。目标成员的 decoration 为：

| 编译案例 | Major | Offset | MatrixStride |
|---|---|---:|---:|
| `row.comp` | RowMajor | 0 | 16 |
| `column.comp` | ColMajor | 0 | 16 |

两次编译均 status 0，errors / warnings 为 0，诊断字符串为空。判据先定位 Params 和 transform，再核对成员及类型链，不拿模块中的第一个 stride 代替目标接口。完整 assembly、输入哈希、host hex、进程命令/状态均保留。

[独立复验](../../research/experiments/shader-matrix-layout/review/REVIEW.md)使用同一库的独立副本工作目录，重跑两次编译，以不导入作者 reader 的字面判据核对 assembly、精确字节位置与 CPU 乘法结果。另三个合成启动失败案例——`-O`、缺失 native library、伪造 malformed RESULT_JSON——均拒绝、移除旧 PASS，并记录 FAILED；这些案例没有调用 native 编译器，不应计成另外三个 shader 测试。未注入 timeout 或任意文件系统中断。

[补充语义审查](../../research/experiments/shader-matrix-layout/review/SEMANTIC-AUDIT.md)逐项追踪这两份已归档 assembly 的 Params 变量 → 成员 0 地址 → 矩阵 load → 与 `(1,2,3)` 相乘 → Output.value store，补上“模块中存在某个乘法指令”还不足以证明消费关系的缺口。对 major、stride、块/成员名、host 元素、load 连线和 store 来源各作一次合成修改，两份输出共 14 个变异均被独立字面判据拒绝。这些是归档文本/字节反例，不是另外 14 次编译；精确标识符检查也不是通用 SPIR-V 验证器。

这证明的是**实际编译器产生了需要区分 major 的接口信息**，以及有限 CPU 解释能够揭示错误编码。原编译夹具没有执行 SPIR-V，也没有调用 GPU API、上传缓冲区、创建 pipeline、验证实际 binding 或读回 shader 结果；同库复跑不是第二种编译器的交叉验证。已检查的 PATH 与有限工具目录中未找到独立 SPIR-V validator CLI，本例不宣称完整模块验证。

### 后续能力门：库存在，不等于可以执行 shader

为判断是否能够开始独立的实际执行方案，另行冻结 ABI 与调用协议，并在一个隔离 Python 子进程中请求 Vulkan 1.0 instance。[能力门原始记录](../../research/experiments/vulkan-capability-probe/README.md)显示：`vkCreateInstance` 尝试一次、返回一次，结果为 `-9 / VK_ERROR_INCOMPATIBLE_DRIVER`。没有成功 instance，因而枚举与销毁调用均为零；未创建 device、pipeline 或执行 shader。子进程正常退出只表示负面结果已记录，不是 GPU 测试通过。

这次观察只针对归档的 loader 字节和 system-path-only 最小环境，不证明机器没有物理 GPU，也不认证驱动/loader 来源。标准目录扫描未见 manifest 是有限线索，不是全局硬件调查；没有安装驱动、改变覆盖变量或重试其他 API。独立审查只复核原始记录和源代码，没有第二次原生运行。[来源与停止条件](../../research/source-notes/vulkan-capability-gate.md)保留接口、环境与证据层级。**原有两种矩阵结果仍是编译输出加 CPU 解释，实际 shader 执行关卡仍未完成。**

## 4. 项目验收：不要只比较结构体 sizeof

以下是原创工程建议，不是规范要求的统一流水线：

1. **先冻结逻辑意图。** 给出非对称小矩阵、向量与预期乘法方向；把 CPU 数学库输出约定和序列化约定分开审查。若只能提供单位矩阵截图，不能排除转置误配。
2. **针对最终编译产物检查接口。** 记录目标编译环境、变体、块/成员身份及 set / binding。检查 major、offset、stride、类型/维度，而不是把 shader 源码中看见的限定词当成所有后续工具链的最终结果。此夹具只检查一个有限命名成员，不提供通用反射器。
3. **检查实际编码字节。** 按已确认布局恢复矩阵，并与逻辑意图逐项对照；padding 不应被当成数据。字节数正确只是一层条件，不能代替结果语义。
4. **加入会暴露错误的对照。** 本例故意把行编码交给列解释，要求意图检查失败。不要把“两个正确编码都能通过”误认为错误编码必然会被发现。
5. **把 GPU 集成作为独立关卡。** 在目标 API/设备上另行验证 descriptor、binding 范围、同步和实际读回；保留与 CPU 意图的比较。这里不能从编译 PASS 直接勾选这些项目已通过。
6. **变体变更重新验收。** shader 编译参数、宏、成员排列、数据类型或主机数学库改变时，需要重新确认接口和字节编码。留存编译输入/产物身份比长期依赖手写 padding 注释更可审计。

显式编码/反射检查增加工具维护和版本管理成本；不必为每个简单矩阵构建完整通用框架。但在跨语言、跨编译器或多个主机上传路径之间交接时，漏掉 major 的“同尺寸”检查可能持续接受错误数据。此处没有测量维护成本或运行性能，不据此推荐某种 major 更快。

## 5. 来源身份与可复现范围

API 签名、枚举和资源释放流程来自固定 [shaderc.h](https://github.com/google/shaderc/blob/3362e24c42ab5bf7ad32c0fec64b0a0ddeb2fda1/libshaderc/include/shaderc/shaderc.h#L513-L606) 与 [env.h](https://github.com/google/shaderc/blob/3362e24c42ab5bf7ad32c0fec64b0a0ddeb2fda1/libshaderc/include/shaderc/env.h)。Python 明确声明指针、size_t、enum 与 uint32 参数，无 varargs；在复制输出后释放 result/options/compiler，父进程设置超时并保存失败日志。不是任意 shader 或任意 native ABI 的安全包装器。

实际库 SHA256 为 `31400b359d2f4b4a43168978412a72913474725befb87966068cfac1922ac6c9`。`shaderc_get_spv_version` 返回 `0x10600` / revision 1，**不是 shaderc 包版本**；实际显式目标生成的 assembly 为 SPIR-V 1.0。精确库发行版本/源码来源未认证，不能把所读 v2025.2 header 标签当作本地构建证明。

所有来源访问日期为 2026-10-31：GLSL pin `0099bf83…`，提交日期 2026-09-11；Vulkan-Docs pin `b94f8bd2…`，2026-10-30；shaderc v2025.2 pin `3362e24c…`，2025-04-23。正文、GLSL 和测试为原创，没有复制第三方实现代码。

关联：[glTF 属性交接](../modeling/gltf-interleaved-attribute-contract.md)区分存储跨度与几何意图；[BC mip 预算](block-compressed-mip-budget.md)区分 payload 与 GPU 分配。本方案补的是编译产物中的矩阵接口约定，不把前两种离线证据扩写成 GPU 执行证明。
