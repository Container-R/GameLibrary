# 偶发存档回退的复现缩减：来源记录

阅读日期：2026-11-23。

- Musuvathi 等，[Finding and Reproducing Heisenbugs in Concurrent Programs](https://static.usenix.org/events/osdi08/tech/full_papers/musuvathi/musuvathi_html/index.html)，OSDI 2008，§3.1、§3.3、§4.2。核读可控环境输入、调度选择、重放失败及实现边界。本文所用暂缓的是一次存档业务操作的发布接缝，不是 CHESS 或线程级重放。
- Hypothesis，[Flaky failures](https://hypothesis.readthedocs.io/en/latest/tutorial/flaky.html)，回放同一输入所见结果及生成的稳定性对缩减的约束。本文将不稳定候选作为未决，是保守的工作流选择。
- Zeller 与 Hildebrandt，[Simplifying and Isolating Failure-Inducing Input](https://www.cs.purdue.edu/homes/xyzhang/fall07/Papers/delta-debugging.pdf)，IEEE TSE 28(2)，2002，§II、§III-B。核读三态、单项最小定义和 ddmin。试件只采用按块和单项删除的简化过程，不宣称实现论文完整算法或保证全局最小。
- Python Software Foundation，[Path.replace（3.12）](https://docs.python.org/3.12/library/pathlib.html#pathlib.Path.replace)，目标存在时替换文件。试件实际执行并读回；未验证异常断电及并行提交安全。
