# 玩法迁移重放：来源与观察

正文问题：用同一输入重放验收小块规则，定位第一次行为分歧。已有《用固定时间步组织战斗模拟》讨论如何安排模拟与输入，《从〈卡拉克沙漠〉看玩法模拟与引擎表现的交接》讨论表现接收器的验收；本题不再重述调度器，也不把接收器错误归为规则错误。引用检索于 2026-11-19 UTC。

| 一手来源与定位 | 直接支持 | 本文新增推导或限制 |
|---|---|---|
| [Riot，Determinism in League of Legends: Implementation](https://www.riotgames.com/en/news/determinism-league-legends-implementation)，2017-06-20，Validating Determinism、Recording Inputs、Time 与 Random Number Generators | 优先对照玩法关键状态，按服务器接收顺序记录网络输入和其他不可消除输入；保留并记录可变帧间隔；随机数的调用顺序、次数及初始种子均可造成分歧 | 该团队为服务器失效恢复做确定性验证，并非跨语言迁移。本库按步比较三个阶段的做法依赖确定的比较边界，不是 Riot 的日志格式。 |
| [C++ 委员会工作草案，expr.mul](https://eel.is/c++draft/expr.mul#4) 第 4 段；[C# 规范，§12.13.3、§12.13.4](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-specification/expressions#12133-division-operator) | 整数商截向零。对于可表示的商，除余满足 x = q·width + r；边界错误与两门语言默认取整不一致无关。 | 格定义 [kw,(k+1)w)，正 w 下 r < 0 意味着截向零的 q 偏大一格，修正 q−1；r=0 保留原 q。C++ 与 C# 的零除、整数溢出不是假定有相同语义。 |
| [Python 3.12 表达式参考 §6.7](https://docs.python.org/3.12/reference/expressions.html#binary-arithmetic-operations) | 对整数地板整除和正除数余数关系。 | 实验对照用 Python 整数，不把浮除后取整当作整个整数域的替代。 |
| [RFC 8259 §4–6](https://www.rfc-editor.org/rfc/rfc8259.html#section-6)、[RFC 7493 §2.2–2.3](https://www.rfc-editor.org/rfc/rfc7493.html#section-2.2) | JSON 数值语法不等于客户端表示保证；binary64 普遍接收器的安全连续整数区间；I-JSON 对大整数建议字符串，对象成员顺序不改变消息含义。 | 精确导出十进制字符串、以字段规定的整数类型直接解析；用数组表达顺序。Node 对照不是对一切 JSON 实现的判断。 |
| [RFC 8785 §3.1–3.2、附录 D](https://www.rfc-editor.org/rfc/rfc8785.html#section-3.1) | JCS 约束 I-JSON 数据、以确定的方法生成 JSON 字节，建议超双精度整数的值用字符串表示。 | 验收用摘要只覆盖选择的字段；需对照的是每步记录而非某段最后一帧。实验没有采用 JCS 或性能采样。 |

原创实验：[玩法迁移重放](../实验/玩法迁移重放/README.md)。Python 参考实现、实际编译运行的 C++ 两种政策、Node 的默认 JSON 解析在命令中统一取证。试件输入、状态和输出在观测文件中；没有 C# 运行、两款引擎或游戏网络实验。记录真实碰撞事实、规范化段摘要和检查点建议是工程方法，未在本试件实跑。
