# NPC 最后目击与有限搜索：来源和证据

- Epic Games [AI Perception in Unreal Engine 5.9](https://dev.epicgames.com/documentation/en-us/unreal-engine/ai-perception-in-unreal-engine)，Perception Events 及查询函数给感知成功、Stimulus Location / Receiver Location、Current / Known 及遗忘设置。未将引擎文档当作时序保证，不绑定其内部源代码或默认设置。
- Travis McIntosh [Human Enemy AI in The Last of Us](https://www.gameaipro.com/GameAIPro2/GameAIPro2_Chapter34_Human_Enemy_AI_in_The_Last_of_Us.pdf)，印刷页 424–425、426–427（§34.4 与 §34.6）。实际读源，下载 PDF 后看过图 34.8 的网格、传播边与 NPC 可视边界；引用此原版的搜索地图、独立检查位置和无明确目标的声音调查。未重分发原图。未从文献外推其回调排序、有效期、路径预算或本文的合成实现。
- [合成复现](../实验/NPC最后目击与有限搜索/README.md)由四个小例分别检查信息泄露、旧事件/对象世代、区域重进和任务生命周期。只代表单观察者、指定观测序列、注入导航状态下的机制。没有运行实际导航、商业游戏或实地定位。
