# 既有稳定ID路线的维护工具

读者使用[中文书库](../../../GameLibrary/README.md)。这里仅校验和预览[既有路线注册表](../../../taxonomy/reading-routes.json)，不是另一套读者导览，也不自动改写[规范书目](../../图书目录.json)。

## 当前无YAML正文：reader模式

在仓库根运行：

```sh
mkdir -p 管理档案/草稿
python3 管理档案/工具/navigation/build_routes.py . --registry taxonomy/reading-routes.json --reader-manifest 管理档案/图书目录.json --expected-count 55 --output 管理档案/草稿/稳定ID路线候选.md
python3 管理档案/工具/navigation/build_routes.py . --registry taxonomy/reading-routes.json --reader-manifest 管理档案/图书目录.json --expected-count 55 --output 管理档案/草稿/稳定ID路线候选.md --check
```

要求非空清单、正数且精确匹配的预期篇数、唯一稳定ID/文件、有效当前与canonical路径、实际H1一致，路线目标须可解析。不从无YAML正文猜证据等级或学科；岗位起点只按稳定ID的ROLE命名空间判断，不另认证职业分类。预期55不是黄金ID集合，历史完整性仍需对照冻结清单。

## 保留的legacy模式

仅检查仍然存在且各自非空的明确旧frontmatter目录，不回退到自动扫描：

```sh
python3 管理档案/工具/navigation/build_routes.py . --registry taxonomy/reading-routes.json --source-dir roles --source-dir knowledge --source-dir solutions --source-dir case-studies --source-dir comparisons --output 管理档案/草稿/旧元数据路线候选.md
```

这条命令仅在上述五目录仍齐全、包含registry所需旧ID时适用。旧正文退出后应使用reader模式；不要删除缺目录错误来制造零扫描通过。两模式必须明确二选一，legacy不接受reader的expected-count。

## 写入与检查边界

只写字面 `管理档案/草稿/` 下的.md，父目录需事先创建；根README/DISCOVERY/CATALOG、新正文、manifest、registry及其他声明输入均不可作为输出，包括解析后符号链接和同文件碰撞。校验完成后才临时写入并替换；`--check`也执行保护。输入错误退出2，草稿缺失或不同退出1，相同退出0。路径相对关系按实际输出位置生成。

这是维护防误写，不保证恶意并发替换文件系统安全或断电持久性；PASS不验证读者理解、正文事实、支持锚点、原范围处置或发表授权。

## 两套回归一起运行

在仓库根运行，原29测试与新增17 reader测试不能遗漏其中之一：

```sh
python3 -B -m unittest discover -s 管理档案/工具/navigation -p 'test_*.py'
python3 -B -O -m unittest discover -s 管理档案/工具/navigation -p 'test_*.py'
```

均为临时合成目录，不执行引擎/历史实验。新CLI反例在子进程显式继承优化标志。

旧 `scripts/navigation` 三文件退出当前树，不保留根wrapper。历史 `research/audits/reading-routes` 中探针/旧测试以及 `research/audits/release-regression-1900` 命令属于其当时版本，不能对新API当现行验收入口；不要重写历史审查或用新版结果替代旧记录。需要复核旧接口时按历史commit检出整组，旧树可从迁移前的 `d0c87c` 修订定位；本次现行测试是上面的46方法。registry仍留原路径，本迁移不宣告其他旧正文或根工具全部退出。
