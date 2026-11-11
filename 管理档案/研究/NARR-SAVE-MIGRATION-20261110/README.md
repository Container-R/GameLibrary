# ink 存档迁移复验包

本包随正文提供固定 ink 提交 35c63e52f1d36060930dc7ed3cfba38ea224b528 的最终 true / false 两次真实原生运行及一次历史失败，以及一次 SQLite 宿主集成运行。均为原创合成故事与合成奖励，不含玩家资料。

## 证据与脱敏

- fixtures 与各次 inputs、Program.cs、编译故事、存档、trace 和退出记录可直接核查。
- provenance.json 逐项给出原文件和公开副本的 SHA-256。transformation 为 unchanged 的文件才是原字节；其他文本仅去除运行环境路径。原始证据未覆盖，公开副本不能冒充全部原始字节。
- source-sha256 / reference-sha256 中的摘要仍对应当时实际源码和引用程序集；路径改成 INK_SOURCE / SDK 标记。历史命令中的 PACKAGE、SDK、INK_SOURCE 是脱敏占位符，不是可直接执行的命令。
- 四份 .sql 是原 SQLite 数据库的逻辑导出，保留 schema、表行、BLOB 与历史 operations.digest；不保证还原后的数据库文件 SHA 与原始数据库一致。
- package.json 中的 candidate_path 原先是绝对路径且参与原包摘要。公开包改成 PACKAGE 占位路径，因此公开包摘要变化；package.sha256 仍记录原摘要。不能用公开包重新计算后声称等于数据库历史摘要。此差异在 provenance.json 明确列出。
- SHA256SUMS 仅验证本次公开副本。没有包含自校验循环，也不认证来源或语义真实性。
- 未附二进制程序集。固定上游源码可按下面方式重新编译；历史命令与哈希保留构建边界，重新编译出的程序集摘要可能因构建路径等变化而不同，不得据此改写旧运行记录。

## 不重跑即可核验

在本包目录运行 `sha256sum -c SHA256SUMS`。Python 标准库可还原 SQL 并检查记录：

```python
from pathlib import Path
import sqlite3, hashlib
for f in Path('host-integration/run-20261111T045701Z').glob('*/*.sql'):
    db = sqlite3.connect(':memory:')
    db.executescript(f.read_text())
    revision, host, content, blob = db.execute('SELECT * FROM active').fetchone()
    assert (revision, host) == (9, 5)
    assert db.execute('SELECT amount FROM inventory').fetchone()[0] == 10
    assert db.execute('SELECT count(*) FROM receipts').fetchone()[0] == 1
    assert db.execute('SELECT count(*) FROM operations').fetchone()[0] == 1
    assert blob == f.with_name(f.stem + '-advanced.save.json').read_bytes()
    print(f, hashlib.sha256(blob).hexdigest())
```

## 自行复现（新运行，不覆盖历史）

要求：Python 3 标准库、git、官方 .NET SDK 8.0.428，其中包含 runtime / reference pack 8.0.34；固定 ink 源码检出且工作树干净。自行取得官方依赖，不需要把本包当软件安装器。

1. 将 `DOTNET_ROOT` 设为 SDK 根目录，`INK_SOURCE` 设为固定提交的干净 ink 检出目录。可从 https://github.com/inkle/ink 获取并检出上述提交。
2. 将 `NATIVE_RESULTS_DIR` 设为新建空目录的路径，禁止使用本包的 native-results。运行 `python3 reproduce-native.py`，然后 `python3 reproduce-native.py --old-score-false`。两次分别使用历史最终 true / false 版 Program.cs，输出新程序集、命令和轨迹；已有结果目录会报错，不覆盖。
3. 同样环境运行 `python3 host-integration/run.py`。它从新原生目录取候选与程序集，建立新的时间戳结果，执行两候选各桥/公路的同库事务与原生继续。此脚本的交易逻辑来自冻结版本，仅 SDK 和原生输入目录改为显式配置。冻结子目录内的 run.py 是脱敏历史快照，不作运行入口。
4. 比较新轨迹的语义事实、选择、退出72/73、库存与修订，不把新的绝对路径、包摘要或程序集摘要写回旧结果。复现脚本为发表时整理的路径适配版本，未另行执行，因此历史成功不构成这些适配脚本已运行通过的声明。

原生构建使用 Roslyn 直接编译固定上游 C# 与 .NET 8 引用集，定义 NETSTANDARD/NETSTANDARD2_0；它不是原 netstandard 项目构建。最初原项目在 NuGet-Migrations 首启发生 IOException，不将新构建解释为解决原问题。原始首启失败日志未纳入本公开包，仅保留其失败范围说明；false 断言失败轨迹仍完整提供，见 025759Z。

详见 [原生结果](native-results/RESULTS.md)、[宿主结果](host-integration/RESULTS.md) 与 [原始来源](sources.json)。这些有限观察不认证生产迁移、并发、断电或跨服务 exactly-once。
