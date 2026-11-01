# glTF 切线基交接：单位向量不等于正确的变换方向

核对日期：2026-11-01。本文核对固定 Khronos 规范与示例实现，并给出原创的精确手推。没有执行数值模型、导入器、shader 或渲染，没有生成资产，也没有观察某个导出器的错误。

[glTF 属性与几何交接](../../solutions/modeling/gltf-interleaved-attribute-contract.md)已有有限字节读取、稀疏属性与实际导入证据，但明确不覆盖切线和最终画面。[CPU 与 shader 矩阵合同](../../solutions/rendering/matrix-major-interface-contract.md)区分存储与代数约定，也不能替代这里的方向语义。本条新增的问题是：**NORMAL 与 TANGENT 都保持单位长度，是否就足以接收一次非均匀缩放？**

## 先分清局部属性合同与接收端实现

固定 glTF 2.0 规范源提交 `59ecbdba704206bb656965ab4e202881806066f1` 的[属性表](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#L1661-L1662)规定单位 NORMAL、单位 TANGENT.xyz，以及表示 handedness 的 `TANGENT.w=±1`。[Using Primitive Data](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#L1813-L1830)给出局部副切线重建 `B=(N×T)w`；同三角形的 w 应（SHOULD）一致，不同则该切线空间未定义。

另一个层次是实现：Khronos glTF-Sample-Renderer 固定提交 `6e8a3d1aaa6f07e9f1310a488453e21325677786` 的 [renderer.js](https://github.com/KhronosGroup/glTF-Sample-Renderer/blob/6e8a3d1aaa6f07e9f1310a488453e21325677786/source/Renderer/renderer.js#L1835-L1862)构造 inverse-transpose normal matrix；所选 [primitive.vert 分支](https://github.com/KhronosGroup/glTF-Sample-Renderer/blob/6e8a3d1aaa6f07e9f1310a488453e21325677786/source/Renderer/shaders/primitive.vert#L83-L161)用它变换法线，而切线使用 model matrix，再构造副切线。这是固定示例代码观察，不是所有引擎的实现保证。

两项提交时间分别为 2026-10-30、2026-10-26；它们用于标识修订，不冒充独立发布版本日期。以下只选择**已有 N/T、静态、未启用 shader 的 USE_INSTANCING 分支、无 morph、无 skin、无 normal-UV transform** 的路径，且仅研究顶点处的基向量；这不排除普通 glTF 节点实例化。

## 一个单位长度检查无法识别的反例

约定列向量、右手叉积。原创局部输入为：

\[
N=\frac{(1,1,0)}{\sqrt2},\qquad
T=\frac{(1,-1,0)}{\sqrt2},\qquad w=+1.
\]

两向量单位长度且垂直，`B=N×T=(0,0,−1)`。若只把 w 改成 −1，B 就变成 `(0,0,+1)`，而 N 与 T.xyz 完全相同。因此，在这个合同中丢掉 w 会丢失一个实际区别，不是无损去除冗余分量。这不是关于某个文件转换器已经丢数据的指控。

现在施加有限、可逆的非均匀缩放：

\[
A=\operatorname{diag}(2,1,1).
\]

切向方向变成 `AT`。要让法线仍垂直于变换后的切平面，inverse-transpose 的关系是：

\[
(A^{-T}N)^T(AT)=N^TT=0.
\]

这个等式使用 A 可逆的前提；不是所有退化变换的处理规则。此例具体得到：

\[
A^{-T}N=\frac{(1/2,1,0)}{\sqrt2},\qquad
AT=\frac{(2,-1,0)}{\sqrt2}.
\]

归一化后的正确方向为：

\[
N'=\frac{(1,2,0)}{\sqrt5},\qquad
T'=\frac{(2,-1,0)}{\sqrt5}.
\]

它们的点积是 `(2−2)/5=0`，叉积为 `(0,0,−1)`。

反过来，若把法线也直接乘 A，然后归一化：

\[
N_{\rm wrong}=\frac{(2,1,0)}{\sqrt5},\qquad
N_{\rm wrong}\cdot T'=\frac{4-1}{5}=\frac35.
\]

**两个候选法线都长为 1，但只有前者保留了本例要求的垂直关系。** 再次 normalize 并不能修复后一种方向错误。这是精确代数反例，没有浮点测量、截图或设备结果，也没有证明某个实际接收器走了错误路径。

## 把接收要求落到具体字段与空间

下表是原创、未执行的交接建议，不是增加一套通用资产合规检查器。

| 接口 | 提交者需要说明 | 接收者不能用什么替代 |
|---|---|---|
| 局部属性 | 是否供应 N/T，T 的四个分量如何保留；适用的局部基约定 | 用 XYZ 相同证明 handedness 相同 |
| 实例变换 | 方向所在空间、normal 与 tangent 各自使用的矩阵、归一化位置 | 只检查单位长度，或只说矩阵字节布局正确 |
| 有限数学接收 | 在明确输入与可逆 A 下，复核上面的方向和点积关系 | 用默认均匀缩放下“看起来正常”证明非均匀缩放路径 |
| 画面接收 | 另行指定实际材质、normal-map、插值与面朝向处理及设备观察 | 把顶点基的代数正确直接升级为最终外观通过 |

若项目只支持某类变换，应把限制写在实例交接中；若需要扩展，先明确新增空间和退化政策，不能把同一份属性读取通过记录自动移用到渲染路径。

## 反射与最终画面：保留边界，不附送修复处方

本例的 determinant 为正。[glTF 实例化条款](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#L2195-L2203)另行规定 determinant 符号与正面绕序的关系；绕序、法线方向及副切线构造不是同一个字段。本文不据此要求所有接收器统一翻转 w，也不宣称示例渲染器的负缩放实现有缺陷。

这里没有证明插值后的基仍正交、normal-map 重建正确或画面无伪影。奇异/近退化变换、剪切、蒙皮、morph、切线生成、双面材质和纹理变换需要各自的合同与证据；不能把一次顶点基手推推广为完整渲染流水线认证。

生成之前后的共享关系另见[面角切线输出与重索引](tangent-corner-output-and-reindexing.md)：旧索引可以提供输入属性，却未必能保存新增切线的逐面角区别；该来源分析与原创手推不改变本文的变换范围。
