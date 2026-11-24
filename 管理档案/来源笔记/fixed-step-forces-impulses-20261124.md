# 固定物理步中的持续推力与一次冲量：来源记录

固定上游源码为 Erin Catto 的 [Box2D 178495ba35695aefe9c321e569d2277f06db3b90](https://github.com/erincatto/box2d/tree/178495ba35695aefe9c321e569d2277f06db3b90)，源码自报 3.2.0。

- [公开 API 注释](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/box2d.h#L467-L526)和[持续力/冲量指南](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/docs/simulation.md#L579-L605)区分单位、持续施加与一次调用。
- [body.c 的质心力与冲量接口](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/body.c#L987-L1107)：启用、动态、醒着；可唤醒；力加到累加量，冲量直接写速度并检查上限。
- [physics_world.c 的外层步](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/physics_world.c#L946-L962)、[solver.c 积分](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/solver.c#L61-L83)、[子步循环](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/solver.c#L1088-L1106)、[清除](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/solver.c#L619-L629)及[完成求解后的 finalize](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/solver.c#L1619-L1668)：实际子步时长参与速度积分，正时长外层步收尾清除。
- 一次冲量与持续力的动量和时间步表达是本文推导；频率/子步对照来自[原生 Box2D 与教学模型](../实验/固定物理步的力与冲量/README.md)。事件分配是应用层策略，不是 Box2D 的功能。
- 先前同题在支持资料路径，为源码说明及手算。移入正式专题后增加了原生测量与排查步骤；旧路径保留跳转，不保留重复正文。
