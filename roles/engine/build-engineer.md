---
id: ROLE-ENGINE-001
title: 构建工程：把源与配置变成可验收、可交接的候选产物
type: role
status: source-backed
primary_discipline: ENGINE
related_disciplines: [PLATFORM, LIVE, QA]
related_roles: [build-engineer, engine-programmer, tools-programmer, qa-engineer]
related_topics: [build-pipeline, candidate-identity, generated-inputs, test-evidence-binding, release-handoff]
engines: [engine-agnostic]
platforms: [cross-platform-responsibility-not-validation]
versions: ["三个雇主岗位原文读取于2026-10-31；首次发布日期未知", "Cyllista开发环境案例发表于2020-10-08；未确认引擎技术版本"]
updated_at: 2026-10-31
review_after: 2027-01-31
verification_method: 日本与美国三个雇主职责原文及Cygames2020技术博客问答、SLSA1.2限定章节核对；交付矩阵和候选产物工作表为原创建议，未运行构建流水线、发布服务或组织验收
sources:
  - https://hrmos.co/pages/cygames/jobs/1793262169510682626
  - https://hrmos.co/pages/bandainamcostudios/jobs/050_0050_sa010_0500_0082
  - https://www.riotgames.com/en/work-with-us/job/8049807/principal-software-engineer-developer-connections-los-angeles-usa
  - https://tech.cygames.co.jp/archives/3442/
  - https://slsa.dev/spec/v1.2/build-provenance
  - https://slsa.dev/spec/v1.2/verifying-artifacts
---

# 构建工程：把源与配置变成可验收、可交接的候选产物

## 定位与责任边界

构建工程要解决的不只是“编译命令能否执行”，还包括开发者如何获得可定位的产物、失败如何被诊断、测试结果究竟属于哪一个候选包，以及重新构建后谁决定原有验收是否仍适用。本文聚焦**从输入与流水线到候选产物交接**，不把构建成功等同于游戏质量合格或获准上线。

公开岗位存在交集，不代表职称同义、固定汇报线或统一放行权限。`build-engineer`、`qa-engineer`、工具程序与发布管理不可自动合并；关联标签仅用于查找资料。

| 原始职责样本 | 本文采用的有限范围 | 不据此推出 |
|---|---|---|
| Cygames，游戏引擎 Build Engineer [B1] | Cyllista及使用它的游戏团队：CI/CD、自动测试与二进制分发、开发支持和仓库维护 | 所有构建工程都使用同一工具，或该岗位有产品上线最终决定权 |
| Bandai Namco Studios，SOL-AVES CI/CD Engineer [B2] | 共享引擎的构建、测试、包分发与流程数据分析；对接引擎开发者 | 共享引擎包分发等于各游戏商店发布，或公开了主机认证细则 |
| Riot，DevCon Game Release Principal Software Engineer，REQ-0010111 [B3] | 高级中央发布架构，跨客户端、服务器、服务、内容、配置与游戏团队协调 | 每位构建工程师都承担这种资历、全公司决策或事故响应权限 |

三者说明“共享开发基础设施”与“面向产品的发布协作”可以相连，但不能合成一个人人包办的标准岗位。小团队可能由程序兼任；这是组织设计选项，不是这三份大团队样本已经验证的普遍分工。分类主归属采用现有 `ENGINE` 的“构建与部署工程”，平台交付、在线配置和测试证据分别关联 `PLATFORM`、`LIVE`、`QA`。

## 原创交付矩阵：交付可解释的候选，而不只是绿色状态

下表是依据职责边界提出的工程交接建议，**不是三个雇主的内部流程，也未在项目中试用**。

| 工作阶段与输入 | 构建工程应提供的可观察产物 | 接收者与最小验收问题 |
|---|---|---|
| 明确构建目标：代码/资产范围、目标配置、平台约束 | 输入清单及选择规则，注明依赖、工具链、生成内容和未固定项 | 引擎/游戏团队：能否解释“这次到底构建了什么”，而非只给分支名？ |
| 执行与故障定位：流水线定义及执行环境 | 唯一调用记录、各阶段终态、日志与输出关联；区分编译失败、环境失败、未执行和取消 | 开发者/基础设施维护者：失败定位到可处理的责任接口；失败不能借用上次成功包 |
| 产生与分发候选：实际可交付文件 | 候选标识、包内容摘要/清单、配置与输入来源；说明可变外部内容是否在包外 | QA/开发者：下载后能否确认取得的是指定候选和配置？摘要不是执行真实性或安全认证 |
| 绑定测试证据：测试计划和实际运行对象 | 指向候选、环境与配置的测试结果集合，保留未测/受阻范围 | QA：结果属于哪个对象？仅同源代码版本不足以证明同一包或同一运行配置 |
| 重建或变更：候选A之后的新输出B | A/B差异及证据继承请求；记录缺失比较，不能静默转移批准 | QA与变更责任人：按已声明的等价性依据决定保留哪些结论、重测哪些部分 |
| 晋级与后续追踪：已审阅候选、目的地与授权 | 候选→分发目标/环境的记录、实际执行结果和未完成步骤 | 发布/平台/运维负责人：批准对象与部署对象是否一致？流水线成功不自行赋予晋级/发布权限 |

“可重复构建”也应说明层级：可重复调用、相同逻辑内容与逐字节相同包并非同一承诺。本文没有运行确定性构建实验。若签名、时间戳或包装导致字节变化，应由项目明确比较对象和允许变化，不能只因摘要不同就断言游戏逻辑已改变，也不能以“只是包装”直接沿用所有测试结论。

作为技术参照，SLSA **v1.2** 将产物 `subject`、构建定义 `buildDefinition` 与执行信息 `runDetails` 区分，`invocationId` 指向一次调用；其依赖清单完整性直到Build L3仍属尽力记录。验证还需要产物摘要匹配、签名及预配置的签名者/构建者信任与预期检查，不能用一串SHA替代。[B5][B6] **这不是三个雇主已采用SLSA的证据，也不证明游戏QA通过或获准晋级；本文未实现签名或声称符合SLSA等级。**

## 有限接收工作表：A通过后，B能否继承？

**完全是假设且未执行的例子：** QA针对候选A完成约定检查。源代码修订未变，但后续构建使用了不同配置、工具链或生成输入，得到候选B。问题不是预设B有缺陷，而是A的证据是否足以支持B。

| 待核对条件 | 必须留下的证据 | 本文建议的接收决策 |
|---|---|---|
| B只声称“同一提交”，没有包及输入对应关系 | 列出未知的产物、配置和依赖身份 | 不自动继承A的验收；先补足对象识别 |
| B与A包摘要相同，但包外配置不同 | 测试时与目标环境的外部配置、服务/内容依赖范围 | 只对确实相同且被原测试覆盖的部分讨论继承，不能宣布整次运行等价 |
| 工具链或生成资产发生变化 | 变化来源、受影响输出、原检查覆盖范围 | 由相应工程与QA责任人选择比较/重测范围，并显式保留未知项 |
| B的流水线成功，但测试阶段跳过或受阻 | 各阶段状态与原因，不把跳过折算通过 | 标记证据不足；是否接受风险由约定权限决定，不由绿色总状态代替 |
| A获准进入内部测试环境，B拟推向另一目的地 | 原批准对象、目的地、有效条件及新请求 | 不将内部测试授权自动升级为公开发布授权 |

这些字段和决策是原创最小工作表，不是签名格式、供应链安全方案、平台认证规范或自动发布实现。亦未规定任何公司必须重新运行全部测试；要求的是**证据继承有可审查的理由和责任人**。

## 核心技术、工具与瓶颈

涉及版本控制与分支/依赖管理、任务编排、构建环境配置、日志与失败分类、产物存储分发，以及测试证据的对象绑定。Cygames样本明确列出Jenkins、Coverity、Perforce、GitHub及Python/C++；Bandai样本包含混合基础设施与多平台流水线；这些是来源中的环境，不是库的推荐安装清单，也未运行对应产品。

常见风险应转成可检查问题，而不是承诺效率数字：生成任务是否向仓库写入新输入？产物标签能否被覆盖？重试是否混入旧输出？运行失败和产品缺陷是否被混成一个状态？更快的流水线是否减少了检查范围而未说明？本档案不提供厂商吞吐量、构建时长或成本收益结论。

## 真实公开案例：CI也可能生产后续输入

Cygames在**2020-10-08**的CEDEC2020后续问答 [B4] 说明：CI定期运行C++缩略图程序，随后由Python经资产系统把缩略图提交至Perforce。本文只读博客问答文字，**未观看视频或阅读嵌入演示稿**。

这个有限实例说明自动化的产物不一定止于最终安装包，也可能回到资产仓库。原创交接推论是：应明确生成任务的输入版本、输出归属及何时成为后续任务的输入。来源没有说这些缩略图必然随游戏出货、曾导致重建错误，或实现了本文的候选晋级协议；不能把它扩写成一个并不存在的发布事故案例。

## 与已有知识的责任接口

- [Addressables内容更新基线](../../solutions/engine/addressables-content-update-baseline.md)：配置的远端state位置不等于实际读取身份；版本化文档支持的基线门禁和旧版客户端接收协议尚未执行。

- [游戏QA](../qa/game-quality-assurance.md)：缺陷复现、版本风险和未测范围；构建角色提供可定位对象，不取代QA证据或其组织权限。
- [技术美术](../technical-art/technical-artist.md)：负责的内容工具/资产交接可能成为构建输入；不因此把所有DCC制作工具归入构建岗位。
- [干净检出后的资产导入](../../solutions/engine/asset-import-intent-contract.md)：已有导入/身份与运行时资源实验，不能直接证明生产包的可复现构建或发布授权。
- [独立调用回执与历史摘要](../../research/source-notes/runner-invocation-freshness.md)：已有有限研究夹具的实际实现；支持区分本次执行与旧PASS，但不是游戏发布流水线或候选晋级服务的验证。
- [Destiny配置准入与回退](../../case-studies/liveops/destiny-config-admission-rollback.md)：是另一条运行时准入/恢复边界，不能用构建完成替代环境兼容和数据恢复决策。

后续研究应验证一个真实构建系统如何表达包外配置、重新签名与测试对象身份，再决定哪些证据可以继承。当前职业/学科覆盖矩阵仍未完成；本档案没有建立全行业职位别名或普遍组织标准。

## 参考来源与日期

所有岗位文本访问于2026-10-31；首次发布和最后更新时间未确认，可读不等于职位仍有效。仅保留短述与原创分析，不转载岗位全文、演示稿、代码或图表。详细访问边界见[来源记录](../../research/source-notes/build-engineer-role.md)。

- **B1** Cygames雇主原文，日语，[*ビルドエンジニア／ゲームエンジン／東京*](https://hrmos.co/pages/cygames/jobs/1793262169510682626)。定位：仕事内容、実際の業務、開発環境。官网职业目录直接链接。
- **B2** Bandai Namco Studios雇主原文，日语，[*【ゲームエンジン】CI/CDエンジニア*](https://hrmos.co/pages/bandainamcostudios/jobs/050_0050_sa010_0500_0082)。定位：仕事内容、担当業務、ゲームエンジン開発の固有の特色。
- **B3** Riot Games雇主原文，英语，[*Principal Software Engineer — Developer Connections, Game Release*](https://www.riotgames.com/en/work-with-us/job/8049807/principal-software-engineer-developer-connections-los-angeles-usa)，REQ-0010111。定位：Introduction、Responsibilities；principal中央架构范围。
- **B4** Cygames Engineers' Blog，2020-10-08，[*Python による大規模ゲーム開発環境 ～Cyllista Game Engine 開発事例～*](https://tech.cygames.co.jp/archives/3442/)。定位：缩略图生成问题的文字回答；不是对整场讲座的审阅。

- **B5** SLSA Working Group，[*Build: Provenance，v1.2*](https://slsa.dev/spec/v1.2/build-provenance)。定位：Model、BuildDefinition、RunDetails、BuildMetadata；读取于2026-10-31。
- **B6** SLSA Working Group，[*Build: Verifying artifacts，v1.2*](https://slsa.dev/spec/v1.2/verifying-artifacts)。定位：How to verify、Step 1与Step 2；仅作技术边界参照。
