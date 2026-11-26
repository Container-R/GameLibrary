# 技能充能：固定源码及可重复对照

- [SimulationCraft 固定版本 `cooldown.cpp`](https://github.com/simulationcraft/simc/blob/568a1cba25697a0ee254ee707dfe0759e603555f/engine/sim/cooldown.cpp)。第 15–45 行：事件只补一格，未满才再排；第 428–493 行：已有事件时再消耗只递减格数并在耗空时更新就绪时机，该分支不会新建恢复事件；首次进入多格充能才建立事件。由此确认正文提到的**串行状态结构**，不是在线游戏的实现或本文规定的同刻处理顺序。
- [同文件第 569–596 行](https://github.com/simulationcraft/simc/blob/568a1cba25697a0ee254ee707dfe0759e603555f/engine/sim/cooldown.cpp#L569-L596)：多格的 `recharge_time` 读活动事件剩余，`full_recharge_time` 另加后续缺失格的时长。来源支持两类查询含义分开，不是成品 HUD 的设计证据。
- [固定时长复现实验](../实验/技能充能恢复/README.md)实现并对照正文的两种产品规则，以及同刻、赶进度、拒绝和满格边界。两格在 0、2 秒耗尽时，3 秒的下一格同为 7 秒，串行和独立的补满时间分别是 17 秒和 9 秒。动态速率说明是设计取舍与算术示例，不是该模型的被测功能。
