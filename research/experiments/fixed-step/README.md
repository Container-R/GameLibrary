# 固定步长调度契约实验

2026-10-31，Linux 云环境，Python 3.12.14，标准库 unittest + fractions。

运行：`python3 research/experiments/fixed-step/test_fixed_step.py`。7 项测试通过，原始输出见 [test-output.txt](test-output.txt)。脚本为本库原创，不复制引擎源码。

范围：用有理数消除测试调度器自身的浮点舍入，验证同一 tick 输入流在不同渲染分段下消费一致、积压保留、追帧上限、单次边沿消费与展示只读。

未验证：Unity/Godot 实际输入系统、物理求解器、网络、浮点数跨架构一致性、CPU耗时或真实战斗手感。该实验不是生产调度器，也不是跨平台确定性证明。
