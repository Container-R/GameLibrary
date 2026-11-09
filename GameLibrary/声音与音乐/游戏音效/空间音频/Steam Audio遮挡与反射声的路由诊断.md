# Steam Audio遮挡与反射声的路由诊断

一台机器仍在运转，玩家走到墙后，直达声变弱，反射声也不见了。接入者提高反射混音量，问题却没有变化。原因可能发生在完全不同的位置：送进效果器的新样本已经被上游切掉；反射被送到了另一条返回路径；声源暂时没有实际混音资源；或者效果器只剩下正在结束的尾声。

本文面向熟悉音频总线与 DSP 基础的技术音频设计师和音频程序员，用 **Steam Audio 4.8.1 的 FMOD 插件源码**建立一套分点诊断方法：先区分直达处理与反射激励，再检查输出路由，最后把声源虚拟化和已有尾声纳入判断。它解释固定版本的实现及由此得到的检查步骤，不是一次游戏听音报告。FMOD 内置 Spatializer、Core 的 `set3DOcclusion` 与本插件是不同处理器，不应互换其参数语义。

## 先把“声音没了”拆成四个可检查的过程

**样本生成（source generation）**是解码器或信号源产生新的音频样本，并由宿主送入插件。游戏仍把机器标为“运行”，不代表这一块音频已经产生。声源也可能仍有播放对象，却暂时没有实际混音资源。

**直达处理（direct processing）**把距离、空气吸收、指向性、遮挡与透射等条件作用在直达支路上，再进行声像或 HRTF 空间化。HRTF 是用头部相关传递函数生成双耳空间线索的处理。

**反射激励（reflection excitation）**是当前送入反射效果的新信号。它与反射模拟结果不同：模拟结果描述环境怎样响应声音，激励则是现在有什么声音进入这份响应。获得了模拟数据，并不能让一个没有音频输入的机器继续产生新的反射声。

**已有尾声（tail）**来自效果器保存的历史输入和内部状态。停止新激励后，它仍可能输出一段时间；如果把返回路一并静音，即使内部仍在处理，玩家也收不到这段尾声。以下所有诊断都把这四件事分别记录，不用一个“混响开关”代表它们。

## 直达遮挡究竟作用在分路的哪一边

本节先限定一条容易观察的路径：有效的 Steam Audio 上下文、HRTF 与模拟源，所需效果和缓冲初始化成功；Reflections 开启，采用 Convolution 反射，Pathing 关闭，没有 Steam Audio Mixer Return，正在处理正常输入块。Convolution 使用脉冲响应计算反射输出；脉冲响应描述一次短激励如何在环境中随时间展开。

在 `SpatializeEffect::process` 中，输入先反交错为 `inBuffer`，即分离为每个声道的连续样本。随后，两条支路读取这份共同输入：[1]

```text
宿主产生样本 → 上游处理 → inBuffer
                              ├→ DirectEffect → HRTF／声像 → Direct Mix Level ─┐
                              └→ 下混单声道 → Reflections Mix Level          │
                                             → 反射效果 → 空间解码 ─────────┤
                                                                        合成输出
```

图中省略了尾声分支，稍后单独讨论。反射的空间解码把 Ambisonics 声场表示转为当前扬声器或双耳输出；它不是再次对反射应用直达遮挡。

源码的关键不是两个旋钮名字不同，而是输入缓冲不同：直达效果读取 `inBuffer`、写入独立的 `directBuffer`；反射处理则**重新从 `inBuffer` 下混**，而非读取已经遮挡的 `directBuffer`，也不读取经过 Direct Mix Level 的输出。[1][2] 因此，在上述条件和相同反射数据下，只调整插件内部直达遮挡，不会因为这条分路关系而把反射激励一起乘零。

但 `inBuffer` 只是插件入口，不是未经处理的素材文件。若游戏把遮挡映射到 Spatializer **之前**的总音量，让整份输入变成零，两路都会失去新的输入。把反射混音量从 1 提高到 2，只会把零继续乘成零。修复应作用于控制的位置，而不是不断提高返回音量。

### 遮挡系数也不是一个通用静音按钮

先区分模式与系数。插件界面的 **Occlusion** 选择 Off、Simulation-Defined 或 User-Defined；**Occlusion Value** 才是手动系数，只在 User-Defined 模式生效。Simulation-Defined 使用绑定模拟源的输出，Off 不应用遮挡。[10] 因此调了一个数值却没有改变声音时，应先检查模式和实际送入 `DirectEffect` 的系数，不要立即判断路由失效。

Steam Audio 的遮挡系数越大，表示这一项保留的直达贡献越多；0 与 1 的方向不能照搬其他中间件。固定实现中，启用遮挡但关闭透射时，直达 gain 乘以遮挡系数；若同时启用频率无关透射，则乘以：

```text
遮挡系数 + (1 − 遮挡系数) × 三个频带透射系数的平均值
```

频率相关透射走三个频带的组合与 EQ 处理。[2] 因此，“遮挡为 0”不总是“直达 gain 为 0”。检查时必须连同 Transmission 的启用状态和类型一起记录。

参数变为零也不等于同一采样立即归零。`GainEffect` 保留上一增益并进行跨块插值；Direct Mix Level 和 Reflections Mix Level 另有块内斜坡。[3] 观察参数变化后最初一个块不足以判断稳定结果，更不能直接从控制数字推断听感。

## 反射混音量控制新激励，不会倒回去改掉历史

在这条路径中，Reflections Mix Level 的斜坡作用于**反射效果之前**的单声道缓冲。[1] 这意味着它更像输入发送量，而不是位于反射返回末端的总音量。把它降到零，会逐渐停止新的反射激励，不会自动抹除已经进入卷积器的历史输入。

固定卷积实现把输入块转换到频域，保留多个历史块，再与脉冲响应的不同分块相乘并累加。已有尾声正来自这份历史。`tail()` 在没有新输入时继续使用保存的输入频谱和剩余响应分块生成输出，递减剩余尾声块数。[4] 这给出了明确的因果关系：**新激励为零、尾声仍有输出，可以同时成立。** 反过来，尾声状态报告尚未完成，也不保证每个采样都非零；输入或响应本来就可能是零。

Spatializer 的处理回调有查询和执行两个阶段。查询阶段收到 `inputsIdle` 时，如果此前记录还有尾声，就要求继续处理尾声；否则返回不处理。执行阶段分别处理反射效果与后续空间解码的尾声。[1] 这条代码路径说明它为自然排空保存了处理逻辑，但不能保证宿主停止、销毁对象或虚拟化时仍以相同方式调用它。

由此可以区分三种制作意图：

| 目标 | 控制应落在哪一层 | 必须接受或另行处理的结果 |
|---|---|---|
| 墙后只压低直达声，仍保留当前反射激励 | 插件内直达遮挡、透射或 Direct Mix Level | 反射仍依赖共同输入、有效模拟数据与实际处理机会 |
| 机器停止发声，但允许环境尾声结束 | 停止新激励，同时保持效果与输出路径直到排空 | 需要验证宿主停止政策和尾声生命周期，不能立即销毁整条链 |
| 要把当前反射连同已有尾声一起压低 | 对实际反射返回或其下游施加合适的淡化 | 共享返回上的变化会影响其他声源，不能假定只改变这台机器 |

第三行不等于“直接静音整个事件”。在本地合成路径中，直达与反射已经合并，后面的总音量会影响两者。若需要独立处理返回，应在设计路由时保留独立控制位置，或实现明确的输出支路；不要误把输入端 Reflections Mix Level 当成能立即控制全部历史反射的返回推子。

## 先认出反射实际从哪里返回

Steam Audio 的三种相关接法容易被口头统称为“混响”，但诊断位置不同。

### 每个 Spatializer 内部合成

前面的默认分析在各个声源内完成反射卷积和空间解码，再与直达声合成。跟在 Spatializer 后的 FMOD 效果接到的是合成信号。它容易按事件追踪，也让每个声源保留自己的反射处理状态。

### 通过 Steam Audio Mixer Return 汇合

当全局反射混合器有效时，反射效果把结果交给它，Spatializer 跳过本地反射解码与合回输出的分支。Mixer Return 再取出混合反射、空间解码，并与该节点的普通输入相加。[1][5]

以 Convolution 为例，各声源的卷积效果保留自己的输入历史，将计算出的频域反射贡献累加到混合器；混合器执行逆变换与混合结果输出后清空本轮累加状态。[4] 因而返回节点本身没有持续新输入，不等于某个声源的反射历史已经被安全迁移或保存。声源侧效果的处理与寿命仍然重要。

官方文档明确指出：反射绕过了 Spatializer 与 Mixer Return 之间的 FMOD 效果。[6] 例如某个事件的直达输出经过低通，而反射绕过它，不能只看事件效果面板就断言两路都已过滤；在事件路径电平表看不到反射，也不能直接判定卷积没有输出。应当在真正的返回点观察。

文档把此接法限制为 Convolution 或 TrueAudio Next；后者必须使用 Mixer Return。[6] 汇合能减少部分重复处理，但本文没有性能测量。是否采用应同时考虑返回分组、需要保留的事件效果和控制粒度，而不是仅依据“更省 CPU”的描述。共享返回若混合多声源，就无法仅凭返回电平判断某一声源是否仍在贡献。

### 普通发送总线上的 Steam Audio Reverb

Steam Audio Reverb 是另一种效果：接收 FMOD 总线发送的音频，用听者位置的 `reverbSource` 模拟结果进行处理。它不等于每个声源 Spatializer 内部的 Reflections。[7] 若项目采用普通 Send，首先查这个 Send 在哪些处理之前、之后；不能将本文对 Spatializer 的 `inBuffer` 分路结论套到那个 Send 上。信号在发送之前被压成零时，接收端效果同样没有新的激励。

## 资源资格估计不是波形电平表

即使信号图正确，声源也未必一直获得真实混音资源。FMOD 的 `FMOD_DSP_PARAMETER_OVERALLGAIN` 提供插件增益信息，用于声音虚拟化判断。[8] Steam Audio 的 `updateOverallGain` 单独计算这份信息：估计直达各项影响后，在 Reflections 开启时加上 Reflections Mix Level，在 Pathing 开启时再加相应混音量，并将结果封顶为 1。[1]

它不是刚刚计算出来的反射 RMS。公式没有读取当前反射输出或脉冲响应能量，而且只要反射开关开启就计入混音量，不要求此刻有有效模拟源。所以这个值为正，既不能证明反射实际非零，也不保证宿主会给该声源真实名额。

固定源码还提供了一个容易检查的反例。关闭 Transmission 时，`getDirectParams` 把三个透射系数设为 1；估计式仍使用“遮挡＋未遮挡比例乘最大透射系数”，于是这一项为 1。实际 DirectEffect 则会检查启用标志，在没有透射时直接乘遮挡系数。[1][2] 在 User-Defined 模式令 Occlusion Value=0、Transmission=Off，直达 gain 的遮挡部分为 0，而资格估计中的对应部分仍为 1。这是两套计算不等价的证据，不应未经运行验证就定性为错误；估计可以有保守目的。

因此，遇到处理突然中断时，应分别记录播放对象状态、宿主的真实／虚拟观测、DSP 查询与执行情况，以及该插件报告的 overall gain。`inputsIdle`、游戏的“正在播放”标志、估计增益和玩家听到的声音都不能互相代替。还应保留优先级与真实声预算：有反射贡献也不意味着能够绕过资源竞争。Core 路径可查询 `Channel::isVirtual`；Studio 的事件虚拟化还应记录 `EventInstance::isVirtual`，不能只检查其中一层。[11]

单纯关闭虚拟化可以作为有明确前后的诊断对照，但不是普遍修复。它可能增加仍需处理的声源数量；若问题其实是上游输入已经归零，保留资源也无法恢复新激励。请求准入和播放回收是另一层政策，见[FMOD Core音效请求的准入与播放回收](../播放管理/FMOD%20Core音效请求的准入与播放回收.md)。

## 用一次有区分力的对照定位，而不是同时调所有旋钮

下面是可在项目中实施的检查方法，不是本文已执行的实验。先只保留一台持续发声的机器，固定位置、素材、反射数据和输出设备，记录实际插件与 SDK 版本。为排除返回路歧义，第一轮采用本地 Convolution 反射，关闭 Pathing，不加 Mixer Return；确认有效模拟源和反射数据。源码中的 Convolution 分支遇到空 `fftIR` 会返回无尾声，本地输出置零，因此不能把“Reflections 已勾选”当成数据已经准备好。[9]

### 记录同一条信号的五个位置

1. Spatializer 入口：宿主是否持续交来音频块，`inBuffer` 是否有样本。
2. 直达效果之后：`directBuffer` 是否按遮挡和透射设置改变。
3. 反射效果之前：下混且乘 Reflections Mix Level 后的单声道激励是否仍存在。
4. 反射处理之后：本地反射结果，或实际 Mixer Return 的结果。
5. 最终输出：后续总线是否又把结果压低，以及设备真正输出了什么。

前三个内部点不一定出现在宿主电平表中。需要开发构建时，可在对应函数处记录有界的计数与缓冲摘要，或把选定样本复制到预分配诊断缓冲，交由非音频线程导出；避免在实时回调中写文件、分配内存或打印大量日志。每条记录带声源身份、块序号、采样率、帧长与声道数。RMS/peak 适合定位能量变化，若要证明两份输入相同，应保存样本或逐样本比较，不能只靠相同 RMS。

手动对照先把 Occlusion 模式设为 User-Defined，确认 `getDirectParams` 返回的 `occlusion` 是所设值；Transmission 设为 Off。记录模式、手动值和实际效果参数三个字段。如果要研究真实几何模拟，则另用 Simulation-Defined，并记录相应模拟输出，不能继续把手动旋钮当作本轮输入。随后只改变一个因素：

| 对照 | 保持不变 | 由数据流预期的区别 |
|---|---|---|
| User-Defined 下 Occlusion Value 从 1 变 0，Transmission 为 Off | 入口、反射数据、反射混音量与实际处理资格 | 直达改变；反射激励不应因这次直达处理被乘零 |
| Spatializer 前总增益变 0 | 插件内参数与路由 | 共同入口和新反射激励一起减少；已有尾声另行观察 |
| 只把 Reflections Mix Level 变 0 | 直达参数与共同入口 | 直达不由这个值压低；新反射激励减少，不能据此要求已有尾声立即消失 |

跨越增益斜坡后再比较稳定窗口，同时保留过渡块，否则短窗口可能只记录到插值过程。不要为了得到整齐数字丢弃与预期不符的块；若反射数据、源绑定或处理状态同时变化，应把它们视为实验条件变化，重新分离原因。

如果入口有信号、反射激励有信号而反射输出没有，接着核对有效源、IR 数据、效果初始化和真正的返回位置。若入口本身没有新样本，则向上游追查产生和传递音频的过程，不先修改反射算法。若 DSP 执行中断，先取得宿主虚拟化与生命周期证据，再判断资源政策，不能仅凭回调缺口宣布已经虚拟化。

### 把尾声和资源竞争留作两个独立对照

尾声对照让一段已产生非零反射输出的输入自然结束，保留效果与返回路径，记录最后一个新激励块以及后续 TailRemaining／TailComplete 与输出样本。再单独测试项目实际使用的停止操作。两者不同，说明停止政策或寿命需要检查，不是把尾声数值调长就能解决。

资源对照保持信号图不变，再增加明确的真实声竞争，记录宿主真实／虚拟状态和回调执行情况。恢复后还要检查循环从哪里继续；这是时间政策，与反射路径是否独立不同，见[循环声音重新听见时，应该从哪里继续](../播放管理/循环声音重新听见时，应该从哪里继续.md)。

最后恢复正常场景和目标设备试听。分点数据能说明某一路在哪里失去激励或输出，但墙后保留的声是否符合空间、玩法和信息泄露要求，要由实际内容判断。本文没有运行 Steam Audio 或 FMOD、捕获音频、试听或测量性能；上述结论是固定源码解释，表格是待实施的因果对照，不是听感验收结果。

## 参考资料

Steam Audio 来源均固定为 Valve **v4.8.1**，提交 `0da18255cca520771f363ee01f100572b39a308e`，查阅于 2026-11-09。标签已核对；版本限定的是源码，不表示运行中的二进制已被认证。

1. Valve，[spatialize_effect.cpp](https://github.com/ValveSoftware/steam-audio/blob/0da18255cca520771f363ee01f100572b39a308e/fmod/src/spatialize_effect.cpp)：`getDirectParams`、`updateOverallGain`、`getData`、`process`，尤其 1001–1297 行的估计、分路与尾声处理。
2. Valve，[direct_effect.cpp](https://github.com/ValveSoftware/steam-audio/blob/0da18255cca520771f363ee01f100572b39a308e/core/src/core/direct_effect.cpp)：`DirectEffect::apply`、`calculateGainAndEQ`；[api_direct_effect.cpp](https://github.com/ValveSoftware/steam-audio/blob/0da18255cca520771f363ee01f100572b39a308e/core/src/core/api_direct_effect.cpp)：`CDirectEffect::apply` 参数与缓冲转交。
3. Valve，[gain_effect.cpp](https://github.com/ValveSoftware/steam-audio/blob/0da18255cca520771f363ee01f100572b39a308e/core/src/core/gain_effect.cpp)：`GainEffect::apply`；[steamaudio_fmod.cpp](https://github.com/ValveSoftware/steam-audio/blob/0da18255cca520771f363ee01f100572b39a308e/fmod/src/steamaudio_fmod.cpp)：`applyVolumeRamp`。
4. Valve，[overlap_save_convolution_effect.cpp](https://github.com/ValveSoftware/steam-audio/blob/0da18255cca520771f363ee01f100572b39a308e/core/src/core/overlap_save_convolution_effect.cpp)：`OverlapSaveConvolutionEffect::apply`、`tail`、`OverlapSaveConvolutionMixer::mix/apply`，历史输入、卷积及返回累加。
5. Valve，[mix_return_effect.cpp](https://github.com/ValveSoftware/steam-audio/blob/0da18255cca520771f363ee01f100572b39a308e/fmod/src/mix_return_effect.cpp)：`process`；[api_indirect_effect.cpp](https://github.com/ValveSoftware/steam-audio/blob/0da18255cca520771f363ee01f100572b39a308e/core/src/core/api_indirect_effect.cpp)：`CReflectionEffect::apply/getTail` 与 `CReflectionMixer::apply`。
6. Valve，[Mixer Return 文档](https://github.com/ValveSoftware/steam-audio/blob/0da18255cca520771f363ee01f100572b39a308e/fmod/doc/mixer-return.rst)：适用反射类型与跳过中间 FMOD 效果的说明。
7. Valve，[FMOD User’s Guide](https://github.com/ValveSoftware/steam-audio/blob/0da18255cca520771f363ee01f100572b39a308e/fmod/doc/guide.rst)：Model reflection by geometry、Apply physics-based reverb to a mixer bus；[reverb_effect.cpp](https://github.com/ValveSoftware/steam-audio/blob/0da18255cca520771f363ee01f100572b39a308e/fmod/src/reverb_effect.cpp)：`process` 的输入与 `gReverbSource`。
8. Firelight Technologies，[FMOD Plug-in API Reference — FMOD_DSP_PARAMETER_OVERALLGAIN](https://www.fmod.com/docs/2.03/api/plugin-api-dsp.html#fmod_dsp_parameter_overallgain)，读取时页脚 **2.03.15（2026-09-21）**，访问于 2026-11-09。采用其虚拟化信息用途；该系列网页可以更新，不据此推断宿主内部调度实现。
9. Valve，[indirect_effect.cpp](https://github.com/ValveSoftware/steam-audio/blob/0da18255cca520771f363ee01f100572b39a308e/core/src/core/indirect_effect.cpp)：Convolution 的效果选择、空 IR 分支与尾声分派。
10. Valve，[Spatializer 文档](https://github.com/ValveSoftware/steam-audio/blob/0da18255cca520771f363ee01f100572b39a308e/fmod/doc/spatializer.rst)：Occlusion、Occlusion Value 与 Transmission 的模式和参数生效条件。
11. Firelight Technologies，[FMOD Core API Managing Resources](https://www.fmod.com/docs/2.03/api/managing-resources-in-the-core-api.html#virtual-voice-system)，2.03 系列，访问于 2026-11-09，Virtual Voice System、Audibility Calculation、Studio API Voice Control：分别查询 Channel 与 EventInstance 虚拟状态。本文不据这些状态推断每个效果器的尾声输出。

[返回空间音频](README.md)
