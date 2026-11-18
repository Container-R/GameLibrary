# AI 主持误交棒的来源与边界

核读日期：2026-11-18。本文案例是 2026 年 11 月的历史变更，不推断当前托管版本。

1. Open Game Master [#769](https://github.com/Lebbitheplow/open-game-master/pull/769)，贡献者开头说明及单后端表格。动作结算曾一律推进；改后玩家指挥的同伴由 End Turn 或主持工具交棒，主持代管路径另行处理。报告 16/16→0/16，只涉及该场景，非百分比预测。
2. Open Game Master [#872](https://github.com/Lebbitheplow/open-game-master/pull/872) 的故障、修订与 Checks；[固定合并提交](https://github.com/Lebbitheplow/open-game-master/commit/99ae54a9e9a63638c77087e9a8529bbb95b3f444)。实际读取 src/lib/dm/claims-logic.ts 204–229、457–462，匹配引用片段的各处语句，仅问句时过滤；claims.ts 139–200，按 request_player_input 对象和同伴指挥者本人角色识别等待，另有英文规则；narration-guard.ts 98–112，等待时返回 handedOn=null。报告 gpt-oss-20b 的八条意大利文和英文 × 三次阅读，24/24 对旧版 23/24；旧版错误发生在意大利文 Dash，问题句故障来自另有报告的桌。问句标点含全角问号不等于实测中文语言理解。
3. Open Game Master [#888](https://github.com/Lebbitheplow/open-game-master/pull/888) 的 What was wrong / The cause / The fix，记录 0.34.1 的直接主持工具路径，修订只在英文措辞规则中识别某些否定；不推断全部语言已能区分否定和明确交棒。该路径与 #872 的阅读判断应分别验收。

原创建议是由可信入口标明当前操作者的确认权；较严格方案并不是声称上游只允许玩家点击。顺序对照仅绑定本文实验 `管理档案/实验/AI主持的战斗回合/`。
