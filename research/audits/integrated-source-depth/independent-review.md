# 三项正文深化：独立来源审查

审查日期：2026-11-01。结论：**在以下精确快照和新增正文范围内，未发现阻断发表的实质问题。** 这是来源与论证审查，不是运行验证、完整文章全部历史主张复核或全库安全认证。

## 审查对象

SHA-256 对应所读正文文件的完整字节；比较范围为指定旧版与本版的正文差异。

| 正文 | SHA-256 | 比较基线 |
|---|---|---|
| `solutions/engine/addressables-content-update-baseline.md` | `4b61e9ff20ab730d7566a7d9a01a0b204fa4ea9390308971ee38299a32faf9a9` | `gamelibrary-publish-riot-diagnosis` 同路径 |
| `roles/localization/localization-coordinator.md` | `e7a50a13e496a327157d81a55ff96b717fcca0ab2795aac8e4d5a9e2b9cc6796` | `gamelibrary-publish-addressables-depth` 同路径 |
| `roles/data/game-data-analyst.md` | `4b994d5bf96beab94df2f3c94587aa44e2d3e6da29e2bf1d0001e9c534d35863` | `gamelibrary-publish-loc-context` 同路径 |

阅读了三项差异、相邻论证和对应来源笔记；随后独立打开决定性原始资料。未读取链接所指历史实验，未执行引擎、查询或玩家实验。后续文件变化不自动继承此结论。

## 1. Addressables：接受 §3.1 的有限结论

独立读取 Unity 官方 1.21.21 页面：

- [Content update dependencies](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-examples.html#content-update-dependencies)：正文及单支、共享依赖、资产间引用链表格。
- [Group restrictions 与 Unique Bundle IDs](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-build-settings.html#unique-bundle-ids-setting)：静态/动态处理及 ID 共存、引用者 bundle 重建段落。
- [Bundle Mode](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/ContentPackingAndLoadingSchema.html#advanced-options)：三种打包模式配置行。页面元数据标识 1.21.21。

未编辑消费者进入更新组有官方假想示例支持。正文没有把它外推为任意依赖检测算法，也没有将迁组、打包输出和用户下载混为一谈。Unique Bundle IDs 的重建影响与限制检查分开，符合来源。新增价值是把原来只按变更文件交接的范围扩展到消费者、实际打包和语义接收；不是仅增加免责说明。

尚未给出真实迁组清单、bundle 数或下载成本是合理边界，不是掩盖已经作出的结果断言。此段可指导检查设计，不能替代项目内构建工具和输出核对。

## 2. Godot：接受说明与消息身份的机制链

独立读取 [Godot 4.6 gettext 文档](https://docs.godotengine.org/en/4.6/tutorials/i18n/localization_using_gettext.html) 的提取、说明、context 与 fuzzy 部分；通过官方仓库 tag 接口确认 `4.6-stable` 指向 `89cea143987d564363e15d207438530651d943ac`。固定实现通过 GitHub 文件接口读取，网页抓取失败未被当成成功证据：

- [GDScript 提取器](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/modules/gdscript/editor/gdscript_translation_parser_plugin.cpp#L76-L140)：76–140、328–356，常量判定、说明与 context 分开传递。
- [模板生成器](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/editor/translations/template_generator.cpp#L37-L213)：37–213，按 context/source 键归集，说明集合与输出字段分离。
- [PO 读取器](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/core/io/translation_loader_po.cpp#L140-L321)：140–321，context 传入添加消息路径，含跳过处理。
- [消息键](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/core/string/translation.h#L44-L61) 44–61 与 [默认添加/查找](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/core/string/translation.cpp#L145-L175) 145–175。

同 source/context 下，不同译者说明不建立不同消息键；这项机制足以支持两个同时存在的 Confirm 用途在确需不同译文时交接不同 context。正文没有把语义判断交给引擎，也没有把原先单按钮用途修订偷换为已经发生的双按钮故障。fuzzy、虚方法覆盖与语言域/回退边界明确；未执行不妨碍这个源码支持的有限结论，但不能据此宣称项目集成已通过。

## 3. DATA：接受反事实记录的有限迁移

独立读取 Microsoft ExP：

- [Pre-Experiment Stage](https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-pre-experiment-stage/)，2020-07-31，Set Up Counterfactual Logging：控制组触发标记、完整覆盖、额外成本与较宽资格取舍。
- [Post-Experiment Stage](https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-post-experiment-stage/)，2021-12-24，Segment By Triggered/Non-Triggered Users、Dilute Gains：首次触发前日志、SRM/补集、总体解释及比例指标限制。

跨领域来源与游戏假设区分清楚。首次机会前资格和到达路径不得已受处理影响，是迁移成立的关键，不被同名字段或随机分配标签替代。拒绝只筛点击者有实际方法价值；观察单位/窗口与原尝试分母之间的断点也明确指出。未异常的 SRM/补集不被写成无偏证明，比例指标不机械乘触发率。

本段仍不是完整估计方案，但正文主动限定这一点，并给出需要交接的资格谓词、评估时点、遗漏影响理由及指标窗口。这不是用边界掩饰已声称提供的统计实现。实际实施仍须设计日志、指标、分配与推断；本文未许诺这些已经完成。

## 总体判断

三项新增都有可定位的机制和具体决策接口，且对旧文有实质增量。官方机制、研究者迁移与未观测结果没有混写。没有需要为了审稿而补造的缺陷，也不建议仅为增加篇幅扩展到当前未研究的完整运行路径。接受范围仅为上述精确快照的新增来源支持正文。
