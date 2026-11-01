---
id: NOTE-MODEL-TANGENT-INDEX-001
title: 切线生成的面角输出：旧顶点索引不是结果接收索引
type: research
status: source-backed
primary_discipline: MODEL
related_disciplines: [GFX, TA]
related_topics: [tangent-generation, face-corners, vertex-indexing, mirrored-uv]
versions: ["MikkTSpace 作者源 3e895b49d05ea07e4c2133156cfa94369e19e409，头文件 Version 1.0", "glTF 2.0 规范源 59ecbdba704206bb656965ab4e202881806066f1"]
updated_at: 2026-11-01
review_after: 2027-02-01
verification_method: 固定作者接口与源码、固定Khronos规范核对；两面角参数化及重索引映射为原创未执行手推，未运行切线生成器、导出器或渲染
sources:
  - https://github.com/mmikk/MikkTSpace/blob/3e895b49d05ea07e4c2133156cfa94369e19e409/mikktspace.h
  - https://github.com/mmikk/MikkTSpace/blob/3e895b49d05ea07e4c2133156cfa94369e19e409/mikktspace.c
  - https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc
---

# 切线生成的面角输出：旧顶点索引不是结果接收索引

## 生成器返回的对象，可能比旧顶点更细

模型接收器原本可能用一个顶点索引同时引用位置、法线和 UV。新增切线后，不能因为前三项仍相同，就认为所有面角的完整结果也相同。关键不是“有没有生成切线”，而是**回调的输出域如何映射到最终顶点记录**。

Morten S. Mikkelsen 的固定 [MikkTSpace 头文件输出回调](https://github.com/mmikk/MikkTSpace/blob/3e895b49d05ea07e4c2133156cfa94369e19e409/mikktspace.h#L79-L107)按面号和面内角点返回未索引化切线结果，警告不要通过既有索引平均或覆盖它们，可以生成新索引。对应[输出循环](https://github.com/mmikk/MikkTSpace/blob/3e895b49d05ea07e4c2133156cfa94369e19e409/mikktspace.c#L401-L413)也保留这两个定位量；所读[UV定向计算](https://github.com/mmikk/MikkTSpace/blob/3e895b49d05ea07e4c2133156cfa94369e19e409/mikktspace.c#L965-L1007)与[分组检查](https://github.com/mmikk/MikkTSpace/blob/3e895b49d05ea07e4c2133156cfa94369e19e409/mikktspace.c#L1144-L1179)保留普通非退化三角形的定向区别。

固定 [glTF Using Primitive Data](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#L1808-L1830)针对**未提供切线且材质具有法线纹理**的情形，规定使用默认 MikkTSpace 算法；并给出 `B=(N×T)w`。这不意味着所有资产必须存切线，也不是所有引擎实现一致的证明。

以下推导说明旧索引为何可能不够用，不冒充一次 MikkTSpace 回调输出。

## 原创输入：共享边的旧属性一致

**原创、未执行。** 两个非退化三角形位于 XY 平面，法线均为 `N=(0,0,1)`。无变换、蒙皮、morph、退化 UV 或四边形。

| 旧顶点索引 | 位置 | UV |
|---:|---|---|
| 0 | O=(0,0,0) | (0,0) |
| 1 | X=(1,0,0) | (1,0) |
| 2 | Y=(0,1,0) | (0,1) |
| 3 | D=(0,-1,0) | (0,1) |

面 F0 使用旧索引 `(0,1,2)`，面 F1 使用 `(0,3,1)`，几何绕序都朝 +Z。O、X 的位置、法线与 UV 在两面完全一致，原本可以引用同一旧记录；两面的 UV 有符号二倍面积却分别为 +1、−1。

F0 的位置参数化为 `(u,v,0)`，F1 为 `(u,−v,0)`。因此两者的单位切向都是 `T=(1,0,0)`，副切向分别为 `(0,1,0)` 和 `(0,−1,0)`。按上述叉积关系，所需符号分别为 +1、−1。

这里沿用[已有切线基说明](tangent-handedness-normal-transform.md)中的符号合同，但问题发生在生成结果的接收，而非实例变换。O 或 X 的同一个旧槽无法同时保存这两份完整结果。将面角结果写回旧索引会让结果依赖覆盖顺序，或者在平均时丢掉两者的区别；不能以 T.xyz 相同证明整个切线属性相同。

## 明确映射：六份记录，不改变面角对应关系

对于这个手推例，可以先保留每个面角的属性，再建立以下最终记录。表中每一行都携带对应旧记录的位置、法线、UV，以及本例推导的 T.xyz 与 w；没有假定其他未列属性已经处理。

| 新记录 | 来源面角 | 旧记录 | T.xyz | w |
|---:|---|---:|---|---:|
| 0 | F0角0 | 0（O） | (1,0,0) | +1 |
| 1 | F0角1 | 1（X） | (1,0,0) | +1 |
| 2 | F0角2 | 2（Y） | (1,0,0) | +1 |
| 3 | F1角0 | 0（O） | (1,0,0) | −1 |
| 4 | F1角1 | 3（D） | (1,0,0) | −1 |
| 5 | F1角2 | 1（X） | (1,0,0) | −1 |

新索引为 F0=`(0,1,2)`，F1=`(3,4,5)`。变化的是顶点记录的共享关系，不是三角形的位置或面角顺序。旧索引0分别对应新0、3；旧1分别对应新1、5：**旧顶点到新顶点未必是一对一映射。** 若转换器只保留一个 `oldIndex→newIndex` 值，就无法表达本例两侧的完整属性。

六份记录是这个特定输入的可行表示，不是所有网格必须完全展开。若其他面角的最终完整属性等价，可以再次共享；反之，仅 w 相同也不足以合并。实际模型的颜色、蒙皮、其他UV集及其他逐顶点数据都需要维持正确的面角对应，本文没有验证这些路径。需要按最终表示的精度和属性合同决定相等性，而不是在此给出通用浮点容差。

## 接收决定：保留输出域，再决定共享

以下是原创未执行的有限接收程序，不是完整导出器：

1. 用 `(face, corner)` 留住每份输出，先不要按旧索引覆盖。输入端仍可以从旧索引读属性，输出端却不能未经验证地沿用同一共享关系。
2. 对本例逐一核对六个角点的完整记录与新索引映射，特别是旧0和旧1的两份去向。检查新索引引用的属性，而不只是顶点总数或生成函数是否成功。
3. 若需要重新合并，按最终所需全部属性建立等价关系，并同步重建属性记录和索引。只按位置／法线／UV合并会重新引入本例冲突，只按切线符号合并也不充分。

通过这些静态对应检查仍不能证明材质采样、插值、设备画面或渲染接缝正确。本文没有调用生成器、生成glTF、运行导入器或观看渲染，也不指控真实工具出现了覆盖错误。

## 与相邻问题及来源身份的界限

[glTF 属性交接](../../solutions/modeling/gltf-interleaved-attribute-contract.md)已有字节跨度和几何接收，但其中的 primitive 索引不等于 [sparse accessor](gltf-sparse-accessor.md) 的目的元素索引；本题又增加了输出面角与最终记录的映射层。[piece 烘焙过滤](model-bake-piece-visibility.md)控制候选表面集合，不负责解决顶点属性共享。任何既有执行结果都不作为本例证据。

MikkTSpace 固定提交为 `3e895b49d05ea07e4c2133156cfa94369e19e409`（2020-03-25），头文件署名 Morten S. Mikkelsen、标注 Version 1.0；提交日期不是版本首次发布日期。glTF规范源固定于 `59ecbdba704206bb656965ab4e202881806066f1`。2026-11-01实读上述接口及分支、规范1800–1840行；没有证明完整生成算法、退化输入政策、切线量化或任意重索引优化正确，也不扩写采样逆变换与四边形三角化问题。
