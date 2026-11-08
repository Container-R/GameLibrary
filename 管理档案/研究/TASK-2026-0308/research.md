# 设置页序列与异步检查点：有限研究笔记

状态：完成一轮研究，尚未形成正式文章或独立发表审稿。本记录为研究归档，不构成正式知识发表。日期：2026-11-08。基线：Container-R/GameLibrary master 660c01e2858941b266d7f123ea3e6b712f580eb6。

## 生产问题与本轮决定

面向 QA 与 UI 程序：语言切换、缩放和字幕预览各自能工作，按某些次序操作却短暂显示旧文本；随后缩放或重新打开预览又恢复，最终截图与设置值均正确。若测试脚本只统计点过哪些按钮、等到某个回调再看最后一帧，就可能既算错覆盖，又错过失败。

有限范围句：在语言内容可异步加载、缩放可能重建布局、预览可重复打开的设置页中，明确操作的起点、受理与完成含义，选择先后覆盖、连续转移和受控异步交错的测试，并在会被后续操作修复之前检查结果。不承诺覆盖整个 UI 状态空间，也不研究组合生成算法性能。

本轮重点不是扩展旧 L/S/P 排列表，而是**完成的身份**：用户第二次选择语言后，旧请求的完成通知不能证明新选择已经呈现在当前预览中；第二次选择甚至可能与第一次值相同，不能只用语言码识别请求。

## 已有内容与缺口核对

已读 管理档案/研究/TASK-2026-0307/旧序列小节待编辑.md 的保留内容；其旧稿来源固定为 eeed184943ddbc6630124455b3730501684e127b。旧例正确区分允许夹入事件的先后关系和紧邻对子，但假设每操作一次且等待完成，未提供完成判据、重复操作和跨行重建方法。

从当前基线远端读取 管理档案/图书目录.json，并核对正文：

- 《游戏 UI 配置回归的约束建模与组合覆盖》（KNOW-QA-003）固定语言与内容，只研究稳定配置，已明确排除操作路径。本题应独立发展，不追加到组合覆盖文章。
- 《关闭装备预览后，未完成的资源加载怎样收尾》（SOL-ENGINE-004）研究 Addressables 加载、失效请求和所有权收尾。新题可以引用其“旧请求不再代表当前界面”的机制，但不重写资源释放教程；主交付是测试建模与判据。
- 《自动测试角色到达终点后，还要检查什么》（KNOW-QA-001）已解释到达结果不等于路径正确。本题应落实到可执行 UI 检查点，而非再次写泛泛的“最终结果不够”。
- 另读旧基线支持资料《单独运行能通过，为什么排在另一个测试后就失败》；已有独立测试间配置污染、重启不等于恢复配置的解释。新题仅保留序列行起点必要条件，避免再发展一篇测试隔离文章。

检索边界：查当前正式目录标题和上述相邻正文，并用旧完整树查“序列/设置/异步/测试”候选；未宣称全文语义穷举。目录实际名为“图书目录.json”。

## 已核实的来源机制

1. NIST 2012 作者预印本把每行定义为事件符号的排列，长度 t 的有序子序列可以夹入其他符号；每个符号在该排列中一次。原始问题来自曾经先连接另一设备即可触发故障的情形。[1] 项目页仍明确同一含义。[2] 因而覆盖 A…B 并不覆盖 A 紧邻 B；将相同按钮的多次调用直接压为一个符号，会丢掉重复次数和调用身份。这后一判断是对定义的推导，不是论文给出的 UI 方案。
2. Unity Localization 1.5.14 的 OnSelectedLocaleChanged 文档说事件在初始化操作完成后调用，预加载已经完成。[3] 此条件没有声明该项目所有文本赋值、布局重算和实际呈现都结束。不能用这个事件单独认定设置页完成。
3. 同版本 LocalizedString.StringChanged 会因首次订阅、语言改变、变量/引用改变和显式刷新等触发；首次订阅会开始加载，完成后给订阅者字符串，加载完成后的新增订阅者也会收到现有值。[4] 所以“收到一次 StringChanged”不是“刚才那次语言点击完成”的一一对应证据。
4. RefreshString 返回 true 代表能够请求新刷新；当前加载仍活动时可能忽略并返回 false。[5] 由此得到具体测试风险：连点预览或显式刷新不能按点击数统计成功刷新数。不能进一步推断 Unity 所有换语言请求都会被丢弃，文档描述的是此方法。
5. Unity Test Framework 1.3.9 的 UnityTest 可跨帧执行，yield return null 跳过一帧。[6] 一帧等待只是时间推进，不是应用语义上的完成证明。实际项目应等有界条件，并在超时时保留未完成状态。
6. Playwright 的点击自动等待检查操作可达条件；重试断言则会反复检查直到条件成立或超时。[7][8] 这是两种不同承诺。一次最终成立也不能证明之前从未显示错误，或成立之后不会被旧回调覆盖。网页 UI 可直接采用此框架；原生游戏只借鉴判据结构，不能声称 Playwright 验证 Unity 原生控件。
7. Playwright 的 BrowserContext 隔离浏览器存储等状态，并提倡每测试新建上下文。[9] 这不替游戏重建云存档、原生单例或后台任务。本文建议的起点需要项目自己的状态检查。

## 从按钮表到有身份的执行记录

以下是原创设计建议，尚未在引擎执行。产品契约必须先选定：本例采用“最后受理的语言选择生效”，预览加载中可显示加载占位，但不允许把旧语言标为新选择已就绪；同值重复选择可幂等，但必须记录是否受理。若项目采用排队逐个应用、禁用控件或保留旧内容直到替换，应修改判据，不能套用本例。

对每个操作记录：run_id、界面实例/代次、request_id、操作类型、目标值、受理状态、请求时刻、内容提交时刻、布局完成时刻、失败或取消原因。这里不要求引擎原 API 自带这些字段；它们可以由应用适配层和测试观察器补足。

最小状态分层：
- desired：当前已受理目标语言与缩放，不等于已经显示。
- content：提交给当前预览的字符串及其请求代次。
- layout：针对该内容版本与缩放版本完成的布局。
- view：预览实例是否仍有效，当前显示的是内容还是加载占位。

开始 L(lang) 前注册观察器，再发请求，以免同步缓存命中时漏掉通知。受理后记录唯一代次；不能收到回调时才读取全局“当前代次”并把旧结果重新贴上新身份。适配层应在发起实际工作时捕获身份，提交时核对归属；测试日志同时保留过期完成的真实身份。事件可能只是通知且没有身份时，需观察真正内容提交处或对所捕获操作句柄建关联，不能从“它发生在点击后”反推因果。

“L 已完成”至少要说明是选择已受理、字符串已得到，还是当前预览布局已提交。正常串行回归可等当前 request_id 的成功内容提交，并核对文本与布局版本；异步交错回归则故意在未完成时发下一个请求，否则串行等待会把要测的竞态消除。不得给所有操作统一塞一个固定 sleep。

只检查文本内容也有盲点：相同文案跨语言可能相同；L(ja)→L(fr)→L(ja) 又会回到同一个值。要结合来源身份及代表性不同文本，避免把首次 ja 完成误认为第三次 ja 就绪。相同语言是否重新请求、是否沿用缓存，是项目契约的一部分。

## 三类覆盖与检查点怎样配合

A. 先后关系覆盖：适合“某状态曾被启用，后续操作受其影响”的风险；NIST SCA 是此类对象。记录的事件必须已按约定受理/完成，不能把脚本计划表直接当实际覆盖。

B. 连续转移：若缩放能重建预览并消除旧缓存错误，应直接做 L→P，检查 P 后再执行 S。此处“连续”指没有插入另一项用户操作，并不意味着内部没有异步回调。需明确事件投影；用户操作相邻与实际提交相邻不能混称。

C. 异步完成交错：用 request 与 completion 拆开事件，例如 L1(ja), L2(fr), C2, C1。必须满足每个 C 在自身 L 后；不合法的“先完成后请求”不是覆盖目标。可用测试专用加载适配器控制完成顺序，保留另一路真实加载集成测试。受控适配器不证明实际平台所有调度。

检查点随风险而定：
- 起点检查：本行的语言、缩放、预览关闭、配置来源及未决任务归属已确定。失败记为准备失败，不计路径已测。
- 受理检查：按钮是否真正产生请求；拒绝与幂等分别记账，不静默等一条永远不会来的回调。
- 提交检查：当前预览是否只接纳属于当前请求/代次的结果；超时报告请求、已发生完成与未完成阶段。
- 修复前检查：缩放、重开预览或重建界面之前检查，否则错误会被随后动作遮住。
- 有限观察段：对“就绪后不得倒退”的要求，观察当前请求完成至所有本次安排的旧请求均完成/取消确认的区间。轮询只保证采样点；如果要断言从未错误提交，必须在每次提交记录断言，若关心实际可见闪帧还需帧级观察。不能把一次等待成功当作全时段安全。

## 代表任务与反例

任务1：给出 L1(ja)→L2(fr)→C2→C1→S。测试人员应在 C2 看到 fr，C1 后仍为 fr，并在 S 之前取证。无归属校验时，C1 可能把界面覆盖回 ja，S 又恢复 fr；仅最后检查和首次等待 fr 都会通过。此为原创假设错误，不声称 Unity 内置 LocalizedString 存在该缺陷。

任务2：预览首次订阅立即收到已加载字符串，而本次用户操作尚未受理。以“收到任意 StringChanged”当完成的测试会误放行。要求从受理及真正提交处关联请求，不按回调个数计步骤。

任务3：当前加载中连续请求 RefreshString；第一次或第二次调用返回 false。测试应区分拒绝/合并与成功完成，依据产品策略判定；不能凭两次点击说已经完成两次刷新。[5]

任务4：本行开始前把磁盘默认语言恢复，但上一行加载完成仍能向复用预览写入。起点重建必须使前行回调无权写当前实例，或销毁隔离实例并核对状态；不能靠每行中途强制重建修好被测过程。此处与既有隔离文章衔接，正文只讲必要接口。

有限模型：check_model.py 枚举固定 L1 在 L2 前、每个完成在自己请求后的三个合法次序，并模拟任务1。model-output.json 保存真实运行结果：无校验版本在 C2 正确、C1 错误、S 又正确；按请求代次拒绝旧完成的版本在 C1 后保持正确。运行命令为 python3 管理档案/研究/TASK-2026-0308/check_model.py。模型没有帧、字体、原生 UI、真实加载或失败取消过程，不是 Unity/Playwright 执行，也不提供缺陷检出率。

## 可发展正文结构与下一步

拟题：《游戏设置页的操作序列与异步完成怎样测试》。候选位置为质量保证/测试设计，但正式导航在成稿后审查，不现在建目录。

1. 用任务1开篇说明最终截图为何会漏报。
2. 明确事件合同与同一起点，区分请求、受理、提交、布局。
3. 用短 L/S/P 对照解释先后关系与连续转移；保留 NIST 定义的准确边界。
4. 重点展开重复选择、请求身份与受控乱序完成，给应用适配层伪代码及日志。
5. 选择修复前检查点，分开最终成立与观察段内不允许回退。
6. 提供一组有用途区别的测试：串行路径、相邻风险、旧完成插入、重复操作/拒绝、重建隔离；解释时间成本与测试钩子风险。

下一步最有价值的工作：选择一个固定 Unity 示例项目，列清真实绑定/布局管线，做一个测试适配层的可审查实现。分别验证缓存命中和延迟加载的同步/异步路径，明确“内容已提交”“布局完成”在哪里观察。补一张标注 request_id 和 view generation 的原创时序图。当前不需再增加泛泛来源或更多排列算例。实现后技术审稿应重点检查身份传播是否可信、错误日志是否来自被测提交而非理想模型；读者审读给任务1及一个重复同值输入，要求独立选检查点并解释判据。未达到这些条件前保持研究笔记状态。

## 原始来源与具体位置

访问日期均为2026-11-08；只保留链接与原创概述，不再分发网页/PDF正文。

[1] D. Richard Kuhn、James M. Higdon、James F. Lawrence、Raghu N. Kacker，Combinatorial Methods for Event Sequence Testing，NIST 作者预印本，2012。PDF物理第1–2页，Sequence-Covering Arrays、Definition、Example 2。首页作者与项目页会议版作者不同，按实际预印本署名。https://www.nist.gov/customcf/get_pdf.cfm?pub_id=906770

[2] NIST ACTS，Testing Event Sequences，Need for Sequence Covering、Definition、Example 2。https://csrc.nist.gov/Projects/automated-combinatorial-testing-for-software/combinatorial-methods-in-testing/event-sequence-testing

[3] Unity，Localization 1.5.14，LocalizationSettings.OnSelectedLocaleChanged，Summary；类索引 Events 项也提供相同约定。https://docs.unity3d.com/Packages/com.unity.localization@1.5/api/UnityEngine.Localization.Settings.LocalizationSettings.OnSelectedLocaleChanged.html

[4] Unity，Localization 1.5.14，LocalizedString.StringChanged，Summary 的触发条件、首次/后续订阅行为，Examples 的 OnEnable/OnDisable。https://docs.unity3d.com/Packages/com.unity.localization@1.5/api/UnityEngine.Localization.LocalizedString.StringChanged.html

[5] Unity，Localization 1.5.14，LocalizedString.RefreshString，Returns、Remarks。https://docs.unity3d.com/Packages/com.unity.localization@1.5/api/UnityEngine.Localization.LocalizedString.RefreshString.html

[6] Unity，Test Framework 1.3.9，Using the UnityTest Attribute，Intro and motivation 及跳过一帧示例。https://docs.unity3d.com/Packages/com.unity.test-framework@1.3/manual/course/unitytest-attribute.html

[7] Playwright，Auto-waiting，Introduction 和 actionability 表。滚动文档，未绑定执行版本。https://playwright.dev/docs/actionability

[8] Playwright，Assertions，Introduction、Auto-retrying assertions。https://playwright.dev/docs/test-assertions

[9] Playwright，Isolation，What is Test Isolation、Two Ways of Test Isolation、How Playwright Achieves Test Isolation。https://playwright.dev/docs/browser-contexts
