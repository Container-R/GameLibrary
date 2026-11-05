# FMOD预约声音时，为什么要读取父混音组的时钟

一段提示音已经预约播放，打开暂停菜单再回来，却没有按现实中经过的时间响起。另一个实现则给预约值加上相同的采样数，等待长度仍然不对。排查时，除了确认时间单位，还需要问：这个数属于哪一个对象的时钟？

本文面向直接使用 FMOD Core 的音频程序员，只讨论固定路由下的预约坐标。它不替代 Studio 音乐转场规则，也不提供完整播放器。

## 先认清预约读取的是谁的时间

FMOD 2.04 文档中，`getDSPClock` 可返回对象自身的 `dspclock` 和父混音组的 `parentclock`。`setDelay` 的起止时间与 `addFadePoint` 的淡化点使用后者，单位为 samples。[1]

假设声道 C 直接属于混音组 G。给 C 安排这些时间时，需要的是 **C 查询得到的 parentclock，也就是 G 自身的时钟**。若改为查询 G 的 parentclock，取得的已经是再上一层的时间，不能只因变量名字相同就替换。

DSP 时钟默认同速，但 pitch 调整可能改变其推进速率。[2] 因此不能把“都叫音频时钟”理解成所有读数永远可互换。

## 相同单位，也可能把等待写长

下面是一组假设读数，不是 FMOD 运行日志。设 G 的当前坐标 P=480000，另一参考时钟 M=960000；它们都以 sample ticks 计数。这里把 tick 理解为相应时钟的一个计数单位，不把它换算成固定的现实秒数。

设计希望 C 在 G 再推进4800 ticks后开始。那么目标坐标应是：

- 采用 G 的坐标：480000+4800=484800。
- 误用 M 的坐标：960000+4800=964800。

第二个数若交给按 G 坐标解释的预约，距离 G 当前值是484800 ticks，而不是要求的4800。问题不在加法，也不在两份数据是不是整数，而在把另一个坐标系的读数当成了 G 的读数。

实际接入时，应确认 C 的所属组、查询返回结果，以及未来目标是否仍在预定时钟中。这个例子不说明两次接口查询是原子快照，也不规定必须提前多少 ticks提交命令。

如果还要安排从484800到489600的淡入，两个端点也必须采用同一个 G 坐标。这只是时间位置的选择，不能代替[交叉淡化的增益与素材关系检查](../../GameLibrary/声音与音乐/音频制作/混音/交叉淡化时为什么声音中间变大或变小.md)。

## 暂停父组，不能靠现实时间替它走完预约

继续同一个例子：C 的预约是484800。假设 G 在自身坐标482400处实际暂停，其时钟停止推进；期间对象、路由和预约都没有改变。此时距离预约还剩2400 ticks。即使现实中过了三秒，也不能在这个模型里把这2400 ticks自动扣掉；恢复后仍需 G 走到预约坐标。

FMOD 的暂停说明指出，暂停会冻结相应对象的播放进度与时钟；父组暂停也会影响子对象，但查询对象的暂停标志返回的是它自己的设置。[1] 因而 C 的本地暂停标志为 false，不足以证明 G 没有暂停。

这里暂停的是 **G**。如果只暂停 C，不能据此推断 G 的时钟停止，也不能声称 C 查询返回的 parentclock随之冻结。诊断记录应写清暂停对象和时钟所属对象，而不是只记一个没有归属的“paused”。

## 先决定预约要跟随哪种时间

若提示音本来就应随音乐组一起暂停，保留 G 的预约坐标符合这个目标。若暂停菜单打开后，它仍必须按现实时间出现，就需要另行设计它的暂停与路由政策；给冻结的 G 填一个更大的 M 坐标，并不能解决这个需求。

本例没有提供跨时钟转换、运行中换组或修改旧预约的算法，也不讨论已经过去的目标如何处理。内容未准备好、请求没有及时生效和输出路径本身仍可能影响结果。预约坐标正确，不代表玩家已经听见声音；日志中的 tick 差也不是测得的设备延迟。

## 来源与适用范围

1. Firelight Technologies，FMOD Engine User Manual 2.04，[*ChannelControl*](https://www.fmod.com/docs/2.04/api/core-api-channelcontrol.html)：[getDSPClock](https://www.fmod.com/docs/2.04/api/core-api-channelcontrol.html#channelcontrol_getdspclock)、[setDelay](https://www.fmod.com/docs/2.04/api/core-api-channelcontrol.html#channelcontrol_setdelay)、[addFadePoint](https://www.fmod.com/docs/2.04/api/core-api-channelcontrol.html#channelcontrol_addfadepoint)、[setPaused](https://www.fmod.com/docs/2.04/api/core-api-channelcontrol.html#channelcontrol_setpaused)的参数和说明。
2. 同一官方手册，[*Glossary — DSP Clock*](https://www.fmod.com/docs/2.04/api/glossary.html#dsp-clock)，§22.17。

2026-11-05读取。API页面页尾显示2.04.00（2026-09-29）；2.04网址仍是可更新的官方文档系列，不是固定实现提交。数值均为原创条件演算，没有运行 FMOD、制作工程、输出音频或试听，不声称跨版本或跨中间件行为一致。

[返回音乐切换正文](../../GameLibrary/声音与音乐/交互音乐/音乐切换/玩法变化怎样触发可听见的音乐切换.md)
