---
id: SOL-ENGINE-001
title: 干净检出后的资产导入：保留导入意图，而不是依赖作者缓存
type: solution
status: source-backed
primary_discipline: ENGINE
related_disciplines: [TA, QA, PROD]
related_roles: [tools-programmer, technical-artist, build-engineer, qa-engineer]
related_topics: [asset-pipeline, import-settings, source-control, clean-checkout, resource-identity, resource-ownership, threaded-loading, resource-duplication, alias-preservation]
engines: [Godot]
versions: ["Godot 4.6 官方文档", "Godot 4.6.3.stable.official.7d41c59c4 本地程序自报；发行与源码对应未确认"]
platforms: [PC]
updated_at: 2026-11-01
verification_method: 官方来源核对；原创 SVG 导入及原生资源候选依赖隔离、同路径请求登记及有限资源复制图的实际无头对照；未验证 GPU、导出包或跨版本缓存复现
sources:
  - https://docs.godotengine.org/en/4.6/classes/class_resource.html
  - https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource.cpp
  - https://docs.godotengine.org/en/4.6/classes/class_@globalscope.html#class-globalscope-method-is-same
  - https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource_loader.cpp
  - https://docs.godotengine.org/en/4.6/classes/class_resourceloader.html
  - https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/resources/resource_format_text.cpp
  - https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/object/object_id.h
  - https://docs.godotengine.org/en/4.6/tutorials/assets_pipeline/import_process.html
  - https://docs.godotengine.org/en/4.6/tutorials/best_practices/version_control_systems.html
  - https://docs.godotengine.org/en/4.6/classes/class_resourceimportertexture.html
  - https://docs.godotengine.org/en/4.6/classes/class_resourceuid.html
  - https://docs.godotengine.org/en/4.6/classes/class_resourceformatloader.html
  - https://docs.godotengine.org/en/4.6/tutorials/editor/command_line_tutorial.html
---

# 干净检出后的资产导入：保留导入意图，而不是依赖作者缓存

> **运行身份说明（2026-10-31）：** 下述 Godot 版本为已安装程序自报，不代表已认证官方发行包或精确源码身份。[共享取证与缺口](../../research/source-notes/godot-runtime-provenance.md)保留原始版本、文件摘要及公共标签查询差异；各次有限行为观察仍按实际归档字段解释。

## 工程故障：场景能打开，交付仍然错误

美术提交了源图片与场景，程序在新目录打开项目，没有丢失引用或报错，却发现纹理尺寸与作者工程不同。只比较源图片哈希、项目能否加载、甚至资源 UID，都可能漏掉这个问题：**源文件相同不等于导入配置相同，身份相同也不等于资源语义相同。**

本文给出 Godot 4.6 的资产交接契约，并用已安装 4.6.3 导入器复现一个具体反例。目标不是缓存逐字节复现、完整构建系统或 GPU 质量测试；不将 Godot 文件规则移植到其他引擎。

## 1. 三层文件的责任不同

官方 *Import process* 说明，源资产旁的 `<asset>.import` 保存导入配置与重要元数据，应纳入版本控制；内部导入产物位于 `.godot/imported/`，删除后可以重新导入，官方不建议提交整个 `.godot/`。[S1] 当前 VCS 文档的忽略建议适用于 4.1 及以后，不应套用到 3.x/4.0。[S2]

| 层次 | 本项目需要保留的事实 | 不能用什么代替 |
|---|---|---|
| 原始资产与引用 | 源文件、原生场景/资源、脚本、项目配置、实际依赖路径 | 作者机器上已有的纹理对象 |
| 导入意图与身份元数据 | 具体资产的导入参数、相应 sidecar、需要保留的 UID；有插件时还有插件/工具版本 | 一条“所有 generated 文件都忽略”的规则 |
| 可生成产物 | 指定工具链根据前两层生成的导入缓存 | 不能反过来把缓存当作唯一配置来源 |

`.import` 虽由工具生成，也含需要保存的作者决策；“生成过”不等于“可丢弃”。某些资源另有 `.uid`，原生资源又可能在自身文件中保存身份；需按格式核查，不用统一忽略 `*.uid` 的捷径。[S5] 本实验保留实际脚本 UID，没有执行其丢失/移动反例。

## 2. 原创实验：只漏一个 sidecar

[夹具与原始记录](../../research/experiments/godot-import-boundary/README.md)包含无外链、无字体的原创 16×8 SVG、引用它的 Sprite2D 场景及资源探测脚本。官方纹理导入器的 `svg/scale` 默认 1.0，较高值放大导入图像。[S3]

先由真实引擎生成合法 sidecar，再把唯一的 `svg/scale=1.0` 改为 2.0，清除该临时基线的缓存并重新导入；实际资源必须达到 32×16，才冻结完整配置输入。随后生成两个隔离目录：共同文件哈希完全一致，唯一差异是其中一个遗漏 `asset.svg.import`，两边均无 `.godot/`。

每个目录先实际执行 `godot --headless --path <directory> --import`，再启动新进程。探测同时读取 ResourceLoader 返回的纹理和实例化场景中 Sprite2D.texture 的实际类型、路径及尺寸；不是只从 sidecar 推测结果。`--import` 是编辑器导入阶段，不能用普通运行程序替代。[S6]

| 实际案例 | sidecar 参数 | 直接加载尺寸 | 场景纹理尺寸 | 场景是否加载 |
|---|---:|---:|---:|---|
| 保留完整输入，从空缓存重建 | 2.0 | 32×16 | 32×16 | 是 |
| 仅遗漏资产 sidecar，从空缓存重建 | 重新采用 1.0 | 16×8 | 16×8 | 是 |

两边资源均为 `CompressedTexture2D`。此次还观察到 **UID 相同而尺寸不同**：因此 UID 一致也不能替代导入语义检查。本结论不依赖 UID 必然变化；路径/项目名、资源格式与工具版本都会影响相关行为，不能从某次观察推导通用生成规则。[S4]

本例隔离的是参数丢失，场景采用源路径引用，没有故意制造 UID 失效。错误案例“成功运行”是要保留的反例，而不是将测试改成只检查返回码为零。具体版本、原创夹具源文件/被测可执行文件摘要、导入前清单、生成的 sidecar、完整命令、日志和加载结果均归档。

## 3. 交接和 CI 应验收语义，不只验收文件存在

以下是原创工程策略，不是官方完整 CI 实现：

1. **声明输入清单**：资产所有者提交源文件及导入意图；工具维护者列出引擎、插件与外部导入器版本；构建任务说明是否需要外部资产取回。不要在验收时悄悄借用作者缓存。
2. **隔离重建**：使用可丢弃的新目录，明确不带生成缓存；先导入再运行资源探测，记录警告与错误。这里的清理仅作用于测试副本，不要求删除用户的工作工程。
3. **选择少量关键语义判据**：纹理可验尺寸、类型与引用；动画/音频应另设各自的参数契约。本文只实测纹理维度、类型和引用，不宣称其他资产类别已验证。
4. **分开报告失败**：缺少输入、导入失败、引用失效、加载成功但语义不符，是四类不同故障。分别定位，比“删缓存再试”更能避免重复丢失作者配置。
5. **升级工具链时重验**：旧配置在新版本下可以成功导入，也可能改变默认值或产物。保留预期语义及前次证据；不要把某个缓存哈希当永久质量标准。

推荐的验收记录至少包含：源版本、受控输入清单及摘要、实际工具版本、导入命令、目标资源、预期语义、实际读数和失败类别。缓存产物可以用于诊断，但不能掩盖输入缺失。

## 4. 代价、取舍与未测试边界

保留 sidecar 增加文本审查和合并工作，却保住了非默认导入决策；发生冲突时不能只选“让编辑器能开”的一边，应确认参数意图。完整干净导入会增加 CI 时间，可按依赖选择验收资产，但要另设周期性全量干净检出以发现遗漏依赖；本文没有量化这些成本或实现依赖调度。

一个最小场景的成功加载不能证明整个项目导出正确。无头加载和尺寸查询也不等于 GPU 渲染、像素质量或显存性能。此处未执行导出包、LFS 获取、跨机器/跨 Godot 版本、DCC 插件、VRAM 压缩、多进程构建或资源移动测试；不承诺缓存逐字节一致。不同引擎的源控制规则需重新查证。

## 5. 运行时补充：候选根不同，不等于可变依赖已隔离

前面验收的是磁盘输入与导入意图；下面是**加载后的对象图所有权**，不能互相替代。若要先加载候选、修正其数据、审核后再发布，新的根对象可能仍引用活动资源的可变依赖。仅延后根引用替换，不能隔离已发生的共享数据修改。

Godot 4.6 [ResourceLoader 的 CacheMode 文档](https://docs.godotengine.org/en/4.6/classes/class_resourceloader.html)明确：普通 `CACHE_MODE_IGNORE` 不重用根与内嵌子资源，但外部依赖使用 REUSE；`CACHE_MODE_IGNORE_DEEP` 将忽略策略传播到外部依赖。[固定官方文本加载器](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/resources/resource_format_text.cpp#L1432-L1453)可见这两类模式的外部加载参数差别。这是来源分析，不是本地二进制身份认证。

[原创两进程夹具](../../research/experiments/godot-resource-candidate/README.md)使用原生 `.tres`：`GradientTexture1D` 根引用外部 `Gradient`，只观察点颜色，不采样 GPU 纹理。每个隔离进程先 REUSE 加载并持有活动根/依赖，再对同一路径发起一个 threaded 请求；在帧回调观察到 LOADED 后取候选，仅把候选 Gradient 的点 0 从红改成蓝，不把候选赋给活动根，也不修改磁盘文件。

| 实际模式 | 活动根与候选根 | 两者外部 Gradient | 改候选后活动点色 | 候选点色 |
|---|---|---|---|---|
| IGNORE | 不同活对象 | 同一活对象 | 蓝 | 蓝 |
| IGNORE_DEEP | 不同活对象 | 不同活对象 | 红 | 蓝 |

前后对象身份保持，活动根仍为原引用，单独保留的活动 Gradient 也得到相同观察；受控输入文件摘要未变。[独立复验](../../research/experiments/godot-resource-candidate/review/REVIEW.md)重新执行两个进程，以不导入作者实现的字面身份/颜色/磁盘判据核对原始记录。请求/get 字段是声明值，实际一次调用的依据是审查后的单调用点、LOADED/finished 控制流与单条 REQUEST/RESULT，而非独立递增计数器。

两种模式首次观察均已 LOADED，状态序列为 `[3]`；这既不证明同步加载，也不证明无卡顿。文档说明过早调用 `load_threaded_get` 可能阻塞，因此本例只在就绪后取结果；没有强行制造大资源或 sleep 来要求观察到 IN_PROGRESS。修改发生在加载完成后的主线程，不是并发写入竞态实验。

一个真实验证器错误被保留：最初要求 instance ID 为正，拒绝了实际非零负整数。修正为精确保留整数符号、非零以及同进程活对象的前后相等/不等，未改变图、预期颜色或 GDScript。[ObjectID 比较源码](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/object/object_id.h)包含 64-bit 表示及有符号转换，不支持正数限定。原始失败和最终完整重跑均在归档；这些 ID 不是持久资产身份，也不能经过有损 JavaScript Number 转换再做比较。

**项目建议**：先列出候选审核/预处理会修改哪些对象，再决定需要隔离根、哪些依赖或整个可变子图；只读审核未必需要深复制。这个简单原生图中的 IGNORE_DEEP 有效，不是任意插件、全局对象或资源图的通用隔离承诺。未测试取消、并发同路径请求、REPLACE、导出包、内存释放、GPU、加载性能或跨构建行为；新二进制摘要与既有身份取证一致，但官方精确来源对应仍未建立。

## 6. 第二次请求返回OK，不等于新的加载策略已经生效

上一节检查候选对象图的隔离范围；这里先问另一道门槛：**这个候选是否真的按本次调用方要求的cache_mode加载？**

新增[同路径请求夹具](../../research/experiments/godot-resource-broker/README.md)只使用原创二点Gradient。每个新进程先以REUSE加载并持有活动资源，然后发第一次threaded请求；明确观察到LOADED但**不get收取**，再对完全相同路径发第二次、相反模式的请求。随后执行status→get1→status→get2→status。没有修改资源、第三次get或人为延迟。

|实际请求顺序|两次request返回|两个get结果|与先前活动资源的关系|
|---|---|---|---|
|REUSE→IGNORE_DEEP|均为OK|同一活对象|均与活动资源相同|
|IGNORE_DEEP→REUSE|均为OK|同一活对象|均不同于活动资源|

两例在第二请求之后及第一次get之后均观察到LOADED；第二次get后为INVALID_RESOURCE，但已持有的活动资源与两个返回引用仍可读到原有点色和offset。因此**请求登记被收取完，不等于Resource引用失效**。活动对象身份、原始颜色及磁盘输入摘要保持不变；调用计数在实际request/get位置递增，原始调用轨迹另行核对。

固定官方源码的[用户token复用与提前返回](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource_loader.cpp#L516-L625)表明：已有同路径用户token时递增计数并返回，未进入保存新cache_mode的任务创建分支；[get后的计数处理](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource_loader.cpp#L791-L801)在计数归零时移除登记。这里支持“未收取请求复用首个策略”的解释，不把公开API说成承诺了每次请求都独立。

作者两个进程与[独立重复及原始记录审查](../../research/experiments/godot-resource-broker/review/REVIEW.md)各自通过两种模式顺序。首请求在发第二请求前已完成，因此这不是worker竞争测试；没有必须观察IN_PROGRESS、性能或线程安全结论。实际程序自报4.6.3，SHA256为`f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`；与上述固定官方源码的精确对应仍未认证，见[共享身份说明](../../research/source-notes/godot-runtime-provenance.md)。对象ID只按单进程活引用精确比较，不作为持久化身份。

**原创工程建议，尚未实现broker：** 同路径调用方的共享/隔离要求冲突时，可以明确拒绝、排队至先前请求收取完，或由单一broker拥有请求并分发事先约定的共享结果。只将应用字典key改成`(path, mode)`不够：若仍把两种策略提交到同一个按路径复用的底层入口，两个应用key不会自动变成两个独立结果。本文没有验证这些解决方案，也不覆盖路径别名、不同type_hint、取消、失败重试或任意资源图。

## 7. 已加载的图再复制：隔离原对象，不代表拆散副本内部的别名

前两节讨论加载策略与请求登记，本节问另一件事：设计工具拿到一个已加载配置，复制后改内部值时，哪些使用者仍会看见变化？重新加载和复制当前内存图不是同一个操作；根对象不同、Array不同、子Resource不同，也不是同一项判据。

Godot4.6 [Resource.duplicate](https://docs.godotengine.org/en/4.6/classes/class_resource.html#class-resource-method-duplicate)说明浅复制共享嵌套容器和资源；默认深复制递归复制容器，但Resource限于内部范围。`duplicate_deep(ALL)`扩大子资源范围，仍不能脱离属性规则和脚本处理就宣称“所有可达对象都独立”。内部路径分类也不等于 `resource_local_to_scene`；后者涉及场景实例化，本例不创建场景。

[固定比较源码](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource.cpp)的 `_duplicate_recursive`、`_duplicate` 和公开duplicate入口展示范围选择、STORAGE属性复制以及资源重映射表。重映射的意义是：原图两个位置都指向B，深复制后可以正确地都指向同一个B'，而不是生成两个互不相干的子对象。这里的内部别名保留是意图，不是隔离失败；脚本依赖也应与可变配置载荷分开。

### 一张图同时区分三种分享关系

原创输入只含脚本Resource根A，其导出、非typed Array为 `[B,B,C]`：B是内嵌Gradient，C是外部Gradient。初始B红/白，C绿/白，两者offsets均为0/1。三个模式分别在新进程中复制为D，然后按冻结顺序：给D的Array追加137；把D中B的首点改蓝；把D中C的首点改品红。每步同时记录原图、别名、持有的外部引用与缓存根，不将活Resource引用误当历史值快照。

作者实际运行的三个新行为进程得到下表。各进程先确认原图、缓存和 STORAGE 属性前提，再记录四个阶段；这不是只比较根对象是否不同。

| 复制调用 | D 与 A 共用 Array | D 的 B 仍是原 B | D 的 C 仍是原 C | 修改结束后 A 的长度 / B 首色 / C 首色 |
|---|---|---|---|---|
| `duplicate(false)` | 是 | 是 | 是 | 4 / 蓝 / 品红 |
| `duplicate(true)` | 否 | 否 | 是 | 3 / 红 / 品红 |
| `duplicate_deep(Resource.DEEP_DUPLICATE_ALL)` | 否 | 否 | 否 | 3 / 红 / 绿 |

三种模式的 D 根均不同于 A；D 最终长度均为 4，D 中 B 首色为蓝、C 首色为品红，两个 B 位置始终共享同一个对象。脚本依赖保持共享，原缓存根没有被副本替换。所有白色端点、offsets 和点数保持冻结值。

独立复跑使用同一冻结输入、协议和安装程序，在新目录执行相同三种模式；另写、提前冻结的字面检查器分别验收作者和复跑原始档案。合计是 **6 个行为进程 + 2 个版本进程**，即三种模式各运行两次，不是六种独立测试场景。每个行为进程的四个阶段不是额外进程。两次运行均成功退出、stderr 为空，输入与程序摘要前后一致。当前最终纯 Python 回归套件有 6 个方法，作者和独立审查各以普通 / `-O` 模式运行一次；这些合成取证测试不是引擎行为试验。

[完整实验归档](../../research/experiments/godot-resource-duplication/README.md)保留冻结协议、原创输入、程序摘要、原始输出、进程记录和独立字面预期。运行前审查发现证据消费者曾用 Python 的宽松 `==` 比较 JSON，可能把数字 0 与 `false` 混同；已在任何本例引擎执行前改为逐层精确类型比较，并保存初始反例和修正后拒绝结果。这是取证代码缺陷，不是 Godot 行为失败。

既要看ID关系，也要看实际值。根ID不同不能证明子对象隔离；两个位置颜色一样也不能证明它们是同一个对象。副本内部两个B引用应始终指向同一个对象；这与副本B是否仍指向原B是两个问题。ID只在同一进程、活引用同时持有时比较，不是持久化资产身份。

### 选择复制策略前，先写清哪些共享是有意的

- 要独立编辑数组结构，不等于要复制每个资源元素；分别验收容器和元素。
- 要保留副本内部的关系，不应把每一次引用都无条件复制成新对象；否则同一个设计参数可能被拆成两份。
- 外部资源是否继续共享，应成为明确的配置政策。ALL扩大复制范围，不是未经评估的默认修复；本实验没有测内存或性能代价。
- 修改当前STORAGE属性的副本，不等于重新从磁盘读取原始版本，也不保证复制所有瞬态状态。

本例不覆盖自定义setter、特殊属性flags、必需构造参数、循环容器、C#回收、信号、线程、缓存驱逐、持久化保存、场景本地化或GPU。不能借用前面的候选加载/请求登记实验补出这些结论；本机二进制与公开源码仍没有认证对应关系。


## 来源与关联

- [S1] [Godot 4.6 Import process](https://docs.godotengine.org/en/4.6/tutorials/assets_pipeline/import_process.html)，Files generated / ResourceLoader 边界。
- [S2] [Version control systems](https://docs.godotengine.org/en/4.6/tutorials/best_practices/version_control_systems.html)，Files to exclude，明确版本适用范围。
- [S3] [ResourceImporterTexture](https://docs.godotengine.org/en/4.6/classes/class_resourceimportertexture.html#class-resourceimportertexture-property-svg-scale)，`svg/scale`。
- [S4] [ResourceUID](https://docs.godotengine.org/en/4.6/classes/class_resourceuid.html)，映射及创建 API；不将身份映射当作语义校验。
- [S5] [ResourceFormatLoader](https://docs.godotengine.org/en/4.6/classes/class_resourceformatloader.html)，`_get_resource_uid` 及 sidecar 行为。
- [S6] [Command line tutorial](https://docs.godotengine.org/en/4.6/tutorials/editor/command_line_tutorial.html)，`--import`。

以上官方 4.6 文档访问于 2026-10-31，与实际 4.6.3 二进制分别记录。正文为原创工程分析；最小 SVG/场景/代码为原创，没有复制第三方资产。关联[技术美术职责接口](../../roles/technical-art/technical-artist.md)：把资产交接从“交了文件”推进到“输入完整且关键行为可复验”。
