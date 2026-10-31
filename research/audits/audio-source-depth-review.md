**集成后记（2026-10-31）**：下列固定提交、FMOD启动拒绝路径、线程直接来源与单参数写入者前提已纳入音乐条目；本审查历史记录保留。未执行中间件测试。

# 交互音乐条目：来源与异步语义深度复核

日期：2026-10-31。对象：本地 `gamelibrary-work/solutions/audio/music-state-transition-contract.md`。本轮只写此审查稿；没有修改工作库或 GitHub。未运行引擎、中间件、音频输出或 SDK 测试。

## 结论先行

既有 FMOD 创作机制与 Wwise 历史限定没有发现直接矛盾。取得真实 Wwise 固定提交，建议替换 mutable master。发现一个应补入状态机/验收的 **FMOD START_FAILED 非对称回调路径**：不能假定每次启动请求都有 STARTING 或最终 STOPPED 通知。建议一并明确 start 的成功提交不是 Active 或可听见的证明。

## 1. Wwise 固定证据已取得

通过已授权 GitHub 只读插件：

1. `search_commits(repository_full_name="audiokinetic/WwiseIncludes", query="", topn=2)` 返回提交 `be96b3af20bf27647f458bac10d973a63cd75e02`，时间 `2018-01-25T16:04:41Z`，主题为更新 2017.2.0 build 6500 SDK includes。
2. `fetch_file` 用该完整 commit ref 读取 `SDK/include/AK/SoundEngine/Common/AkSoundEngine.h`，实际头部版本是 v2017.2.0 Build 6500。返回文件 blob SHA：`2645aa63c9cf13731afe8129e21b206bdfe21968`（不是 commit SHA）。
3. 同一固定版本文件正文核对：PostEvent 异步说明在 L578，失败返回无效 playing ID；SetSwitch 关联 game object 在 L3100–3105；SetState L3179–3183 无该参数；线程配置 bUseLEngineThread 在 L167。不能把音频处理线程配置当成所有回调线程的完整文档。

建议永久链接（已由工具返回确认，不是猜测）：

https://github.com/audiokinetic/WwiseIncludes/blob/be96b3af20bf27647f458bac10d973a63cd75e02/SDK/include/AK/SoundEngine/Common/AkSoundEngine.h

提交元数据：
https://github.com/audiokinetic/WwiseIncludes/commit/be96b3af20bf27647f458bac10d973a63cd75e02

建议替换 frontmatter 与正文两处 master URL；正文改为“固定提交…中的历史 SDK 头文件标明…”。仍保留“当前 Wwise 官方帮助访问受阻、此材料不证明当前兼容”的限制。历史创作案例 2010.1.3 与此 SDK2017.2.0 是两份不同时代资料，不能说二者曾在同一工程联合验证。

## 2. FMOD 创作部分逐项对应

来源：FMOD Studio User Manual [Authoring Events](https://www.fmod.com/docs/2.04/studio/authoring-events.html)，页面页脚2.04.00 / 2026-09-29。这是手册日期，不是本轮确认的软件发布日期。

| 既有主张 | 精确章节 | 复核 |
|---|---|---|
| 独立实例、本地参数可不同 | §4.1.3；§4.10 | 有支持；全局参数不属于实例独立值 |
| transition/magnet region 可量化，marker/loop 不具相同选项 | §4.11.1 | 有支持；不要简化成“一切转场都能量化” |
| 同一逻辑位置有多个可跳转候选，符合条件的最上标记优先 | §4.11.2 | 有支持；不是“最新请求全局优先”规则 |
| 桥接时间线可先于目的地 | §4.11.4 | 有支持；不是立即抵达 |
| 对齐退出边界不保证目标乐句相位正确 | §4.11.3 + 本文设计推论 | offset 独立决定入口位置；应保持为工程验收推论 |

文章没有把 Wwise 的历史取消机制迁移成 FMOD 承诺，处理正确。

## 3. 必补边界：失败启动未必产生 STOPPED

新核对来源：[FMOD 2.04 EventInstance API](https://www.fmod.com/docs/2.04/api/studio-api-eventinstance.html)，`start`、`release`、`FMOD_STUDIO_EVENT_CALLBACK_TYPE`。

短述：重复 start 会重启已播放实例。START_FAILED 表示复音设置不允许启动；该情况下不会发生 STARTING、STARTED、STOPPED。release 标记待释放，实例停止后由异步更新销毁；release 不等于 stop。STARTED 可能等素材加载，不能当设备可听时间。

**建议插入原文章生命周期段落的短补充（原创适配建议）**：

> FMOD 2.04 的启动失败还可能通过 START_FAILED 回调报告；该路径不会补发 STARTING、STARTED 或 STOPPED。适配器应把启动拒绝作为独立结果，按当前 generation 与句柄归属完成状态回收或显式重试决策，不能无限等待 STOPPED。提交 start 后仍处于本地 Starting，不能仅凭返回成功标记 Active；Active 的工程定义及对应观察证据应明确。这里的应用状态与 SDK 同名枚举不是自动一一对应。

建议新增验收行：

| 复音限制拒绝启动 | 接收/诊断 START_FAILED，不等待不存在的 STOPPED；不循环重启；仅处理当前实例，旧会话资源按旧归属清理 | 初始化配置、限制设置、请求/回调轨迹与句柄日志 |

这不是现有文章已承诺的错误行为，而是补齐原方案未覆盖的失败路径。不要声称本轮已执行该测试。

## 4. 异步与线程措辞：增加当前 FMOD 来源，降低对历史头文件依赖

来源：[FMOD 2.04 Studio API Guide](https://www.fmod.com/docs/2.04/api/studio-guide.html)，§13.4 Studio System Processing、§13.8 Sample Data Loading、§13.11 Event Callbacks。

短述：默认模式将命令交异步处理；同步初始化也仍通过 update 处理队列。素材未完成可停在 STARTING。回调线程由初始化配置决定；deferred 设置对 marker/beat 的处理不能推广成所有回调都在游戏线程。

建议作为既有“提交不等于播放”“不猜回调线程”的当前版本直接依据。不需要在正文扩展成线程教程。当前文章使用条件性描述而非硬断言，未发现其线程主张错误。

## 5. 应保留的设计边界

- 同值去重仅对适配器成功提交缓存有效；如外部系统或事件内部逻辑会改同一参数，单写入者假设应明确，否则 submitted_mode 不是参数实际值。可加一句“若其他写入者存在，先仲裁或使缓存失效”；这是设计补强，不是本轮新验证的通用引擎语义。
- 旧 generation 与 revision 联合检查已补入当前稿，正确；不得再简化为只防跨会话回调。
- release、样本数据与 bank 所有权不同层级；文章目前不提供具体卸载代码，因此无需凭此稿新增全套资源管理流程。
- 参数设置成功、事件 STARTED、音乐段落观察、设备可听时刻是不同层次；不要合并为一个“播放成功”布尔值。

来源复核与建议均为静态审查。本轮没有引擎实测，没有当前 Wwise 文档兼容性结论，没有 GitHub 写入。
