# BC 原范围两项补充：变更与适用范围

日期：2026-11-01。这里只处理 `reader-original-scope-checks/environment-texture.md` 指出的 T1、T2，不开新书，不重做全部来源或实验审查。

## 精确输入与输出

- 完整读者正文：batch10 `GameLibrary/技术美术/环境管线/纹理与材质/计算BC压缩纹理和Mip链的数据量.md`，SHA-256 `d7bab2612237eb8c2c9576b5646ff3045fe3a66e81c758990e318f71bc64e155`。
- 完整读取对应旧正文 `solutions/rendering/block-compressed-mip-budget.md`，未打开任何脚本、运行归档或 raw。旧范围核对记录给出的该旧稿 SHA 为 `900eb014097593c77a6dc4ae0bdb8409ebacb4f56296fd19b5fc18b989d8eff6`，本次下方另直接核对文件摘要。
- 新 `book.md` SHA-256：`2cd17b1f5f5d8e2403b0788cced675af8278d78180ad29eb861a3b100c211a1d`。
- 精确统一差异存于同目录 `changes.diff`。正文只增加三段（T1 两段、T2 一段），扩充来源 [3] 的定位并新增来源 [7]。原表格、算术、历史检查范围及“返回本书架”链接均保留。
- 对这三段与来源变化作逆向替换后，逐字符恢复 batch10 原正文；未改 stage 或旧文。

## T1：已提出有限合并，待独立确认

位置：DDS 容器大小说明之后、GPU 上传行跨度说明之前。

新增内容把接收步骤说清：核对文件头/格式/尺寸/级数；不盲信历史 pitch 字段；按每级独立计算长度累加偏移；每段必须落在文件范围内。本例末级从 1784 开始还需要 8 字节，只有 1784 字节的文件不能按完整链接收。多余尾部数据要求解释，不把一个固定文件的精确长度当作所有 DDS 的通用条件。

新增数值来自现有六级长度和基本头大小的算术及旧正文已发表偏移，没有读取制品或重跑截断测试。缺失最后一级与“顶层仍可能显示”的解释不声称本轮调用过解码器。

本次重开 Microsoft 原始 Programming Guide for DDS：
https://learn.microsoft.com/en-us/windows/win32/direct3ddds/dx-graphics-dds-pguide

实际读取 DDS File Layout 行 39–75、pitch 与 runtime 差异 87–88、DDS Variants 89–93。原文说明 D3DX 等工具可能不一致地提供 dwPitchOrLinearSize，建议按格式计算；并列基本与 DX10 头部最低检查。网页存在通用授权提示，但正文可直接公开读取，没有登录或绕过。逐级范围、尾部不足拒绝和额外数据解释属于由布局导出的本例接收建议，不冒充官方完整安全解析算法。

## T2：已提出具体机制合并，待独立确认

位置：资源分配/驻留说明之后。

新增段解释：内存管理可按页/稀疏块，而小 mip 可被共同放入尾部区域；这类管理块不同于 BC 的 4×4 编码块。预算表少一级不能自动证明少一份驻留空间，选择级的数据和也不等于资源分配量。没有给本例假定页大小或声称所有引擎都采用同一布局。

本次重开 Khronos Vulkan 官方滚动规范 Sparse Resources：
https://docs.vulkan.org/spec/latest/chapters/sparsemem.html

实际读取 Sparse Resource Features 行 40–76，Mip Tail Regions 行 113–122，以及查询结果字段 imageMipTailFirstLod / imageMipTailSize / Offset / Stride（513–517）。只读文字，未据未查看图示作结论。来源支持稀疏驻留图像的尾级组合和尾区绑定/大小粒度；不是普通纹理都可逐块流送的承诺。格式支持及创建条件仍需查询，特别没有由本例 BC 算术推断设备支持 BC 稀疏资源。

这是已发表旧文流送限制的必要具体化，不新增完整稀疏资源教程，不新增驻留实验；书中原有“稀疏资源需要额外规则”的范围声明仍保留。

## 未扩大的边界

没有通用安全 DDS 解析器、非法头组合穷举、GPU 资源创建、流送驱动、驻留测量或解码运行。没有更改旧 CPU 证据范围或重新认证历史 runner。两项是否结清由主编辑和独立审读确认，本交付只陈述具体承接与来源，不自行改变管理状态。
