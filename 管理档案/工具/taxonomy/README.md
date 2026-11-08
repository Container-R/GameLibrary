# 分类兼容与声明文集检查

从仓库根检查本批独立确认的当前无YAML正文：

```sh
: "${EXPECTED_READER_COUNT:?先设置本批独立核对的正文数量}"
python3 管理档案/工具/taxonomy/check_taxonomy.py --root . --taxonomy 管理档案/分类/disciplines.json --mode reader --expected-count "$EXPECTED_READER_COUNT" --manifest 管理档案/图书目录.json
python3 -B 管理档案/工具/taxonomy/test_check_taxonomy.py
python3 -B -O 管理档案/工具/taxonomy/test_check_taxonomy.py
```

当前测试20种合成方法，普通/优化重复同一集合，不执行游戏实验。root、taxonomy、mode和正expected-count均显式指定；reader另需manifest。缺文件/空文集/数量不匹配失败，工具位置不决定根。

reader只验证稳定ID/文件唯一、当前canonical路径/H1与清单相符，不要求YAML、不猜每篇学科、不评价正文质量。分类表仍核旧ID兼容、拆分目标、循环和ACCESS条件。清单和预期数同时被改时不能自动发现漏项，应另核冻结ID集合。

`--mode legacy --expected-count <事先确认的旧文数>` 仅适用于根下roles、knowledge、solutions、case-studies、comparisons五旧目录仍存在时；不传manifest。任一目录缺失失败，各目录可空但总文集必须非空。当前旧根目录已退出，legacy模式不适用于当前树，不能用新书数量猜旧文数量，也不能删缺目录检查制造零扫描成功。旧有限frontmatter约定不是完整YAML解析器。

原 `scripts/test_taxonomy.py` 退出当前树；历史源码/审查保留于历史修订，此前18项方法属于旧版本，当前20项测试结果也不能倒写为旧7项方法的执行记录。路径和计数检查不等于行业分类完成或全库整改完成。分类内容见[分类说明](../../分类/README.md)。

## 精简目录兼容

当前路径优先读取 canonical_reader_path，兼容仅有 current_read_path 的旧条目；两者同时存在但不一致仍拒绝。精简目录不需要流程或审稿历史字段。预期数量必须独立核对，不能直接把待检查清单的长度代入以掩盖漏项。既有未支持项和错误不会因字段精简自动获得通过。
