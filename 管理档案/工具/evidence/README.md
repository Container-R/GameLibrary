# 显式归档关系校验工具

本工具只校验声明字节/字段关系，不启动归档代码，不认证执行真实性或原始来源。

`verify.py`保留原算法供模块调用；面向迁址的入口为`verify_relocated.py`，必须显式给出根、已审注册表与策略：

```sh
python3 管理档案/工具/evidence/verify_relocated.py --root 审查快照 --registry 已审注册表.json --policy 已审迁址策略.json
python3 -m unittest discover -s 管理档案/工具/evidence
```

策略version必须为整数1；包括registry_sha256、正expected_checks、非空prefixes、逐项retired_checks及理由。操作数路径可以映射，原文manifest键和历史摘要不改。缺失/不匹配失败；退休项不计pass、complete=false并退出2，不能用全部退休制造空PASS。报告只代表显式声明一致性。

本目录不附带历史519项注册表或raw副本，也不默认认领当前根可验证它们。原注册表、工具版本、失败记录保留于[固定历史](https://github.com/Container-R/GameLibrary/tree/800d505633df0ceaa0bab8de643b0244ba1a5476/scripts/evidence)。新衍生文件须另用公开安全的当前哈希绑定，不能回填旧receipt。策略ID/理由也应避免执行身份。原始检查/当前衍生通过都不是新run。

`isolation.py`保留原技术helper字节，不是沙箱或进程树保证。需要它的未来调用者可显式从`管理档案.工具.evidence.isolation`导入；历史runner仍依赖其固定历史源码，不自动改写原source SHA或授权执行。
