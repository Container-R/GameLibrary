# FMOD Core预约播放的时钟与执行顺序

一段提示音需要稍后开始，并在起播后淡入。程序给时间值加了4800个采样计数，等待却远长于预期；打开暂停菜单后，它又没有按现实中经过的时间响起。如果还接了手工混响，甚至可能出现干声仍在等待、混响已经有新输入的情况。

这几种现象需要分别检查：预约值属于哪个时钟，配置是否及时完成，以及哪条DSP路径先处理了声音。本文面向直接管理FMOD Core声道的音频程序员，在**内存样本已就绪、组层级与路由固定**的条件下，完成一次未来起播和线性淡入，再沿同一个例子诊断这些问题。读者需了解PCM样本和基本返回值处理；文中调用以FMOD 2.04官方文档为依据，伪代码用于表达实现顺序。

## 先把一次播放和它的时间归属对应起来

`Sound`保存可播放的声音资源；`Channel`表示一次播放。本文用C表示本次提示音的声道，用G表示C直接所属的`ChannelGroup`。组可以包含声道或其他组，因此“父组”必须相对当前对象而言，不能只看变量是否命名为`parentclock`。[1][2]

DSP是处理声音的节点。FMOD的`getDSPClock`返回两个计数：第一个属于当前对象的tail DSP节点，第二个属于直接父组的tail DSP节点。tail是该对象DSP链靠近输入的具名位置；这里关心的是这个位置所对应的时钟，而非一个任意全局计时器。对C使用`setDelay`或`addFadePoint`，要取**C查询所得的第二个值**。[1]

设C直接属于G，G又属于上一级组U：

| 查询对象与返回项 | 时钟归属 | 能否直接用于本次C的预约 |
|---|---|---|
| C的`parentclock` | G的tail DSP | 是，本文使用这一项 |
| G的`dspclock` | G的tail DSP | 归属相同，但分开查询不构成同一时刻的快照 |
| G的`parentclock` | U的tail DSP | 不能只因名字相同就替换 |
| C的`dspclock` | C自己的tail DSP | 不是这两个预约接口要求的父时钟 |

这些值的单位都是samples，本文称为sample ticks，以强调它们是相应时钟的计数。单位相同并不说明原点、当前读数和后续推进永远相同。官方文档说明DSP时钟默认同速，pitch调整会影响推进速率；`ChannelGroup::addGroup`还有默认开启的`propagatedspclock`参数，用于递归传播调用组的时钟值。[2][3] 因此，既不能断言父子组必然具有不同读数，也不能凭一次读数相等就把它们永久混用。

实践中先建立组层级，再创建预约声道，并保存“C直接属于G”这一关系。预约期间不重挂组、不释放G；释放组会将其输入移到master组，破坏这里固定时间归属的前提。[3]

## 用同一个父时钟算起点和淡入

下面是条件算例，数字不是实测日志。假设从C查到父时钟P=480000，希望再过H=4800 ticks开始，则：

```text
T = P + H = 484800       起播目标
D = 4800                淡入长度
F = T + D = 489600       淡入终点
```

设另一参考时钟M当前为960000。若误算`M + H = 964800`，再把这个数交给按G时钟解释的预约，G需要再走`964800 − 480000 = 484800` ticks，远多于原要求的4800。加法没有错，错在把M的坐标提交到了P所属的时间域。

未来起播和淡入使用同一个T：起播时间为484800，淡入点为`(484800, 0)`与`(489600, 1)`。`addFadePoint`在相邻点之间线性改变增益，并与其他音量设置共同缩放声音。[1] 所以在这两个点之间，淡入因子为：

```text
g(p) = (p − T) / (F − T)，T ≤ p ≤ F
```

其中p仍是G的时钟坐标。在487200处，因子为0.5；它不是输出功率的一半，也不表示最终混音幅度必然为0.5。素材幅度、声道和组的音量、衰减等还会影响结果。本例把C的基础音量显式设为1，再用fade points控制淡入。**不要先用`setVolume(0)`“准备静音”，再期待fade point中的1覆盖它**；这两个控制量共同缩放，基础音量为零仍会使声音静音。[1]

T以前的等待由`setDelay`负责，不能用“已经添加一个未来的零增益点”代替起播门控。本文只计算T至F之间的插值，不把这条公式延伸到首点以前或末点以后。两个点也不是一套等功率交叉淡化；两份素材互相替换时，还需检查[交叉淡化的增益与素材关系](../../音频制作/混音/交叉淡化时为什么声音中间变大或变小.md)。

H是准备和提交的提前量，D是创作选择的淡入长度，两者用途不同。算例中它们恰好相等，不是推荐配置。如果已知所考虑区间内该时钟稳定推进48000 ticks/s，4800 ticks才可换算为0.1秒；暂停或速率变化后，不能继续用这个换算推算现实等待时间。

## 暂停创建，全部设置成功后再放开

本次方法的输入是一个已经加载完成的内存样本Sound、有效的G，以及正整数H和D。系统已初始化，应用继续执行正常更新流程。样本应覆盖需要观察的淡入区间；若素材开头本身长时间静音，声音到达输出后的首个非零样本就不能直接代表预约起点。

若上游使用非阻塞加载，拿到Sound句柄还不够，需等到`FMOD_OPENSTATE_READY`才能播放。[4] 不要在读取P之后才开始等待文件加载。流式读取、运行中seek、重排已有fade points和复用旧声道各有额外状态，本例直接新建C，并让本次控制代码独占它的属性设置。G及祖先的暂停和pitch变化由项目明确管理，不能让未协调的另一段代码同时改变预约条件。

`System::playSound`可直接指定G，并以暂停状态创建C，给属性设置留下机会。[5] 顺序是：先取得暂停的新声道，准备属性，查询父时钟，设置两个淡入点及同T的起播时间，最后解除C自身的暂停。Derek Burnheim在FMOD论坛的2020年答复也采用了这条预约淡入顺序；其中的示例提前量只是当时的建议，不能替代当前项目的余量检查。[6]

下面是原创伪代码，采用C++风格的API调用。`检查`、`checked_add`和日志函数属于应用层，不是FMOD接口；`检查`在非`FMOD_OK`时立即跳到失败收尾，不执行后续配置。

```text
输入：已就绪的 sound、固定父组 G
      H > 0、D > 0
      minRemaining > 0   // 项目要求在最终检查时仍保留的余量
输出：成功提交记录，或明确的失败原因

C = null
result = system.playSound(sound, G, true, &C)
如果 result != FMOD_OK：
    记录 playSound 失败
    返回失败                // 不使用未成功取得的 C

检查 C.setVolume(1.0)
完成并检查本次必要的其他属性设置
// 若有自定义支路，应在此处完成接线及执行顺序检查。

检查 C.getDSPClock(null, &P) // 取第二项：G 的时钟
T = checked_add(P, H)       // 检查无符号整数加法溢出
F = checked_add(T, D)       // 溢出同样进入失败收尾

检查 C.addFadePoint(T, 0.0)
检查 C.addFadePoint(F, 1.0)
检查 C.setDelay(T, 0)       // 不设置预约结束点

检查 C.getDSPClock(null, &Pnow)
如果 Pnow >= T：
    记录目标已到或已过，进入失败收尾
如果 T - Pnow < minRemaining：
    记录剩余余量不足，进入失败收尾

检查 C.setPaused(false)    // 只解除 C 自己的暂停
记录 C、G、P、Pnow、T、F 及各步结果
把本次 C 的后续管理交回播放管理者
返回提交成功

失败收尾：
    保存首个失败步骤和原因
    cleanupResult = C.stop()
    单独记录 cleanupResult
    不再把 C 当作仍可配置的播放对象
    返回失败
```

`setDelay`的第二项是可选结束时间，0表示忽略这一项，并非在绝对零时刻停声。[1][2] 本例不设置结束预约，由素材与播放模式决定后续结束方式；也不对淡入终点之后的增益作额外推断。

错误处理需要保持对象边界。失败收尾只针对这次成功创建的C，不能顺便停止G中的其他声音。`stop`成功或声音自然结束后，Channel句柄会失效；不能继续设置它，也不能像Sound一样对Channel调用`release`。[1][7] 若收尾返回`FMOD_ERR_INVALID_HANDLE`，保留原错误并废弃句柄。若返回其他错误，单独上报收尾未确认成功，不能把“尝试过stop”记成“已确认停止”。这里没有释放sound或G：它们可能被共享，且必须由各自所有者维持到所有相关使用结束。

### 重新读钟只能筛掉迟到，不能锁住未来

初次读取P之后，属性调用、线程调度和其他工作都会消耗时间。H不能仅凭“4800看起来够大”确定。项目应在目标设备和代表性负载下，检查从读钟到完成提交的控制路径，以及混音块、调度停顿和资源竞争对这条路径的影响，再为H及`minRemaining`选择余量。H越大，临时提示的响应等待也越长，这是可靠提交与响应速度之间的取舍。

第二次读到Pnow，能发现已经过期或已不足项目余量的请求，却不是与后续`setPaused(false)`组成的原子操作。线程仍可能在两者之间停顿；即使所有调用返回成功，也不能据此证明没有错过目标。不要让磁盘读取、等待其他任务等不受控工作夹在最后检查与放开之间，也不要把“提前两个混音块”写成适用于所有项目的保证。[6]

本例采用明确的应用政策：发现迟到或余量不足，就放弃这次新声道，按失败路径收尾。若业务允许改期，可以另建一次请求、重新读取父时钟并重新计算T和F；那是一个新的目标时刻，不能对外仍称原预约按时完成。这里无需猜测FMOD收到过去时间戳会怎样补偿。

## 暂停G，会保留剩余的2400 ticks

继续前面的T=484800。假设配置已经完成，G在自己的时钟到482400时实际暂停，期间没有换组或改变预约。此时剩余距离是：

```text
484800 − 482400 = 2400 ticks
```

暂停会冻结相应对象的播放进度和时钟；父组暂停也会使子对象有效暂停。[1] 因而现实中过了三秒，并不会替暂停的G走完这2400 ticks。恢复后，仍需它的时钟走到484800。

还要区分两个不同操作：

- **暂停G。** C使用的父时钟就是G的时钟，这个预约距离随G一起冻结。
- **只暂停C。** 不能据此推断G的时钟也冻结；G可能继续前进，甚至越过原T。再次放开C时，应重新判断业务是否还需要这次预约，而不是沿用“仍剩原来的距离”的假设。

`getPaused`查询的是对象自己的暂停设置。因此C报告`false`，只说明C本地没有设置暂停，不足以证明G及祖先链都在运行。[1] 日志应分别记录暂停对象、实际生效时对应的时钟和各对象的查询结果。应用发出暂停请求的墙钟时间，不能直接当作G实际停止在482400的证据。

如果提示音应该随游戏音频暂停，这种行为正合需求。如果它必须在暂停菜单中仍按现实时间出现，应将它的暂停与路由政策另行设计，例如预先使用不随该组暂停的播放路径。给冻结的G填入另一个时钟M的数字，不会把它变成墙钟倒计时；临时换组也不能在未重算和核对的情况下保留原预约。

## 干声仍在等待时，检查谁先拉取混响输入

正常组路径之外的手工连接，会带来第二种失效机制。继续使用C和G，再把C的一条支路送到自定义混响R。下面是原创概念图，箭头表示信号流向，不代表执行先后，也不展开每个对象内部的DSP节点。

```text
C ──→ G ──→ 输出
└───→ R ──→ 输出
```

**拉取（pull）**指下游需要数据时，促使尚未执行的上游节点运行。`STANDARD`连接能够执行尚未执行的输入；`SEND`连接只读取输出节点处理时已经存在的输入缓冲，还需要另一条STANDARD或SIDECHAIN路径使输入产生数据。[8] `DSP::addInput`默认使用STANDARD，所以把一条支路叫作“混响发送”，不代表它已经是SEND连接。[9]

FMOD的手工混响教程给出一个具体风险：R先拉取C，但预约依赖的时钟和等待处理在所属组路径中。于是G的干声路径仍处于delay状态，R却已经取得输入。[10] 这时重复修改T并没有解决先执行哪条路径的问题。

针对这个手工图，可以沿两种方向处理：

1. **让G路径先执行，R后执行。** 官方示例在创建声音所属组之后，才把R接到master组，使所属组先运行。实际工程应检查最终DSP图及处理次序，不能把一般意义上的“先创建变量G、再创建变量R”当成任意图都成立的排序规则。[10]
2. **让通往R的连接使用SEND，不由R启动C。** 这样仍需要G路径等执行C并产生数据。如果R在本混音块中先处理，C随后才产生的数据就赶不上这次R处理；官方示例会因此给湿路增加一个混音块的延迟。[8][10]

可以用下表辨认这三种配置，而不是把SEND当成无条件改进：

| 处理次序与连接 | R取得数据的方式 | 对本例的判断 |
|---|---|---|
| R在先，C到R为STANDARD | R可先执行C | 检查新声源是否绕过G路径的预约等待 |
| G路径在先，R在后 | 先由所属路径处理C，再供R读取 | 消除上述“R先拉取”的原因 |
| R在先，C到R为SEND | R读取当时已有缓冲，不启动C | 等另一条路径产生新数据，并接受本例的一块湿路延迟 |

如果把所有可能执行C的连接都改成SEND，又没有其他STANDARD或SIDECHAIN执行路径，输入数据就没有产生者。此时不能期待SEND自己让声音运行。反过来，R后执行时，也不能套用“只要用了SEND，就固定多一块延迟”的结论；这里的一块来自R已处理完、数据随后才到的次序。

混音块可用`System::getDSPBufferSize`查询，软件混音采样率可用`System::getSoftwareFormat`查询。[5] 对大小为B个样本、混音采样率为Fs的块，其时长是B/Fs秒。这是软件处理块的时长，不是从请求到耳机发声的端到端延迟；它也不应与暂停或改变速率的G时钟混成一个换算。

确认“混响提前”时，先在单个新声源、没有旧尾声和其他返回输入的条件下观察，再回到完整混音。已有混响尾声继续衰减、其他声源进入共享R，都不能证明C违反了预约。官方手工教程也未处理声道虚拟化离开、再返回DSP图后的连接恢复，不能直接照搬为完整混响系统；通常的内建混响需求应优先考虑官方建议的`System::setReverbProperties`路径。[10]

## 用一份有归属的记录决定下一步

一次预约至少保存请求身份、sound/C/G身份、P与Pnow、H/D/T/F、各次API结果、失败收尾结果。诊断暂停时补充G及祖先状态；有自定义支路时，再补取样节点、连接类型和实际处理次序。墙钟时间可用于看应用阶段耗时，但必须与这些DSP坐标分列。

| 观察到的现象 | 首先检查什么 | 由此决定的下一步 |
|---|---|---|
| T与P的距离远大于H | P是否真来自C的第二个返回项，C是否仍属于记录中的G | 修正时钟来源或路由身份，不靠缩小H抵消错域 |
| C本地未暂停，P却不再前进 | G和祖先的暂停，及整个音频系统运行状态 | 找到冻结对象，按需求决定等待恢复还是改用另一播放政策 |
| 最后检查时Pnow已接近或越过T | 准备、等待与控制路径耗时 | 放弃本次或按业务改期，不把过去目标当正常提交 |
| 干声未起，R却有新声源输入 | 排除旧尾声与其他输入后，检查支路连接和执行顺序 | 调整手工图，或接受SEND在相应次序下的代价 |
| API返回成功但听不到提示 | 素材是否有声、增益和mute、空间衰减、声音资源及输出路径 | 转向可听性检查，不继续随机更换预约坐标 |

API日志用于回答“提交了什么”和“对象状态是什么”。要判断实际声音何时进入干声或湿声路径，应在能区分两条路径的输出或调试采集位置观察；要测设备响应，还需把测量延伸到设备输出。尤其不能因为T正确，就宣称玩家在对应墙钟时刻已经听见声音。

这套方法的关键是让一组值始终保持同一含义：**从C读取G的时钟，在这个域中设置T和淡入点，及时完成配置，再确认实际处理路径遵守这一预约。** 时间归属、暂停政策、提交余量和图执行各解决一类问题；把它们分别记录，才能在出错时改对地方。

[返回播放管理](README.md)

## 参考资料

以下手册均为Firelight Technologies发布的FMOD Engine User Manual 2.04系列，访问日期为2026-11-06；版本系列网页可能更新。本文的数字、伪代码和示意图为原创说明，没有附带已编译工程、原生运行或输出测量结果。

[1] Firelight Technologies. *Core API Reference | ChannelControl*. `getDSPClock`、`setDelay`、`addFadePoint`、`setVolume`、`setPaused`、`getPaused`、`stop`。
[getDSPClock](https://www.fmod.com/docs/2.04/api/core-api-channelcontrol.html#channelcontrol_getdspclock)
[setDelay](https://www.fmod.com/docs/2.04/api/core-api-channelcontrol.html#channelcontrol_setdelay)
[addFadePoint](https://www.fmod.com/docs/2.04/api/core-api-channelcontrol.html#channelcontrol_addfadepoint)
[setVolume](https://www.fmod.com/docs/2.04/api/core-api-channelcontrol.html#channelcontrol_setvolume)
[setPaused](https://www.fmod.com/docs/2.04/api/core-api-channelcontrol.html#channelcontrol_setpaused)
[getPaused](https://www.fmod.com/docs/2.04/api/core-api-channelcontrol.html#channelcontrol_getpaused)
https://www.fmod.com/docs/2.04/api/core-api-channelcontrol.html#channelcontrol_stop

[2] Firelight Technologies. *Glossary*. §22.8–22.9 Channel Group与Channel、§22.11.1 Parameter Tokens、§22.16–22.17 DSP Chain与DSP Clock。
[参数标记](https://www.fmod.com/docs/2.04/api/glossary.html#parameter-tokens)
[DSP Clock](https://www.fmod.com/docs/2.04/api/glossary.html#dsp-clock)

[3] Firelight Technologies. *Core API Reference | ChannelGroup*. `addGroup`、`release`。
[addGroup](https://www.fmod.com/docs/2.04/api/core-api-channelgroup.html#channelgroup_addgroup)
[release](https://www.fmod.com/docs/2.04/api/core-api-channelgroup.html#channelgroup_release)

[4] Firelight Technologies. *Core API Loading and Playing Sounds*. §4.1–4.2，尤其Non-blocking Sound Creation。
[非阻塞加载](https://www.fmod.com/docs/2.04/api/loading-and-playing-sounds-in-the-core-api.html#non-blocking-sound-creation)

[5] Firelight Technologies. *Core API Reference | System*. `playSound`、`getDSPBufferSize`、`getSoftwareFormat`。
[playSound](https://www.fmod.com/docs/2.04/api/core-api-system.html#system_playsound)
[getDSPBufferSize](https://www.fmod.com/docs/2.04/api/core-api-system.html#system_getdspbuffersize)
[getSoftwareFormat](https://www.fmod.com/docs/2.04/api/core-api-system.html#system_getsoftwareformat)

[6] Derek Burnheim. *Some muted knocking sounds when using pitch bend*，答复2. FMOD Forums，2020-06-16。历史调用顺序说明，不作为任意配置提前量或2.04实测依据。
[原答复](https://qa.fmod.com/t/some-muted-knocking-sounds-when-using-pitch-bend/15883/2)

[7] Firelight Technologies. *Core API Mixing and Routing*. §6.1.1 Channel and Channel Group Handles。
[句柄寿命](https://www.fmod.com/docs/2.04/api/mixing-and-routing-in-the-core-api.html#channel-and-channel-group-handles)

[8] Firelight Technologies. *Core API Reference | DSPConnection*. `FMOD_DSPCONNECTION_TYPE`中的STANDARD、SEND及输入缓冲说明。
[连接类型](https://www.fmod.com/docs/2.04/api/core-api-dspconnection.html#fmod_dspconnection_type)

[9] Firelight Technologies. *Core API Reference | DSP*. `DSP::addInput`。
[DSP::addInput](https://www.fmod.com/docs/2.04/api/core-api-dsp.html#dsp_addinput)

[10] Firelight Technologies. *Core API Using DSP Effects*. §7.1.2 Creating an effect and making all Channels send to it、Order of execution and pull / no pull traversal、'Send' vs 'Standard' connection type。
https://www.fmod.com/docs/2.04/api/using-dsp-effects-in-the-core-api.html

