---
id: SOL-DATA-001
title: 关卡完成率：事件、尝试与玩家分母不能混用
type: solution
status: source-backed
primary_discipline: DATA
related_disciplines: [DESIGN, PROG, QA, PROD, LIVE]
related_roles: [game-data-analyst, gameplay-programmer, game-designer]
related_topics: [telemetry, cohort, event-identity, late-arrival, metric-contract]
engines: []
versions: ["Unity Analytics REST rolling docs accessed 2026-10-31", "GameAnalytics Metrics and Event Types accessed 2026-10-31", "Python standard-library synthetic batch"]
platforms: [offline-synthetic-data]
updated_at: 2026-10-31
verification_method: 官方事件/指标文档核对；原创18行合成输入与预先冻结手算结果；固定快照和有限输入排列，不含真实玩家或服务调用
sources:
  - https://docs.unity.com/en-us/analytics/rest-api/record-event-rest-api
  - https://docs.gameanalytics.com/events-metrics-and-filtering/metrics/
  - https://docs.gameanalytics.com/event-tracking-and-integrations/sdks-and-collection-api/api/event-types/
---

# 关卡完成率：事件、尝试与玩家分母不能混用

## 指标变化之前，先问分子和分母是谁

同一份关卡日志，可以算出6/7、2/6、2/5或2/3。它们并不一定是算术错误；更常见的问题是把不同观察单位、去重规则和已知时间包装成同一个“完成率”。

本方案面向玩法埋点→数据分析→设计判断的交接。使用18行原创合成事件，说明如何保留事件身份、尝试身份、虚构actor身份、观察截止时间和未知状态。**没有真实玩家、SDK、供应商API或统计因果实验；数字不是任何游戏的表现。**

## 1. 三类身份、两种时间

|字段|本实验含义|不能替代|
|---|---|---|
|event_id|一次语义事件的稳定标识；运输重试继续使用同一ID|一次游玩尝试或玩家|
|attempt_id|一次开始→可能结束的关卡尝试；本合成数据内全局唯一|进程、session或所有游戏的通用命名空间|
|actor_id|虚构主体，可有多次尝试|已验证的真实个人或跨设备账号|
|event_time|事件被声明发生的时间|服务何时收到、何时报表已知|
|arrival_time|本批数据可观察到该行的时间|游戏中发生顺序|

[Unity REST文档](https://docs.unity.com/en-us/analytics/rest-api/record-event-rest-api)将user、session和event UUID分开，说明UUID用于抑制意外重复插入；未提供eventTimestamp时采用接收时间。本文借此说明身份与时间不能混同，**不把自定义event_id政策冒充Unity实现**，也不推断服务去重保留期或跨环境exactly-once。

本例所有时间都是相对固定虚构原点的整数秒，假定时钟正确。真实客户端时钟漂移、跨设备身份、schema升级和用户授权不由这个模型解决。

## 2. 先冻结报表契约，不能等结果出来再选口径

本例开始cohort为event_time在`[0,100)`且截至报告as-of已观察到的有效start。终态也必须位于`[start_time,100)`。分别生成arrival_time≤100和≤200两份快照，不把第二份新知识伪装成第一份当时已知。

采用以下**原创有限政策**，不是行业统一清洗标准：

1. 先按arrival截止选择可见行，再按event_id分组。
2. arrival_time是运输元数据，不参与语义payload相等判断；相同ID、相同payload的额外行折叠为重试。
3. 同一ID出现不同语义payload，隔离该ID全部可见变体，不采用任意first/last-wins。冲突检测在事件时间过滤之前；晚到的冲突可能改变既有判断。
4. 在无冲突事件中建立start，再判定开始cohort。完成但没有可见start记为orphan；有旧start但不属于cohort的完成单独记账。
5. cohort内未见有效终态是unresolved，不能自动标为fail。若终态ID被冲突隔离，额外标为conflict-affected。
6. 完成的assistance明确分assisted、unassisted、unknown；缺值不等于无人帮助。

多不同start ID、多不同终态ID、actor不一致和终态早于start，在当前实现中报错，交给数据契约负责人处理；不靠静默选择一条记录制造干净指标。这个完整batch处理器不是流系统、水位线或通用schema验证器。

## 3. 一组可手算的反例

下表未去重行比率也先限定事件时间窗口；它不是所有可见原始行的比率（包括旧start时可见start行是8，而非7）。六个有效开始attempt为a1、a2、b1、c1、d1、e1，共五个actor：P有a1/a2两次，Q/R/S/T各一次。还有两个重试额外行、一个冲突ID的两种终态、一个孤儿完成、一个旧cohort完成和一个超出事件时间窗口的完成。

|同一份输入的口径|as-of100|as-of200|问题或含义|
|---|---:|---:|---|
|as-of可见且event_time∈[0,100)的complete行/start行（未去重）|6/7|7/7|故意保留重复、冲突、孤儿与旧cohort完成，不是cohort成功率|
|完成attempt/已开始attempt|2/6|3/6|本次开始cohort截至快照已知的完成比例|
|有完成的actor/有开始的actor|2/5|3/5|去重到虚构主体，P多次尝试仍只占一个主体|
|完成attempt/已结束attempt|2/3|3/4|排除了unresolved，是另一分母|

as-of100：a1、b1完成；a2明确fail；c1、d1、e1未知。as-of200仅c1晚到完成进入有效结果，unknown assistance仍然保留。d1的同ID complete/fail冲突不能变成一次确定失败；e1仍没有终态。a2在event_time110的complete虽已到达，但不属于固定`[0,100)`观察窗口。

[GameAnalytics Metrics](https://docs.gameanalytics.com/events-metrics-and-filtering/metrics/)的Progression部分定义Win percentage时采用已结束尝试人口，而非全部开始尝试。因此本文2/6不应冒用该供应商指标名。表中2/3具有相似的finished-only分母定义，但仍是本地原创数据处理结果，不是已查询或复制了供应商后台算法。

不要把未结束比例隐藏掉：`completed + failed + unresolved = eligible started attempts`是本例验收不变量，同时另报冲突、孤儿和窗口外记录。否则排除未知后看似更高的百分比，会掩盖埋点或观察覆盖缺口。

## 4. “没有完成”不是“失败”，“完成”也不是“无帮助掌握”

[GameAnalytics Event Types](https://docs.gameanalytics.com/event-tracking-and-integrations/sdks-and-collection-api/api/event-types/)讨论程序关闭导致session end未及时处理及随后恢复记录。这提供一种缺失终态的工程动机，不证明某次关卡未完成的实际原因，更没有定义本文attempt协议。

unknown可以来自未结束、未到达、被冲突隔离或其他未辨明情况；本模型只标记记录能支持的状态。assisted完成也不是无提示引导成功：与[主持人介入后的试玩证据](../production/playtest-intervention-evidence.md)一起使用，保留上下文，不能用埋点名称替代研究问题。

数据报表也不直接授权奖励。分析去重和发奖幂等是不同责任：前者服务解释，后者保护游戏状态；参见[经济事件账本](../design/single-player-economy-ledger.md)。不要因为分析端看到了complete就跳过权威校验或重放保护。

## 5. 可执行的工程验收

- **玩法/埋点侧：** 定义何时开始新attempt、重试是否沿用event_id、终态与assistance的生成点；提供原始字段契约，不仅给事件名称列表。
- **数据侧：** 报表同时携带事件窗口、arrival as-of、去重/冲突政策、cohort与各状态计数；保留旧快照，避免覆盖历史可知状态。
- **设计/制作侧：** 在看百分比之前写清要回答“开始后完成”“已结束时获胜”还是“多少主体至少完成一次”；单个演示cohort不支持难度优化的因果结论。
- **QA：** 用预先枚举的成员列表验证结果，而非只比较两种都依赖同一实现的百分比；注入重试、冲突、晚到和窗口外事件，区分数据契约错误与真实失败。

## 6. 实际证据及未覆盖范围

[冻结契约、输入、报告和原始输出](../../research/experiments/telemetry-attempt-contract/README.md)包含18行事件与两个精确快照。原序、逆序和四个固定seed排列分别在两个as-of核对，共12次精确报告比较。只证明这些完整batch排列，不是所有排列穷举或实时到达过程中间结果相同。

独立复跑重复上述12次比较，另用不导入作者report的字面成员oracle核对两份完整报告。九组额外进程内探针覆盖运输元数据重试、语义冲突、窗口外冲突、未来arrival隔离和四种声明错误；两次实际子进程失败分别验证`-O`及report导入失败会清除旧summary。保留的旧as-of文件不能当作新成功，仍须看本次退出状态与summary。

重要反例：截至arrival36时d1的complete已到、冲突尚未到，完成列表为a1/b1/d1；截至37看见相同ID的fail变体后，d1被隔离，完成列表减少为a1/b1。**新增到达信息不保证完成数单调增加，更不代表设计改善。** 开始cohort成员也依赖当时可见、未冲突的start，固定事件窗口不等于现实数据永不修订。

单独空cohort探针返回三个`[0,0]`计数对；分母零的率未定义，不能渲染成0%。没有借此声称完整输入类型/schema校验。

原创输入SHA256为 `817c7c70973edc2c02ad20897f0f6b451e3a6f224f7b59c22831bac029ac91f4`；report源为 `3e58e54713d0973d867f65a22fad8a092fe8ffcb61c707c65a14fe2769bad6ee`，runner为 `b7b43d29154f8580b439b44a9eeb90c5cd3e84bb709a75ffd7c20a01191c21c5`。Python自报3.12.14，不据版本认证发行构建。

数据类型、ID空间和时钟均按冻结合成契约提供；没有生产吞吐、投递可靠性、真实用户留存、跨设备归因、访问控制或隐私合规结论。三份滚动官方网页均访问于2026-10-31；未把相对更新提示伪造成精确发布日期。
