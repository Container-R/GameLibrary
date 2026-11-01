# 任务队列检查器

从仓库根运行，明确选择当前输入与预先确定的任务数：

```sh
python3 管理档案/工具/queue/validate_queue.py . --taxonomy 管理档案/分类/disciplines.json --queue .agent/queue.json --expected-task-count 155
python3 -B -m unittest discover -s 管理档案/工具/queue -p 'test_*.py'
python3 -B 管理档案/工具/queue/adversarial.py
python3 -B -O -m unittest discover -s 管理档案/工具/queue -p 'test_*.py'
python3 -B -O 管理档案/工具/queue/adversarial.py
```

前一个测试入口含9基础+10 CLI方法；adversarial含同9基础+6追加，二者联合25种方法，不把重复9种计为新覆盖。所有测试使用临时合成输入，不执行引擎或历史档案。

根必填；两个文件路径必须为规范根相对路径，拒绝绝对路径、向上越界、根外符号链接和控制字符。输入缺失失败，不回退、不用空队列替代。`--expected-task-count`必须正整数且精确匹配，计数不是黄金ID集合，不取代身份对照。

为旧外部调用兼容，省略选项仍指旧 `taxonomy/disciplines.json` 和 `.agent/queue.json`；旧分类目录退场后该调用应明确失败，必须使用上面的新路径，不会静默改读。省略计数选项时空tasks仍按旧API允许，不可用作迁移验收。

校验任务ID、学科引用与可选artifact_paths；published声明路径必须存在，目录存在不验证内容，planned缺失仍允许，额外状态和旧expected_artifact自由描述兼容。不是完整schema或并发文件系统安全边界。通过不认证证据、发布或根整改完成。

历史[queue审查](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/research/audits/queue-contract-guard/README.md)及其原源/夹具按当时版本保留；不要用新工具替换旧指纹，或据旧PASS认领当前队列通过。
