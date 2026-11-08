# 书架覆盖校验

```sh
: "${EXPECTED_READER_COUNT:?先设置本批独立盘点并认可的正文数量}"
python3 管理档案/工具/library/check_reader_routes.py --root . --expected-count "$EXPECTED_READER_COUNT" --expected-ids 管理档案/工具/library/reader-ids-current.json
python3 -m unittest discover -s 管理档案/工具/library
```

以上命令在仓库根目录运行。`EXPECTED_READER_COUNT` 必须由本次独立盘点与已接受书目变更给出；不要把扫描结果自动代入期望值，否则可能把漏书也当成新基准。未设置该值时，命令直接停止。

reader-ids-baseline.json 保留原整改55项，不因后续研究改变。reader-ids-current.json 保存既有冻结ID集合，并非当前正文的完整盘点，新增条目必须逐项核对，并保留原ID；本说明不复制会随新增正文失效的数量和ID清单。冻结ID经人工约束，本工具检查全集/数量/唯一性、相对路径根内、canonical/H1与由规范路径推导的真实书架链接。空清单、重复JSON键、缺失条目或目标、越界路径均失败。不认证正文质量、来源或真人检索体验；变更书目时先审冻结ID，不靠工具自动重生黄金集。

## 正文出链

[正文链接检查的范围](链接检查说明.md)说明有限离线检查器、非零退出状态及未支持语法。书架覆盖通过不等于正文链接全部正确。

## 当前正文集合与旧计数模式

```sh
python3 管理档案/工具/library/check_reader_counts.py --root .
```

schema_version 为整数3的精简目录只登记当前条目，不保存旧的派生总数。此模式要求唯一 canonical 路径集合与 GameLibrary 下实际非 README 的 `.md` 正文集合完全相同；缺文件、空库、重复路径、未登记正文、不同路径集合或无效路径均失败。不读取当前 state，不检查或补回历史计数。输出明确说明旧计数校验不适用于此模式。

旧版目录仍使用 `--frozen-count 55`，并保留目录和 state 的原9个数量字段校验；字段缺失或不一致仍失败。冻结基数必须独立确认，不自动从目录产生。旧工具在精简前的136条目录上已因缺少 reader_books_total 失败，不能把新模式成功描述成该旧检查通过。

路径读取优先 canonical_reader_path，路径消费工具兼容仅有 current_read_path 的旧条目；同时存在时必须一致。集合计数工具仍要求 canonical_reader_path。书架检查从 GameLibrary/学科/方向/专题/文章.md 推导专题入口，旧 floor/area/shelf 若存在必须一致，不允许其覆盖规范路径。

当前集合检查无法证明同数量替换没有发生，仍须独立核对ID、标题、导航与变更依据。既有 reader-ids-current.json 只登记96项，而精简前目录与正文各136项；黄金集不因本次字段精简自动扩大，书架冻结ID检查仍会失败，需单独核对解决。此项不是正文或来源的通过结论。
