---
id: SOL-ENGINE-001
title: 干净检出后的资产导入：保留导入意图，而不是依赖作者缓存
type: solution
status: source-backed
primary_discipline: ENGINE
related_disciplines: [TA, QA, PROD]
related_roles: [tools-programmer, technical-artist, build-engineer, qa-engineer]
related_topics: [asset-pipeline, import-settings, source-control, clean-checkout, resource-identity]
engines: [Godot]
versions: ["Godot 4.6 官方文档", "Godot 4.6.3.stable.official.7d41c59c4 实际导入器"]
platforms: [PC]
updated_at: 2026-10-31
verification_method: 官方来源核对；原创 SVG 的实际无头导入与资源加载对照；未验证 GPU、导出包或跨版本缓存复现
sources:
  - https://docs.godotengine.org/en/4.6/tutorials/assets_pipeline/import_process.html
  - https://docs.godotengine.org/en/4.6/tutorials/best_practices/version_control_systems.html
  - https://docs.godotengine.org/en/4.6/classes/class_resourceimportertexture.html
  - https://docs.godotengine.org/en/4.6/classes/class_resourceuid.html
  - https://docs.godotengine.org/en/4.6/classes/class_resourceformatloader.html
  - https://docs.godotengine.org/en/4.6/tutorials/editor/command_line_tutorial.html
---

# 干净检出后的资产导入：保留导入意图，而不是依赖作者缓存

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

本例隔离的是参数丢失，场景采用源路径引用，没有故意制造 UID 失效。错误案例“成功运行”是要保留的反例，而不是将测试改成只检查返回码为零。具体版本、源码/二进制哈希、导入前清单、生成的 sidecar、完整命令、日志和加载结果均归档。

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

## 来源与关联

- [S1] [Godot 4.6 Import process](https://docs.godotengine.org/en/4.6/tutorials/assets_pipeline/import_process.html)，Files generated / ResourceLoader 边界。
- [S2] [Version control systems](https://docs.godotengine.org/en/4.6/tutorials/best_practices/version_control_systems.html)，Files to exclude，明确版本适用范围。
- [S3] [ResourceImporterTexture](https://docs.godotengine.org/en/4.6/classes/class_resourceimportertexture.html#class-resourceimportertexture-property-svg-scale)，`svg/scale`。
- [S4] [ResourceUID](https://docs.godotengine.org/en/4.6/classes/class_resourceuid.html)，映射及创建 API；不将身份映射当作语义校验。
- [S5] [ResourceFormatLoader](https://docs.godotengine.org/en/4.6/classes/class_resourceformatloader.html)，`_get_resource_uid` 及 sidecar 行为。
- [S6] [Command line tutorial](https://docs.godotengine.org/en/4.6/tutorials/editor/command_line_tutorial.html)，`--import`。

以上官方 4.6 文档访问于 2026-10-31，与实际 4.6.3 二进制分别记录。正文为原创工程分析；最小 SVG/场景/代码为原创，没有复制第三方资产。关联[技术美术职责接口](../../roles/technical-art/technical-artist.md)：把资产交接从“交了文件”推进到“输入完整且关键行为可复验”。
