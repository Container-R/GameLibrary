# Box2D 传感区域：检查当前占用，还是检查一步内经过？

2026-11-01。本文是固定官方文档与源码的有限分析，附原创未执行几何情景；没有运行 Box2D、生成运动轨迹或观察事件。**求解器子步更多，不自动等于传感器沿路径检查得更密。** 但也不能据历史版本宣称当前 Box2D 的 sensor 都没有连续检测。

## 先把游戏规则写成检测问题

“仍站在恢复区内”与“这一段运动经过检查线”需要不同信息。前者询问某时刻的占用，后者询问时间区间内的路径。将二者都命名为触发器，并不能决定检测方法。

**原创假设：**一个圆形对象直线平移，实际路径从静止窄区域左侧穿到右侧，步首和步末都与区域分离；必要事件开关已开启、过滤允许，没有其他阻挡改变路径。这不是已经发生的漏报。它只说明：两个端点的重叠结果不足以回答中间有没有经过，增加内部求解次数也必须先问是否改变了传感器的观察位置。

## v3.1.1：子步求解之后才检查 sensor

官方 **v3.1.1** 固定于 `8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3`。正常正 timeStep 路径中，`subStepCount` 进入求解上下文；整个求解返回后，`b2World_Step` 调用一次 `b2OverlapSensors`。窄相查询用当前形状变换计算距离，并非扫掠完整路径；连续碰撞路径还排除了候选 sensor 和自身为 sensor 的 fast shape。[步函数](https://github.com/erincatto/box2d/blob/8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3/src/world.c#L695-L793)、[重叠查询](https://github.com/erincatto/box2d/blob/8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3/src/sensor.c#L47-L106)、[连续路径](https://github.com/erincatto/box2d/blob/8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3/src/solver.c#L212-L245)及[fast shape 排除](https://github.com/erincatto/box2d/blob/8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3/src/solver.c#L425-L450)。

该版 [Sensors 文档](https://github.com/erincatto/box2d/blob/8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3/docs/simulation.md#L922-L956)也明确限制一步内穿越检测。因此，在上述历史版本的假设中，仅增加 solver substeps 或启用 bullet，不能把步末重叠变成路径检测。这里不声称这些设置完全不影响运动结果；结论是它们没有因此建立所需的 sensor 扫掠路径。

## 新 main 快照：非移动 sensor 已有连续路径

另固定官方 main 提交 **`dd8bd3fb525f0f33f1079f8ca3c5770783c44a53`**（2026-10-30），不将它命名为发布版本，也不认定滚动网站与它逐字对应。其 [Sensors 文档](https://github.com/erincatto/box2d/blob/dd8bd3fb525f0f33f1079f8ca3c5770783c44a53/docs/simulation.md#L1071-L1103)说明快速形状经过静止 sensor 可以检测，对快速移动 sensor 仍保留可靠性限制。

源码也不再无条件排除候选 sensor：事件开关与过滤满足后，连续路径可记录 sensor hit；所读暂存容量有限，最终仅转交早于最终 solid hit 的项。[候选与容量](https://github.com/erincatto/box2d/blob/dd8bd3fb525f0f33f1079f8ca3c5770783c44a53/src/solver.c#L138-L215)、[记录](https://github.com/erincatto/box2d/blob/dd8bd3fb525f0f33f1079f8ca3c5770783c44a53/src/solver.c#L295-L312)、[转交](https://github.com/erincatto/box2d/blob/dd8bd3fb525f0f33f1079f8ca3c5770783c44a53/src/solver.c#L542-L550)。这不是把 sensor 变成阻挡物，也不是无限数量、任意轨迹完整捕获的保证。

所以前面的静止区域情景**不能被移用为新版连续路径的漏报反例**。同样，[fast shape 本身为 sensor 仍被排除](https://github.com/erincatto/box2d/blob/dd8bd3fb525f0f33f1079f8ca3c5770783c44a53/src/solver.c#L358-L425)，不能只看到 bullet 查询更多树，就宣称移动 sensor 已普遍可靠。本次未定位首次引入这一变化的发布版本。

## 原创接收决定：由哪条路径负责“经过”？

选择检测方法之前，玩法与物理接收者应先完成三个具体决定，而不是先把 substeps 调大：

1. **明确规则量。** 是步末仍占用，还是区间内曾经过？若是穿越，参与判定的是圆形体积还是中心点？中心射线不是有体积对象的自动替代。
2. **选择实际存在的检测路径。** 在新快照文档支持的非移动 sensor 情况下，可将引擎连续路径作为待验证方案，不必无条件再造一套查询；在所用版本覆盖之外，则明确由游戏查询层负责扫掠与结果归并。把 world step 分得更细是另一种采样策略，不等同于增加 solver substeps，仍需几何与速度条件，不能承诺必不漏报。
3. **定义有限验证。** 对静止区域与直线平移，先规定起止形状、过滤、初始重叠及同一路径多个结果的处理，再检查 shape cast 或所选引擎事件是否回答这个规则。若目标也移动，必须说明相对运动和时间区间；冻结目标做一次 cast 不是已经证明的修复。

旧版 [Ray-casts / Shape-casts](https://github.com/erincatto/box2d/blob/8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3/docs/simulation.md#L1744-L1834)提供查询入口，不能据此假定结果天然按路径顺序到达或任意运动都被覆盖。上述接收步骤未执行，没有完整触发／伤害算法、begin/end 排序或交付帧保证。

## 旋转形状：中心位移不是完整扫掠输入

另看发布标签 **v3.2.0** 的固定提交 `178495ba35695aefe9c321e569d2277f06db3b90`：`b2ShapeCastPairInput` 给出初始相对变换与 `translationB`，`b2CastShape` 描述的是线性移动；它没有用这个平移量表达形状随时间转动。带旋转的 `b2Sweep` 是不同的运动输入，而官方 TOI 文档仍明确保留旋转碰撞可能漏检的限制。[接口与 sweep 定义](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/collision.h#L435-L490)、[TOI 的旋转限制](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/docs/collision.md#L266-L296)。

**原创、未执行的几何反例：**胶囊体的中轴端点为 (−1, 0)、(1, 0)，半径 0.02；中心固定，在平面内绕中心逆时针连续旋转 90°（方向角从 0° 到 90°）。静止圆的中心为 (√2/2, √2/2)，半径 0.05。起点和终点，圆心到中轴线段的最近距离都是 √2/2，大于半径和 0.07，两形状分离；旋转经过 45° 时，圆心恰在中轴正向端点，两形状相交。

整段运动的中心平移为零。若只提交初始姿态与零平移，线性 cast 的输入就没有表示上述旋转。这里证明的是**运动表示缺项**，不是已经观察到 Box2D TOI、world step 或 sensor 漏报；也没有推定一次查询会返回什么，更不把该几何旋转等同于引擎中的恒定角速度轨迹。

因此，对旋转武器或细长判定体，接收方先要决定规则关心的是中心路径还是整个形状扫过的区域。若是后者，不能用“中心没有移动”的线性查询替代旋转路径；若改用含旋转的连续检测，还须保留该版本的限制，另行验证项目关心的运动。这个反例既不给出安全子步数，也不证明某个旋转查询算法能够完整捕获所有经过。

本题与[固定 Tick 的模拟边界](../../solutions/programming/fixed-step-simulation-boundary.md)相邻，但那里的模型与 Godot 观察不能验证 Box2D 的本条路径。这里仅新增版本明确的检测选择依据，不继承其运行结果，也不证明跨引擎碰撞正确性。
