# 待研究课题与研究笔记

通过 `.agent/queue.json` 记录研究任务；成熟知识发布到对应知识目录，不能用此目录的笔记冒充已验证结论。

## 复运行原创模型

仓库的 Python 标准库教学模型可统一运行（不安装依赖、不访问网络）：

```sh
python3 scripts/run_model_tests.py
```

运行前审阅代码。每个 `research/experiments/*/test_*.py` 独立进程执行，任何套件失败则总命令返回非零；未发现测试文件也失败。各实验 README 说明各自前提，`test-output.txt` 是已记录的那次执行，不会被脚本自动改写。全部通过仍不代表真实引擎、设备、物理、声音或网络已经验证。

## 覆盖与分类审计

[初始七篇覆盖快照与ACCESS兼容拆分提案](audits/initial-coverage-and-taxonomy.md)：历史快照不是实时完成率，分类提案尚未应用。
