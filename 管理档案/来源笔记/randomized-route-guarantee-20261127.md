# 随机结果的可达性：来源与证据范围

- TU Braunschweig，[Games with Perfect Information](https://www.tu-braunschweig.de/fileadmin/Redaktionsgruppen/Institute_Fakultaet_1/TCS/Lecture_Notes/games.pdf)，§4 “Attractor”、定义 4.6。讲义对两类顶点使用不同的可控前驱条件，迭代得到有界步数的吸引域与能获胜的位置。正文的单位步把「玩家选行动」和「该行动结果」合在一起；先选择一个动作，再检查其所有可能结果。这是对该构造的合步表达，未直接引用讲义的步数。
- PRISM 模型检查器，[The P Operator](https://www.prismmodelchecker.org/manual/PropertySpecification/ThePOperator/)，Nondeterminism、Numerical Properties、Time-Bounded Path Properties。`Pmax` 在允许策略中取最大概率；离散时间下界限按转移计数。仅当转移的粒度、控制权与概率对应时，这个查询才回答文中验收问题。模型未实际提交给 PRISM。
- [自建有限模型](../实验/随机路径的步数保证/README.md)独立跑出三类验收和固定坏结果的反例；独立重复的成功率由几何公式给出，不是游戏实测。
