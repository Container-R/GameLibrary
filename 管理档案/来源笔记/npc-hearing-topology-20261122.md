# 虚构关卡的 NPC 听觉：来源及范围

| 主张 | 一手材料及位置 | 能支持的范围 |
| --- | --- | --- |
| 游戏事件按事件半径、优先度和 NPC 状态等作反应；按区域与连通点估算声音距离 | Martin Walsh，[Modeling Perception and Awareness in Tom Clancy’s Splinter Cell Blacklist](https://www.gameaipro.com/GameAIPro2/GameAIPro2_Chapter28_Modeling_Perception_and_Awareness_in_Tom_Clancy%27s_Splinter_Cell_Blacklist.pdf)，Game AI Pro 2，第 28 章，§28.3.1 及 §28.4.1，约印刷页 317–321；式 28.1 和 A→B→C→D 例。同区取欧氏距离，跨区先取区域序列，再选择靠近上一点的 choke 并累加线段。 | 作者称近似；文中另给自主设计的带权连通图。原作材料不证明本文的开关门代价、全局最优连接口链、延迟、现实声学、缓存或其它引擎行为。 |
| 画外反应应有用户可察觉的缘由；话语由具体逐渐泛化 | Walsh，同章 §28.4.2 Auditory Detection Fairness，印刷页 321–322。正常镜头缺少自由镜头看到的上下文；缩减满足条件的某些画外事件的听觉，并通过反应台词指出声音。 | 不外推屏幕外全静音；不假定减半的是哪一个内部数值或实际半径。没有实施玩家研究。 |
| Unreal 5.8 提供游戏噪声事件机制及可见输入 | Epic Games，[FAINoiseEvent](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/AIModule/FAINoiseEvent?application_version=5.8)，Variables；地点、响度修饰、最大范围、标签，以及未显式传入时的参数说明。 | 核对的仅是接口。不推测默认 AI 听觉的遮挡，未运行 Unreal；Loudness 不是本文可与门代价相加的物理分贝。 |
| 同直线距离不等于相同判定，听觉图和步行图用途不同 | [Node 合成房间复现](../实验/虚构关卡的NPC听觉/README.md)，同一张图在开关门和通风口、预算变更下的输出。 | 仅是游戏系统可测逻辑，不是音频引擎结果、多人生产性能或声学测试。 |

调阅日期：2026-11-22。
