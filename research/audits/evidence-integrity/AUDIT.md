# 证据一致性工具独立审查

2026-10-31。复制工具至本目录并禁用pycache写入；未执行任何归档引擎代码。9项隔离测试通过，实库65项检查通过、0失败、CLI退出0。执行前后对gamelibrary-work全部文件SHA256快照比较完全一致。隔离损坏源文件导致CLI退出1、报告failed=1。

检查范围、历史排除、哈希非签名、二进制仅元数据比对、非语义验证及静态快照TOCTOU限制准确。resolve后包含性检查拒绝外部符号链接；内部符号链接未禁止，符合只限制根外逃逸而非禁止全部链接的实现。

P2发现：strict_json('{"v":1e999}')接受float inf。parse_constant只拒绝NaN/Infinity字面量，不覆盖有限JSON数字文本经float转换溢出的情况。在隔离summary增加未选中metadata=1e999且保留正确source_sha256，manifest检查仍pass。与README“JSON拒绝非有限数值”的承诺不符。建议parse_float检查isfinite并补±1e999回归；已通知作者。没有当前真实档案污染证据，不把该输入构造称为真实库错误。

本目录保存独立工具副本、测试stdout/stderr、实库报告与verifier.stderr。等待作者修订后再冻结结论。

## 最终复核：已修复

作者增加parse_float有限性判断。冻结版verifier SHA256 b62a4bfc2c8b83506290e513e9de4965023c810531b6d18a17d21301b99c2cd8已复制至final/独立复跑：9项测试通过，65项真实档案检查仍通过，±1e999均被拒绝，未选中metadata溢出案例报告失败。原始结果见final/regressions.txt、final/tests.stderr、final/archive-report.json。未发现剩余阻断问题；初版缺陷不代表真实档案存在错误。
