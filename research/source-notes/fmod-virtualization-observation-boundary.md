# FMOD 虚拟化观察层：来源与适用边界

访问日期：2026-11-01。服务于[音乐状态交接契约](../../solutions/audio/music-state-transition-contract.md)的源文本补充，不是运行验证报告。

## 读取范围

| 原始来源 | 实际读取的相关位置 | 本节采用的范围 |
|---|---|---|
| [Core API：Managing Resources](https://www.fmod.com/docs/2.04/api/managing-resources-in-the-core-api.html) | §9.1.1、§9.1.5–9.1.7，尤其 Interaction with the Core API Virtual Voice System | 区分事件与声道观察，以及保留虚拟声道和已被抢占的句柄；Core 返回策略不升级为 Studio 整体重启策略 |
| [Studio：Advanced Topics](https://www.fmod.com/docs/2.04/studio/advanced-topics.html) | §16.4.1–16.4.2 | 各 stealing 结果需要分开命名；虚拟事件继续其内部行为不等于其底层各声道都参与混音 |
| [EventInstance API](https://www.fmod.com/docs/2.04/api/studio-api-eventinstance.html#studio_eventinstance_isvirtual) | isVirtual；callback types 中 START_FAILED | 查询作用域与已有启动拒绝分支，后者不是本次新增运行结果 |

三页页脚均标示 **2.04.00（2026-09-29）**。这是阅读时的文档身份，不据此断言软件发布日期、任何已安装版本行为或未来兼容性。`/2.04/` 是可变的版本系列网址，不是不可变源码提交。读取的是正文，不声称观看视频、试听素材或从图形推导测量值。

## 源文本与原创合同的分界

正文的分层观察表、入口／尾部条件例子及其恢复决策均为原创、未执行建议。来源支持具体 API 层次区别，不提供本文字段模式、原子观测机制或产品级提示补偿算法。多次查询的身份、成功状态与时钟关系仍要由集成实现证明；不能靠拼接不同时间的记录制造一致快照。

Core 指南对播放后虚拟声道排序的查询建议涉及 `System::update`；这不提供跨 Studio／Core 的任意时刻原子读取保证。Studio 明列的停止、拒绝与虚拟化结果应以各自说明为准，不能把另一节的简写视为通用策略定义。

本文没有验证流式 I/O、编解码器 seek、采样精度、恢复必达性或提示语义期限。real 仅指中间件实际混音状态，不是物理输出证据。未把 Wwise 访问受阻的当前文档、历史 Wwise 项目或旧假端口测试当作 FMOD 虚拟化验证，也不建立跨产品等价关系。旧模型的测试数与适用范围保持不变。
