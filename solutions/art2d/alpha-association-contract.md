---
id: SOL-ART2D-001
title: 精灵透明度交接：四通道字节不说明 RGB 是否已经乘过 alpha
type: solution
status: source-backed
primary_discipline: ART2D
related_disciplines: [TA, GFX, ENGINE, QA]
related_roles: [technical-artist, rendering-programmer, ui-artist]
related_topics: [alpha-association, sprite-handoff, premultiplied-alpha, compositing]
engines: []
platforms: [offline-byte-domain]
versions: ["Pillow 13.0.0 self-report", "Pillow source comparison 293218ad059d994baf1777d882911bed6a49704a", "W3C Compositing CRD 2024-03-21"]
updated_at: 2026-10-31
verification_method: 固定第一方源码与格式文档核对；原创数值 buffer 的 5 次模式转换和 6 次实际 CPU 合成；无图片作品、引擎或颜色管理验证
sources:
  - https://www.w3.org/TR/2024/CRD-compositing-1-20240321/#simplealphacompositing
  - https://www.w3.org/TR/2003/REC-PNG-20031110/#6AlphaRepresentation
  - https://github.com/python-pillow/Pillow/blob/293218ad059d994baf1777d882911bed6a49704a/docs/handbook/concepts.rst
  - https://github.com/python-pillow/Pillow/blob/293218ad059d994baf1777d882911bed6a49704a/src/libImaging/AlphaComposite.c
---

# 精灵透明度交接：四通道字节不说明 RGB 是否已经乘过 alpha

## 生产问题：格式能读，表示仍可能接错

一份精灵或界面图层的宽高、通道数、alpha 值都没有变化，传给下一环节后贡献的颜色却改变了。一个需要排查的原因是：**生产者交付了已经乘过 alpha 的 RGB，消费者却把它当成未乘 alpha 的 RGB，再乘一次。** 这不是文件能否打开或字节预算是否正确能回答的问题。

本文用原始数值 buffer 验证这种表示误接，不使用图片作品或用户素材，不画截图，也不声称已经复现某个游戏的暗边。过滤、图集渗色、颜色编码、混合状态都可能参与真实问题；不能见到边缘异常就直接归因于预乘。

[BC 纹理预算](../rendering/block-compressed-mip-budget.md)关心编码数据量与设备资源量不能混为一谈；这里补充另一个边界：数据量完全相同，也不代表每个通道的语义相同。

## 1. straight 与 associated 之间不是改一个标签

用大写 C 表示未关联颜色，α表示 alpha，关联颜色记作 c：

```text
c = α × C
source-over:
αo = αs + αb × (1 − αs)
co = cs + cb × (1 − αs)
当 αo > 0，输出 straight 颜色 Co = co / αo
```

这是[W3C 固定版本§5.1](https://www.w3.org/TR/2024/CRD-compositing-1-20240321/#simplealphacompositing)的表示区分。该版本是 2024-03-21 Candidate Recommendation Draft，不把它说成最终 Recommendation。RGB 与 alpha 的参与方式必须一起说明；输出颜色采用哪种表示也不能省略。

本实验背景为**不透明黑**，所以αb=1、cb=0，输出αo=1、Co=αs×Cs。这个简化不能直接套给半透明背景；否则可能既算错输出 alpha，又漏掉输出 straight 颜色的归一化。

Pillow 区分`RGBA`与预乘的`RGBa`。[固定 Concepts](https://github.com/python-pillow/Pillow/blob/293218ad059d994baf1777d882911bed6a49704a/docs/handbook/concepts.rst)与[转换源码及模式表](https://github.com/python-pillow/Pillow/blob/293218ad059d994baf1777d882911bed6a49704a/src/libImaging/Convert.c#L406-L435)支持显式转换的含义；直接把同一串字节交给另一模式不是转换。具体 API 接受什么模式仍需按版本核对，不能用名称相似推断可混用。

## 2. 实际数值反例：同一 alpha，颜色又被减弱一次

先冻结一份原创合同：1×1、四个 8-bit 通道，straight 源为`(240,120,60,85)`。alpha 是 85/255=1/3，关联 RGB 应为`(80,40,20)`。这些只是数值探针，不是精灵视觉设计。

|路径|实际操作|实际输出|
|---|---|---|
|显式关联|RGBA→RGBa|`(80,40,20,85)`|
|显式反向转换|该 RGBa→RGBA|`(240,120,60,85)`|
|正确 straight 合成|原 RGBA over 不透明黑|`(80,40,20,255)`|
|正确转换后合成|反向转换得到的 RGBA over 黑|`(80,40,20,255)`|
|错误重标后合成|把关联字节直接解释为 RGBA，再 over 黑|`(27,13,7,255)`|

最后一行 API 正常完成，不是解析器拒绝或异常。它再次对 80、40、20 乘 1/3，产生约 26.67、13.33、6.67，有限样例的整数输出为 27、13、7。正确结果与错误结果的 alpha 同为 255，说明只比较输出 alpha 也找不到这个误接。

oracle 使用独立有理数计算，不复制 Pillow 定点实现。当前所有数字属于**储存通道字节域**；未执行 sRGB 解码、线性光合成、ICC 转换、HDR 或显示测量。不能据此推荐某组字节是物理正确颜色，也不能用这组简单例子代替目标渲染器颜色流程验证。

## 3. 反向转换并不普遍无损

同一夹具还实际检查两个控制：

- alpha 255：关联转换不改变 RGB；over 黑保持原不透明颜色。
- alpha 0：straight 源隐藏 RGB 为 240/120/60；转换为 RGBa 后变成 0/0/0，反向转换仍为 0/0/0。两个透明源 over 黑都不贡献颜色，但原隐藏 RGB 没有恢复。

主例能精确往返，是因为数值专门选成可整除。不能将它升级为任意 8-bit 值都无损，尤其不能把 alpha 0 当作可除的数。较低 alpha 下的量化精度也需另验；本文没有给出全值域误差界。

这不意味着所有流程都应丢弃透明像素中的颜色，也不意味着应把每张纹理一律转成预乘。过滤、编辑、压缩及消费者要求不同，必须确认中间表示与转换时机；本实验不包含这些环节。

## 4. 从文件交付到工作 buffer，明确谁负责解释

[PNG 第二版固定规范§6.2](https://www.w3.org/TR/2003/REC-PNG-20031110/#6AlphaRepresentation)规定文件颜色不预乘。这里只作历史格式边界参考，不声称该版是当前最新版；本实验没有读写 PNG，也未验证任何导入器。文件中的表示、解码后的工作 buffer 和最终消费者的合成约定应分别记录，不能认为 PNG 里会自动携带引擎的 blend 配置。

下面是原创交接建议，不是 Pillow 或工作室强制表格：

|交接字段|要避免的歧义|所需证据|
|---|---|---|
|资产/数据身份|哪次导出或转换产生的字节|文件或 buffer 摘要、内容 revision|
|RGB 表示|straight 还是 associated|模式/API 合同及明确样例|
|alpha 与颜色编码|alpha 范围、位深、RGB 储存编码|实际格式与受控配置；不能仅写 RGBA|
|转换责任|谁在何处乘、除 alpha|转换前后模式与代表值，防止重复执行|
|消费操作|source-over 或其他操作，输入/输出表示|实际版本的 API 与目标工程结果|
|验收范围|字节正确是否被误写成视觉正确|分别标明离线数值、引擎输出、颜色管理与人工视觉验收|

建议同时保留半透明、全透明和不透明探针；若只测试 alpha 255，错误的关联方式可能完全不暴露。先在数据和模式层定位，再决定是否需要修改资产，而不是立即让美术把边缘涂暗或涂亮。

[技术美术职责](../../roles/technical-art/technical-artist.md)可帮助划分工具/材质接口：内容作者确认意图，TA/工具维护转换，渲染侧确认消费者。这里是项目分工建议，不是普遍岗位归属。

## 5. 可复验的证据与停止边界

[实验目录](../../research/experiments/art2d-alpha-contract/README.md)保存实现前的合同、源码、stdout 和每一步数值 JSON。作者在 Python3.12.14/Pillow 自报 13.0.0 上实际执行五组条件：5 次模式转换、6 次 CPU 合成，exit0、stderr 空。每一步记录输入/输出模式与字节；不是只检验最终 PASS 字符串。独立审查在新目录实际复跑，并用另一份有理数与字面 tuple 判据核对全部 11 次操作；仍使用同一 Pillow，不是两种合成实现交叉验证。另有-O 与 PIL 导入失败两项隔离启动检查，均在数值操作前退出且没有留下旧 PASS summary，不作为颜色行为案例计数。

Pillow 标签 13.0.0 解析到固定 commit`293218ad059d994baf1777d882911bed6a49704a`，用作源码比较；解释器及 Pillow 入口、Image 模块、原生_imaging 摘要另行记录，不据版本字符串认证已安装构建。run.py 先清旧 summary、拒绝-O，再导入 Pillow；这不构成一般文件系统或进程故障事务保证。

全文无 PNG 制品、DCC 或引擎导入、GPU 混合、filter/resize/mipmaps、atlas、显示、感知或性能测试。未证明可修复任何具体游戏的暗边，也不声称所有素材应采用同一表示。本条成果是一个可复查的表示交接反例及验收字段，不是未经目标环境验证的资产修复承诺。

## 来源定位

全部读取 2026-10-31。W3C dated Compositing§5.1 用于公式；PNG2003 固定版§6.2 用于历史文件表示边界；Pillow 固定 Concepts 的模式说明、Convert.c 转换与模式表、AlphaComposite.c 支持模式/整数运算用于源代码比较。正文公式、样例及交接表为原创分析；未复制第三方图片或完整源码。
