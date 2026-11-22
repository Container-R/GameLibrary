# 任务目标的既有事实：来源与边界

| 主张 | 原始材料 | 使用范围 |
| --- | --- | --- |
| 对话宿主可共享变量，变量状态与对白当前位置要分别保存 | Yarn Spinner for Unity [Variables and Storage](https://yarnspinner.dev/docs/unity/05-connecting-to-your-game/04-variables-and-storage/)，Variable Storage、Saving and loading。 | 说明变量与执行位置职责，不推断 Yarn 自带任务过往规则。 |
| 目标分派、跨次存储的载入和完成通知分别配置 | Epic Games [Fortnite Creative Tracker Devices](https://dev.epicgames.com/documentation/fortnite/using-tracker-devices-in-fortnite-creative#direct-event-binding)，Functions 与 Events。 | 是设备接口与职责示例，没有执行设备测试，也不推断载入是否会按特定条件产生完成事件。 |
| 当前持有、历史事实、开始后的行动互不等价 | [本库合成实验](../实验/任务目标的既有事实/README.md) 实际读取三种字段；有同模拟步换序、历史未知和读档重放。 | 自建单人条件示例，并非实际产品表现；只有同一有序流、固定对象和范围，且没有模拟异步演出或真实持久化事务。 |

资料查阅于 2026-11-22。
