# 有界来源分析导航审查

2026-11-01。结论：**存在精选问题入口的可说明缺口，不存在本次四篇笔记完全不可达的证据。建议小范围调整既有入口，不建立全量新分类。**

本审查以协调者指定的 `fd1cc1b23d130bb3d7819bce49a9cc71308b4aae` 内容快照为目标，直接检查现有公开正文和导航文件；没有独立核验远端提交归属。没有读取运行档案、恢复状态或任何私人记录。本报告只保存原创建议与定位，不复制历史索引正文。

## 实际检查范围和身份

| 文件 | SHA-256 |
|---|---|
| `README.md` | `7187cc207c82f8206bc4f450040f14cf026b33115a6f172a89caf7dfa049b758` |
| `DISCOVERY.md` | `6a4189aae60856a03130c0e8dd12dc7b248740d34debd600d9dc3005edff622f` |
| `CATALOG.md` | `580b633cd54286fffc95fd8b67935dca539d336422427bb801ab4fcd7b6becad` |
| `research/README.md` | `fac86f1bdb7dae0d26015b49b630a909ca22eac45a947b6501ed28ed51178cc6` |
| `sources/README.md` | `bdbf1daa1bba5e803f3e4e3ebc40446a8b06106f3b4b6d30df0cc591b43ed625` |
| `taxonomy/reading-routes.json` | `dc980d5b1c990a97ec5965e69d3ece9197157c0caa2fbd5a1c0679774d5bc9f6` |

另定向阅读四篇来源分析的标题、问题与证据限制；核对导航生成器的目录/类型白名单及说明。没有重新审核这些文章的全部原始来源。

- `research/source-notes/steam-report-reconciliation.md`：`d04fb350402ea71ce6b5e2bcd96f34df8e0c57a922f8827f054fa38703ff0da2`。
- `research/source-notes/model-bake-piece-visibility.md`：`caf10624424444810788fe4b8a8cf84658967a3c8612d522eda2095615fe669d`。
- `research/source-notes/quaternion-sign-and-cubic-animation.md`：`ad4d6554bde88df8601228a3d5b3b9871da19aefb73d80725604ffcb762cffd1`。
- `research/source-notes/resource-release-and-reuse-routing.md`：`d70c0b4c26d9b4a5876a358a008fd15872c9016e6ebf57969cc885d1dcce8be5`。

计数仅限当前目录：66 个 `.md`，3 个以 frontmatter 分隔符开头，没有 `research/source-notes/README.md`。这不把 66 篇都判为同类成熟知识、完整研究或来源充分。注册表实际有20条路线；生成器扫描 `roles / knowledge / solutions / case-studies / comparisons`，不扫描 `research`，也不接受 `research` 类型。因此只给某篇来源笔记添加 ID，不会使其成为现有路线的合法目标。

## 四项真实路径练习：文件链接检查，不是用户试验

任务是“给定问题，从根 README 沿现有导航找到对应正文”。对以下四项，实际解析 README 到 sources/research 索引的相对链接，再解析目标链接，均确认文件存在。

| 入口问题 | 当前可用路径 | 当前定位 |
|---|---|---|
| 两张 Steam Total Visits 相减能否叫自然流量？ | `README.md → sources/README.md → research/source-notes/steam-report-reconciliation.md` | 来源索引第195行；研究索引第203行也可达 |
| piece 名称始终对应，合并分组为何还需重审？ | 同一路径结构，目标 `model-bake-piece-visibility.md` | 来源197行；研究205行 |
| 关键姿势相同，逐键四元数取负能否保动画？ | 同一路径结构，目标 `quaternion-sign-and-cubic-animation.md` | 来源191行；研究199行 |
| 通用 done 能否授权不同资源释放/复用？ | 同一路径结构，目标 `resource-release-and-reuse-routing.md` | 来源189行；研究197行 |

这四个文件名在当前 `CATALOG.md` 和 `DISCOVERY.md` 中没有直接目标。两份来源/研究索引分别199/207行，末端把新问题与其他研究和历史记录相邻追加。读者已有可用二跳路径，不能称其孤立，也不能宣称改后点击数下降；本次没有测量人的寻找时间、成功率或理解。

## 最小建议：复用既有来源索引

在 `sources/README.md` 前部、来源说明之后增加一个**“精选来源分析：按接收问题进入”**的四行小表，使用上表四个问题、相应链接及一项短限制：

- Steam：文档与有限集合推导，不是真实后台测量。
- piece：节点文档与分组反例，没有运行烘焙。
- 四元数：固定规范与实数代数反例，没有播放器执行。
- 释放路由：已有来源的合同审查，不是统一关闭算法或新的 SDK 运行。

明确标注“非全量分类；入口不提升证据等级；版本与限制以正文为准”。保留后部已有来源定位，避免大段搬移、重写或自动归档历史内容。根 README 可把现有“来源目录”链接文字改为“来源目录与精选分析问题”，**仍指向同一个文件**。这比新增一个近乎重复的 source-notes 首页更小，也不要求人为给63篇补元数据。没有必要同时在研究 README 再复制同一张表。

## 两个既有路线的有限补齐

还检查了注册表中的 graphics、technical-art、narrative 路线，以及两篇目标文章的身份/问题：

- `KNOW-GFX-GRID-001` 已在 CATALOG，但图形程序路线没有“第一个命中格子是否已经证明最近命中”的入口。建议只在该路线加一项，理由限定为有序格子访问与最近命中停止条件的区别；不宣称已运行射线查询。TA 路线再加同文不是必需；只有另有明确的烘焙接收问题才考虑，不能为了覆盖重复放入。
- `CASE-NARR-002` 已在 CATALOG，但叙事路线没有“给对白加历史条件为何也改变首次排名”的入口。建议在现有叙事路线加一项，保留历史生产说明与原创未执行手推的区分。

这两项以已有合法知识 ID 更新注册表并按原生成器重建 DISCOVERY 即可；不用改 parser、类型体系或证据字段。它们填补具体问题，不建立“所有新文章必须进所有相关路线”的规则。

` scripts/navigation/README.md ` 的开头仍称6条路线，与实际20条不符。建议去掉易过期的定量描述，改指当前注册表；不要把本次修正扩成一套新测试框架。DISCOVERY 的“本地候选预览”是生成器现有语义，不为纯外观修正而改生成器。

## 接收与停止条件

如果实施，只需核对新增/修改的相对链接、两项 ID 的唯一解析、生成器原有 check 与既有测试；比较变更确保未改文章证据等级、历史正文或研究目录扫描范围。确认入口问题准确指向上述有限合同即可结束。

不要求为全部66篇建树、为每个学科补岗位、创建私人取证导航、执行归档夹具，或声称已改善用户体验。本报告本身没有修改上述导航文件或远端仓库。
