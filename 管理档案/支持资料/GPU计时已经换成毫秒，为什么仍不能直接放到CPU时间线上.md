# GPU计时已经换成毫秒，为什么仍不能直接放到CPU时间线上

一段渲染工作测出3毫秒，程序员又在提交命令时记录了一个CPU时间戳，想把两者画到同一张性能图上。把两个数都换成毫秒之后，图中GPU工作却像是在提交以前就完成了。

单位相同，不代表起点相同。**测一段工作有多久，与判断它发生在CPU时间线的哪里，是两次不同的换算。** 本文面向编写图形性能工具的程序员，以Windows上的Direct3D 12为具体接口说明；数字全部是原创纸面例子，没有运行显卡或测量延迟。

## 先算同一把尺子上的间隔

D3D12的GPU时间戳读数是计数器刻度，不是毫秒，也不能拿显卡标称主频来换算。`GetTimestampFrequency`返回相应命令队列的时间戳频率，单位是每秒多少刻度。[1][2]

假设一份直接队列（Direct queue）命令列表中的两个有效时间戳分别为：

- 开始标记 `G1=5,004,000`；
- 结束标记 `G2=5,010,000`；
- 该队列的时间戳频率 `fg=2,000,000` 刻度/秒。

两个标记之间差6,000刻度，因此间隔是 `6,000 / 2,000,000 = 0.003秒`，即3毫秒。这里假定结果有效、没有计数器回绕，且两点处于可比较范围；不能换成另一队列的频率。实现时也不能先做整数除法，把不足一秒的结果截成0，再乘1000。

这一步只用了差值，所以计数器从哪里起算并不影响答案。但若把 `G1/fg=2.502秒` 直接放到CPU记录旁边，原点问题就出现了：它不是“应用启动后2.502秒”，更不是墙上时钟的某一刻。

## 用对应的时刻把两把尺子接起来

CPU侧常用的`QueryPerformanceCounter`，简称QPC，也返回自己的计数；它的频率由`QueryPerformanceFrequency`独立取得，不能假定与GPU队列的频率相同。[3] D3D12的`GetClockCalibration`提供一对在近乎同一时刻采样的GPU与CPU读数，用来建立关联。[1][4]

继续这个假设例子，设校准得到 `G0=5,000,000` 和 `C0=90,000,000`，CPU频率为 `fc=10,000,000` 刻度/秒。先把校准时刻当作图上的0毫秒，并假定这个短区间内关联保持有效：

| 记录 | 相对校准时刻的计算 | 图上的位置 |
|---|---|---:|
| CPU提交标记 C=90,010,000 | `(C-C0)/fc` | 1毫秒 |
| GPU开始标记 G1=5,004,000 | `(G1-G0)/fg` | 2毫秒 |
| GPU结束标记 G2=5,010,000 | `(G2-G0)/fg` | 5毫秒 |

现在3毫秒的GPU区间放在了2至5毫秒，而不是把GPU计数的绝对商2.502秒与CPU计数的绝对商9.001秒硬相减。后两者虽同为秒，却没有先对齐起点。

若工具内部需要CPU刻度，等价写法是 `C估计=C0+(G-G0)×fc/fg`。本例两个GPU标记分别对应90,020,000与90,050,000个CPU刻度。这个式子是两种刻度比例和校准点的推导，不是忽略误差后自动成立的永久同步保证。大整数相减、乘法溢出、转换精度和负差值都需在实现中处理；不要把这行数学式当作可直接粘贴的完整计时器。

## 对齐了标记，仍要问标记代表什么

微软把D3D12时间戳查询描述为管线末端操作：GPU完成它之前的工作时才采样。[1] 因此，上表CPU标记与第一个GPU标记之间的1毫秒，只是这两个观测点的间隔，不能自动命名为“调度器等待”。还要知道CPU标记放在哪里、提交中有哪些先行工作、两个GPU查询之间实际夹了哪些命令。

同理，3毫秒不是屏幕已经显示结果所需的时间，也不必等于某一个着色器独占硬件的运行时间。多个队列是否重叠、其他工作怎样竞争，以及呈现和扫描何时发生，需要另外的观测。回到[交换链与呈现队列](../../GameLibrary/图形渲染/画面呈现/输入延迟/交换链和呈现队列怎样影响输入延迟.md)时，应保留这些未测阶段，而不是把图上空白一律归给GPU。

## 校准不是一次取得、以后永远不变

Timing文档提示，某些硬件空闲时GPU时间戳时钟可能停止，关联便会漂移。Queries文档进一步区分同一命令列表内的两个时间戳，与跨命令列表且可能发生空闲的比较。[1][5] 本例特意把两个区间标记放在同一命令列表，并另行假定校准关联有效；真实采集仍须检查该条件，不能用一对很早的校准值解释整场游戏。

文档提到的`SetStablePowerState`是开发期工具，不该在已发布应用的正常运行中开启。它可能把GPU固定在较低频率，改变整个系统的性能条件；稳定状态下的设计比较还需用真实使用场景复核。[6] 解决计时关联问题，不等于已经测到了玩家机器日常负载下的帧耗时。它不适合作为发行版计时器的默认开关。

接入时，可以先保存队列身份、成功取得的频率、校准点、原始计数与标记语义，再生成可读的时间轴。时间戳查询使用`EndQuery`而不是一对`BeginQuery/EndQuery`；解析结果、资源状态以及CPU何时可以读取，还要遵守查询和同步规则。[5][7] D3D12的`Map`本身不会等待GPU写完；读回缓冲可访问，不代表本次结果已经就绪，应通过fence等同步确认对应写入完成。[8] 检查失败或没有有效结果时保留缺失，别把默认0画成一次零耗时工作。

## 参考来源与范围

2026-11-05阅读以下Microsoft原始文档。采用的是当日公开文档，不代表已核某个驱动或Windows安装；没有创建D3D12设备、执行查询、测量GPU或改变电源状态。本文只说明计数换算、时间轴关联与观测范围，不提供完整查询缓冲生命周期实现。

1. [Timing (Direct3D 12 Graphics)](https://learn.microsoft.com/en-us/windows/win32/direct3d12/timing)，页面标注更新2026-08-19；读取Timestamp frequency、Timestamp calibration、Timestamp queries。区分刻度、管线末端采样与漂移。
2. [GetTimestampFrequency](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12commandqueue-gettimestampfrequency)，更新2024-02-22；参数、单位与返回值。
3. [Acquiring high-resolution time stamps](https://learn.microsoft.com/en-us/windows/win32/sysinfo/acquiring-high-resolution-time-stamps)，读取导言和Using QPC in native code的计数及频率换算，未据此全面审查各Windows历史版本。
4. [GetClockCalibration](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12commandqueue-getclockcalibration)，更新2024-02-22；成对计数参数，与Timing的近同时采样说明合读。
5. [Queries](https://learn.microsoft.com/en-us/windows/win32/direct3d12/queries)，更新2022-04-12；时间戳可比范围、查询类型及提取方式。
6. [SetStablePowerState](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12device-setstablepowerstate)，更新2024-02-22；Remarks的开发期用途、低频影响与真实使用场景复核要求。
7. [ResolveQueryData](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12graphicscommandlist-resolvequerydata)，更新2021-10-13；读取参数与Remarks，包含未初始化/未完成查询风险及时间戳64位结果。没有运行页面的遮挡查询样例。

8. [Read back data via a buffer](https://learn.microsoft.com/en-us/windows/win32/direct3d12/readback-data-using-heaps)，更新2021-12-30；读取开头读回要求，尤其fence与Map的职责，未运行截图示例。

---

[返回输入延迟正文](../../GameLibrary/图形渲染/画面呈现/输入延迟/交换链和呈现队列怎样影响输入延迟.md)
