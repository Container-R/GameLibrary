# 玩法模拟与表现交接：来源与验证

- Yossarian King（Blackbird Interactive），GDC 2017，[The Great Divide: Unique Visuals and Deterministic Gameplay in ‘Deserts of Kharak’](https://www.gdcvault.com/play/1024242/The-Great-Divide-Unique-Visuals)。[原始幻灯片](https://media.gdcvault.com/gdc2017/Presentations/King_Yossarian_TheGreatDivide.pdf)使用 PDF 阅读器 1 起算：第 48 页对照二维模拟与三维表现，第 69 页给出固定更新及模拟约束，第 71–72 页列出程序集依赖和单独 C# 线程，第 73–74 页画出命令、状态及事件与失步检测，第 77 页描述定点数学库。讲义没有完整事件身份合同、失步后的修复方法或完整的引擎迁移结果。
- [原创单线程 Node.js 试件](../实验/玩法模拟与表现交接/README.md)支持正文对照表。两种分片读出相同结果；按步号去重漏去 c2；在最后一次规则采样后写回使最终生命从 4 变成 −2。没有调用引擎、网络、实际音频或线程交接，不作为原游戏复现。
