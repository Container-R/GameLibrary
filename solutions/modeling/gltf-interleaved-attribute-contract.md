---
id: SOL-MODEL-001
title: 有效字节不等于正确顶点：glTF 交错属性的偏移、步长与几何验收
type: solution
status: source-backed
primary_discipline: MODEL
related_disciplines: [TA, ENGINE, GFX, QA]
related_roles: [environment-artist, technical-artist, engine-programmer]
related_topics: [gltf, mesh-attributes, interleaved-buffer, asset-handoff, topology]
engines: [Godot]
versions: ["glTF 2.0 specification source 59ecbdba704206bb656965ab4e202881806066f1", "Python standard-library fixture", "installed Godot self-report 4.6.3; source identity unverified"]
platforms: [offline-cpu-format-validation, headless-native-import-data]
updated_at: 2026-10-31
verification_method: 固定官方规范与schema核对；原创有限交错网格CPU读取与独立字面验收；Godot原生导入2次作者进程含1次额外AABB断言失败，另1次独立复跑；未执行DCC导出、编辑器导入或GPU渲染
sources:
  - https://docs.godotengine.org/en/4.6/classes/class_gltfdocument.html
  - https://docs.godotengine.org/en/4.6/classes/class_importermesh.html
  - https://docs.godotengine.org/en/4.6/classes/class_arraymesh.html
  - https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/gltf/gltf_document.cpp
  - https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/servers/rendering/rendering_server.cpp
  - https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc
  - https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/schema/accessor.schema.json
  - https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/schema/bufferView.schema.json
  - https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/schema/mesh.primitive.schema.json
---

# 有效字节不等于正确顶点：glTF 交错属性的偏移、步长与几何验收

## 要交接的是几何，不只是能打开的文件

资产检查显示JSON可读、二进制长度足够，但自制处理工具得到的顶点仍不对。此时不能立即要求美术重导：读取器可能把交错POSITION/NORMAL当作连续POSITION，也可能只验证整个buffer足够，却越过了声明的bufferView。

本方案把三个验收分开：**存储跨度合法、属性解释正确、索引恢复出的几何符合意图**。原创样例仅四个顶点、两个三角形，能用字面表独立对照；不是通用 glTF 解析器；原 CPU 实验没有执行引擎，第7节另有同一资产的实际 Godot 原生导入数据观察，仍未验证任何 DCC 导出或编辑器导入流程。

## 1. 三层地址必须保留

依据固定规范的[Buffer Views与Accessors](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#buffer-views)，bufferView给出buffer中的跨度，accessor给出类型、数量与相对view的起点。vertex属性存在byteStride时，相邻元素按它推进，而不是按单个元素大小推进。

```text
absolute_element_start(i) = view.byteOffset + accessor.byteOffset + i × stride
required_view_span = accessor.byteOffset + (count - 1) × stride + element_size
```

这里count为正数；无byteStride时才用element_size作为stride。需要同时检查view末端不越过声明buffer，以及required_view_span不越过声明view。最后一项是element_size，不是额外一整段stride：末元素之后不必保留下一条记录的所有padding。

本例FLOAT VEC3每元素12bytes、组件4bytes；vertex stride是28bytes。规范还约束对齐、stride范围与类型关系。两个属性共用一个view必须声明stride；索引view不能借用vertex stride。相关[accessor schema](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/schema/accessor.schema.json)和[bufferView schema](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/schema/bufferView.schema.json)描述字段约束，但JSON字段通过不等于实际二进制值和目标几何通过。

## 2. 先冻结意图，再读取字节

原创几何位于z=3平面，POSITION为 `(1,2,3), (5,2,3), (1,8,3), (5,8,3)`；NORMAL均为 `(0,0,1)`。索引为 `0,1,2, 2,1,3`，两个三角形均朝+Z。POSITION声明min/max为 `[1,2,3]` / `[5,8,3]`。这些值在实现前写入契约，而不是看程序结果后改变预期。

| 数据 | 起点/跨度 | 每个元素 | 读取规则 |
|---|---|---|---|
|完整buffer|160bytes|—|16bytes前缀、112bytes顶点view、12bytes索引view、20bytes尾部|
|顶点bufferView|offset16，length112|4条28bytes记录|每条：padding float99、POSITION 3f、NORMAL 3f|
|POSITION accessor|view内offset4，count4|FLOAT VEC3，12bytes|绝对起点20、48、76、104|
|NORMAL accessor|view内offset16，count4|FLOAT VEC3，12bytes|绝对起点32、60、88、116|
|索引bufferView|offset128，length12|6个uint16|无stride，SCALAR|

POSITION最后访问到view内100bytes；NORMAL最后访问到112bytes。若把view长度改为108，整个160bytes backing buffer仍然足够，但NORMAL已越过声明view，必须拒绝。不能把后面的索引或尾部当作未经声明的“可用余量”。

## 3. 两种错误不能混称文件损坏

**正确文件，错误解释。** naive读取器从正确的POSITION绝对起点20开始，却每12bytes读取一次。四次读取仍在顶点view之内，但后续读到了NORMAL、padding及其他字段，不能恢复字面POSITION。只检查内存不越界无法捕获这种语义错误；原资产并未因此变成非法glTF。

**不合法声明，即使内存够。** 缩短view、错误对齐或非法stride，属于另一层失败。有限读取器在读取前检查边界与限定类型，负例必须以预期拒绝原因失败，不能让无关异常冒充已覆盖特定规则。

本夹具在JSON回读、data-URI base64物化后再提取属性；没有从网络解析URI。数值与索引随后对照独立字面几何。读取成功只证明有限契约，不证明完整规范实现、安全解析器、GPU支持或视觉正确。

## 4. 索引代表整组属性，不只是位置

规范[Topology and Connectivity](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#meshes-topology)中，一个primitive的索引同时选择各attribute accessor的同一编号；不能在同一索引流里另配一套不相干的法线编号。所有属性数量需要一致，索引必须落在属性范围内，并避开对应无符号类型的最大保留值。

因此DCC中的“位置数量”和导出后“属性组合数量”不是天然同一预算。若同一位置需要不同法线/UV组合，不能仅凭坐标相同就合并顶点；应验证合并后整组属性与三角形关联。此处是规范推导的交接要求，本次样例没有UV接缝、顶点合并或DCC导出实验，不据此给出导出增量百分比。

## 5. 美术、TA、引擎与QA的交接清单

1. **美术/内容侧给意图证据：** 一小段可辨识几何、朝向、属性语义和预期索引；不要只给文件大小或截图。
2. **TA记录实际布局：** buffer/view/accessor对应、偏移单位、stride、组件类型、数量及POSITION bounds；保留导入/导出配置，参照[资产导入意图契约](../engine/asset-import-intent-contract.md)。
3. **工具/引擎侧分层拒绝：** 先检查支持子集与跨度，再解释数值，再验收拓扑；不把未支持扩展静默当作普通数据。
4. **QA独立核对可观察输出：** 固定字面顶点、索引和三角形；同时测试“合法但误读”与“非法view被拒绝”，避免只看PASS。
5. **渲染验收另行完成：** 坐标系、变换、材质、切线、蒙皮和最终设备画面不在本例范围。纹理容量也不能从顶点数量推断，见[BC逐mip预算](../rendering/block-compressed-mip-budget.md)。

以上为原创交接建议，不是厂商统一流程。完整职责边界见[技术美术](../../roles/technical-art/technical-artist.md)。

## 6. 实验与边界

[源码、冻结几何、原始输出和独立复核](../../research/experiments/mesh-attribute-contract/README.md)保留作者与独立复跑。原始运行包含一组正确提取、一个未越界的错误解释和九个精确原因拒绝；独立字面checker不用作者reader，检查绝对地址、base64、索引和两个三角形叉积，均为`[0,0,24]`。这说明+Z方向，不是光栅化结果。

复核另有六个进程内拒绝探针（其中缺bufferView属于不支持的合法子集，不是格式非法）、两个实际子进程启动失败探针，以及一个刻意保持结构自洽却改变目标属性的接受案例。后者将POSITION指向NORMAL并配套调整bounds，reader返回退化几何而独立意图对照失败，再次表明格式条件不能代替内容意图。两次启动失败分别为`-O`和替换reader导入失败，均退出1且清掉旧summary；不外推解释器启动、权限或任意终止的原子报告保证。

原创buffer SHA256为 `06572d2d89cac7d7dc8c9586ecde6325b82fe0615dfe0e5d4236d7e37a16f268`；reader为 `b9b5709b6730c3acaf662112169a28f50e9330ee05bf8208ca1692515d7d3e36`，runner为 `499ba210218426691e50597d067e69d2aea39a8bd3bc124d2d2a71041004b8f0`。Python自报3.12.14；没有据此认证上游解释器构建。不要把每个字段比较累计成新的独立格式实验。

限定子集：一个已提供的binary buffer，一个mesh/primitive，TRIANGLES，FLOAT VEC3 POSITION/NORMAL，UNSIGNED_SHORT SCALAR indices。也不支持合法的无bufferView隐式零初始化accessor；当前缺该字段会抛KeyError，不应把它误报为规范禁止。没有稀疏accessor、矩阵、normalized整数、外部URI解析、扩展、压缩、蒙皮或动画。NORMAL长度的1e-6容差、字面POSITION bounds精确比较是该有限reader政策，不是规范指定epsilon或一般导出浮点容差。标准库CPU处理不是官方validator、DCC导出、引擎导入或GPU运行。

## 7. 同一文件真正进入引擎后，不能再要求所有表示逐字相等

[原生导入夹具](../../research/experiments/godot-gltf-import-boundary/README.md)把此前 `mesh.gltf` **逐字节复制**到隔离工作目录，保留 JSON 与嵌入160字节 buffer 的固定摘要。实际调用 `GLTFDocument.append_from_file`，读取 `GLTFState` 中的 `GLTFMesh.mesh`（ImporterMesh），再调用其 `get_mesh()`，读取返回的 ArrayMesh。这是同一次导入的两个数据阶段，不是两个独立解析器，也没有生成或渲染场景。

实际返回码为0；状态包含1个mesh、1个node、3个accessor、2个bufferView及160字节buffer。两个阶段均为1个 TRIANGLES surface，四个位置与原字面表精确一致：

| 交接项 | 源文件 / CPU意图 | ImporterMesh | ArrayMesh读回 |
|---|---|---|---|
| 索引 | `0,1,2,2,1,3` | `0,2,1,2,3,1` | 与ImporterMesh相同 |
| 位置 | 原四个字面坐标 | 精确一致 | 精确一致，仅此有限输入 |
| 法线 | 全部`(0,0,1)` | 精确一致 | 约`(3.66e-10,-3.05e-5,1)`，在预冻结每分量`1e-4`容差内 |
| UV | 无此输入属性 | 无 | 无；不是UV正确性验证 |

**索引变化不自动等于几何损坏。** Godot 4.6 [ArrayMesh文档](https://docs.godotengine.org/en/4.6/classes/class_arraymesh.html)说明三角形正面采用顺时针；预先检查的[固定导入源码](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/gltf/gltf_document.cpp#L1482-L1518)交换每个三角形后两个索引，并按原顶点顺序映射已使用顶点。全部四顶点均被使用，所以本次在运行前即冻结上述目标索引，不是事后排序凑相等。导入后数学叉积Z为-24，而提供的法线仍近+Z；不能为追求二者同号擅自翻转源法线。

ArrayMesh 的小法线差异是**实际读回观察**，不是本研究测得的视觉误差，也不据此给出所有网格通用误差界限。这里没有验证其实际GPU物理布局；源buffer的28字节stride不能当作ArrayMesh或GPU存储stride。

### 不能把诊断边界变成事后补出的强断言

第一次作者运行的原生导入成功，但完整 Python 验收失败：代码额外要求平面 AABB 的Z尺寸严格为0。这个条件不在冻结几何契约内；实际 AABB位置为`(1,2,3)`、尺寸约`(4,6,1e-5)`。原源码、原始输出和失败回溯保存在 `historical-zero-depth-aabb/`，没有改标为PASS。

随后检查的[固定渲染服务源码](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/servers/rendering/rendering_server.cpp#L451-L458)在计算点集AABB后以 `SMALL_VEC3` 限制最小尺寸。修正仅移除多加的零厚度断言，把AABB保留为诊断；源输入、位置/索引判据及预定法线容差不变。新作者运行和一次独立重复均通过。总计作者2次导入（含首次全验收失败）、审查者1次导入；另有1次版本探测，不算导入案例。审查者3项旧PASS清理反例不启动Godot，其中仅1个合成程序实际执行，不是坏glTF资产测试。

### 接口证据不等于编辑器或视觉证据

实际安装二进制摘要为 `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`，自报4.6.3/`7d41c59c4`；它与用于比较的公开源码提交 `35e80b3a…` 未建立认证对应关系，见[共享来源边界](../../research/source-notes/godot-runtime-provenance.md)。源码解释是比较依据，不是认证该二进制实现的证明。

因此工程交接应分别规定：不可变源字节、API成功与实际资源枚举、逻辑几何/属性、目标表示约定、最终渲染验收。前四项在本小输入上有有限证据；编辑器`.import`配置、DCC导出、材质/切线/UV/蒙皮/动画、场景组装、错误资产安全性、GPU渲染和性能仍不在范围。原CPU负例没有因此变成Godot拒绝测试。

## 来源定位

Khronos源固定到 `59ecbdba704206bb656965ab4e202881806066f1`，提交日期2026-10-30，读取2026-10-31。正文公式、属性和索引要求对应该不可变源；schema是同一项目的补充证据，不算独立厂商交叉验证。访问其他手册失败的发现线索未充作已读来源。
