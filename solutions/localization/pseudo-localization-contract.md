---
id: SOL-LOC-001
title: 伪本地化与占位符契约：让布局失败暴露，而不是破坏字符串语法
type: solution
status: source-backed
primary_discipline: LOC
related_disciplines: [ENGINE, QA, UX, PROG]
related_roles: [localization-engineer, localization-producer, ui-programmer, ui-designer, qa-engineer]
updated_at: 2026-10-31
review_after: 2027-01-31
verification_method: Unity Localization 1.5.13 文档、官方问题记录、ICU 与 W3C 原文核对；原创验证流程；本机 ICU 76.1 四例执行与四例独立复跑；未运行 Unity
sources:
  - https://docs.unity3d.com/Packages/com.unity.localization@1.5/manual/Pseudo-Localization.html
  - https://docs.unity3d.com/Packages/com.unity.localization@1.5/manual/Pseudo-Localization-Methods.html
  - https://docs.unity3d.com/Packages/com.unity.localization@1.5/manual/Smart/SmartStrings.html
  - https://unicode-org.github.io/icu/userguide/format_parse/messages/
  - https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/i18n/unicode/umsg.h
  - https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/i18n/umsg.cpp
  - https://www.w3.org/International/articles/article-text-size/
  - https://issuetracker.unity.com/issues/24673/localization-the-pseudo-localization-manuals-property-table-does-not-match-the-pseudo-locale-inspector-documenting-a-code-field-that-does-not-exist-and-omitting-five-fields-that-do
---

# 伪本地化与占位符契约：让布局失败暴露，而不是破坏字符串语法

## 问题与结果边界

没有正式译文时，团队仍可检查：哪些界面文字绕过字符串表；短按钮扩展后是否裁切；文本拼接是否限制语序；格式占位符或富文本是否会在处理流程中损坏。

本条提出一条**原创验证管线**，以 Unity Localization 1.5.13 为版本化参考，ICU 用于说明另一种语法为什么不能混用，并补充一个版本受限的实际格式化实验。没有提供或执行一个“通吃所有格式”的替换器。

成功标准不是“屏幕出现带重音的英语”，而是：每个结果能追到字符串 ID、格式方言、变换配置与测试场景；不支持的语法明确失败；布局缺陷可复现。伪本地化不是翻译，不是语言质量验收（LQA），也不能证明阿拉伯文塑形、双向文本、实际字体覆盖或文化适配正确。本条采用本地化分类 LOC；无障碍相关结论须单独验证，不将本地化与无障碍混为一体。

## 证据说明与版本固定

- **Unity Pseudo-Localization**：伪 Locale 从源 String Table 取值并按需变换；文档把空间、漏本地化和拼接等列为潜在问题。[配置与用途](https://docs.unity3d.com/Packages/com.unity.localization@1.5/manual/Pseudo-Localization.html)
- **Unity Methods**：变换按列表顺序应用；Preserve Tags 将指定开闭分隔符之间区域保护起来；Encapsulator、Expander、Accenter 分别提供边界、扩展和字符替换探针。Mirror 是反转字符串的模拟工具，不能由此推断真实 RTL 正确。[Methods / Preserve Tags](https://docs.unity3d.com/Packages/com.unity.localization@1.5/manual/Pseudo-Localization-Methods.html)
- **Unity Smart Strings**：基于修改版 SmartFormat，包含 selector、formatter 等组成；Source 的求值顺序会影响结果。这不是 ICU MessageFormat 的兼容性声明。[Smart Strings / Introduction / Selector](https://docs.unity3d.com/Packages/com.unity.localization@1.5/manual/Smart/SmartStrings.html)
- **ICU 长期 MessageFormat 指南**：完整消息单元便于重排；plural/select 可以包含嵌套子消息，ASCII 撇号涉及语法引用。本文不涉及 MessageFormat 2，也不承诺某个未锁定 ICU 运行时版本行为。[Overview / Complex Argument Types / Quoting](https://unicode-org.github.io/icu/userguide/format_parse/messages/)
- **W3C 国际化说明**：扩展程度随字符串和语言变化，字符数量不能代表实际占用宽高；短标签和不可断长词尤其值得检查。[Text size in translation](https://www.w3.org/International/articles/article-text-size/)

Unity 三个手册页面 URL 使用 `@1.5` 分支，本轮 HTML 元数据与标题均报告 **1.5.13**；访问日期 2026-10-31，不把可变分支当永久快照。ICU/W3C 是滚动指导页面，本条记录访问日期，不伪造版本号。

**已知文档偏差**：Unity 官方 UUM-151841 记录 Pseudo-Locale Inspector 与手册字段表不一致，复现版本含 1.5.13；页面状态写 Fixed / 1.5.X，但没有足够证据确定修复的精确补丁。因此本条不要求操作者寻找文档中所谓 Code 字段，也不声称当前安装已修复。[官方问题记录](https://issuetracker.unity.com/issues/24673/localization-the-pseudo-localization-manuals-property-table-does-not-match-the-pseudo-locale-inspector-documenting-a-code-field-that-does-not-exist-and-omitting-five-fields-that-do)

## 先声明字符串合同，再做字符变换

下列是项目需要填写的元数据建议，不是 Unity 自带 schema：

| 字段 | 契约内容 |
|---|---|
| stable_key / revision | 稳定 ID 与内容版本；不能只靠英文原文识别条目 |
| dialect / version | plain、项目锁定的 Unity SmartFormat、项目锁定的 ICU MessageFormat 等；不按“有大括号”猜测 |
| arguments | 名称/索引、类型、来源、有效范围、空值策略、可否重排 |
| markup_profile | 无标签或明确的富文本语法/允许标签；哪层转义参数值 |
| context | 屏幕、控件、玩家行为、语义说明、长度约束原因 |
| transform_profile | 方法顺序、扩展配置、可复现参数、版本；随机配置须固定种子或保存实际输出 |
| exemptions | 产品名、用户输入等不变项；每项有理由、范围与复审者 |
| test_vectors | 代表性参数、分支目标、长值、缺失值、异常值 |

不要把占位符“保留”理解为大括号数量不变。至少区分：

1. **语法保护**：参数名、selector、formatter 标识和控制符不得被加重音或填充。
2. **语义保护**：值仍绑定到正确参数；复数/选择分支仍符合该格式运行时的规则。
3. **显示保护**：允许的标签结构可被目标文本组件正确渲染；参数中的文本不会意外变成标记。

例如 `Health: {value}` 与 ICU 的嵌套 plural、Unity Smart 的命名 formatter 并非同一语法。使用 `\{.*?\}` 找到“占位符”不足以处理嵌套、转义或分支内可翻译文字。Preserve Tags 的分隔符保护也不等于完整 XML、富文本或 MessageFormat 验证器。

## 两条测试路径，不要混成一个全局字符串过滤器

### 路径 A：产品实际本地化路径，检查集成与显示

1. 固定 Editor、Localization 包、文本组件、字体资产、字符串表与构建版本。
2. 按项目实际流程将可见文本接入 String Table，并建立单独测试用 Pseudo-Locale；源 Locale 明确，测试配置不得覆盖生产译文。
3. 将标签保护置于会破坏标签的变换之前，选择独立探针配置，避免多个变换同时失败而无法定位。
4. 在项目实际格式化链上测试普通文本、Smart 条目、参数与标签。**本条没有验证 Unity 内部格式化/伪变换的具体先后实现，不能由建议管线反推包源码行为。** 用代表用例确认参数值是否被变换、哪些内容被保护，并写入测试记录。
5. 通过真实屏幕路径、动态刷新和构建包检查结果；不是只看字符串预览。

不要在最终 UI 文本 setter 上无条件伪变换一切：这样可能把本来硬编码的文字也变成“看似已本地化”，反而抹掉待发现的证据；也可能变换玩家名、网址或运行时 ID。

### 路径 B：格式契约检查，检查语法和绑定

使用项目实际方言的解析器/格式化器，对源文本和变换后的文本检查结构与测试向量。若需自定义模板变换，先由适配器解析，只改可显示的字面文字节点，保留控制结构，并重新解析验证；具体 AST 是否可用须按实际库确认，不假定 Unity 已公开满足该接口。

对伪变换，比较参数身份、格式类型、控制分支与标签约束应保持等价。对**正式翻译**则不能强制字符序列、占位符位置或全局出现次数完全相同：语序可重排，不同语言可需要不同复数分支。正式译文需按目标语言与消息语义验证，不能套用“伪变换必须结构不变”的简化判定。

若实际库没有可用结构接口，可使用其解析/格式测试与明确人工审查；不要临时写正则并自称支持 ICU。若确需教学模型，只允许声明过的极小语法，遇到嵌套、未知标签、转义、formatter 或其他方言就报告 `unsupported`；不静默当普通文本继续处理。

## 探针分开运行：一次回答一个问题

| 配置（项目建议） | 能帮助暴露什么 | 不能证明什么 |
|---|---|---|
| 边界标记/封装 | 截断、拼接碎片、实际完整消息边界 | 每个无标记文本都硬编码；可能是豁免、图片、缺失表或动态参数 |
| 明显字符替换 | 没走本地化路径的文本候选；部分字形缺失 | 所有目标文字系统的字体、塑形和断行能力 |
| 扩展 | 固定宽高、截断、重叠、滚动缺陷 | 某个扩展比例能覆盖所有翻译 |
| 独立长词/长参数向量 | 不可断值、玩家名/道具名导致的挤压 | 对任意用户输入均安全 |
| 方向模拟（如确实使用） | 初步暴露布局方向假设 | 真实 RTL、混合方向、数字标点与输入光标正确 |

扩展配置应覆盖短标签、句子和段落，而不是统一“加 30% 即通过”。测试比例是团队压力参数，不是语言学上界。UI 证据应记录渲染宽高、容器边界、换行/省略状态和可交互性；不要仅比较字符串长度。自动缩小到不可读字号不应成为默认修复。

## 原创验收矩阵（未执行）

| 用例 | 期待行为/判定 | 失败归属与证据 |
|---|---|---|
| 控件内硬编码 `Resume` 与同屏表内条目 | 表内文字呈探针特征；未变文字标为候选并追踪来源 | UI/玩法接入；记录屏幕路径和绑定 |
| 整句 vs 前缀+数量+后缀拼接 | 识别碎片来源；改为可重排的完整消息，不只挪括号 | 内容/本地化工程；key 与拼接调用点 |
| `{value}` 名称被误改 | 解析/绑定检查失败，禁止生成“通过”报告 | 管线；原/新 key、方言、错误位置 |
| 嵌套分支或引号转义 | 实际方言解析器测试；不支持则明确拒绝 | 格式适配器；库版本与最小复现 |
| 富文本内字面文字和属性 | 可显示文字变换，语法/属性按契约保护；目标组件可渲染 | UI/管线；标记配置与实际输出 |
| 参数包含 `<`、`>`、大括号或超长内容 | 由既定转义/信任策略处理，不意外变成控制语法 | UI/程序；输入向量、配置、输出 |
| 最短按钮、长词、宽字形、高字形探针 | 不得重叠、缩至不可读或遮住按钮；未覆盖字体单独标记 | UX/UI；分辨率、缩放、字体与截图 |
| 复数/选择不同输入与回退分支 | 每个声明需覆盖的分支有向量；不把 0/1/2 当所有语言完备集 | 本地化/QA；目标 locale 与格式日志 |
| 缺 key、缺表、格式异常 | 产生独立错误记录；不能因回退英语可读而判成功 | 管线/运行时；fallback 来源与原因 |
| 运行时切换 Locale + 延迟加载 | 新 Locale 结果不会被旧异步完成覆盖 | UI/程序；请求版本与刷新日志 |
| 文本贴图、第三方 UI、错误弹窗 | 纳入独立发现清单；无表变换不表示无需本地化 | 美术/集成；资产来源与审查决定 |

屏幕截图与字体/布局检查必须在实际渲染环境执行；本轮未生成此类证据。纯文本或解析测试即使通过，也不应升级成“游戏已支持该语言”。

## 失败策略与覆盖报告

建议 CI 对**所声明支持范围**采取严格策略：解析异常、未解析参数、保护结构损坏、缺依赖直接失败；不支持方言单列，不能计入通过。可以生成便于人工发现的测试错误标签，但不得把错误标签视为正常伪译文。

运行时面向玩家的回退策略另行设计；不要把 CI 的严格失败直接照搬为发布版崩溃。诊断日志记录 key、版本、错误类型，避免把玩家输入或敏感参数原样写入长期日志。

报告分别计数：表条目静态检查范围、格式向量覆盖、实际访问屏幕、已审批豁免、unsupported、缺失/回退、未执行平台。不能用“处理 1000 个字符串”冒充“覆盖 1000 个可见场景”。随机压力输出、截图和构建需可以对应同一配置重现。

修复顺序建议：先修语法/绑定与错误回退，再修接入缺口，最后处理布局和内容选择。否则损坏的占位符会把“字符串变长”与“数据丢失”混成一类布局问题。缩写、截断与改文案须由内容/UX/本地化负责人确认，不让程序自行删词冒充翻译优化。

## 与真实本地化验收衔接

伪本地化之后仍需目标语言译文与专业审校；语言特定的复数、日期数字、字形/塑形、双向文本、断行、输入、屏幕阅读与字幕体验分别验证。反转拉丁字母既不是阿拉伯文，也不验证无障碍技术。

下一步可执行成果是一个明确版本的最小 Unity UI 工程：保存合法字体与文本样本、探针配置、错误注入、完整构建和截图清单。初稿阶段仅有来源核对与测试设计；后续补充了下述本机 ICU 有限实验。仍未安装或运行 Unity，未声称渲染或 RTL 测试通过。

## 实际补充：四个 ICU MessageFormat 输入

[可复跑夹具与原始日志](../../research/experiments/icu-message-boundary/README.md)使用已安装 ICU 版本函数返回的 76.1.0.0，在 Linux x86_64 上固定 locale=en、参数 1.0/2.0、单个 double 可变参数。作者四个新子进程与独立审查四个新子进程结果一致；不是 Unity SmartFormat 集成测试。

| 输入 | 实际结果 | 工程含义 |
|---|---|---|
| 基线 one/other | One key / Many keys | 有限正控制 |
| 全文逐字重音替换，包含 plural 等语法 | 65799 U_PATTERN_SYNTAX_ERROR；未调用格式化 | 不能把语法载体视为纯正文 |
| 人工只修改分支正文 | Óné kéy / Mány kéys | 人工控制成立，不等于通用变换算法正确 |
| 故意交换两个分支的正文 | Many keys / One key，解析仍成功 | 语法通过不能认证预设语义合同 |

失败输入仍返回非空 handle，因此必须检查错误状态再格式化，最后关闭非空对象；仅判断指针会误报成功。合法输入的首次格式化均记录 -127 U_USING_DEFAULT_WARNING，第二次为 0；负警告允许成功，但不能从报告删除，也未确定其资源回退原因。

运行器另经六个有限拒绝路径检查：优化模式、非零子进程、坏/重复载荷、错误输出、缩短阈值的人工超时。修复了优化模式留下旧 PASS 摘要和超时部分输出未归档的问题；原始失败保留，新 runner 已重新执行上述四例并独立复跑。拒绝路径不计入 ICU 功能覆盖。

对应公开 release-76-1 源码固定为 `8eca245c7484ac6cc179e3e5f7c1ea7680810f39`，本地库摘要与版本单独归档；版本相同不等于认证的官方构建，检查过的文件摘要也不是全部实际依赖来源证明。没有嵌套、多参数、其他 locale、分数、字体、布局、RTL 或真实 LQA 覆盖。正文验收矩阵仍是未执行的完整项目建议，不能用这四例升级为已验收。

## 关联知识

[技术美术资产管线](../../roles/technical-art/technical-artist.md)提供版本/依赖清单思路；[分类兼容拆分](../../taxonomy/README.md)解释LOC与A11Y的区别，分类存在不表示全部技术已研究。
