# 延迟补偿：命令目标、采用目标与历史样本不是同一个量

2026-11-01。本文只核对 Valve 官方 SDK 的一个固定源码版本，并给出原创手算；没有运行游戏、网络或命中测试。关联[客户端移动预测与服务器纠正](../../../GameLibrary/网络与在线服务/实时同步/移动预测/客户端移动预测与服务器纠正.md)，不改变其原有验证范围。

## 固定来源中的时间选择

来源为 Valve 官方 `source-sdk-2013` 提交 **be57e3d01ac7d7aa6a2cacbfef187c0b46616db0**，不是对当前商业游戏或其他 Source 分支的保证。仓库名也不表示这些文件就是 2013 年的原始字节。

`StartLagCompensation` 先以命令 tick 减插值 tick 得到目标，再用有界的网络延迟加插值时长校验；差异严格超过 0.2 秒时改用延迟估计目标。这里的网络量直接来自 `GetLatency(FLOW_OUTGOING)`，不自行改称 RTT/2。历史记录按递增 simulation time 加到表头；搜索从新到旧，在条件允许时插值，否则复制选中记录。空历史、死亡记录及过大位移有退出路径。HL2MP 的 `FireBullets` 用 Start／Finish 包围基类调用。[S1–S3]

因此，接收方不能只问“客户端希望查哪个时刻”，还要问服务器是否保留了这个目标，以及实际用哪条记录或哪两条记录采样。一个有效输入序号并不回答这两个问题。

## 原创手算：更旧的命令不必得到更旧的查询目标

**以下数值全部人为规定，未执行。** 设 tick 间隔为 0.01 秒，服务器 tick 为 1000，插值量为 0.02 秒，转换为 2 tick；上述 API 返回的网络量为 0.06 秒。校验量为 0.08 秒，并假定在所配上限内，未被截断。两次试次互相独立，不讨论发送者权限或异常流量。

| 命令 tick | 减去 2 后的初始目标 | 服务器到目标的时间差 | 校验量减该时间差 | 采用目标 tick |
|---:|---:|---:|---:|---:|
| 992 | 990 | 0.10 秒 | −0.02 秒 | 990：不进入替换分支 |
| 970 | 968 | 0.32 秒 | −0.24 秒 | 992：由服务器 tick 减去 8 得到 |

例子避开转换舍入及 0.2 秒比较边界；它是源码分支的理想算术说明，不是浮点执行结果或网络测量。第二行说明：直接把命令携带的旧时间当作最终查询时间，会误读服务器的接收政策。它不说明此政策对所有游戏都公平，也不是建议采用这组时长。

## 目标确定之后，还要辨别历史采样

继续**人为假定**被考察玩家已通过调用路径的选择和有效性检查，没有死亡或过大位移；`sv_unlag_fixstuck` 在本例关闭。取两条相邻、时间递增的记录：

- 9.88 秒，位置 x=2；
- 9.92 秒，位置 x=6。

其他位置分量不变。对于第一行的目标 9.90 秒，位置插值系数为：

$$
\alpha=\frac{9.90-9.88}{9.92-9.88}=\frac12,
\qquad x=2+\alpha(6-2)=4.
$$

第二行目标为 9.92 秒，与该记录时间相等，位置候选为 x=6。**这只是位置候选，不是整套姿态、最终放置或命中结果。** 本例不定义射线、骨骼、碰撞体或伤害，因此不能从 x=4／6 推出命中或未命中。

也不能反过来把“两条记录夹住目标”写成所有路径的保证。所读代码在不满足插值条件时有复制记录分支；例如搜索耗尽且没有更旧的下侧记录时，会保留最老记录并走复制分支，而非一律拒绝；这不等于取得了准确目标时刻。本文只推导上述已明确夹住目标的试次，不重建完整历史耗尽政策。

## 应交接哪一份时间账

以下是原创接收建议，不是 Valve 的日志格式：

| 要保留的区别 | 它帮助回答的问题 |
|---|---|
| 命令 tick、插值 tick 与初始目标 | 请求原本落在哪个时间，而不是笼统记录一个 ping |
| API 网络量、校验量、是否进入替换分支、采用目标 | 目标是保留还是被重新估计，不能只看命令时间 |
| 实际历史记录时间、插值关系或未处理原因 | 查询准备使用什么状态，而非假定目标恰好存在于历史 |
| 补偿涉及的对象／字段与后续查询结果 | 历史采样与实际命中分别有什么证据 |

只有前三项明确后，才适合继续定位“时间选择”和“命中查询”是否给出了不同预期。不能把一次玩家画面、一个命令序号或“已开启补偿”当作整条链路的解释。记录这些量也不意味着需要向客户端暴露服务器历史。

对象范围同样必须声明：此管理器不是全世界快照回滚；可选的 `fixstuck` 路径还会递归处理碰到的玩家，并有意越过外层的 `WantsLagCompensationOnEntity` 选择。因此，既不能说全世界都回到了同一时刻，也不能说只有外层选中的玩家才可能被移动。[S1] 本例关闭该分支，不为它编造运行结果。

如果要分析动态门或移动平台是否影响射击，必须再核对实际查询链、对象时间与过滤规则。2026-11-01初版只读到HL2MP包装函数，没有读完基类 `FireBullets`；下面是2026-11-03对同一固定提交的后续补读，仍不作“现在的门一定挡住历史目标”之类最终命中判断。与[预测纠正的依赖时间](prediction-dependency-time-contract.md)类似，对象时间应有明确含义；但该文的客户端重放问题不能替这里的服务器历史选择作证明。

## 回退了哪些玩家，不等于查询只看哪些对象

历史状态准备完以后，还需要真正进行碰撞查询。在所读HL2MP包装函数中，基类 `FireBullets` 调用位于 `StartLagCompensation` 与 `FinishLagCompensation` 之间。这只是调用次序；`StartLagCompensation` 存在提前返回的路径，不能仅凭调用发生就断言本次确实回退了某个玩家。沿类的继承关系核对后，本次继续读到 `CBaseEntity::FireBullets`：以服务端、非PORTAL、非TF、单发的路径为限，它根据发射起点、选定方向和距离构造终点，再调用 `AI_TraceLine`。[S3–S4] 单发的限定很重要；同一函数的多弹丸路径还包含部分弹丸采用扫掠体的分支，不能把全部武器都说成同一种线查询。

这次线查询带着 `MASK_SHOT` 和一个明确的过滤器。`AI_TraceLine` 最终进入 `UTIL_TraceLine`，由后者调用引擎的 `TraceRay`。这一层传入的是射线、内容掩码、过滤器和结果存放位置，不是把“刚才被补偿的玩家名单”当作唯一查询对象。[S5]

过滤器会排除指定的忽略对象，并检查游戏侧的碰撞规则；`MASK_SHOT` 则包含solid、moveable、window等内容类别。[S6] 因此，**没有被这套玩家补偿管理器回退，不等于被射线排除。** 反过来，进入补偿处理也不等于必然成为命中对象：实际射线、几何、掩码和过滤都还要成立。

还要区分游戏过滤回调与引擎自身的世界查询。此处过滤器继承的查询类型是 `TRACE_EVERYTHING`；固定接口说明另有 `TRACE_EVERYTHING_FILTER_PROPS`，后者才把静态道具句柄交给过滤回调。不能把已读的 `ShouldHitEntity` 条件说成世界几何和每个静态道具都逐一执行的统一流程。[S7]

这些代码把“历史准备”与“实际查询”接起来了，却仍没给出某一扇门的最终结果。若要查一个具体遮挡问题，下一步应提供该次射线起终点、对象的有效碰撞形状与类别、过滤结果和实际返回的trace，而不是只展示玩家历史坐标或延迟补偿开关。引擎内部如何完成几何查询、后续伤害处理是否生效，不由这个调用链单独证明。本次没有地图、角色、射线或伤害运行；也不能由此宣称所有未回退对象都处在同一个精确“当前时刻”。

## 原始来源与阅读边界

以下链接都固定到同一提交。读取日期为 2026-11-01；提交记录的 committer 日期为 2026-10-10，不表示本文所读文件恰在该次提交修改，也不确认任何商业发行版本。

- **S1** [player_lagcompensation.cpp](https://github.com/ValveSoftware/source-sdk-2013/blob/be57e3d01ac7d7aa6a2cacbfef187c0b46616db0/src/game/server/player_lagcompensation.cpp)：全文阅读；核心定位为 `FrameUpdatePostEntityThink` 241–343、`StartLagCompensation` 345–438、`BacktrackPlayer` 440–602；另核对后续恢复路径。本文没有宣称所有字段采用相同插值。
- **S2** [shareddefs.h，16–19](https://github.com/ValveSoftware/source-sdk-2013/blob/be57e3d01ac7d7aa6a2cacbfef187c0b46616db0/src/game/shared/shareddefs.h#L16-L19)：tick／时间转换宏。
- **S3** [hl2mp_player.cpp，640–659](https://github.com/ValveSoftware/source-sdk-2013/blob/be57e3d01ac7d7aa6a2cacbfef187c0b46616db0/src/game/server/hl2mp/hl2mp_player.cpp#L640-L659)：仅据这一包装函数建立调用次序，不视作完整射线或伤害实现审计。

新增来源于2026-11-03读取，同样固定到上述提交；没有更换为其他分支或当前商业游戏。

- **S4** [baseentity_shared.cpp，1563–2036](https://github.com/ValveSoftware/source-sdk-2013/blob/be57e3d01ac7d7aa6a2cacbfef187c0b46616db0/src/game/shared/baseentity_shared.cpp#L1563-L2036)：完整读取 `CBulletsTraceFilter` 和 `CBaseEntity::FireBullets`。继承关系定向核对HL2MP、HL2、Player、CombatCharacter、Flex、AnimatingOverlay、Animating与BaseEntity头文件；未把头文件检索称为整个SDK实现审计。
- **S5** [ai_debug_shared.h](https://github.com/ValveSoftware/source-sdk-2013/blob/be57e3d01ac7d7aa6a2cacbfef187c0b46616db0/src/game/shared/ai_debug_shared.h)：完整读取转发/宏路径；[util_shared.h，249–314](https://github.com/ValveSoftware/source-sdk-2013/blob/be57e3d01ac7d7aa6a2cacbfef187c0b46616db0/src/game/shared/util_shared.h#L249-L314)：定向读取线及扫掠体封装，不是引擎几何实现。
- **S6** [util_shared.cpp，212–313及378–402](https://github.com/ValveSoftware/source-sdk-2013/blob/be57e3d01ac7d7aa6a2cacbfef187c0b46616db0/src/game/shared/util_shared.cpp#L212-L313)：标准过滤、忽略列表与游戏碰撞检查；[bspflags.h，125–130](https://github.com/ValveSoftware/source-sdk-2013/blob/be57e3d01ac7d7aa6a2cacbfef187c0b46616db0/src/public/bspflags.h#L125-L130)：MASK_SHOT及相邻掩码定义。
- **S7** [IEngineTrace.h](https://github.com/ValveSoftware/source-sdk-2013/blob/be57e3d01ac7d7aa6a2cacbfef187c0b46616db0/src/public/engine/IEngineTrace.h)：完整读取接口、查询类型和静态道具回调说明；没有取得或运行引擎内部的碰撞实现。

2026-11-01初版访问 Valve 开发者站的 *Latency Compensating Methods in Client/Server In-game Protocol Design and Optimization* 页面时返回 403，未重试或绕过；未将搜索摘要、转载或旧论文机制拼接为本提交的实现证据。

本说明不包含编译、引擎、网络、模型或玩家实验，也不继承关联文章的测试。表格、位置算式和接收建议均为原创未执行分析；不转载大段代码或源资产。

---

[返回《客户端移动预测与服务器纠正》](../../../GameLibrary/网络与在线服务/实时同步/移动预测/客户端移动预测与服务器纠正.md)
