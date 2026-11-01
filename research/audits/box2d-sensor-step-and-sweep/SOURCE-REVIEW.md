# TASK121 独立来源审查

日期：2026-11-01。结论：**接受限定版本、独立来源笔记方案**。审查 gate SHA256：`549f202739ef647fb5dc56de362665bc5cfa820b783229b46afc9e78b99c199b`。仅建议新增 `research/source-notes/box2d-sensor-step-and-sweep.md`；不改写既有 fixed-step 文章，不继承任何其他引擎实验结果。

## 独立打开的来源与身份

- 官方 tag 接口核对 `v3.1.1` 直接指向 `8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3`。
- 在该固定提交直接读取 [simulation.md](https://github.com/erincatto/box2d/blob/8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3/docs/simulation.md#L922-L956) Sensors 922–956、[world.c](https://github.com/erincatto/box2d/blob/8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3/src/world.c#L695-L793) 695–793、[sensor.c](https://github.com/erincatto/box2d/blob/8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3/src/sensor.c#L47-L186) 47–106/135–186、[solver.c](https://github.com/erincatto/box2d/blob/8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3/src/solver.c#L212-L245) 212–245/425–450。
- 新固定快照 `dd8bd3fb525f0f33f1079f8ca3c5770783c44a53` 的提交接口显示日期 2026-10-30；直接读取 [simulation.md](https://github.com/erincatto/box2d/blob/dd8bd3fb525f0f33f1079f8ca3c5770783c44a53/docs/simulation.md#L1071-L1103) 1071–1103 和 [solver.c](https://github.com/erincatto/box2d/blob/dd8bd3fb525f0f33f1079f8ca3c5770783c44a53/src/solver.c#L138-L312) 138–312、358–425、542–550、1935–1964。
- 独立打开[滚动官方 Simulation 页](https://box2d.org/documentation/md_simulation.html)：当前页面标题标示 Box2D 3.2.0，Sensors 段明确描述静止 sensor 的快速穿越支持。页面标签不是该固定提交对应已发布版本的证明，也未核验网站部署提交或功能首次引入版本。

## 支持的机制与必须相邻保留的限定

1. **历史 v3.1.1**：正常正时间步路径把 substep 参数交给求解器，求解返回后仅调用一次 sensor overlap。后者按当前变换做距离判断；连续路径在候选端及 fast-shape 端排除 sensor。因此增加求解 substeps 并没有在这条代码路径加入每子步 sensor 检查；bullet 也不会解除这两处排除。
2. **新快照**：候选 sensor 可进入连续路径，但须通过双方事件开关、形状/身体过滤及适用的其他筛选。TOI 候选先按 `<=` 当前 solid fraction 暂存，最后只把 `<` 最终 fraction 的项转交。fast shape 自身为 sensor 仍跳过。不能把候选 AABB、TOI 暂存项和最终 begin/end 交付混为一谈。
3. 容量 8 是该 `b2SolveContinuous` 调用的连续 context 暂存数组限制：context 在身体的 shape 遍历之前创建，并非“每个 sensor 可无限接收”或已证明按距离保留最近八项。正文如提容量，应保留这个局部范围，不推演具体漏报数量。
4. 新文档对非移动 sensor 的支持必须和旧版限制一起呈现；不接受“当前 Box2D sensor 都无 CCD”。也不从 bullet 扩展查询树推得任意移动 sensor 的可靠性。

## 原创情景与介入决策

两端分离而中间穿越的静止区域/直线平移圆形情景，是在既定实际轨迹、事件启用、过滤允许、无阻挡改道前提下对**旧版步末占用测试**的逻辑反例；没有观察到实际运行，也不是新版静止 sensor 路径的反例。增大 substeps 可能改变求解轨迹，因此不得额外声称任意配置下最终姿态完全不变。

新增价值是明确选择占用检测、已存在的引擎连续检测，或显式体积扫掠的责任，而不是重复“固定步并非万能”。更细 world-step 采样仍需速度/几何条件；中心射线不等于圆形体积；冻结移动目标做单次 cast 不能自行证明相对运动覆盖。暂不主张事件顺序、准确交付步、全部后处理或伤害正确性。本轮未逐条验证完整 ray/shape-cast API 使用协议，不能据此发布可运行查询实现。

无代码执行、构建、物理测试、运行档案读取、既有文章改写或远端写入。
