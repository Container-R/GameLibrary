---
id: SOL-ENGINE-002
title: Addressables 内容更新：先证明用了哪个已发布基线，再验证旧版客户端
type: solution
status: source-backed
primary_discipline: ENGINE
related_disciplines: [QA, PROD, TA, PLATFORM, LIVE]
related_roles: [build-engineer, tools-programmer, qa-engineer, technical-artist]
related_topics: [addressables, content-update, build-baseline, release-compatibility, asset-pipeline, catalog-operation-ownership]
engines: [Unity]
versions: ["Addressables 1.21.21 官方文档；未执行 Unity"]
platforms: [跨平台，具体发布平台须分别验证]
updated_at: 2026-11-01
review_after: 2027-01-31
verification_method: 八篇 Unity 官方版本化文档在所列章节核对；原创基线选择、依赖交接、catalog 操作所有权与旧版客户端验收协议，未执行 Unity 构建、内容托管或客户端加载测试
sources:
  - https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-builds-overview.html
  - https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-build-settings.html
  - https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-build-create.html
  - https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-examples.html
  - https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-builds-check.html
  - https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/ContentPackingAndLoadingSchema.html
  - https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/LoadContentCatalogAsync.html
  - https://docs.unity3d.com/Packages/com.unity.addressables@1.21/api/UnityEngine.AddressableAssets.Addressables.LoadContentCatalogAsync.html
---

# Addressables 内容更新：先证明用了哪个已发布基线，再验证旧版客户端

## 决策：构建成功不等于更新了正确的发行线

给已发布 Player（客户端构建）P 做内容更新，不能只交付“构建成功”和一个 catalog。应回答两个不同问题：**本次实际读取的 previous state 属于 P 的哪个平台发行基线？P 是否能通过这个候选 catalog 加载预期的新旧内容？** 第一问是构建输入身份，第二问是运行兼容性；任一未知都不应改写为通过。

本文是文档支持的工程协议，不是 Unity 实验报告。下述假设场景、验收门禁和记录字段均为原创建议；没有 Unity 构建、客户端运行、服务部署或下载量数据。初始阅读日期为 2026-10-31；2026-11-01 补读依赖示例与 Bundle Mode，并加入 §3.1；随后补读 catalog 加载操作所有权，加入 §4.1。版本页面标识 Addressables 1.21.21。

## 1. 一个容易遗漏的具体输入边界

官方要求按每次已发布完整应用、每个平台保存 `addressables_content_state.bin`；同一发行线的后续内容更新仍使用原始发行基线。默认构建会更新这个文件，不能把工作目录里“最新的文件”自动当作该发行线的归档。[S1](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-builds-overview.html#content-update-build-workflow)

更关键的是，设置页明确描述：**配置的远程 previous-state 文件不存在，但本地缓存已有文件时，系统会读取本地文件。** 默认缓存位置为 `Library/com.unity.addressables/AddressablesBinFileDownload/`。这里只能据此讨论该条件，不能扩大成超时、鉴权失败或所有 HTTP 错误都会回退。[S2](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-build-settings.html#update-a-previous-build-setting)

由此得到一个工程反例，而非已执行故障复现：作业界面指向发行线 P 的 URL，工作机却留有发行线 Q 的 state，且 P 的远程文件不存在。**配置意图不足以证明实际输入身份。** 我们不预设错误基线一定构建成功、一定报错或一定生成某种错误 bundle；需要拒绝的是“未核实输入仍宣称 P 更新已通过”。

注意两个缓存不能混为一谈：这里的 previous-state 缓存参与**制作更新**；客户端的 bundle 缓存参与**运行时取资源**。清空客户端缓存不能修复构建作业选错的基线。

## 2. 原创交接协议：把选择结果变成可核对的证据

以下是建议门禁，尚未执行，也不是 Addressables 自带的发行签名或摘要验证功能。

| 阶段与责任 | 必须交接的具体记录 | 停止晋级的条件 |
|---|---|---|
| 发行基线登记：构建负责人 | 原始 player 制品身份、平台、源提交、Unity/包/构建脚本版本；该次发布对应 state 的归档位置与摘要；原始 catalog 与内容清单 | 只能找到最新工作副本，无法关联已发布制品 |
| 输入选择：更新作业负责人 | 预期基线摘要、配置来源、实际选择来源与所读文件摘要；是否存在可被选择的本地缓存；用于确认读取对象的工具证据 | 只有 URL 或配置截图；实际选择无法确认，或摘要与发行登记不符 |
| 分组审核：内容与构建负责人 | 检查前后分组差异、变更资产及预期消费者、restriction 配置；本次检查使用的同一基线身份 | 为“让构建通过”临时改 restriction，却仍称原发行线增量更新 |
| 候选输出封存：构建负责人 | catalog/hash/bundle 文件清单与摘要、目标内容位置；变更样本与未变样本分别解析到哪个 bundle | 只记录输出目录名；未变内容的引用目标失踪或无法确认 |
| 旧版客户端验收：QA 与功能负责人 | 实际旧版 Player 身份、所用候选、运行时缓存前提、请求与加载结果、功能语义结果 | 只测新 Editor 工程；加载句柄成功但内容不符，或没有测未变样本 |

“实际选择来源”不能靠推测填写。显式选择与受控暂存还需配合在实际获准工具链中验证过的读取观测点；本文未验证可直接使用的 API 或日志字段。若当前工具链没有足够观测能力，应先实现受审查的构建输入交接或追踪，再声称输入已验证。只在构建结束后对一个可能已被覆盖的缓存文件取摘要，也不能独自证明此前读入的是这些字节。保存摘要是关联证据，不是发行授权或供应链认证。

建议让作业使用独立工作目录并从受控归档取得指定基线，降低跨发行线残留的机会；仍须核对实际输入，不能把“干净机器”当成文件正确性的替代品。不要为清理缓存而覆盖或删除唯一的原始发行归档。

## 3. 静态分组不是“资产永远不能改变”

同为 1.21.21，设置页使用 **Prevent Updates**，示例页仍写 **Cannot Change Post Release**。保留这个文档措辞差异；本文不声称检查过某个已安装 Inspector 的确切标签。官方假想示例说明，已安装本地旧数据可继续占据空间，而引用转到新的远程内容，并不是原地改写已安装 bundle。[S4](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-examples.html)

设置页要求仅在完整构建时改变组的 Update Restriction。内容更新前的限制检查可以重新组织变更资产；创建页因此建议先分支，并说明 catalog 将变更与未变内容分别指向新旧 bundle。输出文件存在不代表所有输出都应成为发布引用；依赖哈希检测也有不等同于实际 bundle 变化的局限。[S2](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-build-settings.html#group-update-restriction-settings) [S3](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-build-create.html#check-for-content-update-restrictions-tool)

原创建议：给内容作者一张“变更资产 → 使用它的场景/功能 → 预期新语义”的小清单，再由构建负责人核对真实输出引用。分组规则负责打包组织，功能负责人负责语义验收；不要让“静态”一词替代任何一项责任。

### 3.1 未编辑资产，也可能进入更新范围：先追依赖，再看打包结果

“内容作者只改了一个文件”不能直接推出“发布只需替换一个 bundle”。官方 *Content update dependencies* 的假想示例说明，依赖变化也会使未直接编辑的消费者进入更新组，影响可沿资产引用链传播。这里补充的是文档机制，不是本库构建结果或通用依赖检测算法。[S4：依赖示例](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-examples.html#content-update-dependencies)

考虑一个**原创、未执行的交接场景**：两种装备各自通过材质引用同一纹理，第三种装备使用另一组材质与纹理。内容作者只改共享纹理。此时，两种装备的源文件可以都没有编辑，但“没有编辑”不等于“更新依赖未变”；也不能反过来直接宣布这两个装备必然分别产生两个新 bundle。实际分组、依赖表示与检查结果仍待核对。

| 接收层 | 针对此次共享纹理变更要回答什么 | 在实际结果出现前保留什么未知 |
|---|---|---|
| 编辑对象与引用关系 | 哪个纹理变了；哪些材质直接引用它，哪些装备经这些材质间接引用；第三种装备是否确实没有相关依赖 | 未核对的引用边不能因“文件没改”而删除，也不能凭相似外观补出 |
| 限制检查后的资产组织 | 在既定发行基线和组 restriction 下，工具实际移动了哪些资产；哪些仍留在原组 | 预先关注的消费者不是已观测的迁组清单 |
| 构建后的打包与引用 | 保留各组实际 Bundle Mode；受影响资产被放进哪些 bundle，是否与其他内容同包；候选 catalog 实际指向哪些新旧输出 | 资产数量不能直接换算为 bundle 数量、文件字节数或下载量 |
| 客户端接收 | 使用哪个旧版客户端与缓存前提，加载哪种装备验证共享纹理的新语义；用第三种装备核对预期不变内容 | 构建输出变化不替代客户端语义结果，也不证明每个用户都下载相同文件 |

其中，组并不天然对应一个输出文件：官方 `Bundle Mode` 决定组内资产如何打包，因此应记录实际模式，再核对构建输出，而不是用组数代替 bundle 数。[Content Packing & Loading：Advanced Options / Bundle Mode](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/ContentPackingAndLoadingSchema.html#advanced-options)

这张表是接收建议，不是独立发明或复现 Unity 的依赖算法。它补充前文的基线门禁：**即使用对了原始基线，更新范围仍需从依赖关系与实际打包结果核对，不能只从编辑清单推算。**

还应把两种影响分开：限制检查决定资产组织；`Unique Bundle IDs` 则服务于内存中新旧 bundle 共存时的身份冲突问题。设置页明确指出，启用该选项时，包含引用变更资产的 bundle 也需要重建。它可以扩大更新成本，但不能据此把每次迁组都解释为该选项造成，或不经构建就填入具体成本数字。[S2：Unique Bundle IDs](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-build-settings.html#unique-bundle-ids-setting)

## 4. 旧版客户端验证：最小有区分力的候选测试

先限定发行线和平台，再选一个可明确识别版本的变更资产 A，以及同一交付范围中预期不变的资产 B。预先写下 A 的新语义和 B 的原语义，不能加载后再把观察到的值填成预期。以下四步是**待实施协议**，不是测试结果：

1. **正确基线对照。** 用归档 P/T 基线制作候选，保留输入选择、分组差异、输出与引用记录。运行实际已发布的客户端构建 P，而不是重建一个近似 P。
2. **缓存前提对照。** 在隔离测试数据中分别测试未缓存相关远程 bundle 和已有旧 bundle 的客户端状态；记录两者，不把其中一种成功推广到另一种。加载 A、B 并核对业务语义与错误，不仅检查下载完成。
3. **基线误选负例。** 在隔离构建环境放入已知不同的 Q 基线，设置受控的 P 远程 state 缺失条件。先检验自建身份门禁能否阻止晋级；若获准进一步观察包行为，完整记录实际读取来源和构建结果，不预设其一定成功或失败。此负例不得指向生产服务。
4. **第二次更新。** 沿 P 的原始基线制作另一候选，确认交接流程不会因一次更新输出而丢掉原始发行归档。明确哪些旧 catalog/客户端状态在本次支持范围内；范围外标为未测，而不是自动兼容。

运行时检查更新、更新 catalog、处理已加载资源是不同动作。官方运行时页将旧资产释放责任交给调用方，不能据 catalog 更新成功宣称现有对象已经自动换成新资产。[S5](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-builds-check.html)

本协议优先验证受控启动后的加载。若产品要求会话中更新，另立持有旧对象、释放、重载与功能状态交接用例；不能直接继承启动用例结论。`Unique Bundle IDs` 的内存中 bundle ID 冲突用途也不是客户端兼容性证明，并有构建和更新成本。[S2](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-build-settings.html#unique-bundle-ids-setting)

### 4.1 手动加载附加 catalog：先交代加载操作的所有权

前文“释放旧资产”仍然必要，但它不是唯一的释放对象。Addressables 1.21.21 文档另有一个前置条件：指向同一 catalog 的先前 `LoadContentCatalogAsync` 操作若未释放，后续加载可能复用**操作缓存**，不下载新的远端 catalog；手动加载 catalog 后，更新前也须释放该加载操作句柄。释放操作并不等于卸载已加载的 catalog。[Manage catalogs at runtime：Load additional catalogs / Update catalogs](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/LoadContentCatalogAsync.html)

**原创未执行情景：**应用已加载附加 catalog C，并保留加载操作；远端另有新 catalog/hash。再次调用同 catalog 的加载入口，即使成功，也不能单凭这个结果声称取到了新远端版本。这里应先修正操作所有权，而不是先清 bundle 缓存：

- **不需持续持有加载操作：**显式选择 `autoReleaseHandle=true`，由系统在完成时释放。之后不再读取该句柄结果，也不再手动重复释放。
- **需要手动持有：**显式选择 `autoReleaseHandle=false`，给该操作一个确定的所有者；在完成且不再需要操作后由它释放，并在后续重载／更新前满足上述前置条件。所需结果处理应安排在释放之前，不能把无效句柄留给后续任务查询。

这些是同一拥有引用的两种互斥管理选择，不是完整异步管理器实现。若还有其他持有者，只释放自己的一份引用，不足以宣称所有先前加载操作都已释放。[API 的 bool 参数](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/api/UnityEngine.AddressableAssets.Addressables.LoadContentCatalogAsync.html)明确了自动释放时点；不能把无 bool 重载的行为靠猜测填写。

应分开记录四类对象：**加载操作缓存、按 hash 判断更新的 catalog 缓存、已加载资产、客户端 bundle 缓存**。它们也都不同于 §1 制作更新时的 previous-state 缓存。释放加载操作只是移除操作复用这道阻碍；hash 未变化时仍可使用已有 catalog，因此释放不保证发生下载，更不保证 CDN 最新性或现有资产自动替换。

若将这一情景纳入旧版客户端验收，应分别保留“旧加载操作仍持有”与“已按所有权释放”的条件，并核对实际解析内容和预先定义的新旧语义；不能把第二次调用成功当成版本证据。这里没有请求日志、Unity 运行结果或下载量，也未设计取消、并发重载与发布原子性协议。

## 5. 何时不走这条增量路径

原发行客户端须已启用远程 catalog。官方区分仅内容更新与代码更新：代码变更需要新 player，通常也需新内容；复用旧 bundle 需分析 type tree 兼容性。Unity 或 Addressables 升级要求新 player 与新内容构建。具有自身补丁机制或不支持远程内容分发的平台，官方建议完整内容构建。[S1](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-builds-overview.html#when-to-perform-a-full-rebuild)

这些限制不提供一个通用兼容性算法。原创建议是把“发行线继续内容更新”和“新版客户端发行”作为不同变更审批入口，避免为了省一次构建，把代码或工具链变化悄悄塞进内容更新任务。

## 6. 成本、未证范围与相邻知识

维护每个平台的历史制品、基线和可回放测试环境需要存储与构建资源；旧版客户端和缓存状态组合会增加 QA 成本。可以按实际支持的发行线缩小范围，但必须显式记录范围，不能用“最新版能运行”替代旧版客户端承诺。

本文没有执行 Unity、CDN 部署或客户端加载；未证明所有网络失败路径、发布原子性、回滚安全、目录签名、运行时内存上限或下载性能。第三方服务的上线顺序和并发读者一致性还需要独立协议与实际验证。文档中的 catalog/hash 输出关系不是 CDN 原子提交保证。

- [构建工程师](../../roles/engine/build-engineer.md)：把包内程序与外部内容组合交付；本文补充基线身份这一个具体门禁。
- [干净检出后的资产导入](asset-import-intent-contract.md)：同样重视输入意图，但其 Godot 导入与资源候选实验**不能充当本文 Unity 流程的运行证据**。
- [来源核对记录](../../research/source-notes/addressables-content-update-baseline.md)：官方文档的版本、章节、分日补读记录和证据边界。
