# 菜单朗读仲裁：有限模型材料

- [仲裁轨迹与判据](event-trace.md)、[脚本](trace_model.py)、[运行输出](trace-result.json)。
- [因果与时效判据](causal-freshness.md)、[脚本](causal_freshness_model.py)、[运行输出](causal-freshness-result.json)。

这两份原创标准库模型只检验人工输入下的应用层状态，不接入平台、声音、存储或网络。将脚本放在可写目录后，运行 python3 trace_model.py 与 python3 causal_freshness_model.py；它们会重写各自同目录的输出JSON。

[返回正文](../../../GameLibrary/本地化与无障碍/无障碍设计/屏幕朗读/菜单朗读的过期淘汰与操作结果保留.md)

- [输入契约边界测试](test_contract_boundary.py)、[结果](contract-boundary-result.json)。它刻画可信输入前提，不实现完整回执验证。
