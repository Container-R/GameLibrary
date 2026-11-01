---
id: ROLE-MUSIC-001
title: 游戏作曲：把完整乐曲变成有意图的交互编配
type: role
status: source-backed
primary_discipline: MUSIC
related_disciplines: [SFX, NARR, DESIGN, PROG, QA]
related_roles: [composer, interactive-audio-designer, audio-programmer, narrative-designer, gameplay-programmer]
related_topics: [interactive-arrangement, musical-identity, stem-combinations, intentional-absence]
engines: [engine-agnostic]
platforms: [cross-platform-responsibility-not-validation]
versions: ["Darren Korb 原始访谈，2020-12-24", "Keiichi Okabe 原始问答，2018-03-07"]
updated_at: 2026-11-01
review_after: 2027-02-01
verification_method: 两份具名作曲者原始英文访谈/问答正文核对；三声部交互编配表为原创未执行建议；未试听、制作音乐或验证中间件与玩家效果
sources:
  - https://gameplay.co/hades-game-music-sound-design-darren-korb-supergiant-games/
  - https://blog.playstation.com/archive/2018/03/07/nier-automatas-composer-keiichi-okabe-reveals-the-secrets-behind-the-action-rpgs-award-winning-soundtrack/
---

# 游戏作曲：把完整乐曲变成有意图的交互编配

## 定位：可组合不等于每种组合都合适

本档案研究作曲工作中的一个具体问题：**完整作品拆成可移除的声部、可重复的段落后，哪些组合仍承担原定音乐功能，哪些缺席是刻意安排？**

把几个 stem 对齐，解决的是一起播放的技术前提，不自动决定它们应当怎样组合。作曲与编曲需要说明旋律、节奏、和声推进或音色在该段承担什么，再与交互音频共同选择可用版本。这里的“允许组合”仅指项目的音乐设计决定，不是版权许可，也不表示作曲者独自拥有全部叙事、玩法或发布决定权。

小团队可能由同一人作曲、编曲和实现；分工较多的项目可能分别交接。以下分开的是决策，不把两个实践样本升级为全行业岗位编制。

## 两份公开制作样本

- **Darren Korb，《The Sound of Hades》，2020-12-24。** Gameplay 的原创采访文字稿中，Korb 以 Supergiant Games 音频总监身份说明部分声部分合与段落推进，并谈到为一首歌曲的剧情落点预先构思写法。[S1] 采用的是他的具体制作叙述，不把主持人的评价或创作者的情感目标当作玩家效果数据。
- **Keiichi Okabe，PlayStation.Blog，2018-03-07。** 冈部启一在《NieR:Automata》原始问答中区分节奏先行与围绕旋律展开的写法，也讲述一首作品被安排到不同于原请求的场景。[S2] 这说明创作重点与使用情境值得明确，不证明那次使用有错，也未公开一套 stem 组合表。

两份所读正文均为英文：前者是媒体原创采访，后者是具名作曲者在平台官方博客上的问答。没有试听歌曲、分析乐谱或观看视频。

## 原创例子：三声部不是八种自动获准的编配

**完全假设，未创作或测试。** 一段探索音乐有低声部伴奏 A、独立旋律 M、打击乐 P。项目希望有稀疏漫游、活跃行进和一次突出主题的到达时刻。先约定这个例子里 M 承担主题陈述；这不是所有作品的规则。

| 使用目的 | 本例候选编配决定 | 交接时必须回答的问题 |
|---|---|---|
| 稀疏漫游 | 候选 A；把主题暂时缺席写成有意的背景处理 | 当前需要主题陈述，还是允许只保留质感？不能把 M 不响一律判成故障 |
| 活跃行进 | 候选 A＋P；是否加入 M 留给本段音乐判断 | 加入打击乐改变了什么？不能仅因轨道更多就宣称强度更高 |
| 突出主题的到达 | 候选 A＋M；P 是否参与须另定 | M 的入口是否依赖前置弱起或完整乐句？从任意中点打开它不等于完成主题陈述 |
| 没有合适的现成组合 | 另写版本、另设进入位置，或接受明确的表达折中 | 不让实现者通过任意静音替团队决定一种未讨论的编配 |

这些行没有声称 A、M、P 已经在和声、织体或音域上兼容。即使文件等长、节拍一致，候选仍需作曲/编曲评审；反过来，某声部单独听不完整，也不一定不适合作为特定情境的背景层。作品可以允许有意的沉默、不完整陈述或张力，不应建立“所有时候必须听见旋律”的机械检查。

### 交付的是音乐选择，不是组合数量

建议交付一份短的**编配选择表**，仅列实际需要的组合：每行写明使用目的、参与声部、主题或其他核心材料的角色、入口限制，以及明确接受的缺席。附可讨论的候选版本或工程定位，而不是仅标记“低/中/高”。此表本身不能证明听感。

若玩法可能越过中间状态，作曲与交互音频应共同确认仍有合适的音乐路径。需要桥段、不同入口或另一种编配时，应回到创作决策；不要假定在正确拍点开关轨道就解决乐句问题。实际调度与取消机制另见[音乐状态交接](../../solutions/audio/music-state-transition-contract.md)，本表不替代它。

## 接收与协作：分别检查三件事

1. **音乐意图是否明确。** 设计/叙事提出想突出或不突出什么；作曲/编曲给出候选及取舍。情绪词是目标，不是测量结果。
2. **实现是否采用该选择。** 交互音频确认可达组合、入口及退出；程序报告实际状态和播放机制。显示“主题模式”不证明旋律已按预期进入。
3. **情境中是否成立。** 听感评审需要真实候选与上下文；玩家理解或情感效果需要另行证据。本文没有完成这两种验证。

音乐结构、配器、和声、旋律与节奏判断是该工作的核心；DAW、记谱工具和导出流程服务于表达及交接，不是能力证明的替代物。技术人员可以核对文件格式、对齐、路由与状态，不能用这些检查自动批准编配；作曲者也不能以线性混音满意替代游戏内行为验证。

## 取舍与有界后续

手工为每个组合写独立版本会增加录制、编辑和维护成本；完全自由组合则把尚未讨论的音乐决定交给运行逻辑。合理目标不是最大化组合数，而是为实际需要的情境保留足够的、有意图的选择。

若继续验证，先只制作上述必要候选，分别记录创作者评审和实际情境检查；不要为凑覆盖率枚举全部子集。无须从两个案例推导统一轨道数量、情绪阈值、编配规则或最优工作流。本档案不提供职业收入、招聘或全行业权限结论。

- [交互音频设计](../audio/interactive-audio-designer.md)：素材、事件、集成与交付接口；本文细化音乐内容选择，而非再造一份通用 manifest。
- [PCM 循环帧合同](../../solutions/music/pcm-loop-frame-contract.md)：素材边界与计数；数值正确不等于本例编配已获音乐认可。
- [离线 stem 归一化](../../solutions/audio/silent-stem-normalization-boundary.md)：输入寿命和增益行为；它不决定哪些声部应共同出现。

## 来源与边界

详见[来源定位](../../research/source-notes/game-composer-role.md)。正文中的三声部、候选组合和接收步骤均为原创未执行建议，不是来源项目内部规范。

- **S1** James Parkinson / Darren Korb，[The Sound of Hades](https://gameplay.co/hades-game-music-sound-design-darren-korb-supergiant-games/)，Gameplay，2020-12-24；Korb 关于声部分合、段落推进及 Good Riddance 写作的回答。
- **S2** Keiichi Okabe，[Nier: Automata’s composer Keiichi Okabe reveals the secrets behind the action RPG’s award-winning soundtrack](https://blog.playstation.com/archive/2018/03/07/nier-automatas-composer-keiichi-okabe-reveals-the-secrets-behind-the-action-rpgs-award-winning-soundtrack/)，PlayStation.Blog，2018-03-07；写作方法问答和场景使用轶事。
