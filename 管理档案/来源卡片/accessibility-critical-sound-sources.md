---
id: SRC-A11Y-CRITICAL-SOUND-001
title: 关键非语音声音可访问性原始来源取证
type: source
status: source-backed
primary_discipline: A11Y
updated_at: 2026-10-31
sources:
  - https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/104
  - https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/103
  - https://gameaccessibilityguidelines.com/ensure-no-essential-information-is-conveyed-by-sounds-alone/
  - https://www.naughtydog.com/blog/the_last_of_us_part_ii_accessibility_features_detailed
---

# 原始来源取证与断言边界

读取日期：2026-10-31 UTC；方式：公开网页正文文本读取及指定段落复查。四份文档来自三个发布方：XAG103/104是同一机构的相关指南，不算两个独立用户研究；Naughty Dog功能说明与PlayStation转载不重复计数。所有URL为可变网页，没有固定提交或网页内容hash，不伪装不可变快照。

## S1 — Microsoft XAG104

- URL：https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/104
- 标题：Xbox Accessibility Guideline 104: Subtitles and captions。
- 页面更新：2026-03-04；这不是该指南初次发表日期。
- 已读定位：Goal；Overview；Implementation guidelines，尤其非语音captions与空间提示、开场前设置、类别控制、呈现配置。抓取定位：正文33–38、51–70、84–121行；行号会随站点变化，章节/条目才是稳定检索入口。
- 支持：对白与非语音信息不能混为一类；检查重要声音及其空间上下文和呈现可配置性。
- 不支持：本项目通用毫秒延迟、固定并发队列算法、完整认证完成、本文候选措辞的玩家效果。

## S2 — Microsoft XAG103

- URL：https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/103
- 标题：Xbox Accessibility Guideline 103: Additional channels for visual and audio cues。
- 页面更新：2026-03-04。
- 已读定位：Goal/Overview；Options for multisensory communication，Visual options、Spatial audio、Haptic options；Implementation guidelines。抓取34–38、52–116、138–148、200–203行；最后一处直接说明关键声音的其他感官表达与触觉不宜独占的原因。
- 支持：感官渠道有不同适用条件；颜色不是唯一信息载体；触觉不能作为唯一替代；多种视觉表现不能自动覆盖无法依赖视觉的玩家。
- 不支持：本文设计的身份披露上限、方向可信度分级或具体拥挤调度是XAG指定算法；本稿把这些明确标为原创推导。

## S3 — Game Accessibility Guidelines

- URL：https://gameaccessibilityguidelines.com/ensure-no-essential-information-is-conveyed-by-sounds-alone/
- 标题：Ensure no essential information is conveyed by sounds alone。
- 页面未显示发表/更新日期；不能由网站页脚或搜索爬取时间推算。
- 已读定位：标题下正文、Category & Level、About the guidelines；抓取9–13、18–20、35–37行。
- 支持：对白以外也有必要声音信息；静音首次体验可帮助内部发现缺口。
- 边界：这是指南团队原始建议。页面引用的玩家发言未作为本研究数据；未访问其论坛链接、未试玩示例；静音内部检查不代表真实聋人/重听玩家研究。

## S4 — Naughty Dog历史开发者功能披露

- URL：https://www.naughtydog.com/blog/the_last_of_us_part_ii_accessibility_features_detailed
- 标题：The Last of Us Part II: Accessibility Features Detailed。
- 署名：Matthew Dunnerstick；发布日期：2020-06-09。
- 已读定位：Accessibility Presets；视觉/听觉相关设置表；Subtitles。抓取14–17、144–160行。部分功能表带补丁条件，不能消除这些版本限定。
- 支持：一个开发者实际公开设计的多选项组合：听力预设、字幕相关配置与HUD/触觉提示可以协同，并可单项调整。
- 不支持：当前Remastered版本功能完全相同；每个玩家都受益；本库已经实机测过；选项存在等于信息一定被理解。该源不是用户研究论文。

## 原创内容归属

[主方案](../../GameLibrary/本地化与无障碍/无障碍设计/声音信息/怎样让关键声音信息不只依赖听觉.md)的可知范围、相对行动窗口、拥挤/取消策略和跨岗位接收合同，以及[泵站假设遭遇](../来源笔记/critical-sound-encounter.md)全部为本研究原创。后者的事件、对话和缺陷版本不是任何原作复述，不包含真实玩家或受试数据。

正文没有复制游戏截图、音频、表格或源码；仅短述相关机制后自行分析。未播放嵌入视频，未调用可能受限的GDK接口。静态信息审计不提供GPU、引擎、设备、呈现或认证结果。

## 归档关系

本档案对应[主方案](../../GameLibrary/本地化与无障碍/无障碍设计/声音信息/怎样让关键声音信息不只依赖听觉.md)与[原创假设遭遇](../来源笔记/critical-sound-encounter.md)。来源依据、原创合同、假设反例和未执行的验收保持分层。
