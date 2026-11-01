# 精选阅读路线生成器

标准库工具，具体路线以 [当前注册表](../../taxonomy/reading-routes.json) 为准，包含已有岗位档案入口和跨学科问题入口。是编者选择关系，不是自动角色分类、职业同义词库或用户寻路试验结果。CATALOG仍为完整清单。生成物只描述当前输入目录；它不能独立证明远端发表状态。

在仓库根运行：

```sh
python3 scripts/navigation/build_routes.py . --registry taxonomy/reading-routes.json --output DISCOVERY.md
python3 scripts/navigation/build_routes.py . --registry taxonomy/reading-routes.json --output DISCOVERY.md --check
python3 scripts/navigation/test_routes.py
```

生成索引应放在仓库根，链接以该位置解析；它不是可任意搬移的独立站点。

## 契约

- 通过文章稳定ID解析路径，移动保留ID会更新链接；不根据文件名猜角色，不猜主题或合并QA标签。
- role入口显式subject_profile_id，必须存在且type为role；problem入口禁止该字段，不计为岗位成果。每条目标附问题/编者关联理由。
- 标题、status、primary_discipline均来自原文；既不提升证据等级，也不因有实验就宣称verified。needs-research不能作为路线目标。缺失/重复ID、未知状态、非法注册字段报错。
- 字符输出HTML转义并转义可能产生Markdown链接的方括号，路径使用URL编码。注册表字符串不能含换行。现有阅读关系不隐含跨引擎统一算法。
- 确定性顺序取注册表；`--check`只比较不写文件，缺失/不同退出1，一致退出0。校验/解析错误退出2。完整校验后在输出目录写临时文件再替换，校验或临时写失败不会先截断旧输出；不是并发发布协调或断电持久性保证。
- 工具读取知识目录中的全部.md检查重复ID和元数据；候选变化可能使预览过期。没有读取.agent或把草稿误算成远端状态。

## 明确限定的 frontmatter 解析

不是完整YAML解析器。识别LF分隔的首部`---`，仅消费顶层`id,title,type,status,primary_discipline`五个单行标量；允许非空裸文本或无内嵌同类引号/转义的成对单/双引号文本。拒绝这些必需字段的重复、缺失、引号包裹的必需字段键、缩进/多行、块标量、别名/锚点、集合、反斜线与行内注释形式；裸文本也拒绝注释开头、空白后#、冒号后空白/行尾及null/布尔/数字或日期等歧义起始（这些文本应加引号）。必需字段后出现缩进注释亦保守拒绝。所有非空非注释顶层行必须使用无空格小写键`key:`形式（否则报错，不静默忽略键变体）；合法的其他字段内容不解析，尤其不声称校验sources/versions或完整YAML合法性。仓库若改用复杂YAML写法，应升级解析约定或显式报错，不能把本工具当通用YAML验证器。

## 验证范围

作者 11 项隔离测试与独立增加的 5 项测试分开记录；独立套件继承作者测试，因此其 16 项不是 16 项新测试。集成者在最终仓库路径重跑作者测试与 `--check`。记录见 [审查档案](../../research/audits/reading-routes/REVIEW.md)。

这些检查证明限定输入和脚本行为，不证明角色分类覆盖完整、读者寻路更快或已经远端发布。未做用户导航试验；文章的来源与执行边界仍应到正文确认。

后续 QA 职责档案以显式 `ROLE-QA-001` 加入精选路线；它是责任集合入口，不建立 qa-tester、qa-engineer 或 performance-qa 的全局同义关系。原四路线审查记录保留其历史快照。

关卡策划以显式 ROLE-DESIGN-001 加入第六条路线；[集成审查](../../research/audits/level-designer-role/integration-review.md)仅核对文章关联与生成一致性，不宣称用户寻路效果。
