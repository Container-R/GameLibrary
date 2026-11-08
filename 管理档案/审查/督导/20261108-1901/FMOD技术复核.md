# FMOD 音效准入与回收：发表后技术复核

复核时间：2026-11-08T10:55:00Z（北京时间 18:55）。方式：未参与初稿的独立模型全文与原始资料核对。对象为提交 `f6ef8e1cd780f0253d8d507e54050ae89ffc2b64` 的 `GameLibrary/声音与音乐/游戏音效/播放管理/FMOD Core音效请求的准入与播放回收.md`。本报告不重新认证其他文章。

## 结论

技术内容通过本轮复核，没有发现必须修改正文的实质错误。文章完成了预先约定资源和单控制者条件下的请求至终止方法，而不是仅提醒“虚拟不等于结束”。事件身份与有限结果表、入口和多级预算、暂停创建、失败清理、原句柄终止判断及幂等归还形成连贯流程；每项政策的代价和不覆盖的系统恢复均在相关位置说明。

这不是运行认证。正文没有 SDK、听音、设备输出或性能结果；本轮也没有新增这些观察。未知创建失败冻结新准入，是偏向一致性的应用选择，不能用本次通过证明它适合全部游戏的可用性要求。

## 字节与发表身份

- 远端默认分支为 `master`，核对时 HEAD 为 `f6ef8e1cd780f0253d8d507e54050ae89ffc2b64`，父提交为 `adc5d742355be863ae42ff99ee5f82bec7e6389f`。
- 正文 26,135 字节，Git blob `a525d0b2b1afe43c203bbee95a9418ad54677de3`；SHA-256 `5b17c8beb471ced1faf8329c84ec060af359230f3ec480c7b630bffa9cadda1e`。
- 来源记录 `管理档案/研究/TASK-2026-0303/sources.json` 为 8,845 字节，Git blob `facac2961f3cdfe910a82b979d0e6ae2689340df`；SHA-256 `811a6d67efb226e632d4dcc800467b4baa66d96e1b7cec69d7a37aa9990ba1fc`。
- 本轮所读正文、来源与远端树的 blob 一致，并与既有最终审稿绑定相符。随后对全文和决定性官方资料作了独立实质核对，不以摘要一致代替内容审查。

## 决定性来源与判断

原始资料均为 Firelight Technologies 官方 FMOD Engine User Manual 2.04 系列，访问日期 2026-11-08。System、ChannelControl、Channel 页脚再次显示 2.04.00（2026-09-29）；系列 URL 并非不可变快照。

1. **三种上限。** [System::init](https://www.fmod.com/docs/2.04/api/core-api-system.html#system_init) 的 maxchannels 包含虚拟 Channel；[setSoftwareChannels](https://www.fmod.com/docs/2.04/api/core-api-system.html#system_setsoftwarechannels) 限定实际混音数并要求初始化前或 close 后设置。正文把业务 B 单独定义，未把少量真实声误当少量在途对象。每个相关创建者的可信上界也是容量保证的必要前提，文中没有用一次查询的余量替代这个前提。
2. **暂停创建与失败。** [playSound](https://www.fmod.com/docs/2.04/api/core-api-system.html#system_playsound) 允许暂停起播并继承 Sound 默认频率/优先级；[isPlaying](https://www.fmod.com/docs/2.04/api/core-api-channelcontrol.html#channelcontrol_isplaying) 明确暂停 Channel 仍 considered playing。正文先占额度再创建及配置的顺序有依据。公共 playSound 说明与 [FMOD_RESULT](https://www.fmod.com/docs/2.04/api/core-api-common.html#fmod_result) 未提供文中可依赖的全错误原子回滚约定；正文将未知创建隔离明确写作保守政策，没有反过来声称 FMOD 必然残留播放。
3. **配置前提与资源归属。** [set3DAttributes](https://www.fmod.com/docs/2.04/api/core-api-channelcontrol.html#channelcontrol_set3dattributes) 要求 FMOD_3D。正文的固定资源映射和 2D 分支处理满足这一要求。[Sound::release](https://www.fmod.com/docs/2.04/api/core-api-sound.html#sound_release) 会停止该资源的实例，故失败清理只停止本 Channel、不释放共享 Sound 的责任划分正确。
4. **终止码和句柄。** [Mixing and Routing §6.1.1](https://www.fmod.com/docs/2.04/api/mixing-and-routing-in-the-core-api.html#channel-and-channel-group-handles) 对自然结束/stop 与偷取分别写 INVALID_HANDLE 和 CHANNEL_STOLEN；[Managing Resources §9.1.5](https://www.fmod.com/docs/2.04/api/managing-resources-in-the-core-api.html) 的偷取说明使用 INVALID_HANDLE。本轮再次看到该差异。正文保留两者但限定成功创建的原句柄、System/路由/资源有效性，未把未初始化句柄或已销毁 ChannelGroup 当正常终止。按返回值逐次检查输出、统一幂等归还的流程能处理自然结束与主动 stop 相撞。
5. **虚拟、排序与观察。** Managing Resources §9.1.1、9.1.4–9.1.6 支持时间继续推进、优先级先于可听性、永久偷取与虚拟恢复的区别。[Channel::setPriority](https://www.fmod.com/docs/2.04/api/core-api-channel.html#channel_setpriority) 的数值方向与正文纸面例一致。正文排除了静音阈值等会改变排序的条件，没有从优先级推导实际设备输出或玩家理解。[System::update](https://www.fmod.com/docs/2.04/api/core-api-system.html#system_update) 参与虚拟状态更新；文中没有声称一次 update 使后续所有查询成为原子快照。

## 设计与反例复核

- 逐项检查了“已登记成功重投”“已登记拒绝重投”“结果表满的未登记拒绝”三个分支。它们不共用无限去重承诺，结果保留期与实例终止分离。合法的新事件也不会因素材相同被错误去重。
- 多预算在同一所有者下预留，暂停、虚拟及清理不明都继续持有额度；关闭同时退还原记录的全局、类别与发声者额度。仅一次计数减法不能替代记录代次和归还标记，正文已经交代这些条件。
- 反例“高重要提示在入口满时到达”没有被排序策略偷偷解决，正文明确需要同时预留入口与实例份额。“旧槽位重用后收到停止”也由实例代次区分。
- 创建失败冻结、清理错误保留、轮询成本和时效性均是采用选择。若项目要求持续接收高价值提示，必须另行建立经确认的错误恢复协议与保留通路；不能单纯把 B 调大或无限重投。

## 本轮未覆盖

没有 FMOD 库编译、原生返回值观测、实际混音/听音、性能或设备故障恢复验证；没有对相邻 CRI 循环文章和预约播放全文作技术重认证。文章标题与范围不承诺这些能力，因此没有据缺少运行结果否定其文档依据的方法价值，也没有将方法通过扩大成整个音频专题通过。
