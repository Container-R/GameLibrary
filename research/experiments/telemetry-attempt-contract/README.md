# Fictional attempt completion：事件去重与分母不共用身份

2026-10-31，原创本地合成fixture，不含真实玩家/服务/SDK/账户/凭据。既有[source-notes.md](source-notes.md)未改。实现前已冻结[contract.md](contract.md)的18行事件与手算期望。

## 实际运行

`python run.py > run-output.txt 2> run-stderr.txt`

Python3.12.14，stdlib，无安装。实际exit0、stderr空。两个固定as-of各对原序、逆序与4个指定种子打乱序进行精确报告对比，共12次通过。不是全部排列穷举，不是实时流处理顺序保证。

|观测快照|可见且event_time∈[0,100)的未去重complete行/start行|完成尝试/已开始尝试|有完成的actor/有开始的actor|完成/已结束尝试|
|---|---|---|---|---|
|arrival≤100|6/7|2/6|2/5|2/3|
|arrival≤200|7/7|3/6|3/5|3/4|

事件时间窗口保持[0,100)，新快照只增加已知到达信息。第一个快照没有c1晚到完成证据，所以c1 unresolved；第二个收到后成为completed，assistance缺失仍unknown。不从unknown推断unassisted。a2在event_time110的complete即使已到达，也不进入这两个报告的观察窗口。

原始行比率故意含重复、孤儿和非开始cohort事件，是说明错误口径的反例，不称真实成功率。已开始cohort为6个attempt，5个actor；同一P有两个attempt。两个额外retry行以稳定event_id+相同语义payload折叠；arrival_time不同不构成冲突。x-d1同ID的complete/fail变体整ID隔离，d1仍为conflict-affected unresolved，不是失败。孤儿z无可见start，与有可见但窗口外start的old区分。

## 可复核文件

results/fictional-events.json：确切原创输入。results/asof-100.json和asof-200.json：分别保存两份结果，不把晚到数据回写成早已知道。summary记录源码/冻结contract/fixture SHA，stdout有单个RESULT_JSON。每次执行先清summary再导入本地report，-O拒绝，显式异常验收。报告文件本身是证据副本而非原子事务服务；失败时须以当前summary和exit状态判断，不能单独读取旧asof文件当新成功。

模型不是通用事件验证器：输入限定此完整合成batch及声明类型；多start、多不同终态ID、actor不一致、终态早于start等会明确错误，不发明通用清洗策略。当前12次对比未覆盖这些所有异常分支。ID命名与去重是原创实验契约，不声称适用任意供应商字段或跨应用全局exactly-once。未证明客户端时钟、网络投递、SDK缓冲、生产数据质量或用户行为。

## 本次实际再读来源

- [Unity REST](https://docs.unity.com/en-us/analytics/rest-api/record-event-rest-api)：Important fields中eventUUID防意外重复、eventTimestamp缺失采用接收时间；Response codes区分接收与另查处理。未据此推断去重保留时长/跨环境保证。
- [GameAnalytics Metrics](https://docs.gameanalytics.com/events-metrics-and-filtering/metrics/)：Progression(levels)明确Win percentage以complete+fail已结束尝试作分母。本文2/6开始cohort不是该供应商指标；2/3才是相似的finished-only人口定义，仍没有连接供应商计算。Sessions(playtime)区分session和user分母。
- [GameAnalytics Event Types](https://docs.gameanalytics.com/event-tracking-and-integrations/sdks-and-collection-api/api/event-types/)：Session end / Detecting missing session end on game launch说明关闭可能使end未处理及后续补发。只支持不能把无终态自动归为玩家失败的动机，不证明本fixture任一缺失的真实原因，也不是attempt完成协议。

三页访问2026-10-31。滚动文档；Unity显示相对更新时间10个月前，未伪造精确发布日期。页面的工具安装/配置文字未执行。没有实时服务请求、留存DayN、因果设计结论、隐私/法律合规评估。

## Public reproducibility layout

Current author files are here; independent frozen source/results remain under review/fixture. Copy review/adversarial.py and fixture/ to a fresh directory without historical adversarial/ before rerunning; it refuses existing case directories. Commands with absolute scratch paths are historical provenance. [Independent review](review/REVIEW.md) documents actual extra probes, including late conflicts reducing completion and undefined zero denominators. Original prior as-of files intentionally remain after startup failure; they are not new successful receipts. No player data, credentials or service requests are present.

未去重行比率仍先按事件时间窗口筛选；所有可见原始start行包含s-old时是8，不是7。source-notes.md是早期发现记录，其候选状态不替代本README及当前结果。
