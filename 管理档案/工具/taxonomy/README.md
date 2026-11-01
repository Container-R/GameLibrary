# 分类兼容与声明文集检查

从仓库根检查当前无YAML的67篇正文：

```sh
python3 管理档案/工具/taxonomy/check_taxonomy.py --root . --taxonomy 管理档案/分类/disciplines.json --mode reader --expected-count 67 --manifest 管理档案/图书目录.json
python3 -B 管理档案/工具/taxonomy/test_check_taxonomy.py
python3 -B -O 管理档案/工具/taxonomy/test_check_taxonomy.py
```

测试18种合成方法，普通/优化重复同一集合，不执行游戏实验。root、taxonomy、mode和正expected-count均显式指定；reader另需manifest。缺文件/空文集/数量不匹配失败，工具位置不决定根。

reader只验证稳定ID/文件唯一、当前canonical路径/H1与清单相符，不要求YAML、不猜每篇学科、不评价正文质量。分类表仍核旧ID兼容、拆分目标、循环和ACCESS条件。清单和预期数同时被改时不能自动发现漏项，应另核冻结ID集合。

`--mode legacy --expected-count <事先确认的旧文数>` 仅适用于根下roles、knowledge、solutions、case-studies、comparisons五旧目录仍存在时；不传manifest。任一目录缺失失败，各目录可空但总文集必须非空。当前旧根目录已退出，legacy模式不适用于当前树，不能用新书数量猜旧文数量，也不能删缺目录检查制造零扫描成功。旧有限frontmatter约定不是完整YAML解析器。

原 `scripts/test_taxonomy.py` 退出当前树；历史源码/审查保留于历史修订，不能把新的18测试结果倒写为旧7方法的执行记录。路径和计数检查不等于行业分类完成或全库整改完成。分类内容见[分类说明](../../分类/README.md)。
