---
id: SOL-SFX-001
title: 交互音乐状态交接契约：玩法意图不等于可听见的切换
type: solution
status: source-backed
primary_discipline: SFX
related_disciplines: [MUSIC, PROG, DESIGN, QA]
related_roles: [interactive-audio-designer, composer, audio-programmer, gameplay-programmer, qa-engineer]
updated_at: 2026-11-01
verification_method: FMOD 2.04.00 官方文档与 Wwise 历史一手案例核对；新增 MAGI/FFXV 历史演讲正文及指定图页审阅与未执行内容接收问题；原创假端口模型7项测试及200条有界调度复核；补充 FMOD 虚拟化及事件／bank 生命周期的官方文本溯源与未执行观察、退出合同；未运行中间件或游戏引擎
sources:
  - https://www.fmod.com/docs/2.04/api/managing-resources-in-the-core-api.html
  - https://www.fmod.com/docs/2.04/studio/advanced-topics.html
  - https://www.fmod.com/docs/2.04/api/studio-api-eventinstance.html
  - https://www.fmod.com/docs/2.04/api/studio-api-bank.html
  - https://www.fmod.com/docs/2.04/api/studio-guide.html
  - https://www.fmod.com/docs/2.04/studio/authoring-events.html
  - https://qa.fmod.com/t/best-practices-for-tempo-sync-beatmatched-timing-across-events/20836/2
  - https://www.gamesounddesign.com/in-depth-creation-of-dynamic-music-in-a-video-game.html
  - https://www.gamesounddesign.com/in-depth-creation-of-dynamic-music-in-a-video-game-page-four.html
  - https://github.com/audiokinetic/WwiseIncludes/blob/be96b3af20bf27647f458bac10d973a63cd75e02/SDK/include/AK/SoundEngine/Common/AkSoundEngine.h
  - https://www.gdcvault.com/play/1024486/Epic-AND-Interactive-Music-in
  - https://media.gdcvault.com/gdc2017/Presentations/Iwamoto_Sho_Epic_AND_Interactive.pdf
---

# 交互音乐状态交接契约：玩法意图不等于可听见的切换

## 解决的问题与适用范围

战斗强度每帧变化，音乐却应在合适的拍、小节或乐句边界转场。把“进入战斗”直接做成每帧播放一次音乐事件，会把持续音乐生命周期与强度更新混在一起；具体后果可能是重启、重叠实例或触发实例限制，不能假定各中间件行为相同。

本条给出**原创团队交接契约**，目标是：同一音乐会话只启动一个受控实例；玩法只表达意图，音乐工程决定转场；快速反复变化、失败和迟到回调都可追踪。主要面向单一背景音乐实例，不涵盖节奏游戏输入判定、多首独立事件的采样级同步、动态变速或网络音乐同步。

证据分层：FMOD 2.04.00 文档支持当前版本的创作机制；Wwise 案例只作为历史设计反例；下文适配器、职责表与验收项是本文建议，**不是厂商提供的现成实现，也不是已通过运行验证的方案**。

## 已核对的机制，不作跨产品等价推断

- **FMOD 手册 2.04.00（页脚标记日期 2026-09-29；不据此断言软件发布日期）**：事件实例独立，可有不同本地参数。transition region 与 magnet region 可按拍值/小节量化；transition marker 与 loop region 不具备同样量化选项。多个可用逻辑标记发生竞争时，垂直位置靠上的标记优先；transition timeline 可在到达目标前承载过渡。以上分别见官方手册 §4.1.3、§4.11.1–4.11.4。本文只采用这些边界，不把完整手册改写成教程。[FMOD：Authoring Events](https://www.fmod.com/docs/2.04/studio/authoring-events.html)
- **FMOD 官方人员案例（2023-11-06）**：Jeff 描述用条件决定 transition region 的退出或 magnet region 的进入，再通过量化控制节奏对齐。其示例不是“在游戏帧回调中自行估算下一小节”。[FMOD 官方论坛原答](https://qa.fmod.com/t/best-practices-for-tempo-sync-beatmatched-timing-across-events/20836/2)
- **Wwise 历史项目**：Louis-Xavier Buffoni 的原作者案例建立于 Wwise 2010.1.3；以 Intensity Switch 驱动音乐容器，并处理段落尾音。作者在文章中把 Switch 值简称为 state，**不表示可把 SetSwitch API 随意换成 SetState**。[原案例：Game Interface / Assigning Content](https://www.gamesounddesign.com/in-depth-creation-of-dynamic-music-in-a-video-game.html)
- **历史快速变化反例**：同一案例第四部分指出，待转场目标尚未开始时可能撤回旧转场，快速变化可能跳过中间强度；目标已经开始则不能假定仍可撤回。因此音乐图不能只设计相邻强度之间的边。[原案例：Jump Transitions](https://www.gamesounddesign.com/in-depth-creation-of-dynamic-music-in-a-video-game-page-four.html) 这是该案例语义，不是对 FMOD 或当前 Wwise 的取消保证。
- **Wwise API 边界证据**：本轮访问日期为 2026-10-31；已锁定提交 `be96b3af20bf27647f458bac10d973a63cd75e02`，历史公开头文件标明 v2017.2.0 Build 6500，PostEvent 为异步提交；SetSwitch 带关联 game object，SetState 签名没有该参数；音频处理是否使用独立线程受配置影响。这里只据此警告“提交不等于播放”“名字相似不等于作用域相同”“不能猜测回调线程”，不提供当前 SDK 接入代码。[Audiokinetic 官方公开头文件](https://github.com/audiokinetic/WwiseIncludes/blob/be96b3af20bf27647f458bac10d973a63cd75e02/SDK/include/AK/SoundEngine/Common/AkSoundEngine.h)

## 一份可交接的最小合同（原创建议）

### 1. 三种状态必须分别记录

| 字段 | 含义 | 禁止推断 |
|---|---|---|
| desired_mode | 玩法当前希望的音乐强度，例如 Explore / Tension / Combat | 不表示音乐已经切换 |
| submitted_mode | 适配器最近成功提交给当前实例的目标值 | 不表示规则已命中或素材已就绪 |
| observed_section | 从实际支持的观察机制获得的音乐段落；未知时明确 unknown | 不用参数设置返回值冒充已听见 |

每条记录至少附 `session_id、generation、revision、game_time、event_identity、result`。若中间件观察值不能反推出准确段落，则保留 unknown，并用 profiler 捕获辅助调试，不能“补全”一个想当然的段落。

### 2. 生命周期与意图更新分离

采用单写入者管理 `Stopped / Starting / Active / Stopping`：

1. **进入会话**：确认资源准备条件与实例作用域；创建或启动一次。初始目标值在何时设置，须按所选版本 API 与项目验证，避免先听见默认段落后才修正。
2. **更新意图**：更新 desired_mode 与 revision，不重新启动音乐。只有提交成功才更新 submitted_mode；失败保留待提交状态，按有界重试策略处理。
3. **同值去重**：仅当当前 generation 已成功提交相同值且未失效时才去重。切换场景或重建实例后不能沿用旧缓存。
4. **连续强度可合并**：普通强度请求使用“最新值优先”，而不是强制逐个播放过期状态。胜利、死亡、章节结束等一次性叙事事件使用独立命令语义，不能被强度合并器吞掉。
5. **退出会话**：明确淡出/立即停止策略，以及何时释放实例与资源。停止与释放不是同义词；具体 API 顺序必须按目标 SDK 确认。
6. **迟到通知**：携带或关联旧 generation 的通知只能更新旧会话记录，不得清空新实例句柄；对象与回调数据的寿命必须覆盖仍可能到达的通知。

异步启动、资源就绪与重试任务在执行前必须联合检查 **generation、生命周期和 revision**：已退出或已取消的 Starting 会话不得因迟到资源就绪而重新启动；退出时撤销待启动/重试任务，无法撤销的完成通知只做旧任务清理。重试应读取当前最新 desired_mode，或确认其捕获的 revision 仍有效；同 generation 的旧请求不能覆盖已提交的新意图。资源清理需保持句柄归属，不能释放新会话资源。

这里的“成功提交”只是适配器成功边界；若底层 API 返回值无法检测素材或路由错误，还必须单独保留诊断/观察通道。不要建立“未观察到目标就不断重新 Play”的自激恢复循环。

FMOD 2.04 的复音限制可通过 `START_FAILED` 报告启动拒绝；此路径不会产生 `STARTING`、`STARTED` 或 `STOPPED`。适配器应把它作为独立失败结果处理，按当前 generation 与句柄归属回收或决定有界重试，不能无限等待不存在的 STOPPED。`start` 返回成功仅表示提交，不据此把本地 Starting 标为 Active；Active 的工程定义与观察证据须明确，应用状态并不自动对应SDK枚举。[EventInstance API：callback types](https://www.fmod.com/docs/2.04/api/studio-api-eventinstance.html#fmod_studio_event_callback_type)

同值去重假设由此适配器独占参数写入；若外部系统或事件逻辑也会改同一值，先仲裁或使缓存失效。submitted_mode记录的是提交，不冒充参数实时读值。

#### 场景退出时，事件释放与 bank 持有是两项责任

FMOD 2.04 文档中，`stop(ALLOWFADEOUT)` 允许 AHDSR 的 release 与 DSP 尾部继续；`EventInstance::release` 则标记实例待释放，在 stopped 后由 Studio 更新处理销毁。它既不是 stop，也不建立 bank 的保留权。[EventInstance：stop mode / release](https://www.fmod.com/docs/2.04/api/studio-api-eventinstance.html#studio_eventinstance_release)

另一层的 `Bank::unload` 会销毁相关对象、卸载样本并使相关句柄失效；样本加载引用计数也不能阻止整个 bank 卸载。[Bank：unload / unloadSampleData](https://www.fmod.com/docs/2.04/api/studio-api-bank.html#studio_bank_unload) 因而依次请求“允许淡出、释放实例、卸载 bank”，不能被记录成尾音已经完整完成。

**原创未执行退出例：**场景 A 的逻辑对象要结束，但产品希望 A 的音乐尾部继续。这里需要选择资源寿命，而不是只排列三个 API 名称：

- **保留尾部：**停止接受 A 的新意图，按已约定的事件停止／释放策略处理；让音频管理方继续持有所需 bank，而非随 A 的逻辑对象一起卸载。管理方收到项目定义的结束记录后，还须收束其他使用者，再决定卸载。代价是延长资源驻留；这只是保留所需资源，不是保证完整可听输出。
- **优先回收：**明确允许中断，并处理整体卸载后的对象失效。不能一面立即卸载，一面把早先提交 ALLOWFADEOUT 当作已兑现的尾音承诺；“立即回收”在这里是产品优先级，不是同步释放耗时保证。

通知路径也要保留这个选择。DESTROYED 表示即将销毁，不单独说明自然停止或淡出成功；STOPPED 也不是扬声器声学尾部结束回执。若已调用 release，实例可能在通知排队到游戏线程处理之前失效。搬运的应是具有正确寿命的、已复制的项目身份、通知类型及退出政策记录，而非假定届时还能查询原句柄。不要因一次先前的有效性检查，继续盲目轮询已释放对象。

继续服务 Studio update，并按初始化模式处理回调线程；不能阻塞等待尚待自己提交处理的命令，也不能把 deferred marker/beat 选项推广到所有通知。[Studio API Guide §13.4、§13.11](https://www.fmod.com/docs/2.04/api/studio-guide.html) 具体错误、超时及共享使用者收束仍须项目实现；前文 START_FAILED 的独立失败路径不变，不能让它等待不存在的 STOPPED。

本例没有运行中间件或试听，不证明总线／混响的所有尾部、跨 bank 依赖、流式 I/O 或用户内存回收安全。既有假端口与虚拟化证据也不覆盖这里的卸载行为。版本、读取范围与限制见[来源记录](../../research/source-notes/fmod-event-bank-teardown.md)。

### 3. 谁拥有时间

玩法拥有意图产生时间；音乐工程拥有允许的退出点、目标入口和桥段；音频集成拥有调度与输出诊断。不要用渲染帧累计出的下一小节时间代替中间件音乐时间线，然后在那个帧上临时启动目标。

建议记录 `intent_time → dispatch_time → observed_transition_time`，并注明各时间戳的时钟域。观察回调到达游戏线程的时间不等于声卡出声时间；没有时钟映射或外部录音测量，不应报告“端到端延迟精确到采样”。

例如固定 120 BPM、4/4 时每小节 2 秒。这只是音乐周期的算术例子，**不是请求必在 2 秒内可听见的服务承诺**：资源准备、规则优先级、桥段、边界附近的调度和输出缓冲都须另测。若设计要求急迫反馈，可把即时提示音与随后量化的背景音乐转场拆开，而不是为追求立即响应破坏全部音乐规则。

FMOD 2.04 API Guide §13.4/13.8/13.11也直接说明命令异步处理、样本加载与依初始化设置变化的回调线程；deferred marker/beat设置不能推广为所有回调都在游戏线程。[当前版本依据](https://www.fmod.com/docs/2.04/api/studio-guide.html)

回调处理建议只搬运小型有界记录，避免磁盘 I/O、阻塞等待和直接调用游戏对象；具体线程归属、同步方式与溢出策略由音频程序员按集成版本验证。这里提出实时路径防护要求，并未验证某个回调一定运行在音频线程。

#### 制作案例：提前进入预结束段，不等于最终同步已解决

《Final Fantasy XV》的 MAGI 制作演讲给出另一项内容约束：为了保留乐曲推进，某些转场使用逐曲安排的同步点，而非任意拍点；讲者举出可能等待16小节、约14秒的情形。其结构将主循环到预结束段设为音乐优先，再将预结束段到结束段设为同步优先。利维亚桑案例分别用龙卷风与结尾场景启动这两阶段。[GDC 2017 原始幻灯片，PDF第26–27、31页](https://media.gdcvault.com/gdc2017/Presentations/Iwamoto_Sho_Epic_AND_Interactive.pdf)

第32页的最终同步图还区分固定场景片段与可变 QTE、音乐过渡时间。因此，准备进入预结束段和最终高潮的时间编排不能压成一个“提前触发”指令。这里是该项目公开的制作方案，不是通用等待上限，也不是当前中间件的调度保证。

**原创接收问题：**一个需要音乐结束落点的遭遇，是否同时交代了准备信号、允许的音乐入口、最终编排的固定段落与可变玩家操作窗口？若只有终止事件，不应仅凭合法同步点承诺既保留完整乐句又立即落到结尾。窗口不足时，应明确讨论改写过渡、调整入口或接受时序折中；这些是接收方的选择，不冒称 FFXV 的兜底规则。

本例不推断图形比例、时长相加关系或预测算法，也未验证听感及运行时行为。资料版本与阅读范围见[来源记录](../../research/source-notes/ffxv-pre-end-music-window.md)。

### 4. 虚拟化必须注明观察层：事件非虚拟，不等于关键声道参与混音

FMOD 文档给出一个具体反例：`EventInstance::isVirtual` 查询成功且输出状态为 false 时，底层部分乃至全部 Core 声道仍可能因软件声道限制而虚拟化。该事件查询针对事件复音限制，不是各声道状态的汇总。[Core 资源管理 §9.1.7](https://www.fmod.com/docs/2.04/api/managing-resources-in-the-core-api.html)、[EventInstance::isVirtual](https://www.fmod.com/docs/2.04/api/studio-api-eventinstance.html#studio_eventinstance_isvirtual)

这里补强的是 `observed_section` 的**证据来源**，不重定义前文 Active，也不修改旧模型的生命周期语义。即使段落位置已知，仍须另问承载关键信息的声道是否参与实际混音。SDK 的 real 是中间件状态，不是扬声器输出或玩家听见的回执。

以下是原创观察决策表，尚未接入或执行。每行都应保留**查询返回码／回调类型、事件与相关声道身份、观察时间及其时钟域**；查询失败不能填成 false。分别采集的事件、声道和位置状态不是一个原子快照。

| 已取得的有限观察 | 可以记录什么 | 仍需核对的证据或决策 |
|---|---|---|
| 事件查询成功且 isVirtual 为 false | 该次事件层观察为非虚拟 | 哪个 Core 声道承载关键入口？不能据此代填该声道的虚拟状态 |
| 相关 Core 声道仍有效，查询为虚拟 | 保留的声道当前不作为 real 声道参与混音 | 内容位置与返回策略是什么；信息入口是否已在虚拟期间经过？ |
| 已有独立诊断确认容量抢占，随后该声道句柄失效 | 不把这个已被抢占的声道记为“等待恢复” | 是否仍有重播意义？**句柄失效本身不能反推抢占原因** |
| 收到 START_FAILED | 按前文独立启动拒绝路径记录 | 不归类为已启动但暂时虚拟，不等待该路径不存在的 STOPPED |
| 相关声道查询为 real，或段落位置已推进 | 只记录对应层、对应时刻的状态 | 仍需路由与输出证据；不能升级为关键入口已送达或已被理解 |

**条件例子（原创、未执行）：**一个非循环提示由可辨识的入口和较长尾部组成。假定同一有效 Core 声道在整个入口期间虚拟，随后在内容尚未结束时恢复为 real；期间没有 seek、重新触发、循环、变速或停止。Core 默认策略让虚拟位置推进并在返回时从相应位置继续，因此“后来成为 real”不能补证此前入口已送达。Core 的 `FMOD_VIRTUAL_PLAYFROMSTART` 是另一种返回策略，但不能据此声称整个 Studio 事件及其所有乐器会重启。[Core §9.1.6](https://www.fmod.com/docs/2.04/api/managing-resources-in-the-core-api.html)

这个例子不保证一定恢复，也不假定尾部仍有信息价值。项目应分别决定：尾部是否足以表达当前意图、延迟入口是否仍有效、是否需要另一个语义适当的提示；不要因句柄存在或段落推进就关闭待确认项。它与[关键声音信息的替代通道](../accessibility/critical-sound-information-contract.md)互补，不能让视觉等替代信息随声音虚拟化一起消失。

Studio 的停止、拒绝新增与 Virtualize 也不是同一结果；不要把 Core 指南中的 stealing 简称推广到全部 Studio 策略。[Studio §16.4.1–16.4.2](https://www.fmod.com/docs/2.04/studio/advanced-topics.html) 本节只核对文档和提出观察合同，没有运行中间件、听音或测量设备输出；旧假端口测试不覆盖虚拟化。文档版本与边界见[来源说明](../../research/source-notes/fmod-virtualization-observation-boundary.md)。

## 音乐图与玩法合同一起验收

以下表是交付接口建议，不是声称所有工作室都采用这些岗位边界。

| 责任接口 | 应交付的证据 | 常见交接缺口 |
|---|---|---|
| 作曲 / 音乐设计 | 各模式音乐意图、节拍信息、入口/出口、桥段与尾音、可接受响应区间 | 只交线性混音，未说明可切位置 |
| 交互音频设计 | 参数值映射、完整有向转场图、优先级、紧急路径、默认/缺失状态 | 只听相邻上升路径，忽略下降与跨级 |
| 玩法程序 | 强度判定、滞回/最短驻留策略、终局优先级、会话边界 | 每帧重播；暂停或离开场景后仍投递 |
| 音频程序 | 单实例所有权、资源就绪与失败处理、版本/线程合同、可观测日志 | 把 API 接受请求记成已播放 |
| QA + 音频设计 | 时序压力脚本、profiler 捕获、听感记录、平台/版本/素材哈希 | 只看参数变化，没有听音与实例数检查 |

滞回用于减少玩法状态抖动；量化用于约束音乐切换时机。二者不能互相替代。阈值和驻留时间应来自设计试听，不在公共条目中发明“行业标准毫秒数”。

## 最小验收矩阵（尚未执行）

| 输入/故障 | 应检查的不变量或产品决策 | 必留证据 |
|---|---|---|
| 连续 600 帧提交同一模式 | 会话启动次数为 1；普通更新不得增加音乐实例 | 适配器日志 + 实际实例列表 |
| 一个小节内 Explore→Tension→Combat | 不要求 Tension 必须可听见；Explore→Combat 有有效设计路径 | 实际转场路径与录音 |
| Combat→Explore，紧邻边界前后各测试 | 离开战斗的响应与尾音满足已声明规则；无通用“立即撤回”假设 | 带时间戳的 profiler 捕获 |
| 同一边界切到不同目标段落 | 分别检查退出节拍与目标乐句位置；对齐切换边界不自动代表乐句衔接正确 | 两端拍号、入口设置、录音 |
| 参数请求失败后重试 | 不把失败缓存为已提交；恢复后仍能应用最新目标 | 返回值和 revision 轨迹 |
| 复音限制拒绝启动 | 独立处理 START_FAILED，不等待 STOPPED，不无限重启；旧实例不影响新会话 | 限制配置、回调与句柄轨迹 |
| 资源尚未就绪 / 素材缺失 | 不产生无限 Play 循环；明确静音、保留旧音乐或降级策略 | 失败原因及恢复记录 |
| Starting 尚未完成即退出，随后资源就绪 | 取消的会话不得启动；资源按原任务归属释放 | 生命周期、任务取消与句柄记录 |
| 旧 revision 重试晚于新模式成功提交 | 旧请求不得覆盖最新意图；重试读取最新值或丢弃失效任务 | revision、提交顺序及实际参数轨迹 |
| 会话 A 退出，B 启动，A 回调迟到 | A 通知不能停止或清空 B | generation 与实例对应表 |
| 胜利事件与强度下降同时发生 | 按产品优先级只产生预期终局行为 | 规则优先级、最终路径 |
| 暂停、切后台、恢复、场景重载 | 是否继续音乐由产品明确；恢复不得意外复制实例 | 平台、配置及前后实例数 |

[原创假端口状态模型](../../research/experiments/audio-lifecycle/README.md)已执行7项测试，含4096条长度4的有界动作序列；[独立种子复核](../../research/experiments/deep-model-qa/README.md)另执行200个调度。它们覆盖声明的成功缓存、生命周期、generation/revision失效与START_FAILED路径；守卫不满足动作可为空操作，不能当作4096个不同产品场景。这些测试**不能证明**量化、尾音、流式加载、混音或设备时延正确。升级为运行验证必须提交目标版本、最小音频工程、合法测试素材、输入脚本、捕获与听感结果。

## 取舍、失败模式与后续验证

- 一个持续事件/容器便于集中音乐规则，但大型音乐图需要命名和优先级审查；这不是所有配乐项目都必须采用的结构。
- 默认“最新强度优先”可能丢弃戏剧性中间段。若某桥段必须完整播完，应把不可打断期作为显式合同，而不是依赖偶然调度。
- 每条跨级边都手工制作可能膨胀成本。允许共享过渡或兜底路径，但要写明允许哪些听感折中，并覆盖全部可达输入。
- 本轮已读取来源正文；未运行 FMOD、Wwise、Unity 或 Unreal，未下载项目、试听素材或观看视频。Wwise 当前官方文档访问受阻，未绕过限制；因此不把历史资料升级为当前兼容性结论。
- 下一步最有价值的验证是 **FMOD 2.04 的三模式最小工程**：固定合法测试音色、一个持续实例、显式条件/量化/优先级，重放上表并确认快速变化期间的实际行为；未验证前不对取消机制、采样精度或跨产品迁移作保证。

## 关联知识与检索入口

问题关键词：interactive music、music state、quantized transition、transition region、magnet region、exit cue、music switch container、音乐强度抖动、音乐事件重复启动。

关联：[固定 Tick 与引擎表现边界](../programming/fixed-step-simulation-boundary.md)、[玩法程序职责](../../roles/programming/gameplay-programmer.md)。待研究关联：异步资源生命周期、音频 QA 与平台时延。岗位职责与交付证据见[交互音频设计](../../roles/audio/interactive-audio-designer.md)；该档案也有来源与适用范围，不用本条有限接口表替代。

来源访问日期：2026-10-31。保存原创契约分析和必要的短述，不转载中间件源码、音乐、工程素材或原文全文。

## 素材边界的互补验收

[音乐循环素材的 PCM 帧合同](../music/pcm-loop-frame-contract.md)提供独立的作曲交付检查：前置、主体、尾部与接口端点映射。它已执行有限离线提取，但没有替代本条尚未执行的真实中间件转场验收。

[离线 stem 增益边界](silent-stem-normalization-boundary.md)提供独立的实际离线混音证据；它不升级本文假端口模型的中间件生命周期或可听切换结论。
