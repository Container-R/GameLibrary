# 纠正重放深度门槛：命令后缀正确，依赖世界却来自另一个tick

2026-10-31，只读源码/文档与本地能力检查；未制作新模型或执行引擎、网络、安装、主树/远程写入。

## 选择一个边界

**权威快照与ack有效、未确认命令后缀也正确时，重放读取的另一个实体若仍停在客户端当前tick，会不会把一次纠正重新算错？**

推荐从单角色加法模型推进到“重放所读状态的时间归属”这一验收，而不是继续增加乱序/丢包种子。不是声称现有16项测试或200种调度有bug；现有文档已诚实说明未复现ECS部分快照。缺的是能独立辨明这类错误的业务判据，而不是再添加一句未测声明。

## 已检查的实际文件与已排除的重复方向

实际文章路径不是solutions/networking，而是：
- `gamelibrary-publish-broker/solutions/programming/client-prediction-authority-boundary.md`
- `research/experiments/client-prediction/test_prediction.py`
- `research/experiments/deep-model-qa/stress_models.py` 的prediction部分与README范围。

现有测试已经覆盖新serverTick但同ack仍接受纠正、过期快照、倒退/超前ack、epoch、历史耗尽、一次性效果及每serverTick消费预算。故不把“相同ack误丢新纠正”当作新缺口。

当前Snapshot只有epoch/tick/ack/x；Client.reconcile用权威x加未确认axis后缀和，既不读取速度、碰撞体也不读取其他实体。200种调度的独立判据同样是输入前缀/后缀之和；随机权威偏移是外部注入整数，而非真实相互作用。它们无法表达“自己的输入和基线都正确，但读取了错误时间的另一实体”。

文章“先恢复所有影响运动字段”及Unity部分快照说明已有方向性提醒；本文建议把这个提醒变成可审查的**依赖集合与时间契约**，不是将现有内容重写成未经验证的全世界回滚承诺。

## 实际读取的一手资料

1. Unity，**Prediction edge cases and known issues**，Netcode for Entities **1.4.1**：
   https://docs.unity3d.com/Packages/com.unity.netcode@1.4/manual/prediction-details.html
   本轮实际读取正文及页面元数据：版本1.4.1，页面生成器标记2025-05-13；这不是当前最新包声明。定位 **Interactions between predicted ghosts using partial snapshots**、Example、Possible mitigations。

   文档说明部分快照只回退/重模拟其中的ghost，其余实体可保持较新的状态；两者交互可能出错。列出的缓解包括分组发送、调整优先级或交互策略，且选择有代价。**本门槛没有验证这些缓解在项目中的正确性，也不将自定义模型说成Unity ECS运行结果。**

2. Gabriel Gambetta，**Client-Side Prediction and Server Reconciliation**：
   https://www.gabrielgambetta.com/client-side-prediction-server-reconciliation.html
   本轮实际读取Server reconciliation和Odds and ends，页面未明确首发日期。它解释输入序号后缀重放，并指出多玩家情形即使确定性、无人作弊，纠正后也可能仍不匹配。本文不复制其图示、数字或协议实现。

两者分别为引擎官方材料和原作者说明，不拿同一内容译文当独立复核。访问日期2026-10-31。没有重试既有Valve403页面或绕过访问限制。

## 原创手算反例：不是Unity复现，也不是物理求解器

先选一个可完全枚举的离散政策：A在整数格移动，B是另一实体占据的禁入格；每tick先取得该tick的B格，然后A处理一次+1意图。候选格若等于B格，A本tick留在原地。没有连续碰撞、面积、随机数、网络运输或作弊。

权威基线是tick0：A=0、ack=0。A待重放的命令为seq1:+1、seq2:+1；明确本例seq1/seq2分别对应tick1/tick2，**不推广成seq总等于serverTick**。B在tick1为1，tick2为3。

|计算|tick1读到的B|tick1结束A|tick2读到的B|tick2结束A|
|---|---:|---:|---:|---:|
|独立手算权威/同时间依赖重放|1|0（格1被占）|3|1|
|只恢复A，B冻结在客户端tick2|3|1|3|2|

两行使用相同有效权威A基线、ack和输入后缀，唯一变化是依赖B的时间归属。第二行虽然确定、没有重复输入或重复效果，结果仍不同。

这个表是原创解析推导，尚未执行。它不声称B在Unity中恰好按这个更新顺序，也不暗示所有实体必须一起回滚。若随后送达完整tick2、ack2、A=1快照，客户端可以收敛；这里暴露的是**重放期间的错误交互与纠正幅度**，不是已经证明永久失同步。

## 最小后续交付物与判据

优先补既有NET文章一个“纠正包能恢复哪些重放依赖”的工程小节：
- 记录基线stateTick、已最终处理命令范围、输入到模拟tick映射，以及重放会读取的其他状态；不把有效ack当作依赖完整证明。
- 每个重放tick的依赖应有明确时间来源，或明确声明项目允许的近似/跳过交互政策；不能把缺失历史默默当当前状态。
- 按项目选择分组纠正、保存必要依赖历史、调整预测交互范围或等待权威结果。公开引擎缓解选项不是本库已实现的万能修复。

若需要可执行补充，只做上表的固定小模型与独立字面预期：完整依赖轨迹得[0,1]，冻结最新依赖得[1,2]；额外证明依赖轨迹缺tick时明确返回“不能按此合同精确重放”，不静默填最新值。记录原始输入和首个分歧tick，不做UDP/socket模型、不添加大量随机种子或新增文章计数。

**实施门槛**：只有把“依赖缺失的接收/拒绝策略”写清并获得独立判据，才值得执行；单纯输出两行算术结果并不能验证生产快照分组或Unity修复。没有实际Unity运行环境时，源深度+手算验收表本身可能比新增一个教学脚本更有价值。

## 实际能力与停止条件

本轮只运行了PATH/目录检查：`command -v Unity`、`unity-editor`、`dotnet`均未找到；`godot`为`/usr/local/bin/godot`，/opt未显示Unity安装。此结果只说明检查到的执行入口，不是全盘搜索或安装不存在证明。

现有Godot可以用于其自身确定的场景，但不能冒充Netcode for Entities的partial snapshot执行。当前不建议为了这个门槛安装Unity/SDK或用临时UDP模拟制造运行数量。

本轮结束于一个源支持、可手算证伪的依赖时间问题。没有修改原模型、没有宣称它违反单角色加法合同，也未宣布任何Unity缓解已奏效。下一步可以先深化文章验收协议，是否值得小模型由协调者决定。
