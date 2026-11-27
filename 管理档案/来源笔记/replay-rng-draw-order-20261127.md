# 重放的随机取数顺序：一手来源

- [正式正文](../../GameLibrary/玩法程序/玩法系统/时间与模拟/同一个随机种子，为什么重放还是抽到了不同奖励.md)；[Godot 试件及运行记录](../实验/重放与随机取数顺序/README.md)。
- Riot Games，[Determinism in League of Legends: Implementation](https://www.riotgames.com/en/news/determinism-league-legends-implementation)，2017，Random Number Generators。作者明确指出调用顺序、次数和初始种子都影响可复现性，并为游戏规则统一使用受控 API。该项目的具体 PRNG 整理不等价于本文示例的流拆分。
- Godot 4.7，[RandomNumberGenerator](https://docs.godotengine.org/en/4.7/classes/class_randomnumbergenerator.html)，类说明、seed 与 state。底层算法不是 API 承诺；写 seed 会重置内部状态，先 seed 后 state；state 只恢复从真实实例读出的值。
- 原创可控试件使用 Godot 4.7.2 官方构建 `ed1daf0bf` 在本机 headless 运行。`randi()` 是观测对象；打印逐事件状态，两个影响规则的流先取一次再对照检查点。外层仅按固定顺序直接调用，不跑场景动画、物理、网络或真实重放系统。取模仅演示映射丢失区别，不提供概率保证。
