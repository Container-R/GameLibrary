# BC 压缩纹理：逐 mip payload 与资源预算的边界（来源门槛／待实施）

日期：2026-10-31。状态：source-backed proposal；未执行格式实验、DirectXTex、图形 API 或 GPU 测量。限定 2D、单层、单面、BC1 / BC7，紧密排列 payload。主关联 TA / ENGINE / rendering；不新增大而泛的 VFX 指南。

## 已读一手证据

1. [Microsoft Texture Block Compression in Direct3D 11](https://learn.microsoft.com/en-us/windows/win32/direct3d11/texture-block-compression-in-direct3d-11)，BC1 / BC7 表：每 4×4 block 分别 8 / 16 bytes。这是编码块的大小，不是每个小 mip 都可按面积乘 0.5 / 1 得到整数实存字节。
2. [Microsoft DDS Programming Guide](https://learn.microsoft.com/en-us/windows/win32/direct3ddds/dx-graphics-dds-pguide)，DDS File Layout / DDS Variants：压缩行 pitch 使用向上取整的块宽，至少一块；文件基本 magic+header 共 128 bytes，DX10 扩展时共 148 bytes。文档警告历史工具写入的 pitch 字段不总可靠，也区分计算 pitch 与运行时 pitch。这里不把文件长度直接当显存。
3. [Microsoft D3D10 Block Compression](https://learn.microsoft.com/en-us/windows/win32/direct3d10/d3d10-graphics-programming-guide-resources-block-compression)，开头及 Virtual Size versus Physical Size：base resource 创建约束为尺寸 4 的倍数；60×40 示例的后续 mip 需要块 padding。**NPOT 不等于非 4 倍数**。离线能算 7×5 的 block payload，不代表特定 D3D API 可以创建该 base resource。小 mip 的合法性也不能反推小 base resource 的合法性。
4. [Khronos Vulkan Formats](https://docs.vulkan.org/spec/latest/chapters/formats.html)，BC 格式条目（访问时 latest）：BC1 为 64-bit / 4×4，BC7 为 128-bit / 4×4；格式支持必须查询。不以此次 CPU 测试证明设备支持。初次请求 registry 整本规范超过工具 16MiB，改读官方分章页面成功，并非绕过权限。
5. [VkMemoryRequirements](https://docs.vulkan.org/refpages/latest/refpages/source/VkMemoryRequirements.html)，Members：资源所需 allocation size、offset alignment、memoryTypeBits 是独立 API 输出。本实验不会调用它；若生产预算要升级为设备资源数据，应另外记录该目标 API 查询及实际驻留测量。
6. [D3D12 GetCopyableFootprints](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12device-getcopyablefootprints)，pRowSizeInBytes / Remarks：未 padding 的行字节数不是 upload footprint 的 row pitch；该 API 服务于上传布局。它也不等同于运行时已驻留显存。另一个手工拼接 GetResourceAllocationInfo URL 返回 404，未作为已读证据。
7. DirectXTex 当前 main 经 GitHub 插件解析到不可变 commit **ec66b78b37389e8373a8e14ccc3cd29be94146b3**（2026-10-21）。已读源码：
   - [DirectXTexUtil.cpp#L908-L973](https://github.com/microsoft/DirectXTex/blob/ec66b78b37389e8373a8e14ccc3cd29be94146b3/DirectXTex/DirectXTexUtil.cpp#L908-L973)：正常 ComputePitch 分支分别计算 ceil(width/4)、ceil(height/4)，每轴至少 1，乘 8 或 16，包含 overflow 处理。另有 CP_FLAGS_BAD_DXTN_TAILS 兼容路径；本模型**不启用**该路径。
   - [DirectXTexImage.cpp#L47-L72](https://github.com/microsoft/DirectXTex/blob/ec66b78b37389e8373a8e14ccc3cd29be94146b3/DirectXTex/DirectXTexImage.cpp#L47-L72)：2D 每级累计 slicePitch，尺寸大于 1 时右移一位。只做源码比较；没有编译执行 DirectXTex。

所有页面访问时间为本日；Microsoft 页面有通用授权提示但正文可读，未访问登录区。以上逐条为来源归纳，下述为原创验证方案。

## 核心问题与有限数值模型

输入正整数 W,H、BC1 或 BC7、选定 mip 数（不得超过完整链）；逐级尺寸为 max(1, floor(W/2^i))、max(1, floor(H/2^i))。每级 payload 为 ceil(w/4) × ceil(h/4) × blockBytes。完整链到 1×1 结束；不得把 padding 后的 4 倍数当作下一 mip 的逻辑尺寸。

拟固定样例：1×1、4×4、8×8、60×40、7×5、1×8，BC1 与 BC7 都计算。1×1/7×5/1×8 是离线布局数值边界，不声明 D3D base resource 合法。用独立手工期望表验证逐级尺寸、块数、总量，额外拒绝 bool、0、负数、float、未知格式和越界 mip 数。Python 大整数防止本模型溢出，但不构成 C++ 或 GPU 分配大小安全验证。

两个明确反例待运行：4×4 BC1 完整链三层，每层一块，总24 bytes，不是 top8×4/3；7×5 的中间尺寸应3×2而不是4×3。4/3 来自无限的、每级面积四分之一几何级数；有限小尺寸、窄长尺寸、NPOT floor 和 BC 最小块会使其不再是精确公式。不能宣称所有情况一定高估或一定低估。

输出同时列 base-only、full-chain、选择性 mip 子集 payload、DDS container bytes；上传行对齐、GPU allocation、驻留预算保留独立未知栏目。选择子集求和只是文件/数据量核算，不是证明引擎能省掉同等 resident memory；streaming page、mip tail 打包、资源生命周期与引擎策略不在测试范围。

## 可行的实际离线格式制品（待批准实施）

已检查环境：Python 自带 struct/hashlib 可用；Pillow 自报 13.0.0，安装位置中的 DdsImagePlugin 可读，支持 DXT1 解码；未调用编码或解码。texconv/compressonatorcli/nvcompress 不在 PATH；不安装、不下载工具。不用第三方美术、不编辑用户图像。

建议用**原创手工编码 BC1 常量色 block**：两个 RGB565 endpoint + 全零 selector，拼装 60×40 的 6 级链（60×40→30×20→15×10→7×5→3×2→1×1），每级可给不同已知 endpoint 色以识别偏移错误。写标准 legacy DXT1 DDS header 和紧密 payload；保存原始 DDS、base64、字节 SHA。

独立 reader 以 header 校验格式/尺寸/mip count、逐级实际偏移和切片长度；用已安装 Pillow 对每一级单独包成临时 DDS 后真实 decode/load，核对逻辑尺寸、已知像素色和末端像素。这样证明这些有限块与容器片段能被该 CPU decoder 消费，不是假称 Pillow 自动遍历原文件全部 mips。完整原始容器另外做精确总长、偏移、无多余尾字节校验。加一份故意少一块的副本应由严格布局 checker 拒绝；不要把 decoder 容忍或只读取首级误作全链完整性证明。

BC7 **仅数值布局模型**，不手写复杂编码、不声称格式 decode 验证。若 Pillow 原生 decoder 能力实际不可用，保留失败输出并把 artifact 降级为字节布局验证，不换装工具、不伪造 decode 成功。

## 验收与停止条件

固定数值表与唯一 BC1 链制品完成后停止扩展，交独立 reviewer 重跑；先冻结源码再留实际执行命令、Python/Pillow 版本及相关源/原生模块 SHA、stdout/stderr、strict check summary。失败不保留旧 PASS，禁用仅 assert 验收。无需 GPU、引擎、性能 benchmark、视觉质量或压缩率营销结论。

本稿是 source/proposal gate，没有上述案例运行结果；下一步需父代理确认精确范围。
