# 程序化随机流：来源和证据

- Unity 6000.0 [UnityEngine.Random](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityengine/random)，Static vs instanced：共享静态状态，独立实例是不同的设计。没有运行 Unity，不沿用文档性能范围作为本文结论。
- Godot 4.6 [RandomNumberGenerator](https://docs.godotengine.org/en/4.6/classes/class_randomnumbergenerator.html)：seed 初始化、state 仅恢复为曾保存的有效状态、相似种子与算法实现边界。此处只采用按职责分配的不同实例，不用实现细节号称所有引擎跨版本保序。Godot 4.6.3 实际运行验证整数采样与状态还原；合成场景没有搭建真实地图或任务线程。
- Salmon、Moraes、Dror、Shaw，[Parallel Random Numbers: As Easy as 1, 2, 3](https://thesalmons.org/john/random123/papers/random123sc11.pdf)，SC11 §§1–2，式 (2)、(3)：由计数／键直接计算对应随机数，工程应避免全局先后分配重新引入顺序。没有运行 Random123，也没有进行均匀分布、相关性或密码用途测试。
- [取证脚本](../实验/程序化随机流/README.md)：Python 3.12.14 随机实例的合成地图、稳定顺序、固定编码向量，和 Godot 的原生采样分别供复跑。共享状态更改只在固定测试点对照，随机分流不证明稳定拓扑求解或跨块资源仲裁。
