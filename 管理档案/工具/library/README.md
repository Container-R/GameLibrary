# 书架覆盖校验

```sh
python3 管理档案/工具/library/check_reader_routes.py --root . --expected-count 55 --expected-ids 管理档案/工具/library/reader-ids-baseline.json
python3 -m unittest discover -s 管理档案/工具/library
```

冻结ID由当前55旧项登记取得并经人工约束，本工具检查全集/数量/唯一性、相对路径根内、canonical/H1与真实书架链接。空清单、重复JSON键、缺失条目或目标、越界路径均失败。不认证正文质量、来源或真人检索体验；变更书目时先审冻结ID，不靠工具自动重生黄金集。
