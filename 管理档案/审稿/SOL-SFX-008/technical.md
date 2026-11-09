# 独立技术审稿

最终结论：**通过技术审稿**。已重新通读修订全文，首轮参数模式遗漏得到实质修复；新增资源状态查询说明经 FMOD 原始文档核对成立。该结论仅限下列当前字节版本与固定源码解释，不代表运行或试听验证。

- 审稿类型：独立模型审稿。未参与初稿，未修改正文，未运行 Steam Audio/FMOD、未捕获或试听音频。
- 实际全文：`GameLibrary/声音与音乐/游戏音效/空间音频/Steam Audio遮挡与反射声的路由诊断.md`。
- 当前实际字节 SHA256：`741b322bf49eb4668bf69f24e8bfc84a1d541468758b1d0bbd6c5aaa0b521499`。
- 首轮字节 SHA256：`1c52da2ecb6b7e7d4fccb79a112df56cb77363c64cc1f59f966170ed2154283b`；当时结论为需修订，以下保留问题与解决记录。
- 来源范围：已核读的固定上游源码 Steam Audio v4.8.1、提交 `0da18255cca520771f363ee01f100572b39a308e` 的 Spatializer、DirectEffect、GainEffect、卷积、IndirectEffect、API 转交、Mixer Return、Reverb、增益斜坡及相关 RST 文档。FMOD 在线文档的 2.03.15 页脚未在此次审稿重新读取；不将作者报告的在线读取冒充独立复核。

## 首轮问题与解决记录

### R1：明确遮挡模式和实际系数，避免对照调了一个不生效的旋钮

位置：“遮挡系数也不是一个通用静音按钮”“资源资格估计不是波形电平表”的 Occlusion=0 表述，以及“用一次有区分力的对照”首行“插件内 Occlusion 从 1 变 0”。

正文没有区分 UI 的 Occlusion 模式与 Occlusion Value 数值。固定版 `fmod/doc/spatializer.rst` 的 Occlusion 为 Off、Simulation-Defined、User-Defined 三种模式；只有 User-Defined 才读取 Occlusion Value。`getDirectParams` 中 `applyOcclusion == PARAMETER_DISABLE` 强制系数为 1，User-Defined 才读 `effect->occlusion`，否则读取模拟输出。这是会改变实验结果的真实反例：在 Simulation-Defined 模式只修改用户数值，入口和反射数据均保持不变，直达也可能毫无变化。读者可能误判插件分路或遮挡处理失效。

通过条件：
1. 说明模式与系数不是同一参数，明确第一轮选 User-Defined，调整 Occlusion Value 的归一化值 1→0（UI 可显示 100%→0%），Transmission 选 Off。
2. 在记录项中加入实际生效模式及 `getDirectParams` 输出的 flags、occlusion 和必要的 transmission 值，避免仅记录旋钮。
3. 将估计反例中的 Occlusion=0 写清为已启用遮挡且实际传入直达参数的系数为 0。若保留 Simulation-Defined 实验方案，则说明要验证模拟输出真的变化，而非同改其他场景因素。

修复不需扩大成完整插件教程，也不要求添加未执行的音频实验。

复核：已解决。修订稿在原理章节明确三种模式和手动数值的生效条件；对照前明确 User-Defined、Transmission Off，要求核对 getDirectParams 返回的 occlusion 并记录模式、手动值、实际效果参数。估计反例也明确同一模式。虽然未逐项列 flags 名称，但“实际效果参数”连同已明确的模式与关闭透射条件，足以排除本轮反例，不为字面措辞继续阻塞。

## 已核对的决定性机制

1. **分路成立。** `SpatializeEffect::process` 中直达由 inBuffer 写 directBuffer；反射再次从 inBuffer 下混并应用 Reflections Mix Level，不读 directBuffer 或直达混音结果。正文将初始化、有效源、反射数据、Convolution、本地返回、正常输入块等条件放在结论前，限定合理。
2. **遮挡/透射公式成立。** `DirectEffect::calculateGainAndEQ` 区分 ApplyOcclusion 和 ApplyTransmission；频率无关透射按平均值组合，频率相关模式进入各带 EQ。开启透射时遮挡系数 0 不保证直达归零，是充分且必要的反例。
3. **新激励与历史状态区分成立。** 卷积 apply 保存输入频谱，tail 使用历史频谱和剩余 IR 分块；Reflections Mix Level 在效果前，不是尾声返回推子。tail 状态与每块实际能量不同，正文已避免把 TailRemaining 当成非零证明。
4. **返回归属成立。** API 把有效 mixer 交给 IndirectEffect 的 mixer 重载；Spatializer 跳过本地反射解码；Mixer Return 混合解码结果和普通输入。卷积 mixer 每轮输出后 reset 累加器，不拥有各声源卷积输入历史。正文没有把共享返回误写成已迁移所有尾声状态。
5. **overall gain 反例成立。** `updateOverallGain` 使用最大透射系数而不按实际 DirectEffect flags 重走算法；Transmission Off 时 getDirectParams 把三带透射设为 1，估计中的遮挡项因此为 1。正文只据此说明估计不等于波形，未武断称其为错误。
6. **空 IR 分支成立。** `IndirectEffect::apply` 对 Convolution 且 fftIR 为空的本地路径清空输出并返回 TailComplete；有 mixer 时返回 TailComplete。检查数据准备情况比只看 Reflections 开关有效。
7. **平滑限定基本成立。** GainEffect 按上一块增益逐块逼近目标并在块内插值，另两路混音量使用 applyVolumeRamp。正文没有把零参数等同首块严格为零。

## 主动反例及范围评估

- 停止新激励但继续回调：历史卷积仍可能输出，文章的方法可区分。
- 停止或回收声源并销毁效果：保存返回节点不足以保证尾声，正文已指出寿命与宿主调度必须独立确认。
- 插件入口非零但下混信号为零（例如声道相消）：不会推翻独立分路；五点采样法会定位在入口与反射激励之间，不需要为这一反例另写算法文章。
- Mixer Return 路由中反射绕过中间 FMOD 效果：原始 RST 明确支持，文章提供了具体低通反例与正确观测位置。
- 合法 IR 但当前反射能量为零、TailRemaining 但样本为零：正文已处理，不将状态或旋钮当电平表。
- 模拟源丢失、开关关闭或效果初始化失败：代码能跳过处理，文章列入条件及后续诊断，不构成其限定结论的反例。

## 分项判断与发表条件

- 选题价值：通过。读者能区分控制位置、返回路由和资源问题，避免用增大反射混音量处理上游归零。
- 机制及证据：通过上述源码核查；核心知识在正文，不依赖后台记录。
- 方法完整性：通过。R1 已修复；五个观测点、三个单因素对照、尾声与资源独立对照构成可实施的方法。
- 取舍：足够。明确本地合成与共享返回的控制粒度、绕过效果和声源寿命，不伪造性能收益。
- 可读性：结构与目标读者匹配；最终独立读者审读仍由另一审读者负责。
- 导航：本次没有从根入口逐层检查，不给导航通过结论。

非阻塞建议：稳定窗口可明确采用预先选定的幅度误差阈值，而非等待 GainEffect 在有限块内精确等于目标；这是平滑读数的严谨化，不影响分路结论。

## 新增资源查询内容的独立复核

重新打开正文来源 [11] 的 FMOD 2.03 Core API Managing Resources 原文（2026-11-09）。Audibility Calculation 明确 overall gain 为资格计算因素之一并提供 Channel::isVirtual；Studio API Voice Control 提供 Studio::EventInstance::isVirtual；Interaction with the Core API Virtual Voice System 明确事件非虚拟时其底层 Channel 仍可因软件声预算而虚拟。因此修订稿要求分别记录、不能只检查一层成立，也没有据状态推断卷积尾声必然存在。

来源：https://www.fmod.com/docs/2.03/api/managing-resources-in-the-core-api.html#virtual-voice-system 。在线读取支持新增主张；仍不声称读取了来源 [8] 页脚或宿主内部实现。

代表性操作复核：入口与反射激励持续非零、直达因 User-Defined 系数变化而降低时，可判定内部直达分路没有切断新反射激励；若改上游总增益导致入口与激励同时减少，应追上游而非提高反射返回。将 Reflections Mix Level 降零后的尾声另观测，再将生命周期和资源竞争拆开，足以完成标题承诺。全文新增内容没有改变主线或引入未证实的声音品质结论。

通过绑定当前 SHA256。此记录不批准任何后续字节版本，也不代替导航审查或编辑发表决策。
