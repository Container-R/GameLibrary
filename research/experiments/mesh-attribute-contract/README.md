# Interleaved mesh attribute contract：字节读取不等于渲染验收

2026-10-31。来源pin与原始几何在实现前写入 [geometry-contract.md](geometry-contract.md)。Khronos glTF commit `59ecbdba704206bb656965ab4e202881806066f1`，官方spec及两个schema已读，不复制全文。

## 实际执行

`python run.py > run-output.txt 2> run-stderr.txt`

作者实际exit0、stderr空；Python3.12.14，stdlib struct/JSON/base64，无安装。原创160bytes与glTF2 JSON经磁盘JSON重读、嵌入base64严格解码后，由原创受限reader提取。不是外部模型、DCC导出或引擎导入。

POSITION恢复[(1,2,3),(5,2,3),(1,8,3),(5,8,3)]；四个NORMAL均(0,0,1)；索引[0,1,2,2,1,3]恢复两片+Z平面三角形。用独立字面顶点/索引/三角形oracle对照，不以未越界代替语义正确。

朴素读法起点正确20bytes，却以12而非28递增，得到[(1,2,3),(0,0,1),(99,5,2),(3,0,0)]。所有读均在声明vertex view内，仍非原始POSITION。这是reader误解合法fixture，不是认定原始glTF有错。

## 九个实际拒绝

1. vertex view缩至108bytes，buffer仍160：NORMAL最后访问终点112，超出view，而非大buffer。
2. stride26不满足4倍数。
3. stride8小于VEC3元素12。
4. POSITION accessor offset2违反FLOAT分量对齐。
5. vertex view offset18违反FLOAT分量对齐。
6. index view定义stride违反角色限制。
7. index4越过四个顶点。
8. 65535以禁止最大值理由拒绝。
9. POSITION首值NaN以非有限值理由拒绝。

异常原因逐项精确检查；每项在内存副本单一修改，原始制品不变。reader还实现bounds、normal长度、count/target等约束，但未将其每个分支都计为独立已测案例。

## 证据与边界

results/mesh.gltf带内嵌buffer；results/mesh.bin.base64保存相同160bytes。解码SHA `06572d2d89cac7d7dc8c9586ecde6325b82fe0615dfe0e5d4236d7e37a16f268`。summary及stdout单个RESULT_JSON含实际恢复值、错误读法、九拒绝和源hash。

限定一个mesh/primitive、FLOAT VEC3 POSITION/NORMAL、ushort SCALAR索引、TRIANGLES、无sparse/normalized/扩展。合法glTF也可省略accessor bufferView并初始化零；这种implicit-zero形式被本subset排除，当前reader缺字段会抛KeyError，不是把所有无bufferView资产认定为格式非法。reader不获取URI或任意文件，runner仅解码自建数据URI。不是通用安全parser或官方Validator；无GPU、DCC、引擎、法线变换、坐标转换、材质、skinning、动画、quantization验证。NORMAL单位长度1e-6容差是本reader政策，不冒称规范epsilon。+Z朝向为字面拓扑判断，不是光栅化结果。

清旧summary在reader import前；-O拒绝、显式非assert验收；不保证解释器/权限/任意终止报告原子性。重跑用独立复制目录。冻结reader `b9b5709b6730c3acaf662112169a28f50e9330ee05bf8208ca1692515d7d3e36`；runner `499ba210218426691e50597d067e69d2aea39a8bd3bc124d2d2a71041004b8f0`。

对应文章见 [几何交接契约](../../../solutions/modeling/gltf-interleaved-attribute-contract.md)。一次仅为归档官方文本hash的大参数命令被exec工具以Argument list too long拒绝，未执行；不涉及fixture运行失败，未改动已通过源码/结果。采用不可变commit链接保留来源定位。

## Public reproducibility layout

Current author files are at this directory; independent frozen sources/results remain under review/fixture so review/negative.py can resolve them. To repeat negative.py, copy it and fixture/ to a fresh directory without historical negatives/; it refuses existing case directories. Historical absolute command paths are provenance, not required checkout locations. No binary files or Python caches are included; original mesh.gltf embeds the same bytes as mesh.bin.base64. [Independent review](review/REVIEW.md) separates invalid layouts from unsupported implicit-zero accessors and structurally acceptable but unintended geometry.
