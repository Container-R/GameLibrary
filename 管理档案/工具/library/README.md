# 书架覆盖校验

```sh
: "${EXPECTED_READER_COUNT:?先设置本批独立盘点并认可的正文数量}"
python3 管理档案/工具/library/check_reader_routes.py --root . --expected-count "$EXPECTED_READER_COUNT" --expected-ids 管理档案/工具/library/reader-ids-current.json
python3 -m unittest discover -s 管理档案/工具/library
```

以上命令在仓库根目录运行。`EXPECTED_READER_COUNT` 必须由本次独立盘点与已接受书目变更给出；不要把扫描结果自动代入期望值，否则可能把漏书也当成新基准。未设置该值时，命令直接停止。

reader-ids-baseline.json 保留原整改55项，不因后续研究改变。reader-ids-current.json 保存当前经审查接受的完整ID集合，新增条目必须逐项核对，并保留原ID；本说明不复制会随新增正文失效的数量和ID清单。冻结ID经人工约束，本工具检查全集/数量/唯一性、相对路径根内、canonical/H1与真实书架链接。空清单、重复JSON键、缺失条目或目标、越界路径均失败。不认证正文质量、来源或真人检索体验；变更书目时先审冻结ID，不靠工具自动重生黄金集。

## 正文出链

[正文链接检查的范围](链接检查说明.md)说明有限离线检查器、非零退出状态及未支持语法。书架覆盖通过不等于正文链接全部正确。

## 当前正文集合与派生计数

```sh
python3 管理档案/工具/library/check_reader_counts.py --root . --frozen-count 55
```

该只读检查要求目录里的唯一 canonical 路径集合与 GameLibrary 下实际非 README 的 `.md` 正文集合完全相同，再检查目录和当前 state 的9个数量字段。冻结基数55由调用方明确给出；后增数量等于当前总数减55。缺文件、空库、重复路径、不同路径集合、遗漏字段或布尔/浮点冒充整数均失败，不能用旧的总数文字代替真实集合。

它不改写历史运行计数，也不自动修复元数据。若正文和目录同时替换了同数量的书，当前集合检查仍可能通过；因此必须保留上面的冻结ID、标题和书架检查，不能拿这个工具认证历史内容未丢失、文章质量或来源。普通与优化Python的同14方法及独立同8方法用于回归，不是读者验收或引擎测试。
