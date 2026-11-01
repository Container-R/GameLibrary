# 显式教学模型选择入口

```sh
python3 管理档案/工具/models/run_model_tests.py --root 审查快照 --models-dir 相对模型目录 --expected-suites 已审列表.json
python3 -m unittest discover -s 管理档案/工具/models
```

默认只列出selected_not_executed。必须声明非空唯一suite列表且与目录实际匹配；不存在旧research根不应空PASS。单独授权、审过具体源文件之后才使用`--run`；默认每suite 60秒，可给正有限`--timeout`。超时和非零退出失败，保留原输出；不保证整个后代进程树终止。子进程沿用父解释器优化模式。当前不附自动可执行的旧模型集；历史模型仍在固定历史版本，不能将教学测试通过称引擎QA。
