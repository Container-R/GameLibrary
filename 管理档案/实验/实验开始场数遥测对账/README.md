# 实验开始场数遥测对账：复现材料

配套[正文](../../../GameLibrary/数据分析/实验分析/实验数据质量/实验开始场数下降时的遥测对账.md)。本包是 Python 标准库确定性教学模型，不含真实玩家数据，也未接入生产采集系统。

在本目录使用 Python 3.12 运行：

```sh
python3 -m unittest -v test_experiment.py
python3 -O -m unittest -v test_experiment.py
python3 analyze.py inputs/case-08.json
```

核对全部保存输出而不覆盖原件：

```sh
python3 - <<'PYCODE'
import subprocess
from pathlib import Path
for p in sorted(Path('inputs').glob('case-*.json')):
    actual = subprocess.check_output(['python3', 'analyze.py', str(p)])
    assert actual == (Path('outputs') / p.name).read_bytes(), p.name
print('12 outputs match')
PYCODE
```

可选运行 `python3 make_fixtures.py` 重建 inputs 与 oracle；它会覆盖这些教学文件，建议在副本中执行。生成器含答案，不是盲读材料。原始字节及本次执行范围见 [运行记录](run-record.json)。

- [模型边界与结果说明](ENGINEERING.md)
- [原始来源、定位及条件](sources.json)
- `inputs/` 是可观察输入，`outputs/` 是分析器实际输出。
- `oracle/` 保存隐藏世界与预期检查，分析器不会读取它；测试会使用它。

记录差集不能自动区分永久丢失和迟到；序号没有缺口不证明整段完整。生产接入中的异常整理、越窗分类、持久化与跨端状态机未由本模型实现。
