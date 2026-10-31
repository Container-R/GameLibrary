---
id: SOL-ENGINE-002
title: Addressables 内容更新：先证明用了哪个已发布基线，再验证旧版客户端
type: solution
status: source-backed
primary_discipline: ENGINE
related_disciplines: [QA, PROD, TA, PLATFORM, LIVE]
related_roles: [build-engineer, tools-programmer, qa-engineer, technical-artist]
related_topics: [addressables, content-update, build-baseline, release-compatibility, asset-pipeline]
engines: [Unity]
versions: ["Addressables 1.21.21 官方文档；未执行 Unity"]
platforms: [跨平台，具体发布平台须分别验证]
updated_at: 2026-10-31
review_after: 2027-01-31
verification_method: 五篇 Unity 官方版本化文档逐节核对；原创基线选择与旧版客户端验收协议，未执行 Unity 构建、内容托管或客户端加载测试
sources:
  - https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-builds-overview.html
  - https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-build-settings.html
  - https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-build-create.html
  - https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-examples.html
  - https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-builds-check.html
---

# Addressables 内容更新：先证明用了哪个已发布基线，再验证旧版客户端

## 决策：构建成功不等于更新了正确的发行线

给已发布 Player（客户端构建）P 做内容更新，不能只交付“构建成功”和一个 catalog。应回答两个不同问题：**本次实际读取的 previous state 属于 P 的哪个平台发行基线？P 是否能通过这个候选 catalog 加载预期的新旧内容？** 第一问是构建输入身份，第二问是运行兼容性；任一未知都不应改写为通过。

本文是文档支持的工程协议，不是 Unity 实验报告。下述假设场景、验收门禁和记录字段均为原创建议；没有 Unity 构建、客户端运行、服务部署或下载量数据。阅读日期为 2026-10-31，版本页面标识 Addressables 1.21.21。

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

## 4. 旧版客户端验证：最小有区分力的候选测试

先限定发行线和平台，再选一个可明确识别版本的变更资产 A，以及同一交付范围中预期不变的资产 B。预先写下 A 的新语义和 B 的原语义，不能加载后再把观察到的值填成预期。以下四步是**待实施协议**，不是测试结果：

1. **正确基线对照。** 用归档 P/T 基线制作候选，保留输入选择、分组差异、输出与引用记录。运行实际已发布的客户端构建 P，而不是重建一个近似 P。
2. **缓存前提对照。** 在隔离测试数据中分别测试未缓存相关远程 bundle 和已有旧 bundle 的客户端状态；记录两者，不把其中一种成功推广到另一种。加载 A、B 并核对业务语义与错误，不仅检查下载完成。
3. **基线误选负例。** 在隔离构建环境放入已知不同的 Q 基线，设置受控的 P 远程 state 缺失条件。先检验自建身份门禁能否阻止晋级；若获准进一步观察包行为，完整记录实际读取来源和构建结果，不预设其一定成功或失败。此负例不得指向生产服务。
4. **第二次更新。** 沿 P 的原始基线制作另一候选，确认交接流程不会因一次更新输出而丢掉原始发行归档。明确哪些旧 catalog/客户端状态在本次支持范围内；范围外标为未测，而不是自动兼容。

运行时检查更新、更新 catalog、处理已加载资源是不同动作。官方运行时页将旧资产释放责任交给调用方，不能据 catalog 更新成功宣称现有对象已经自动换成新资产。[S5](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-builds-check.html)

本协议优先验证受控启动后的加载。若产品要求会话中更新，另立持有旧对象、释放、重载与功能状态交接用例；不能直接继承启动用例结论。`Unique Bundle IDs` 的内存中 bundle ID 冲突用途也不是客户端兼容性证明，并有构建和更新成本。[S2](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-build-settings.html#unique-bundle-ids-setting)

## 5. 何时不走这条增量路径

原发行客户端须已启用远程 catalog。官方区分仅内容更新与代码更新：代码变更需要新 player，通常也需新内容；复用旧 bundle 需分析 type tree 兼容性。Unity 或 Addressables 升级要求新 player 与新内容构建。具有自身补丁机制或不支持远程内容分发的平台，官方建议完整内容构建。[S1](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-builds-overview.html#when-to-perform-a-full-rebuild)

这些限制不提供一个通用兼容性算法。原创建议是把“发行线继续内容更新”和“新版客户端发行”作为不同变更审批入口，避免为了省一次构建，把代码或工具链变化悄悄塞进内容更新任务。

## 6. 成本、未证范围与相邻知识

维护每个平台的历史制品、基线和可回放测试环境需要存储与构建资源；旧版客户端和缓存状态组合会增加 QA 成本。可以按实际支持的发行线缩小范围，但必须显式记录范围，不能用“最新版能运行”替代旧版客户端承诺。

本文没有执行 Unity、CDN 部署或客户端加载；未证明所有网络失败路径、发布原子性、回滚安全、目录签名、运行时内存上限或下载性能。第三方服务的上线顺序和并发读者一致性还需要独立协议与实际验证。文档中的 catalog/hash 输出关系不是 CDN 原子提交保证。

- [构建工程师](../../roles/engine/build-engineer.md)：把包内程序与外部内容组合交付；本文补充基线身份这一个具体门禁。
- [干净检出后的资产导入](asset-import-intent-contract.md)：同样重视输入意图，但其 Godot 导入与资源候选实验**不能充当本文 Unity 流程的运行证据**。
- [来源核对记录](../../research/source-notes/addressables-content-update-baseline.md)：五篇官方文档的版本、章节和证据边界。
