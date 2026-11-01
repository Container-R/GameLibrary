# 书架覆盖校验

```sh
python3 管理档案/工具/library/check_reader_routes.py --root . --expected-count 65 --expected-ids 管理档案/工具/library/reader-ids-current.json
python3 -m unittest discover -s 管理档案/工具/library
```

reader-ids-baseline.json 保留原整改55项，不因后续研究改变。当前 reader-ids-current.json 在原集合上明确增加 SOL-LOC-002、SOL-PROG-002、SOL-A11Y-002、SOL-NET-002、SOL-A11Y-003、SOL-ENGINE-003、SOL-NET-003、SOL-ENGINE-004、SOL-PROG-003 与 SOL-ANIM-003，共65项；这不是从扫描结果自动产生的通过名单。冻结ID经人工约束，本工具检查全集/数量/唯一性、相对路径根内、canonical/H1与真实书架链接。空清单、重复JSON键、缺失条目或目标、越界路径均失败。不认证正文质量、来源或真人检索体验；变更书目时先审冻结ID，不靠工具自动重生黄金集。

## 正文出链

[正文链接检查的范围](链接检查说明.md)说明有限离线检查器、非零退出状态及未支持语法。书架覆盖通过不等于正文链接全部正确。
