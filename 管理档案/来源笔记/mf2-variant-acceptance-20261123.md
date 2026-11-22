# MF2 译文分支验收：证据

| 主张 | 一手资料或实际运行 | 边界 |
| --- | --- | --- |
| 比较可匹配的变体时先比较前面的选择器；变体行位置不决定本例的优先级 | [Unicode UTS #35 Part 9，CLDR 49，Pattern Selection](https://www.unicode.org/reports/tr35/49/tr35-messageFormat.html#pattern-selection)，Compare Variants、SelectorsMatch、SelectorsCompare。 | 两列字符串及星号；无复数选择。 |
| 可显示专门提示或全星兜底，同时有错误 | [messageformat 4.1.0](https://github.com/messageformat/messageformat/releases/tag/messageformat%404.1.0)，[选择逻辑](https://github.com/messageformat/messageformat/blob/439fb0c/mf2/messageformat/src/select-pattern.ts)，Node 24.22.3 实跑。 | 该版缺参、不可选择和未注册函数的错误类别不同，不泛化为其他实现的 API。 |
| 标签替换移除了正文内插值，构造错误与回调诊断不同 | [原生对照](../实验/MF2译文分支验收/README.md)，输出末两项。 | 合成输入；不检验玩家界面、自然语言质量和语言资源回退。 |

调阅日期：2026-11-23（北京时间）。
