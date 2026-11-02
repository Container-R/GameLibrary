# EnTT组件消费者修正：独立反例闭合

2026-11-02。**接受本次有限消费者修正。** 不授权原生执行，不替代另一审查者的fixture／runner完整审查。原拒绝报告、原反例脚本与旧冻结文件保留。

## 最终输入

- checker：`21dffbb35f6ae3365c8d8c14b581f6e36e566da449464446ff484a3cc05a2a2e`
- independent-oracle：`92f2fe2c5dbfe5e3fa3a8a281b171e2bbde033bdcea0257ea86658f9d32eeb15`
- INPUT-MANIFEST：`7af256d00360edbed9722d80196503548afada426016060312f42f96ef1faf38`
- 新独立脚本 independent-consumer-check-v2.py：`6d1d60f89b0a36c63c2288adc6bc3eed618db01e74c7fee49234900797dde5d3`
- 原脚本 independent-consumer-check.py 仍为 `fb36f888f88f91b3232f6597b9c8c45eff9adedb9bd1fe3c1618c7eb22e8a01e`，没有覆盖。

实际对照 history/rejected-v1 与当前checker：唯一语义增量是对R/H/S/B/L检查index不等于0xfffff、version不等于0xfff，错误名live_reserved_handle。prepared的两个规范null映射不在此列表，原类型／关系检查继续执行。oracle结构比较仅types、invariants和clarification变化，增加普通live身份的保留域限制；没有改tokens、阶段、读写计数、描述性成员判断或成功行数，也没有把合法版本固定为0。

## 实际纯Python复核

分别在普通与-O运行独立v2脚本，两模式结果相同：

- 原4个合成正例继续接受；原81个反例继续拒绝，案例构造未改。
- 原10个错误接受案例继续使用原构造，现在全部拒绝；额外明确断言异常为checker.CheckError且错误名恰为live_reserved_handle，不能凭其他意外异常宣称闭合。
- 新增且明确单列1个正例：将全部普通身份一致提升到合法版本1，保留prepared null哨兵、JSON null与相等关系。通过。这是消费者关系域的合成检查，不预言该无销毁夹具会实际分配版本1。
- 合计同一5正例、91反例；两解释器模式不相加为新案例或原生场景。结果保存在 independent-v2-normal.json、independent-v2-optimized.json。

新脚本相对旧脚本仅更新三个冻结摘要、增加这一个合法版本正例以及保留反例的具体错误断言／摘要输出，没有删除或重写旧反例以适应修复。

另在保留的旧拒绝副本重放同一4正例／91反例，两模式仍非零，均报告原10个false-accept。安全stdout及退出码保存在 independent-rejected-v1-normal.json、independent-rejected-v1-optimized.json；明确这是本轮重放，不伪装成第一次测试的原日志，也不复制含工作定位的traceback。旧报告仍保存最初发现。

本轮仅Python解释器消费合成记录；无compiler、native、runner.main、真实进程组信号或网络调用。没有更改作者checker/oracle/manifest、旧真实输出或回执，也未改stage或远端。此处的有限接受不证明任意恶意oracle安全、所有EnTT身份规则均覆盖，或原生输出已经出现。
