# BC payload：逐 mip 数值与真实离线 DDS 解码

2026-10-31；本次最终执行 **14 个数值案例、6 个非法输入拒绝、6 个 Pillow 原生解码、1 个截断布局拒绝通过**。没有 GPU/API 资源创建、压缩器、质量评估或驻留测量。来源与证据边界见 [proposal.md](proposal.md)。源码已冻结；运行不访问网络。

## 执行与真实结果

```sh
python run.py > run-output.txt 2> run-stderr.txt
```

从任意目录运行；输出放在本脚本旁 results/。不要在归档原始证据目录直接重跑：先复制到新目录，再执行。实际退出码 0；Python 3.12.14，Pillow 自报 13.0.0。stderr 保留 `getdata` 弃用警告（预计 Pillow14 移除），没有静默丢弃警告；此次方法仍实际返回像素。版本自报和模块字节 SHA 是本地执行身份记录，未验证发行二进制与上游 tag 完全对应。

| 基础逻辑尺寸 | BC1 完整链 bytes | BC7 完整链 bytes |
|---|---:|---:|
|1×1|8|16|
|4×4|24|48|
|8×8|56|112|
|60×40|1664|3328|
|7×5|48|96|
|1×8|40|80|
|17×17|256|512|

4×4 的 base BC1 为8 bytes，乘4/3约10.67，低于24；17×17 base为200，乘4/3约266.67，高于256。因而常数倍率并非严格上界或下界。后者只测离线布局，不声称17×17可作为 D3D10 BC base resource 创建。

## 唯一实际完整制品

原创手工 endpoint+selector 组成的 BC1 block；没有第三方素材、输入图像或图像编辑。六级色标依次红、绿、蓝、黄、品红、青，RGB565端点正好对应255/0通道，selector全0。相同色的其他endpoint设0，无需压缩优化算法。

| mip | 逻辑尺寸 | BC1 payload bytes | DDS绝对偏移 | 全部解码像素 |
|---|---|---:|---:|---|
|0|60×40|1200|128|红|
|1|30×20|320|1328|绿|
|2|15×10|96|1648|蓝|
|3|7×5|32|1744|黄|
|4|3×2|8|1776|品红|
|5|1×1|8|1784|青|

`results/markers.dds` 共1792 bytes：128 byte legacy DDS 描述 +1664 byte payload。SHA256 `1e8f263dbf5aafe04b26626ba7b17ef9ec455337d2f8fed3ddcdbcf145e2f20f`。每一级从完整文件按独立字面偏移表取片，另包装为单级 DDS，使用实际 `Image.open().load()` 解码并遍历全部逻辑像素验证颜色。不是声称 Pillow 一次读取原文件就验证了完整 mipchain；它是否自动遍历全链不在实验中。小级别 wrappers 是离线 decoder 探针，不是 D3D 资源创建证据。

`check_fixture` 是**特定原创制品 checker，不是通用 DDS parser**：独立字面 header、完整长度、逐级偏移；marker色还检查每片的归属。最后删8bytes生成的负例由长度检查明确拒绝，未把它交给宽容 decoder 来推测完整性。

## 保存与复核

- 当前 `results/summary.json` 含完整数字表、实际解码记录、制品与源码 SHA，以及 Python/Pillow包入口、DDS插件、原生 `_imaging` 模块 SHA。
- `run-output.txt` 含单一 RESULT_JSON；`run-stderr.txt` 为实际警告；当前运行exit0。
- `results/*.base64` 是对应二进制的无损编码；先在新建临时目录用 `base64.b64decode(..., validate=True)` 解码去掉首尾空白后的文本，再比较 summary 的 SHA，勿覆盖工作文件。
- `historical-six-pairs/` 保留第一次已通过的6尺寸对版本及日志。随后父审查建议补充17×17以同时证明倍率高估方向，修改源码后重新执行全部固定案例；这是增加案例，不是隐藏失败或调整预期。两轮均保留弃用警告。
- 源码验收使用显式异常而非 assert；启动先清旧 summary，再拒绝 `-O`。原始运行未包含runner故障注入；后续v1/v2合成负例分开记录于文末。

## 适用界限与预算交接

本模型只接受完整链；proposal 中曾讨论的自选 mip 数与选择性子集接口**未实施**，也没有相应通过数。BC7只有算术，没有BC7编码/解码制品。除已测有限样例，任意大尺寸、DDS变体、数组/立方/3D纹理、其他BC格式均未验收。

建立预算时应分别给出逻辑尺寸/格式/实际存储mips、紧密payload、容器与包文件长度、上传footprint、目标API分配查询、实际resident量。前两类可由本模型和离线制品支持；后几类需要平台/引擎实测。发行包二次压缩、资源对齐、稀疏页和streaming mip-tail策略不会被简单求和自动涵盖。本实验不能推断节省1664bytes文件payload就一定省同量VRAM。

## Public archive representation

The binary `results/markers.dds` is reconstructed from the lossless `results/markers.dds.base64`; binary copies and Python caches are not checked in. Recorded absolute runtime paths are historical provenance, not required checkout paths. Independent review and frozen checker are under [review/](review/REVIEW.md); its historical `fixture/results` invocation corresponds to public `review/results`. Copy to a separate directory before reproducing.

## Current runner and preserved history

Current sources/results are corrected v2 (run.py SHA256 `1ca81455b9ef0605a01b7dbfff15454a3294c16bfe335e5f964919ba251b7cef`). Original reviewed v1 source/results and review are under historical-v1. Import failures in v1 could leave old PASS, and an emitted offset mutant bypassed author checks but not the independent oracle. V2 invalidates old summary before optional imports and checks numeric offsets and block axes against independent expected dimensions/counts. See [correction details](v2-correction.md). This is not protection against interpreter startup, filesystem permission or arbitrary termination failures. The intermediate offset-only passed draft is omitted from the public selection; original failure evidence and final v2 are retained.

Final v2 independent review is [review/REVIEW.md](review/REVIEW.md). [Original synthetic failures](negative-v1/README.md) preserve the actual false acceptance and stale receipt; [final negative records](negative-v2/observations.json) contain twelve child invocations, all rejected. Seven runner cases clear prior summaries; no final negative reaches a decode. The terminal checker after rejected offset mutation only tests missing-summary rejection, not offset semantics. Harness -O refusal is a separate invocation, not a thirteenth child. See each PUBLIC_LAYOUT.md for reproducible archive selection.
