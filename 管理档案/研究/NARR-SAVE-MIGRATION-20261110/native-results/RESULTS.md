# 固定 ink C# 原生观察

固定源码提交：35c63e52f1d36060930dc7ed3cfba38ea224b528。SDK 8.0.428，runtime / reference pack 8.0.34。采用独立 Roslyn 编译，不代表上游原 netstandard 项目验证。

| 运行 | 输入及断言版本 | 退出与范围 |
| --- | --- | --- |
| direct-roslyn-20261111T025759Z | 扩展版 false，错误预测同名值仍为 bool | 1；保留实际失败，此轮未获得直接继续文本 |
| direct-roslyn-20261111T025948Z | 最终版 false，按字段有无预测类型 | 0；直接算术1且仅公路，映射后算术1且桥/公路 |
| direct-roslyn-20261111T030108Z | 最终版 true | 0；直接算术2且仅公路，映射后算术11且桥/公路 |

最终两轮共同覆盖显式 bool 与省略默认值两条分支。每轮 Program.cs、inputs、artifacts、trace、命令及构建/退出记录均保留；环境路径脱敏见 [公开包说明](../README.md)。历史失败没有清零或改断言。原项目构建曾在 NuGet-Migrations 首启因 IOException 失败，独立 Roslyn 构建不是修好原项目，不据此宣称 netstandard 可移植性。

固定 seed 235 的有限轨迹在故事序列长度或路径变化时不同，不构成普遍概率结论。四类本地 mock 出口（external、observer、tag、text）未隔离两轮合计库存80，隔离候选只记录 plan、库存0；这不是生产奖励服务或持久化原子事务。

[复现与摘要核验](../README.md)
