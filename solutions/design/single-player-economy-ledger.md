---
id: SOL-DESIGN-001
title: 单机成长经济：用事件账本验证来源、消耗与升级可达性
type: solution
status: source-backed
primary_discipline: DESIGN
related_disciplines: [DATA, PROG, QA]
related_roles: [economy-designer, systems-designer, gameplay-programmer, data-analyst]
engines: [engine-agnostic]
platforms: [single-player]
updated_at: 2026-10-31
verification_method: 两项原始设计资料核对；原创 Python 整数货币模型14项测试；SQLite 四场景10进程、单个双写者握手序列及独立复跑；读者阻塞 COMMIT 后同事务重试两轮各2进程；未进行真实玩家试验
sources:
  - https://gamebalanceconcepts.wordpress.com/2010/09/08/level-10-final-boss/
  - https://unity.com/how-to/building-game-economy-guide-part-2
  - https://www.sqlite.org/lang_transaction.html
  - https://www.sqlite.org/lockingv3.html
  - https://www.sqlite.org/pragma.html#pragma_synchronous
  - https://www.sqlite.org/atomiccommit.html
  - https://docs.python.org/3.12/library/sqlite3.html#transaction-control
---

# 单机成长经济：用事件账本验证来源、消耗与升级可达性

## 问题与范围

“每局收入减支出为正”不代表玩家能在预期阶段买到升级；“收入与支出相等”也不是成长经济的通用目标。本方案解决一个窄问题：**无真实货币购买、无玩家交易、固定 NPC 价格的单机游戏中，一次性奖励、重复产出、经常性开销与一次性升级共同作用时，如何验证升级何时可达，以及内容结束后的余额走势？**

本文不给商业化、付费转化或真实金融建议。数值均为原创演示假设，不是任何已发行游戏的配置或推荐比例。

## 原始依据与原创推导的边界

Ian Schreiber 的 *Level 10: Final Boss*（2010）在 Economic Systems 区分资源产生、消耗与转移；Scarcity 讨论有限与可再生资源造成的体验差异；Inflation 段落提出记录总量和人均量，并举出只在首次任务发放奖励的设计思路。[S1] 本文仅借用这些分析视角，不把其多人市场论述直接套到单机固定价格。

Unity 的 *Building an in-game economy* 在 Resources and game progression / Mapping your sources and sinks 强调资源对成长的作用，以及按来源、去向映射收益和消费。[S2] 它是面向商业化的高层指南，不是验证“任何阶段必须收支相等”的数学定理；本文不采纳其中付费/习惯养成设计为任务目标。

以下公式、事件模式、示例配置与验收检查均为**本库原创实现建议**，不是来源原话或其已验证项目结果。

## 先定系统边界，再记账

选择“一个存档中玩家持有的金币”为库存 B，单位为 coin。任务奖励是 source，购买 NPC 服务是 sink；玩家自己的背包与仓库转移只改变存放处，不能再计一次新增金币。若未来引入玩家交易，应另定全体玩家边界，不能把收款方的收入当成系统铸币。

每个事务保存：`eventId, saveId, configVersion, gameTime, reason, currency, delta, balanceAfter`。演示代码只保留前三者中的事件 ID 和必要账本字段，**没有**生产存档、并发、原子提交或崩溃恢复实现。

逐事件守恒式：

`B_after = B_before + minted - destroyed + transfers_in - transfers_out`

以阶段汇总时，一次性来源 `G`、每次遭遇奖励 `r`、经常性费用 `c`、完成遭遇数 `n_s`、升级价 `P` 的关系是：

`B_s = B_(s-1) + G_s + n_s × (r-c) - P × I_s`

其中 `G_s` 仅首次发放，`I_s` 只有首次购买成功时为 1。B 是库存（coin），r/c 是 coin/encounter，n 是 encounter/session，汇总净流量才是 coin/session；不能直接拿金币余额与每小时收益相减。

## 演示配置与事件顺序

假设每 session 是 30 分钟体验窗口；战斗频率是完成数量假设，不是测得行为。

| 配置 | 演示值与语义 |
|---|---|
| 初始/欢迎奖励 | 首次存档一次性发 100 coin |
| 完成遭遇奖励 | 12 coin/encounter |
| 遭遇后服务费 | 4 coin/encounter，先获胜入账再扣费 |
| 常规完成数 | 6 encounter/session |
| 升级 | 240 coin，只能买一次，在 session 结束时检查 |
| 升级收益 | 此模型不改变收入率或战斗完成率，避免隐藏正反馈 |
| 随机性、离线收益 | 均未建模 |

因此购买前净积累为 48 coin/session。第 1、2 次结束余额分别是 148、196；第 3 次达到 244 并支付 240，剩 4。到第 10 次余额为 `100 + 10×48 - 240 = 340`。

这里余额持续上涨并不自动叫“通胀”：本模型没有玩家市场或价格调整。更准确的风险是**一次性购买完成后，金币是否失去用途**。可能的设计结果包括允许储蓄、结束内容、增加确有玩法价值的用途或重新审视重复奖励；不能为了账面平衡凭空加令人厌烦的收费。

## 分群与敏感性：不要让平均数伪装成每个玩家

两个等权重行为假设：每 session 完成 6 次的 A 和 3 次的 B，其净收入分别是 48 与 24。A 在第 3 次购买，B 在第 6 次；第 5 次时只有 50% 完成购买。若把所有人替换为平均 36 coin/session 的同一个虚拟人，会得到第 4 次人人可买的错误分布结论。

这不是玩家预测，只是**阈值运算与平均不能交换**的反例。真实研究应保留按进度、经验/技能、玩法偏好划分的可解释样本；不把没有证据的人群标签写成真实占比。

实际运行的单变量敏感性结果：

| 场景（其余不变） | 首次可买 session | 第10次余额 |
|---|---:|---:|
| 基准：奖励12、价格240、欢迎100 | 3 | 340 |
| 每次只完成3遭遇 | 6 | 100 |
| 无欢迎奖励 | 5 | 240 |
| 奖励降至10 | 4 | 220 |
| 奖励升至14 | 3 | 460 |
| 价格升至300 | 5 | 280 |

这显示离散购买时点有台阶：奖励变高未必改变首次购买 session，但会改变之后的库存。需同时观察时间、余额和选择，不只看“几局能买”。若奖励来自随机掉落，应保留分布、相关性和极端路径；不能把期望掉落当作每个人必得的奖励。

## 工程实施与验收

1. **列账本而非仅列商店**：逐项标明一次/重复、触发条件、上限、币种、退款、重读存档是否可重领。内容设计必须签清事件顺序。
2. **先建可解释基准**：固定配置与输入序列，输出每次来源、消耗、余额和首购时点。先查重复发奖、扣费失败、币种混加，再做调参。
3. **增加约束**：余额不足不得部分扣费或先记拥有物；奖励/购买使用稳定事件 ID。示例重复事件直接报错，生产系统可用幂等返回，但必须与资产变更处于同一事务边界。
4. **再引入人群与反馈**：明确完成率、购买策略、升级对产出的影响和样本来源。玩家可以不买，故“可负担”不是“会购买”；模型结果不能当作乐趣/留存证据。
5. **对照真实试玩**：记录可达时间分布、目标前余额、失败支出、未消费原因和内容阶段；按同一配置版本比较，不用总金币量单独推断体验。
6. **保留反例**：首次奖励误设为每 session 重领，会改变成长曲线；升级允许重复扣款则伪造持续 sink。完成整条内容后再跑长尾，检查需求耗尽。

## 已执行的模型验证

Python 3.12.14，纯标准库，14 项测试通过：基准阈值/库存、一次性事件计数、重复事件无副作用拒绝、余额不足无副作用拒绝、整数单位检查、账本守恒、分群平均反例、单变量敏感性，以及期初库存经条目入账、构造参数不能注入状态、无效事件 ID 无副作用拒绝、无效参数及布尔币值拒绝。

账本的余额、条目和已见 ID 都从空状态构造；期初库存必须用 `post` 记账，才能被守恒式计入。事件 ID 必须为非空白字符串；`kind` 仅是描述标签，不强制来源/消耗标签与金额符号一致。模型字段并未做防篡改封装，所有余额变动必须走 `post`，不承诺外部直接改字段后仍满足不变量。

已归档路径：`research/experiments/economy-ledger/model.py`、`test_model.py`、`scenario-output.json`、`test-output.txt`。仓库根目录运行 `python3 research/experiments/economy-ledger/test_model.py` 与 `python3 research/experiments/economy-ledger/model.py`。**仅证明该演示模型在这些输入下满足断言**；该内存模型未测试引擎存档、并发交易、崩溃恢复、真实玩家或经济是否有趣；另有下节严格受限的 SQLite 进程终止补充，不扩大原模型结论。正文保持 `source-backed`，不将模型通过外推为完整经济已验证。

## 存储边界补充：提交了，却没来得及应答

内存中防重复还不等于持久幂等。[原创 SQLite 夹具](../../research/experiments/sqlite-ledger-boundary/README.md)把余额变化与 event_id 唯一 receipt 放进同一数据库、同一 SQL 事务。固定单存档、coin、amount/reason 两字段请求合同；先以 opening 事件记入 100，再尝试 reward-1 增加 25。

本机 Python 3.12.14 / SQLite 自报 3.53.1，显式 DELETE journal 与 EXTRA 同步设置并逐连接回验。四个场景跨十个实际子进程，另有十个独立复跑进程：

| 边界 | 实际观察 |
|---|---|
| 更新余额并插入 receipt 后、COMMIT 前直接退出 | 新进程读到余额 100、只有 opening，无 reward-1 |
| COMMIT 返回后、业务应答前直接退出 | 新进程读到余额 125、reward-1 恰一条 |
| 同 ID、同 payload 重试 | 返回保存的原收据，余额仍 125，不重复发奖 |
| 同 ID、金额改为 26 | 明确冲突拒绝，余额和完整收据集合不变 |

检查点日志不是业务应答；两个终止进程均没有正常 RESULT_JSON。关键不是假定调用者总能知道提交结果，而是未知结果重试时仍能识别原事件。生产 payload 身份可能还需币种、配置版本、存档 ID 等，不能套用这个极小字段集合。

另一个独立补充进程执行十组输入/事务检查，包括余额已变为 135 时重试仍返回该事件原余额 125，以及人为使 receipt INSERT 失败后，之前的余额 UPDATE 被回滚。这说明“返回原结果”不等于“查询当前余额”，也检验了本例双写失败路径；不是一般并发或跨节点保证。

来源依据为 [SQLite 事务](https://www.sqlite.org/lang_transaction.html)、[同步设置](https://www.sqlite.org/pragma.html#pragma_synchronous)、[回滚日志提交机制](https://www.sqlite.org/atomiccommit.html)和 [Python 显式事务控制](https://docs.python.org/3.12/library/sqlite3.html#transaction-control)。这些官方页面解释接口与环境假设，不替代本例测量；Python 滚动文档当时为 3.12.16，非运行时精确源码。版本/source_id 是自报，二进制摘要不是官方构建认证。

**边界：** os._exit 只测试进程直接终止与重开，不是断电、OS 崩溃、磁盘写撕裂、热日志路径或硬件 flush 验证。EXTRA 读回不证明底层设备兑现持久性。该终止夹具无并发写者；另有下节单个写锁序列。无 WAL、云同步、支付、反作弊、远程权益或真实玩家证据；也不推荐所有游戏采用 SQLite。完整原始输出、源码、历史失败与数据库无损文本副本见夹具。

### 写锁扩展：BEGIN 失败不等于 COMMIT 失败

[双写者握手夹具](../../research/experiments/sqlite-writer-contention/README.md)在两个连接都配置就绪后，让 A 持有未提交的奖励事务，再命令 B 以 busy_timeout=0 执行 BEGIN IMMEDIATE。B 实际收到 SQLITE_BUSY（5），未进入事务；在 A 仍持有期间读到旧余额 100。父收到这个结果后才允许 A 提交，收到提交成功后才允许 B 重试同一请求；B 返回原收据，最终新读者看到余额 125、奖励仅一次。

作者与审查者各执行一个序列、四个子进程（初始化、A、B、新读者），不是四种竞争场景。通过管道/事件握手决定先后，不靠 sleep 猜测；原始角色输出与父收发记录一起保存。

这只验证 BEGIN IMMEDIATE 的被拒绝入口。SQLite 文档另说明 COMMIT 因读取者而 BUSY 时事务可能仍活动；这个双写者实验未构造该情况；下节另有读者阻塞 COMMIT 的新证据，不能把“没有进入事务”套到任何 BUSY。等待明确提交后重试是实验协议，不是无限立即重试的生产建议；公平性、吞吐、完整隔离性、超时取消和多写者队列仍未验证。

### COMMIT BUSY：重试提交，而非再次执行奖励

[读者阻塞提交夹具](../../research/experiments/sqlite-commit-busy/README.md)补足BEGIN竞争实验未覆盖的分支。在本机Python3.12.14/SQLite自报3.53.1，DELETE journal、EXTRA、busy_timeout=0下，两个独立连接保留重叠事务：读者持有余额100的读事务；写者已执行余额+25及receipt插入。第一次COMMIT实际返回SQLITE_BUSY（5），Python `in_transaction`仍为true；写者可见125，原读者仍可见100。

释放读者后，写者**仅重试同一事务COMMIT**，不重新BEGIN或重做业务DML。提交成功后，另一个新只读进程核对完整收据opening100、reward-1金额25/结果125与余额125。实际SQL trace包含一次奖励UPDATE、一次INSERT和两次COMMIT尝试。两个进程是一轮受控序列加独立读回，不是并发压力测试。

因此重试入口必须区分“BEGIN未进入事务”和“COMMIT失败但仍保留修改”。后者直接重复非幂等UPDATE可能重复发奖。生产仍需错误分类、实际事务状态和截止期限，选择继续提交或明确回滚后幂等重试，不能无限重试所有异常。

[SQLite Transaction §2.3](https://www.sqlite.org/lang_transaction.html)解释该活动事务语义。这个扩展不改变旧实验范围，不证明WAL、断电持久性、云同步、公平性或真实游戏正确性。环境重置前的本地档案已丢失，当前归档为明确标记的新运行，而非冒充恢复的旧证据。

## 原始来源与访问限制

- **S1** Ian Schreiber，[*Level 10: Final Boss*](https://gamebalanceconcepts.wordpress.com/2010/09/08/level-10-final-boss/)，2010-09-08，作者教学原文；读取 Economic Systems、Scarcity、Open and closed economies、Inflation、Trading，本文仅采用资源边界/有限性/监测视角。访问 2026-10-31。
- **S2** Unity，[*Building an in-game economy*](https://unity.com/how-to/building-game-economy-guide-part-2)，未标明发布日期，网页无固定引擎版本；读取 Resources and game progression / Mapping your sources and sinks。访问 2026-10-31，商业化上下文不作为本方案目标。
- 检索词：sources/sinks、stock/flow、一次性奖励、资源源汇、game economy。Machinations 文档正文在本次读取中未呈现，HvA 的 Dormans 论文 PDF 返回 403，未绕过限制，也未据搜索摘要声称读过论文。上述失败仅保留为后续线索，不支持本文技术断言。

所有表格、模型与代码为独立原创；未保存付费书籍、第三方完整课件或原文图表。

## 关联知识

[玩法程序职责](../../roles/programming/gameplay-programmer.md)明确规则与验收交接；[客户端权威边界](../programming/client-prediction-authority-boundary.md)说明持久副作用为何不能随预测重放重复执行。
