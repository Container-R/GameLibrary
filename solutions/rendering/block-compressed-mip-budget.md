---
id: SOL-GFX-001
title: BC 压缩纹理预算：逐 mip 计算 payload，不把 DDS 文件长度当作显存
type: solution
status: source-backed
primary_discipline: GFX
related_disciplines: [TA, ENGINE, MODEL, PLATFORM, QA]
related_roles: [technical-artist, rendering-programmer]
related_topics: [block-compression, mipmaps, texture-memory, dds, asset-budget]
engines: []
versions: ["BC1 / BC7 tight 2D payload", "DirectXTex ec66b78b37389e8373a8e14ccc3cd29be94146b3 source comparison", "Python 3.12.14", "Pillow 13.0.0 self-report"]
platforms: [offline-cpu-format-validation]
updated_at: 2026-10-31
verification_method: 官方格式文档与固定源码核对；14 个有限算术案例、6 个输入拒绝、6 个实际 Pillow 单 mip 包装解码及截断拒绝；独立同环境复跑，不含 GPU 验证
sources:
  - https://learn.microsoft.com/en-us/windows/win32/direct3d11/texture-block-compression-in-direct3d-11
  - https://learn.microsoft.com/en-us/windows/win32/direct3ddds/dx-graphics-dds-pguide
  - https://learn.microsoft.com/en-us/windows/win32/direct3d10/d3d10-graphics-programming-guide-resources-block-compression
  - https://github.com/microsoft/DirectXTex/blob/ec66b78b37389e8373a8e14ccc3cd29be94146b3/DirectXTex/DirectXTexUtil.cpp
  - https://docs.vulkan.org/refpages/latest/refpages/source/VkMemoryRequirements.html
---

# BC 压缩纹理预算：逐 mip 计算 payload，不把 DDS 文件长度当作显存

## 先决定你要批准哪一种预算

美术提交一张 BC1 纹理，预算表用“宽×高×0.5，再乘4/3”估计完整 mipchain；平台性能工具却显示另一个数字。此时不应直接要求美术缩图，也不应把差额全归咎于引擎浪费：**先分清紧密编码 payload、文件容器、上传布局、资源分配和实际驻留**。

本方案解决前两层的可复算性，并规定后面三层需要什么额外证据。它不是通用 VRAM 计算器，也不比较 BC1 / BC7 视觉质量。算术范围为单层、单面、二维、完整 mipchain 的 BC1 / BC7；不含立方体、数组、3D、跨平台转码、稀疏资源和包文件二次压缩。

**具体结论：**原创60×40 BC1 完整链的紧密 payload 是1664 bytes；本次 legacy DDS 实际文件是1792 bytes，其中128 bytes是描述数据。这两个数字都不是已测显存。小纹理用4/3常数有时低估、有时高估，不能当严格安全余量。

## 1. 核算契约：逻辑尺寸先缩小，再计算块覆盖

BC1 一个4×4块占8 bytes，BC7占16 bytes。[Microsoft 格式表](https://learn.microsoft.com/en-us/windows/win32/direct3d11/texture-block-compression-in-direct3d-11)和[Khronos BC格式定义](https://docs.vulkan.org/spec/latest/chapters/formats.html)相互印证此格式属性；它不代表当前设备一定支持这些格式。

令 W,H 为正整数，完整链最后一级为1×1。对每一级 i：

```text
w_i = max(1, floor(W / 2^i))
h_i = max(1, floor(H / 2^i))
blocks_x = ceil(w_i / 4)
blocks_y = ceil(h_i / 4)
row_payload_i = blocks_x × block_bytes
payload_i = row_payload_i × blocks_y
full_payload = sum(payload_i)
```

必须保留两组尺寸：**逻辑 texel 尺寸**和**编码 block 数量**。例如15×10下一级为7×5，不是把15×10先补成16×12再得到8×6。即使逻辑尺寸是1×1，仍至少需要一个编码块。

这与固定版本 DirectXTex 的正常 [ComputePitch 分支](https://github.com/microsoft/DirectXTex/blob/ec66b78b37389e8373a8e14ccc3cd29be94146b3/DirectXTex/DirectXTexUtil.cpp#L908-L973)以及 [2D mip累计/尺寸右移路径](https://github.com/microsoft/DirectXTex/blob/ec66b78b37389e8373a8e14ccc3cd29be94146b3/DirectXTex/DirectXTexImage.cpp#L47-L72)一致；没有执行或移植整个 DirectXTex，也不采用 `CP_FLAGS_BAD_DXTN_TAILS` 旧数据兼容分支。

**API合法性是另一道门槛。**“NPOT”只表示非2次幂，60×40仍是4的倍数。[D3D10文档](https://learn.microsoft.com/en-us/windows/win32/direct3d10/d3d10-graphics-programming-guide-resources-block-compression)的基础资源约束与较小 mip 的块 padding 要分开阅读。本文可离线计算7×5或17×17，并不能由此证明这些尺寸可在指定 D3D API 中创建为基础 BC 资源。不得用 CPU decoder 接受小 mip wrapper 替代目标设备的创建/支持查询。

## 2. 可核对的六层制品：1664 + 128 bytes

下面是实际生成并留存的原创 BC1 DDS。每一级使用不同 RGB565 端点色和全零 selector；不是从第三方图像压缩而来，也不是压缩质量测试。

| mip | 逻辑尺寸 | 块数 X×Y | payload bytes | 文件绝对偏移 | 解码色标 |
|---|---|---|---:|---:|---|
|0|60×40|15×10|1200|128|红|
|1|30×20|8×5|320|1328|绿|
|2|15×10|4×3|96|1648|蓝|
|3|7×5|2×2|32|1744|黄|
|4|3×2|1×1|8|1776|品红|
|5|1×1|1×1|8|1784|青|
|合计|6层|208块|1664|文件结束1792|—|

[Microsoft DDS布局说明](https://learn.microsoft.com/en-us/windows/win32/direct3ddds/dx-graphics-dds-pguide)区分 magic、基本 header、可选 DX10 header 与 surface 数据。这里采用128-byte legacy描述；采用 DX10 扩展的容器描述为148 bytes，不能把128硬编码到所有 DDS。BC7在本文只有数值模型，没有 BC7 文件或解码实验。

本次完整 DDS SHA256 为 `1e8f263dbf5aafe04b26626ba7b17ef9ec455337d2f8fed3ddcdbcf145e2f20f`。相同输入若文件字节不同，先检查 header、级数、顺序和额外尾数据，不能只看文件名“BC1”。历史 DDS 的 pitch字段也可能不可靠，不能用一个未经验证的字段取代逐级长度校验。

## 3. 为什么4/3不是小纹理预算的可靠上下界

4/3来自每级面积恰好变为四分之一的无限几何级数；有限链、奇数下取整、窄长尺寸和最小块占用均会改变这个前提。

| 离线BC1案例 | 各级bytes | 实际完整链 | base×4/3 | 错误方向 |
|---|---|---:|---:|---|
|4×4|8,8,8|24|约10.67|低估|
|17×17|200,32,8,8,8|256|约266.67|高估|

这里的“实际完整链”是通过数值验收的 tight layout，不表示这两个案例都创建了GPU资源。即使只求 top level，4×4内的1×1逻辑区域也不能按0.5 byte独立保存为BC1块。因此审批大量小贴图、图集拆分方案或尾部 mips 时，应枚举真实布局，不把倍率偏差默认为可忽略。

格式与分辨率变更仍需独立的内容验收；字节较少并不自动意味着 alpha、法线或文字边缘可用。本文没有这类视觉验收数据。

## 4. 五种数字，五种证据

以下为原创工程交接协议，不是厂商规定的统一表格。

| 预算层 | 应记录什么 | 能回答的问题 | 不能直接推出 |
|---|---|---|---|
|紧密payload|目标格式、逐级逻辑尺寸/块数、实际保存级数|编码数据本身多少字节|GPU分配与驻留|
|容器/发行包|真实文件长度、header/metadata、包压缩口径|磁盘/传输占用；是否缺级或多数据|解包后的资源占用|
|上传布局|目标API返回的每级row pitch、offset、总上传空间|CPU上传缓冲区如何排布|纹理自身永久分配|
|资源分配|目标资源描述、设备/API、size/alignment等查询结果|该资源需要怎样的分配空间|当前全部实际resident|
|实际驻留|引擎/平台工具口径、场景、时刻、streaming状态和峰值|运行负载下驻留多少|另一设备或另一场景同样成立|

[D3D12 GetCopyableFootprints](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12device-getcopyablefootprints)明确区分未补齐行大小与上传 row pitch；不要把上传 footprint 改名为显存。[Vulkan VkMemoryRequirements](https://docs.vulkan.org/refpages/latest/refpages/source/VkMemoryRequirements.html)则提供资源分配size/alignment等字段，本文未调用这些 API。

对拟议 streaming 优化，允许先求指定 mip 集合的 payload 作为数据量分析，但还应检查引擎是否真的不分配/不驻留对应部分、尾部是否按页或 mip-tail共同管理。删除磁盘中的一层和运行时卸载一层不是同一操作。本次脚本只实现完整链接口，没有子集streaming测试。

## 5. 提交给美术、TA、渲染与QA的最小验收问题

1. **输入究竟是什么？** 导入后的逻辑宽高、平台实际格式、层数/面数、mip数量是什么？不要直接拿源PNG尺寸或文件大小。导入配置丢失问题见[资产导入意图契约](../engine/asset-import-intent-contract.md)。
2. **测量名词一致吗？** 优化目标是包体、上传峰值、分配量还是驻留量？预算表必须写单位bytes/MiB及是否包括header、是否全链，不能只写“纹理内存”。
3. **尾部和偏移完整吗？** 每级尺寸按逻辑floor递减；每级blocks独立ceil；长度与级数匹配。首级能显示不代表小mip完整。错误长度应阻断交付，而非让后续decoder偶然容忍。
4. **设备证据在哪里？** 离线布局通过后，目标API格式支持/资源创建以及分配、驻留仍由平台/渲染侧提交证据；没有这些数据时保留未知，不以模型替代。
5. **优化代价由谁验收？** TA与内容作者验证视觉和导入结果，渲染/平台确认资源口径，QA验证目标设备与场景。角色协作见[技术美术](../../roles/technical-art/technical-artist.md)。
6. **是不是错把容量问题当性能根因？** VFX仍可能受透明overdraw、模拟与renderer开销约束，不能从省下若干纹理bytes推断帧时提升；参照[Niagara性能预算](../vfx/niagara-performance-budget.md)的控制变量测量。

## 6. 已执行证据与复验边界

[实验说明与源码](../../research/experiments/texture-block-budget/README.md)保存精确命令、原始stdout/stderr、manifest和无损base64。模型使用7组尺寸×2格式共14个固定案例；另有6个非法输入拒绝。完整DDS用独立字面header/长度/偏移表检查，故意删最后8 bytes的副本被拒绝。

六个 mip 分别从完整文件取片，包装成单级DDS后调用已安装Pillow的实际 `load()`，遍历全部逻辑像素确认尺寸和色标。**这不是Pillow自动遍历完整链的实验。** checker只针对这个固定原创制品，不是通用 DDS 安全解析器。独立审查重跑并使用不导入作者模型的偏移/颜色检查；仍用同一个Pillow decoder，不宣称两个独立codec交叉验证。

环境自报Python3.12.14/Pillow13.0.0；manifest记录解释器、DDS插件与原生模块文件SHA，不据版本字符串声称认证了上游构建来源。`getdata` 弃用警告原样保留，当次调用成功；未来环境升级需要重新验证，不隐去警告维持“干净日志”。首轮6组尺寸通过后增加17×17反例并重跑，旧版本和结果保留在historical-six-pairs中。

模型源SHA为 `cea6af8ac132485f7492ee60ab1019daaf9f690257bafc62d989fcfdc5697544`；原始runner源SHA为 `d821626c603c48c4b02c21e1384a6fd0f808c034172e11e61aff9a0435637c64`，当前加固版为 `1ca81455b9ef0605a01b7dbfff15454a3294c16bfe335e5f964919ba251b7cef`。没有执行GPU、D3D/Vulkan资源创建、BC7解码、压缩器或真实游戏帧时测试。文章保持source-backed：有限CPU结果只升级其明确覆盖的部分，不升级整个平台预算方法为实机验证。

## 来源版本与定位

全部官方页面访问于 **2026-10-31**；滚动网页不视为固定SDK版本。DirectXTex commit `ec66b78b37389e8373a8e14ccc3cd29be94146b3` 的提交日期为2026-10-21，使用不可变链接仅作源码比较。

- Microsoft D3D11：BC1/BC7格式表；DDS Programming Guide：DDS File Layout、DDS Variants、pitch计算。
- Microsoft D3D10：资源约束与Virtual Size versus Physical Size，特别是60×40示例。未采纳其中概括性的性能措辞作为此次benchmark结论。
- DirectXTex：Util.cpp 908–973正常块布局分支；Image.cpp 47–72二维逐级尺寸与累计。
- Khronos：Formats中BC条目；VkMemoryRequirements Members。读取官方分章页，未将工具无法加载的整本规范当作已读。
- D3D12 GetCopyableFootprints：pRowSizeInBytes与Remarks；访问时页面更新时间2025-11-25。它支持上传布局区分，不提供本次实际资源数据。

### Runner 验收补充

独立合成负例揭示原runner导入失败可留下旧PASS，且故意错一字节的输出偏移能绕过作者检查、但被独立字面偏移checker拒绝。原始制品已通过后者。当前v2在可选依赖导入前清除旧摘要，独立检查偏移前缀和每轴块数；重新执行有限fixture，原版源/结果与失败证据保留，不把旧结果配给新源。仍须核对本次退出状态，不把文件存在或PASS字样当作执行证明；不保证解释器启动、权限或任意中断安全。
