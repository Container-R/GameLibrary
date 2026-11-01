# 叙事设计与写作职责：来源定位

对应 [ROLE-NARR-001](../../历史正文/roles/narrative/narrative-designer-writer.md)，访问2026-11-01。本文记录定位，不重复正文事实概括。

| 原始材料 | 身份、日期与定位 | 使用边界 |
|---|---|---|
| [Guerrilla Spotlight: Annie Kitain](https://www.guerrilla-games.com/read/guerrilla-spotlight-annie-kitain) | 官方工作室采访，2023-04-17；受访者 Annie Kitain，Lead Writer；采访者未署名。写作过程与协作/挑战问答，网页文字68–79 | 区分受访时角色与其谈论的项目，不泛化岗位权限或排列覆盖 |
| [Monolith Soft：シナリオプランナー編](https://www.monolithsoft.co.jp/interview/2307.html) | 2023-07-18；受访者仅标姓河野、佐藤、岩本。范围85–105，规划/事件127–138，修改与下游145–175，表达/实现186–200，反馈233–242 | 页面声明委托外部采访者制作；工作室正式发布，不是独立生产审计。未将所有职责强行对应单一游戏 |
| [Building Non-linear Narratives in HORIZON: ZERO DAWN](https://www.guerrilla-games.com/media/News/Files/GDC2017_Szczepanski_BuildingNonLinearNarrativesInHorizonZeroDawn.pdf) | Leszek Szczepański，Gameplay Programmer，Guerrilla；Game Narrative Summit，GDC 2017。27页；重点PDF页11、14–19、22、25–26，均从1开始。具体日及文件修订未知 | 读取抽取文字，未分析图片/连线或视频；这是任务系统材料，不是对白条件数据库说明 |

两篇访谈正文与演讲抽取文字实际可读。没有取得上述工作室的内部模板、源代码、对白资源或本地化包；正文桥梁例子及语义交接表是原创未执行建议，不可归为任一家公司的实施方式。未测玩家理解、译文、存档或奖励重复执行。

不复制来源图片、PDF、游戏对白或长段翻译；仅有限转述、链接与原创分析。发现阶段另一场 GDC2021 Dialogue Stubbing PDF 返回403，未绕过访问限制，也不以搜索摘要充当已读演讲。既有 ink 文献分析不是这些公司的生产证据。

## 2026-11-01 补读：S4，ink 的 glue lookahead 与外部函数绑定

官方 `inkle/ink` **v1.2.1** 标签对应固定提交 `35c63e52f1d36060930dc7ed3cfba38ea224b528`。本次采用同文件 [ink-engine-runtime/Story.cs](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs) 的以下范围：

- [ContinueSingleStep，590–660](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L590-L660)，及 StateSnapshot／RestoreStateSnapshot，788–825。
- [CallExternalFunction，1943–2028](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L1943-L2028)：字符串求值拒绝、快照探测门与实际 delegate 调用位置。
- [BindExternalFunctionGeneral，2038–2061](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L2038-L2061)，及 [无参数 Func／Action 重载，2104–2150](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L2104-L2150)：核对注释与参数默认值，不能概括为所有绑定入口相同。

这是单一官方 C# 实现的局部控制流与接口注释，不适用于未经核对的 inkjs 或其他版本。正文桥梁发奖是原创条件情景；对执行位置的接收建议未编译、运行或接入奖励系统，没有实际调用次数或事务保证。没有将已有存档兼容分析或其他引擎观察转移为本例证据，也没有复制源码、真实对白或图像。原岗位访谈与演讲的历史阅读范围不变。
