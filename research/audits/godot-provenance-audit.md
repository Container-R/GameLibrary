# 已有 Godot 证据的来源措辞审查（只读）

2026-10-31；行号为本次读取 `gamelibrary-work` 快照，修改后需重新定位。未修改主树、未重跑引擎、未发起GitHub请求。范围：四篇相关方案、五个已有夹具README、相关独立复核说明、sources目录及TA关联入口。

## 判断：保留观察，撤回身份暗示

没有发现正文直接声称“已验证官方发行包签名”或“已按该提交构建复现”的句子。主要风险是把二进制自报版本当作独立确定的发行身份，尤其原始字符串含`official`，以及把夹具source_sha256简称“源码哈希”令读者误认为引擎源码对应关系。

已查阅作者的 `research-drafts/godot-animation-events/provenance-receipt.json`：它**明确标注为工具结果相关字段的人工摘录，不是完整原始响应**。记录公开`4.6.3-stable`解析为`35e80b3a8822a9df9be390814b62f44c0a9c69e8`；安装二进制自报完整hash`7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3`的查询返回422/No commit found。不得把此摘要再称为“完整raw receipt”。本次审查不独立认证这两个查询；根写入者应归档实际工具响应或如实保留摘要级别。

父代理报告共享安装文件SHA256为`f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`，自报`4.6.3.stable.official.7d41c59c4`。四份后续夹具summary中有该二进制摘要；fixed-step当前summary缺binary_sha256（此前完整性审查已记录此缺口），因此不能追溯补写成“当时日志已测得此文件摘要”。共享环境关系应与各次实际归档字段分开陈述。

**结论限于身份对应未建立**：本地文件摘要、版本自报、公开tag指向是三类证据；目前不能互相替代。不得据此称本地二进制危险、恶意、伪造或推翻实际采集的回调/焦点/导入/路径观察。也不能由同一安装文件的重复运行认证官方来源。

## 一个共享说明路径

建议新增 `research/source-notes/godot-installed-binary-provenance.md`，可附同名前缀receipt JSON；标题“已安装Godot二进制：自报版本与公开源码身份尚未对应”。建议正文核心：

> 本库相关运行使用环境中已安装的Godot可执行文件。记录的版本字符串`4.6.3.stable.official.7d41c59c4`是程序自报，`official`不是本库认证结论。文件SHA256用于标识被测文件，不证明发行来源。公开4.6.3-stable查询与程序报告的提交信息未建立对应；当前不能把这些执行结果归属于已认证的官方4.6.3发行包或精确公开源码提交。保留原始输出；结果仅适用于所记录的本地文件、夹具和环境。4.6系列官方文档另作设计/API参考，不是该二进制源码审计。固定步长早期归档未独立保存二进制摘要，其具体证据缺口不回填。

链接相对路径：四篇solutions使用`../../research/source-notes/godot-installed-binary-provenance.md`；五个fixture README使用`../../source-notes/godot-installed-binary-provenance.md`；sources/README使用`../research/source-notes/godot-installed-binary-provenance.md`；TA角色文使用`../../research/source-notes/godot-installed-binary-provenance.md`。新增说明需保留查询日期/工具/响应级别，不补造签名或来源证明。

## 逐路径修改建议（窄措辞，不改原始日志）

下表路径均相对仓库根；每组行号按原文件有效。把共享说明链接放在首次实测段落，避免每句重复长免责声明。

| 路径与行号 | 当前风险/定位 | 建议窄措辞 |
|---|---|---|
| `solutions/programming/fixed-step-simulation-boundary.md:10` | versions把完整自报字符串标为实际夹具 | 保留字符串，改尾缀为“本地程序自报版本；发行/源码对应未确认” |
| 同文件`:12,103,105,113` | Godot4.6.3实际/集成标题及首次运行段 | 首次改“本地安装Godot（自报…）实际运行”，标题可用“已安装Godot的实际回调/暂停反例”；105加共享说明链接。保留全部观测数字 |
| `solutions/ux/modal-focus-recovery.md:11,208` | versions与首段直接称4.6.3 | versions标自报；208改“本地安装Godot的无头实验（自报4.6.3，身份限制见说明）” |
| `solutions/engine/asset-import-intent-contract.md:11,30,88` | 实际导入器/实际4.6.3二进制 | versions标自报；30改“已安装且自报4.6.3的导入器”；88区分官方4.6文档与本地执行身份，加共享链接 |
| 同文件`:59` | “源码/二进制哈希”可能被读作引擎源码 | 改“原创夹具源文件/被测二进制文件摘要”，不暗示两者可重构引擎 |
| `solutions/ai/navigation-readiness-and-partial-path.md:11,28,85` | 实际Godot4.6.3/源码摘要 | versions标自报；28“本地已安装Godot的实际…查询”；85“程序自报…；夹具源文件/二进制摘要…”，加共享说明 |
| `research/experiments/godot-fixed-step/README.md:1,33,58` | 版本标题、引擎字符串、实际二进制4.6.3 | 标题“已安装Godot固定回调…（自报4.6.3）”；33“程序自报…”；58保留“不是源码审计”并补“发行身份对应未确认”/共享说明 |
| 同文件`:33`后 | early summary缺二进制摘要 | 明示当前summary只存夹具来源摘要和版本输出；不可把后续共享环境测量伪装为当次归档字段 |
| `research/experiments/godot-pause-input/README.md:1,17,56` | 实测字符串但未说自报 | 1加“自报”；17改“被测程序自报…，本地文件SHA256…”，链接说明；56补“未认证发行来源” |
| `research/experiments/godot-focus-boundary/README.md:1,3,49` | “实际Godot4.6.3”“四份源码” | 3改“本地程序自报…；二进制与四份原创夹具源文件摘要”；49官方文档与本地自报版本分开；共享链接 |
| `research/experiments/godot-import-boundary/README.md:3,11,43` | 4.6.3失败模式/实际版本 | 3“本地安装Godot的资产交接…”；11“程序自报版本”；43“被测程序自报…”，共享链接 |
| 同文件`:77` | “五份源码及引擎哈希一致” | “五份原创夹具源文件及被测可执行文件摘要一致；不认证官方发行来源” |
| `research/experiments/godot-navigation-sync/README.md:3,13,82` | 4.6.3夹具/实测/二进制4.6.3 | 3本地安装夹具；13“程序自报…”并链接；82官方4.6文档与自报版本单独记录，源码对应未确认 |
| 同文件`:91` | “四份主源文件”含义尚可 | 可明确“主夹具源文件”，保留重复运行不扩大范围的原句 |
| `sources/README.md:7,31,33,37,39` | 汇总入口简写4.6.3真实执行 | 增加统一说明行：以下4.6.3均为本地程序自报版本，发行/源码身份未对应；链接共享说明。不要删官方文档出处 |
| `roles/technical-art/technical-artist.md:110` | 间接推广为4.6.3反例 | 改“已安装Godot（自报4.6.3）的实际反例”，仍链接原导入条目，可附共享说明 |

## 复核说明的追加澄清

不要重写历史判据/数字，也不要把原PASS改成整体无效；追加今日身份边界说明即可。

- `research/experiments/godot-focus-boundary/review/README.md:29`：`Independent execution used`后注明`a local executable reporting`；matching version/binary digest仅表明复跑一致性，不认证官方来源。`source hashes`明确是fixture sources。
- `research/experiments/godot-pause-input/review/audit.md:9`：`Engine:`改`Executable self-report:`；five source hashes是夹具，不是引擎源码。
- `research/experiments/godot-import-boundary/review/README.md:13`：`Five fixture-source hashes and local executable SHA256`；追加共享身份限制。
- `research/experiments/godot-navigation-sync/review/README.md:7`：`Three actual processes of the local executable (self-report 4.6.3)`；保留有限初始化实验PASS，同时追加不是发行认证。

## 明确保留且不应误改的内容

1. 所有version.txt、summary.json、RESULT_JSON、命令、原始日志及其摘要原样保留；`official`字符串不得删除/替换。也不要因文案变更去重写历史hash。
2. “官方4.6文档”“官方建议提交.import”等有实际Godot文档依据的措辞可保留；问题是文档与执行文件身份被合并，不是官网资料失效。
3. `sources/fixed-step-primary-sources.md:9`已经注明stable文档滚动未冻结，无本地二进制认证声明，无需为此次身份问题改写该出处。`research/source-notes/asset-import-policy-availability.md`仅把Godot案例当有限现象引用，不声称官方构建/源码对应，无必要修改。
4. 保留source-backed状态；执行证据仍属有限本地文件观察。若未来取得认证发行构建，建立新的单独运行记录/对照，不覆盖旧记录。
5. 共享说明涉及工具结果摘录，当前不能凭422推断“该提交从未存在”“二进制一定被修改”或安全风险。需要发布包校验/签名、可靠取得链或可重现构建等另外证据才能提高身份保证。

本次仅提出修改建议；根写入者负责核对实际凭证、统一链接和发布授权。受众澄清暂停继续有效。

## 2026-10-31 15:20 UTC — 已暂存澄清的只读复核

读取 `/tmp/provenance-paths.json` 指定21个修改路径，实际共享说明采用 `research/source-notes/godot-runtime-provenance.md`（取代上文建议名）。已检查共享说明及3份凭证JSON、四篇方案的版本元数据/前置说明、五个夹具前置说明、四份历史审计追加段、TA/sources/research入口。

- 总体通过身份边界审查：明确自报版本不认证官方来源，夹具源文件hash不是引擎源码hash；没有安全/伪造/引擎缺陷推断，没有自动抹去观察或改为verified。
- fixed-step当时缺binary_sha256明确标注，明确禁止以较晚摘要回填。四篇方案完整版本字符串保留且追加自报说明；无需机械执行上文所有标题替换建议，前置统一限定足够。
- tag-resolution明确是selected metadata；author receipt明确是人工摘录；另有完整结构化422错误响应单独保存。本次检查文件内容/级别一致，不冒称重新发起或认证原始查询。
- 21个路径中的全部本地Markdown目标检查无缺失；3份JSON可解析。未改主树或重跑引擎，未改/重生成原始日志。历史65项完整性检查结果由集成者另行提供，此审查未冒称再次执行。
- **一项窄措辞修正建议**：共享说明第18行“同机复跑是相同构建的重复证据”仍可能脱离前句读取成早期缺摘要记录也已确认同构建。建议改为：“对于已归档二进制摘要一致的复跑，它们只提供同一文件身份下的重复观察；早期缺摘要运行仍按其原记录限制解释。这不是所有官方4.6.3发行物或其他平台的复现。”已发给根写入者；除这处进一步限定外未见实质阻碍。

本复核只评价措辞与本地证据引用一致性，不认证二进制、官方发行链或工具响应真实性。发布暂停未改变。

集成修正：共享说明已将“同机复跑”收窄为归档二进制摘要一致时的同文件重复观察，早期固定步缺摘要另行保留限制。历史数据未改写。
