# 非语音关键声音提示：原始来源预审

访问2026-10-31；仅阅读公开正文与图示说明，未观看嵌入视频、未进入需要NDA的API链接、未执行玩家试验。Microsoft页面虽含通用authorization提示，正文由公开工具正常返回；未绕过访问限制。

## 官方来源边界

1. [XAG104](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/104)，Microsoft，页面最后更新2026-03-04，非精确首发日期。定位Goal/Overview/Implementation guidelines。
   - 支持：区分对白字幕与覆盖声音信息的captions；重要且未以视觉表达的非语音声音需要替代；来源方向不明确时提供空间指示；开始前可配置或默认启用；类别独立开关、表现定制、预览、避免遮挡。
   - 不支持：特定战斗预警毫秒阈值、通用去重/优先级算法、完整声音事件总线架构、必然改善完成率。这些若出现须标原创合同或待测。
2. [XAG103](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/103)，Microsoft，最后更新2026-03-04。定位Implementation guidelines，关键音频信息的额外感官通道及haptics Note（本次文本200–203行）。
   - 支持关键声音用额外感官表达；图形可表达类型/方向。触觉不是唯一替代，因为设备可能不支持、玩家可能关闭或无法舒适使用。不能把静音+振动算所有玩家可访问。
3. [XAG总览](https://learn.microsoft.com/en-us/xbox/accessibility/guidelines)，V3.2明确发布于2023-06-08；页面最后更新2026-08-14。Introduction明确其为最佳实践，不作为合规/法律验证清单。示例内容仅说明特定方面，不代表整款示例游戏满足所有指南。文章不能声称XAG认证通过。
4. [Game Accessibility Guidelines: significant background sounds](https://gameaccessibilityguidelines.com/provide-captions-or-visuals-for-significant-background-sounds/)，原始指南发布者，未见作者个人名或日期。正文提出删去该声音是否影响故事、玩法或氛围作为重要性判断，并指出不必把所有声音转成文本。支持选择重要信息、避免过载的设计视角。该页转载玩家反馈及14%个案统计未追溯原始数据，故不拿这些作为当前工程收益证据。

## 待审矩阵必须分离的原创推导

- 信息权限/隐藏信息：替代提示应表达玩法授予玩家的感知信息，不能直接泄露敌人真实坐标、身份、未揭露剧情或随机结果。该限制是工程公平性/叙事设计约束，不是假称XAG写了同一算法。也不能以“防剧透”为由抹掉本可听到的关键线索。
- 时机：显示起止、事件取消、同源重复、同时声音竞争、镜头旋转后的方向参考系须有项目合同；指南没有为这些给出统一数值。
- 过载：高优先级信息不能因字幕队列阻塞而错过行动窗口；“重要信息覆盖”不是所有混音事件无差别刷屏。
- 体验边界：静音桌面走查只检验合同覆盖，不能替代聋/重听玩家、阅读负荷及真实操作验证。无需也不应捏造参与者或通过率。
