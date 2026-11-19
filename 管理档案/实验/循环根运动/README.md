# 循环根运动：复现实验

[返回正文](../../../GameLibrary/角色动画/角色移动/根运动与动作对齐/循环动画回到起点时，怎样提取连续的根运动.md)

## 一骨 Godot 对照

`project.godot` 和 `check_loop.gd` 使用 Linux 上自报 `4.6.3.stable.official.7d41c59c4` 的 Godot，单个 AnimationTree、仅手动推进、线性循环、关闭采样插值跨界、root_motion_local=false。生成一个根骨，无网格或外部动画资产。各输出对照值次序是 [运动增量x, accumulator x]；输出量化到 0.00001。没有验证该构建来源与公开 4.6 分支字节等同，也没有运行引擎角色碰撞、混合、根旋转、事件或 seek。

```sh
set -e
sh run.sh > /tmp/gl-motion-one.json
cmp /tmp/gl-motion-one.json observed.json
sh run.sh partitioned > /tmp/gl-motion-steps.json
cmp /tmp/gl-motion-steps.json partitioned-observed.json
```

两种长帧处理从一致的相位 0.25 开始、都推进 4.5 秒。前者取一次引擎根增量；后者将每次引擎根增量相加（该试件所有运动沿同一轴且无旋转）。都实际运行两次并逐字节比较。若其他 Godot 版本给出不同结果，应独立确认用的时长、采样和取值，不强制当成相同实现。

## 精确二维刚体试件

```sh
python3 -B check_unwrapped_rigid.py > /tmp/gl-motion-rigid.json
cmp /tmp/gl-motion-rigid.json rigid-observed.json
```

列向量，乘法先做右侧；刻意选择非零起点、离散相位和整 90° 转向，用整数检查连续时间表示在离散采样时的区间组合、反向和整圈合成。没有模拟动作曲线插值、碰撞、时间量化或引擎旋转抽取。数学结果和原生平移对照不能彼此替代。
