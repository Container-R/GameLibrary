---
id: NOTE-BIZ-STEAM-TRAFFIC-001
title: Steam 流量报表对账：两个 Total Visits 不能直接相减为自然流量
type: research
status: source-backed
primary_discipline: BIZ
related_disciplines: [DATA, PLATFORM]
related_roles: [game-data-analyst]
related_topics: [steam-store, traffic-reporting, utm, measurement-scope]
engines: [engine-agnostic]
platforms: [Steam]
versions: ["Steamworks公开英文滚动文档，核对2026-11-01；无固定版本"]
updated_at: 2026-11-01
verification_method: Valve两页公开原始文档定向阅读；原创未执行的有限集合反例与报表接收表；未访问账户或验证实际报表
sources:
  - https://partner.steamgames.com/doc/marketing/traffic_reporting?l=english
  - https://partner.steamgames.com/doc/marketing/utm_analytics?l=english
---

# Steam 流量报表对账：两个 Total Visits 不能直接相减为自然流量

## 接收问题不是减法，而是能否解释差值

市场交来两张表：Store & Steam Platform Traffic Breakdown 与 UTM Analytics。分析师能否用前者的 Total Visits 减去后者的 Total Visits，把差值填成“非 UTM 流量”，再叫作“自然流量”？

**不能仅凭同名字段这样接收。** 先要证明两个数使用可比的计数单位、范围及观察条件，而且被减项确实是前者中的子集。即使能够得到非 UTM 访问，也还需要另一个分类依据才能称为自然流量：链接是否带追踪参数，与来源是否付费不是同一个问题。

本文只研究这项报表对账决定，不讲投放策略、渠道增量估计或个人身份关联。

## 官方文档给出的边界

[Store and Platform Traffic Reporting](https://partner.steamgames.com/doc/marketing/traffic_reporting?l=english)的 Accessing Reports 区分单 app 报表与 partner 游戏集合汇总。Visits 指独立页面加载，不是独立玩家；同一客户可以多次返回。Notes on Data collection date ranges 说明，自 2021-03-23 起，曝光和访问报告排除拒绝适用 cookies 的用户。

[UTM Analytics](https://partner.steamgames.com/doc/marketing/utm_analytics?l=english)的 Discrepancies Between UTM Analytics and Traffic Breakdown 明确指出，两表的流量范围及 cookie 选择影响不同；UTM 数值有时可高于另一张表。Privacy 还说明部分组合因最低门槛不显示。Testing a link 分别给出访问数按小时更新、转化在访问后 4 天定稿；转化成熟度不能当作访问数的等待规则。

两页均为 2026-11-01 读取的滚动文档，没有固定版本或统一修订日期。以上是文档条件，不是本次观察到的后台行为。

## 原创有限反例：负差和正差都不能替代子集证明

为单独检查减法逻辑，**假设**已经有共同计数单位：每个字母代表一次不同的页面加载记录。T、U 是两种观察规则选出的集合，不代表任何真实 Steam 记录或其内部算法。

| 假设输入 | 两个总数之差 | 真正的集合差 | 能否把总数之差称为 T 中不属于 U 的数量？ |
|---|---:|---|---|
| T={a,b}；U={b,c,d} | 2−3=−1 | `T \ U = {a}`，数量 1 | 不能；负数不是“负的自然访问” |
| T={a,b,c}；U={c,d} | 3−2=1 | `T \ U = {a,b}`，数量 2 | 仍不能；正数也没有证明子集关系 |

对这些有限集合，有：

$$
|T|-|U|=|T\setminus U|-|U\setminus T|.
$$

只有在 $U\subseteq T$ 时，右侧第二项才为零，总数相减才能直接表示 $|T\setminus U|$。这个等式没有替 Steam 建立共同计数单位或集合关系；现实报表若连这些前提也未确认，更不能由两个总数反推出交集、漏记人数或缺失访问。

还要区分“未被 U 观察到”与“实际未带 UTM”：某条带参数的访问若未进入 U 的观察范围，仍可能位于 `T \ U`。因此，即使得到集合差，也不能未经额外证据把它直接命名为实际未带参数的访问。

因此，负差值得调查口径，不必先认定算术错误；正差也不是对账成功的充分条件。**把负差截断为零不会修复解释错误。** 本例是未执行的数学说明，不是复建平台过滤器或测量缺失率。

## “非 UTM”与“自然”还隔着一层分类

即使另有证据建立了同一观察总体中的 UTM / 非 UTM 分区，“非 UTM”也只回答追踪参数分类。它没有回答付费来源、推荐、直接访问等来源分类问题。

原创假设：团队投放了一条未加 UTM 参数的付费链接。仅按是否带参数分类，它不会因此变成非付费来源。这个反例只说明两套分类不能互相替代，不声称 Steam 会将该访问显示在哪个具体来源行，也不要求团队识别个人。

因此接收表应分别定义“非 UTM”与“自然”的业务含义。如果无法提供来源分类依据，保留“未建立该分类”，不要用一个差值填补。

## 市场到分析的最小接收凭据（原创建议，未执行）

| 凭据 | 接收时要保存什么 | 没有证据时如何处理 |
|---|---|---|
| 报表身份 | 完整报表名称、原列名、app 或 partner 范围及对象 | 不因两列都叫 Total Visits 就合并 |
| 计数单位 | 页面加载、访问、转化等原始定义；不要擅自改成人数 | 不计算“剩余玩家” |
| 筛选与时间 | 日期区间、筛选条件、报表实际使用的时区解释、提取时点 | 未确认的时区或范围明确标记，不自行换算 |
| 可见性与成熟度 | 已知覆盖条件；隐藏、未显示与零值分开；若还带转化列，另记其成熟条件 | 不补零、不推算具体被排除者，不把转化定稿规则套给访问数 |
| 差值用途 | 声明仅作算术核对，还是要估计某个分类；后者需对应集合关系和分类依据 | 缺少依据时拒绝“非 UTM / 自然流量”标签，而不是拒绝保存两张原表 |

市场负责说明链接与活动范围，分析负责确认指标和推导前提；平台报表的公开限制不能靠内部表格命名消除。若发现差异，应先保留各自原值与条件，再向有权限的负责人核对；本文不提供任何补齐个人数据或绕过可见性限制的方法。

## 与现有材料的关系及限制

[Steam 胶囊图交接](steam-capsule-handoff.md)处理素材用途与发布条件；本文处理其后可能使用的流量证据，但不声称某张图提高了访问。[完成率分母合同](../../solutions/data/attempt-completion-denominator-contract.md)可帮助区分观察单位；本文不继承其合成数据测试，也不打开运行归档。

本次没有登录账户、提取实际 CSV、测试链接、播放视频或解读截图。没有对平台去重窗口、完整过滤算法、个别隐藏行或任何真实活动做推断。两个官方网页来自同一平台，不是两项独立效果验证；原始集合例子只说明接收前提，不是新的因果或流量估计方法。
