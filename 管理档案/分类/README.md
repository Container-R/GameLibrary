# 学科、职业与技术关联

`disciplines.json` 是初始候选骨架，须在后续研究中核实职业边界并按证据维护。

## 2026-10-31.2：ACCESS 的兼容拆分

行业组织分别维护[本地化](https://igda.org/sigs/localization/)与[游戏无障碍](https://igda.org/sigs/game-accessibility/)专业社区，支持区分这些交叉但不等价的研究目标。本库保留旧 `ACCESS` ID、名称和范围，新增候选 `A11Y`、`LOC`；`split_into` 是一对多导航，不是别名或自动重分类。

- 既有消费者继续读取原字段和旧 ID；新增字段为可选，文件结构 schema_version 仍为1。
- 新内容按主要验收目标选主类；交叉使用 related。历史引用不静默改义，旧条目逐篇复核后才能迁移。
- 旧元数据索引按文档实际 primary_discipline 生成；无YAML新书使用显式图书目录，不据ID猜其学科，不把候选节点数当完成率。旧聚合类和新分支不得重复计算学科覆盖。
- [首次审计](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/research/audits/initial-coverage-and-taxonomy.md)是应用前的历史提案，保留当时22节点内容指纹；本次有24个ID，其中ACCESS为遗留聚合节点，不是24个已研究学科。
- `python3 管理档案/工具/taxonomy/check_taxonomy.py --root . --taxonomy 管理档案/分类/disciplines.json --mode reader --expected-count 56 --manifest 管理档案/图书目录.json` 检查旧ID保留、缺目标、重复ID、循环和错误单目标别名。测试只验证仓库兼容约束，不验证整个行业分类。

分类依据读取于2026-10-31，不复制机构目录；各领域岗位/技术仍需独立研究。
