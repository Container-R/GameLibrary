# 断续心跳的游玩时长：证据与边界

## 原始资料（2026-11-21 核对，北京时间）

- Android Developers，[The activity lifecycle：onPause / onStop](https://developer.android.com/guide/components/activities/activity-lifecycle#onstop)：Paused 在多窗口中仍可能可见；Stopped 对应 Activity 不再可见。应用的可交互玩法状态与上传成功是不同层次；生命周期事件参与指标状态判断，不直接测量人的注意力。
- Android Developers，[SystemClock](https://developer.android.com/reference/android/os/SystemClock)：`elapsedRealtime()` 是开机后的单调计时、含深度睡眠；`uptimeMillis()` 不含深睡。不能把这些设备各自的起点当成共同业务时钟。正文 UTC 锚点和误差政策是工程建议，不是 Android 自带跨设备精确对齐的保证。
- Apache Beam，[Programming Guide §8.4 Watermarks and late data](https://beam.apache.org/documentation/programming-guide/#watermarks-and-late-data)：区分事件时间、处理时间和迟到；水位线是对输入完整性的进度判断，保留期限和重新输出策略另行设置。正文以账号日替换重算，不声称已经部署 Beam。
- Unity Analytics，[FAQ：Events](https://docs.unity.com/en-us/analytics/faq#events)：Event Browser 可能看到因网络确认失败而重送的记录。事件 ID 重用及业务载荷冲突隔离是正文建议，没有复现 Unity 的接收和去重实现。

## 推导与观察

合格状态、20 秒示例采样、30 秒衔接阈值以及无支持尾部的两档是本文示例政策。账号秒按多个设备流区间的并集计算；设备秒按设备分别并集后求和。[实际执行的合成事件试件](../实验/断续心跳的游玩时长/README.md)只验证这些定义的输出，不验证平台事件质量、真实时钟偏差或玩家行为。
