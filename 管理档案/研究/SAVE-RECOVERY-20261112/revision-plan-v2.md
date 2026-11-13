# v2 修订计划（组合测试执行前）

依据独立技术预审的实际组合反例，不覆盖 fixture.py、article-v1.md、experiment-report.md 或 run-01。原独立证据位置为 `review-notes/supervision-20261111-2250/save-technical/probe-result.json`；审查定位在 evidence-review.md。

1. 同 ID 当前根匹配仅返回 observed_active，durability=not_established，requires_resolution=true，进程退出码 3，明确不是保存成功。即使上次可能完整成功，没有额外确认记录时也保守返回这一状态。不能凭新一次读取确认旧 fsync，也不盲目补同步。
2. 父代匹配但同候选目录残留时，返回 candidate_exists、publication=not_attempted、requires_resolution=true，退出码 3，保留现场。首版不自动续写、清理或生成新 ID 推进旧快照。人工/上层核对父代、根与残留后，可另起一个明确的新保存请求；这不是同请求无条件重试。
3. 正常路径返回 published_visible，final_directory_sync=returned_success，durability=platform_contract_required。该字段表示实际调用结果，不表示已实验验证断电。
4. 夹具启动即拒绝优化模式（退出码 4），避免 assert 被删除。生产验证应使用不可关闭的显式校验。
5. 在 v2 重跑原 51 项并调整“同请求已完成”的错误预期；另外冻结两个组合：EIO→同 B 重试、ENOSPC→同 B 重试，均应退出3、现场不变、无同步或写入；分别观察 observed_active 与 candidate_exists。再测 -O、PYTHONOPTIMIZE=1 均启动拒绝、不创建输出目录。

这些修订改变原先有歧义的结果接口，不宣称原计划已经覆盖组合反例。无新增持久修复框架。
