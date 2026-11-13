# 多文件存档：复现材料

本目录为恢复后新运行的公开派生材料，不是历史旧运行恢复。原始文件未改动。环境记录整体不发布，实际运行时间、主机、系统、解释器、库、编译器、挂载详情和容量信息均不披露；绝对研究路径替换为 `<EVIDENCE_ROOT>`，工作区为 `<WORKSPACE>`，解释器路径为 `<PYTHON>`。这些占位符用于阅读日志，不是可执行命令。数据内容、选择结果、退出码和数据摘要不变。逐文件原始/派生摘要见 [redaction-manifest.json](redaction-manifest.json)。日志中的 base64 数据是夹具生成的教学存档内容。

输入为 fixture-v2.py、probe-v2.py、experiment-plan.md 和 revision-plan-v2.md。初始计划有历史判据，v2 修订明确替换同操作重试的成功含义；以 v2 为准。原计划提及的 brief.md 不作为运行依赖，完整当前读者承诺在正式文章。

在 Linux/Python 3 的隔离测试目录复制这四个输入后运行：

```sh
python3 fixture-v2.py suite ./new-run
python3 probe-v2.py
```

输出目录必须不存在。probe 创建脚本同目录的 probe-v2，勿在已带归档结果的目录直接运行；先将四个输入复制到新的空目录。不要启用 -O 或 PYTHONOPTIMIZE。夹具会记录本机环境信息，新的原始输出不能未经检查直接上传。

归档包含51例结果、包装层事件日志与4项补充结果，不包含每例磁盘目录和 mountinfo；结果中的快照保留数据摘要。51项摘要见 [summary.json](run-20261112-new/summary.json)，逐例见 [results.jsonl](run-20261112-new/results.jsonl)，补充见 [results.json](probe-v2/results.json)。它们仅支持进程中止与软件错误注入，不支持物理掉电保证。
