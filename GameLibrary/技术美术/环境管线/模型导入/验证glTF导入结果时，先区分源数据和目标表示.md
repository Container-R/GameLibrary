# 验证glTF导入结果时，先区分源数据和目标表示

导入工具返回成功，读回的顶点位置也正确，索引却变了，法线还多出很小的分量。此时直接比较源数组和引擎数组，可能把正常的目标表示转换判成损坏；把所有差异都归为“引擎做了优化”，又会漏掉真正的错误。

解决办法是把验收放在明确的交接处：先确认源 accessor 表达什么，再规定导入阶段允许怎样改变编号和绕序，最后检查运行时网格读回是否满足对应的属性要求。本文面向维护模型导入与验证工具的程序员，以固定 Godot 4.6 源码中的 glTF → ImporterMesh → ArrayMesh 路径为例，给出可以照着建立的比较过程。[1][2]

这里处理网格局部空间中的有索引三角形、位置和显式法线，不把场景节点变换、材质、蒙皮、动画或最终图像一起塞进数组比较。源 accessor 的寻址和索引组装可先读[普通交错属性读取](读取glTF交错顶点数据时的偏移与步长.md)；遇到 sparse 时先完成[稀疏属性展开](用cgltf完整展开glTF稀疏属性.md)。源层尚未正确时，不能通过放宽引擎读回容差解决问题。

## 先确定比较的是哪一层

同一文件在处理过程中会有几种表示。为每一层保留自己的结果，才能定位差异首次出现在哪里。

| 交接处 | 取得的内容 | 要回答的问题 |
|---|---|---|
| 源文件和已解析资源 | 文件身份、buffer、primitive绑定、逐顶点属性和三角形索引 | 实际读的是预期文件，字段和数值是否正确？ |
| ImporterMesh | 导入完成后的 surface、primitive、属性和索引数组 | 是否符合预先说明的目标编号、绕序及属性转换？ |
| ArrayMesh读回 | 运行时网格接口返回的数组与格式信息 | 经过目标存储表示后，离散结构和数值精度是否仍满足要求？ |
| 最终场景与图像 | 节点、材质、渲染结果 | 视觉和完整资产交接是否正确？这需要另外验收。 |

在 Godot 中，可以用 `GLTFDocument.append_from_file` 把文件导入一个 `GLTFState`。检查返回值后，枚举实际 mesh、surface 和 primitive，而不是仅凭返回成功便宣布模型正确。对取得的 ImporterMesh，先调用 `get_surface_arrays` 保存导入层数组，再调用 `get_mesh()` 得到 ArrayMesh，并读取它的 `surface_get_arrays`。[1]

具体取数时，遍历 `state.get_meshes()`，取得每个 GLTFMesh 的 `mesh` 属性，并确认它不是空值。按各自的 surface 数量读取数组，位置、法线和索引分别位于 `Mesh.ARRAY_VERTEX`、`Mesh.ARRAY_NORMAL`、`Mesh.ARRAY_INDEX` 槽；同时记录 primitive 和数组长度。primitive 要按各自API的枚举核对，例如目标使用 `Mesh.PRIMITIVE_TRIANGLES`，不能把 glTF 的 mode=4 直接当成 Godot枚举整数。固定转换循环按 surface 顺序创建目标，比较时仍要核对数量与对应关系，不能把“第0项存在”当作整份文件通过。[2][6]

`get_mesh()` 会缓存生成的网格；反复调用同一个对象不等于多次独立导入。固定实现首次生成时，把每个 surface 的数组、混合形状、LOD和标志交给 `ArrayMesh.add_surface_from_arrays`，后者进入 RenderingServer 的打包路径。ArrayMesh读回则从 RenderingServer 重新取得数组。因此这两处检查是同一次处理的不同阶段，不是两个独立解析器互相作证。[2]

## 在读目标结果之前写出预期

一个小而有区分力的输入，比一份复杂资产更容易说明问题。先选定源文件和资源字节，记录精确身份，再从已核对的源表示写出以下要求：

- 哪些 mesh、surface 和 primitive 应该出现，哪些属性应存在或缺席。
- 每个顶点的完整属性，以及每个三角形的有序三个索引。不能只保存位置集合。
- 目标会执行哪些有依据的变换，例如每个三角形换绕序、按确定规则移除未使用顶点。
- 哪些量必须精确一致，哪些量允许近似，以及近似的度量、阈值和适用阶段。

预期不能从待验证的目标输出反向生成。例如把源索引和目标索引都排序后发现相同，已经丢失了三角形连接顺序和绕序，无法证明原问题正确。也不要从同一段导入代码生成期望值，再把相同错误重复一遍当成通过。小输入可以直接列字面值；生产工具则需要独立的解码检查和明确的转换关系。

所有比较要在同一坐标空间进行。本文比较网格局部数组，不把 node 的世界变换应用到一侧；若项目确实需要坐标系变换，应把位置、法线和绕序各自的规则先写进契约，再开展对应验证，而不是看见符号不同就临时翻转法线。

## 索引不相等时，先验证编号与绕序的关系

固定 Godot glTF 导入源码对有索引 TRIANGLES 先交换每个三角形的后两个索引，把逆时针绕序转换为目标采用的顺时针约定。它还标出用到的源顶点，按原顶点顺序建立紧凑编号，再把各顶点属性和索引一起映射。[3] 这里是两个明确操作，不是允许任意重排的理由。

用一个纸面输入说明如何算目标。源顶点0没有被使用，其余四点组成矩形：

| 源编号 | 位置 |
|---|---|
| 0 | `(3,5,3)`，未被索引引用 |
| 1 | `(1,2,3)` |
| 2 | `(5,2,3)` |
| 3 | `(1,8,3)` |
| 4 | `(5,8,3)` |

设这些点的法线均为 `(0,0,1)`，源三角形索引为 `[1,2,3, 3,2,4]`。这个含未使用顶点的例子用于推导，并没有作为新资产送进引擎运行。

1. 交换每组三个索引的后两项，得到 `[1,3,2, 3,4,2]`。
2. 按源编号顺序保留被使用顶点，建立映射 `M(1)=0、M(2)=1、M(3)=2、M(4)=3`。未使用的0不分配目标编号。
3. 对已换绕序的索引应用 M，预期目标索引为 `[0,2,1, 2,3,1]`。
4. 目标位置数组应按源1、2、3、4的顺序排列；法线也必须应用同一个映射，而不是各自重新排序。

此时正确验收不是“目标顶点数等于源顶点数”。应检查每个保留源顶点 i 都满足 `目标位置[M(i)]=源位置[i]`，其他承诺保留的逐顶点属性同理，并检查每个目标三角形与映射后的有序源三角形一致。若未来例子增加UV，位置相同并不允许把不同UV的顶点合并；关系要覆盖实际使用的完整属性。

这个例子的源第一面叉积为 `(0,0,24)`，换绕序后为 `(0,0,−24)`。提供的法线仍是 +Z；Godot 的正面约定已经发生变化，不能仅为了让数学叉积与法线同号而擅自把法线取反。[3]

如果另一套管线还会重排三角形、拆分顶点、合并完全等价顶点或生成LOD，就需要为那些步骤分别取得对应关系和保真要求。本文的 M 只解释所核对的“保留使用顶点并按源顺序紧凑编号”路径。不要让一个无序位置集合比较替代这些契约；尤其透明混合可能对提交顺序敏感，保留几何不自动等于保留最终图像。

## 目标数组读回为何可能只能近似相等

ImporterMesh保存的逻辑数组，不保证以同样的逐分量浮点形式进入运行时表示。先核对实际标志，再用对应分支解释误差：固定 glTF 导入器为每个 primitive 初始设置 `ARRAY_FLAG_COMPRESS_ATTRIBUTES`，随后在强制关闭、二维网格等条件下清除它。本文纸面例子的点虽然共面，Z却为3，不能因此当成该源码的二维条件；默认选项下没有其他清除条件时，会保留压缩标志。[3]

对同一个 surface i，分别读取 `ImporterMesh.get_surface_format(i)` 和 `ArrayMesh.surface_get_format(i)`，与 `Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES` 做按位与，记录该位是否设置。两个完整格式数还包含其他信息，不要求整个整数相等。若标志与预期不符或无法取得，应先解释配置和转换路径，暂停该项数值验收。[2][4]

未置该位时，下面的普通法线分支可以解释所选格式；置位时，必须使用压缩分支自己已预定的数值要求。缺少适用要求就记为尚未验收，不能拿旧样本的 `10⁻⁴` 容差直接放行，也不必为了通过检查而关闭压缩。导入 API 的选项与网格存储格式是不同标志集合，不要把 `Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES` 直接作为 `append_from_file` 的 flags 参数。

固定源码提供了一个具体机制：在未设置 `ARRAY_FLAG_COMPRESS_ATTRIBUTES` 的法线分支中，法线先进行八面体编码，得到两个分量；两个分量乘65535、钳制并转换成16位无符号整数保存。读回时再除以65535并做八面体解码。[4]

这已经足以说明：“没有开启该属性压缩标志”也不能推导出法线逐位保持。以 +Z 为例，八面体编码给出 `(0.5,0.5)`，而0.5乘65535是32767.5，存入该整数格式无法保留半个单位。解码会重新归一化，得到的方向可以很接近 +Z，却不必逐分量等于原来的 `(0,0,1)`。[4] 这是固定分支的数学机制，不是对所有方向给出的最大误差界。

同一未置该标志的3D位置分支仍会把分量显式转成 float，再按 float 读回，所以高精度输入也不保证逐位保留。[4] 开启压缩标志时还有另一套位置与法线/切线打包分支，不能套用上面的两个数解释全部运行时结果。因此验收记录要保存实际格式和标志，区分所走路径；源 buffer 的 stride 也不能当作 ArrayMesh 或 GPU 的物理布局。

近似要求应按属性用途制定。对本文的小输入，可以预先规定：

- 索引、primitive、surface数量和属性是否存在，按离散规则精确检查，不能使用数值容差掩盖结构错误。
- 特意选择能精确表示且该目标路径不改变的位置，在该用例中要求精确一致。这不是所有模型位置都可逐位比较的通用保证。
- 法线读回先检查分量有限、向量非零；如果契约要求单位长度，再分别检查长度误差与方向误差。不要把所有法线先改成预期方向再比较。

方向误差可用归一化后两向量点积的夹角；实现时把点积钳到[−1,1]再取反余弦，避免浮点舍入使定义域越界。分量最大绝对误差也可以作为一个具体小用例的判据，但它与角度误差不是同一个量。阈值应来自项目所需精度及选用表示的分析或专门验证，不能看完这次误差再不断增大到通过。

如果尚不能给出合理阈值，记录差异并将该项判为尚未验收，比给出一个通用的 `epsilon` 更诚实。格式发生变化时，应重核相关阈值，而不是沿用旧结果。

## 沿着第一次分歧定位问题

将上述要求落实成测试时，每次用新的导入状态保存完整阶段结果，并分别标记成功、失败或尚未验证。一个可执行的顺序是：

```text
固定输入身份和预期规则，检查源资源与源数组
导入；失败则保存错误，不继续读取不存在的结果
核对实际 mesh、surface、primitive和属性集合
读取并保存 ImporterMesh 数组
按约定的绕序/编号映射比较源层与导入层
取得 ArrayMesh；为空或转换失败则停止本阶段
保存 ArrayMesh 数组、格式和所需诊断值
比较离散结构，再按逐属性规则比较数值
任何阶段失败都保留失败与已有输出，不从局部成功推出总通过
```

这样，错误可以落到具体边界：

- 源数组已经错了：先修 accessor绑定、偏移、步长、类型或索引读取。
- 源层正确，而 ImporterMesh 的映射或属性不符：调查导入转换、所用选项或预期规则是否与该版本一致。
- ImporterMesh符合预期，而 ArrayMesh读回超出预定要求：调查目标打包、格式选择与读回路径。
- 两层数组都通过，图像仍异常：转向节点、材质、切线、剔除或渲染配置等尚未覆盖的边界，不能宣称整条资产链已经正确。

这些是缩小调查范围的规则，不是自动归责于某个引擎模块。输入或期望错误也可能在目标层才显现，所以失败报告应同时保留实际值、期望关系、格式与版本。

## AABB为何不能随手加进“必须完全相同”

边界框适合做诊断，却不一定保存为源点集的精确最小外包框。固定 RenderingServer 源码从点集计算AABB后，对尺寸施加 `SMALL_VEC3` 的最小值限制。[5] 因而一个所有顶点Z均为3的平面，不意味着目标AABB的Z尺寸必须严格为0。

既有四顶点、两三角形导入材料正遇到这个问题：首轮导入本身成功，位置和索引也符合预期，但测试额外要求AABB零厚度，导致完整验收失败。预先冻结的契约只要求记录AABB，并未批准这个严格断言。后续保留原失败，移除这项多加的断言，在不改变输入、位置/索引规则和法线容差的条件下重新运行。[6]

这里的教训不是“遇到失败就删断言”。需要先分清：它是产品实际需要的约束、目标接口承诺，还是测试作者未经依据添加的假设。如果产品确实需要零厚度框，应从源几何另外计算并保留那个量，不能将目标AABB读回冒充它。修改验收契约时保留旧失败、依据和新版本；新的通过不把旧失败变成从未发生。

## 既有观察与这套方法的边界

既有材料的源索引为 `[0,1,2,2,1,3]`，ImporterMesh和ArrayMesh均读回 `[0,2,1,2,3,1]`。两个阶段的四个位置与源字面值一致；ImporterMesh法线为 +Z，ArrayMesh约为 `(3.66×10⁻¹⁰,−3.05×10⁻⁵,1)`，满足运行前规定的每分量 `10⁻⁴` 容差。输入没有UV，因此只验证UV缺席，不能说UV导入正确。[6]

这些是固定旧输入和旧执行的有限观察，不是本文新跑的引擎结果。旧二进制的自报版本与用于比较的公开源码没有建立认证对应关系，所以不能断言其法线差异正是本文所列的某个源码分支造成，也不能用它认证当前官方构建。源码机制与历史读回应分别使用。

这套方法的交付是可追踪的比较关系与首次分歧位置：源数据是否正确、目标编号与绕序是否符合预期、运行时读回是否满足属性要求。它不会自动完成编辑器导入配置、所有glTF类型、恶意文件安全性、GPU布局、渲染质量或性能验收。把这些边界分开，才既不会把正常转换误报成坏数据，也不会用“数组大致相同”放过真正缺失的验证。

## 参考来源

1. Godot Engine，固定修订 `35e80b3a8822a9df9be390814b62f44c0a9c69e8`：[GLTFDocument.append_from_file](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/gltf/doc_classes/GLTFDocument.xml#L28-L38)、[ImporterMesh接口](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/doc/classes/ImporterMesh.xml#L90-L106)。导入状态、逻辑surface数组、运行时网格生成及缓存。
2. Godot Engine，同修订：[ImporterMesh.get_mesh](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/resources/3d/importer_mesh.cpp#L578-L625)、[ImporterMesh格式标志](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/resources/3d/importer_mesh.cpp#L149-L151)、[ArrayMesh写入与读回](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/resources/mesh.cpp#L1818-L1843)、[ArrayMesh格式读回](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/resources/mesh.cpp#L1935-L1937)。两个阶段的调用关系。
3. Godot Engine，同修订：[索引换绕序与使用顶点映射](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/gltf/gltf_document.cpp#L1482-L1530)、[索引应用映射](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/gltf/gltf_document.cpp#L1692-L1715)、[ArrayMesh正面约定](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/doc/classes/ArrayMesh.xml#L49)、[初始压缩标志](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/gltf/gltf_document.cpp#L1438-L1444)与[清除条件](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/gltf/gltf_document.cpp#L1738-L1750)。仅用于所述索引三角形路径，不批准任意优化重排。
4. Godot Engine，同修订：[位置与法线打包](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/servers/rendering/rendering_server.cpp#L597-L627)、[对应读回](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/servers/rendering/rendering_server.cpp#L1484-L1511)、[八面体编解码](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/math/vector3.cpp#L90-L113)。正文明确限定未设置属性压缩标志的示例分支。
5. Godot Engine，同修订：[AABB尺寸限制](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/servers/rendering/rendering_server.cpp#L451-L458)。目标诊断量不必等于源点集零厚度。
6. 本库原创，2026-10-31的[固定历史导入材料](https://github.com/Container-R/GameLibrary/blob/1a7bf18b24ba56395892c4c0cdb3b2acecc16985/research/experiments/godot-gltf-import-boundary/README.md)、[冻结契约](https://github.com/Container-R/GameLibrary/blob/1a7bf18b24ba56395892c4c0cdb3b2acecc16985/research/experiments/godot-gltf-import-boundary/contract.json)及[构建来源边界](../../../../管理档案/研究记录/source-notes/godot-runtime-provenance.md)。保留首轮失败与后续结果，不将本次源码阅读称为新执行。以上来源于2026-11-06重新核读。

[返回模型导入](README.md)
