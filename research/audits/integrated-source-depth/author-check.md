# 三项既有主题深化：作者侧对抗性自查

2026-11-01。**所查整合未发现需要阻止采用的实质问题，无修订请求。** 这是作者侧自查，不是全新独立审阅：本检查者撰写了三份新增小节与来源追加，并参与其来源阅读。此次对主线整合后的确切字节及基线差异重新检查，不把自己之前的写作当作第二份独立证据。

范围为本地整合快照 `gamelibrary-publish-data-trigger` 中三篇正文和对应三份安全来源记录。没有重新审计全库、运行档案或既有实验；没有运行软件示例，没有修改被审文件，也未向远端写入。本结论绑定下面的内容摘要，不声称该快照已经发布。

## 确切比较对象

| 文件 | 指定基线快照 | 基线 SHA-256 | 整合 SHA-256 |
|---|---|---|---|
| `solutions/engine/addressables-content-update-baseline.md` | `gamelibrary-publish-riot-diagnosis` | `3e6cce88a51371ae0001e362ef2d1faa27b2b4ab2645457d25f6f095dd313218` | `4b61e9ff20ab730d7566a7d9a01a0b204fa4ea9390308971ee38299a32faf9a9` |
| `research/source-notes/addressables-content-update-baseline.md` | 同上 | `e00741828e6b0766836f7a2568af5e66574d3ad27435d9bd8826a667728f54e0` | `ea98b43e276c3e451e3d2ac4a6a6714e8e80a1e76d4d593e2f6dee7e186904c9` |
| `roles/localization/localization-coordinator.md` | `gamelibrary-publish-addressables-depth` | `fe5e65f65eb02da5f95eb18c809baa0a90f2e2fe5f2da4d7cf1d13f51e501e25` | `e7a50a13e496a327157d81a55ff96b717fcca0ab2795aac8e4d5a9e2b9cc6796` |
| `research/source-notes/localization-coordinator-role.md` | 同上 | `70479f0c5b8aac53cbad7f2654565eafd32ff0a11eaadf431a46fd7b7a6837b7` | `b031331649e37d6ad5544f3a5e28367e314ea09af272d8100fec2a56120609f9` |
| `roles/data/game-data-analyst.md` | `gamelibrary-publish-loc-context` | `386c78014f630b45e4ec1909907e9c9904dccdd4ef33ef3df837682a47086637` | `4b994d5bf96beab94df2f3c94587aa44e2d3e6da29e2bf1d0001e9c534d35863` |
| `research/source-notes/game-data-analyst-role.md` | 同上 | `50561caa24eb94ec26775aa05374006aecd362f018842ee9f50ed1107fd651e7` | `102164e6ba2dd7b988c0e334374f2edc9931b5f5540da6bb40f51534ae196660` |

已逐项检查完整差异；正文未改部分在本轮来源选择中已全文读取，来源记录也核对了保留段与新增段。这里的摘要只是定位文档字节，不是执行或产品身份认证。

## 逐项挑战与结果

### Addressables：是否把依赖例子变成预先知道的构建结果？

没有。新增 §3.1 明确是装备／共享纹理假设，实际组变更、依赖表示、bundle 和 catalog 结果保留未知。官方示例的依赖传播与本库的资产核对表分别归属；不是换名后宣称独立复现。Bundle Mode 只用来阻止组数等同输出数，未概括全部打包细节。Unique Bundle IDs 的引用 bundle 重建成本与限制检查的资产组织分开，未把两个机制相互冒充。

复核依据为已实际读过的官方 [Content update dependencies](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-examples.html#content-update-dependencies)、[Unique Bundle IDs](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-build-settings.html#unique-bundle-ids-setting) 与 [Bundle Mode 配置行](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/ContentPackingAndLoadingSchema.html#advanced-options)。原始 previous-state 缓存条件、实际消费字节的证据限制、未执行 Unity 与旧版客户端的边界没有被补充覆盖掉。来源记录保留原部分阅读历史，新增日期不伪装成原始完整阅读。

### LOC：是否由写注释跳到真实 UI 会选对消息？

没有。整合后的句子补明“源消息与 context 相同”的条件；说明归集与二元消息键的区别成立。适用范围明确是常量单数内置提取、POT、有效非跳过 PO 及默认 Translation；未把虚方法、完整语言域或回退写成已查明。fuzzy 例外保留，未声称所有注释均无行为。是否拆分两种 Confirm 用途仍先由语言接收者判断，没有强迫所有同文异境换词或拆键。

已读固定源码依据是 `89cea143987d564363e15d207438530651d943ac` 下的 [生成器键与注释归集](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/editor/translations/template_generator.cpp#L77-L99)、[字段写出](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/editor/translations/template_generator.cpp#L175-L213)、[默认消息添加／查找](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/core/string/translation.cpp#L145-L175)。Plarium／PlatinumGames 的实践陈述没有被改成 Godot 实现或验证结果的来源；角色仍明确引擎特定例子与总体协调职责的差别。

### DATA：是否把对称筛选冒充随机实验或完整估计方案？

没有。主线已加入“设以玩家为随机分配单位”，同时保留资格及此前路径不受处理影响的假设。这个设定不是已实施的随机化方案。控制组只记录本会触发条件，不被写成已经展示提示或揭示个人潜在结果。点击筛选的缺陷与全部分配／共同资格的不同取舍清楚，未凭假设计算功效。

最重要的完整性限制也保留：资格不等于估计方案；首次触发前日志的处理不能与原教程开始事件、尝试分母及玩家单位混用。未发现 SRM 或补集差异不被写成无偏证明；比例指标没有使用未经推导的子群乘法外推。

来源为已读 Microsoft [实验前 Counterfactual Logging](https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-pre-experiment-stage/) 与 [实验后 Triggered/Non-Triggered Users、Dilution](https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-post-experiment-stage/)。新增段明确是跨领域迁移，不把 Microsoft 方法或旧合成 DATA 输入说成游戏效果证据；原角色的两份实践者来源没有被扩成统计方法来源。

## 当前 verification_method 原样核对

- Addressables：六篇 Unity 官方版本化文档在所列章节核对；原创基线选择、依赖交接与旧版客户端验收协议，未执行 Unity 构建、内容托管或客户端加载测试
- LOC：两篇具名实践者原文及 Godot 4.6 文档和固定源码特定链路核对；同文异境交接表为原创未执行建议；未翻译、集成、运行界面或执行LQA
- DATA：日英第一方实践者及 Microsoft ExP 方法原文所列章节核对；教程比较与资格设计为原创未执行建议；未收集玩家数据、执行实验或测量改版效果

三项都增加了可定位的机制知识，而不是新增执行证据：依赖消费者与打包粒度、说明集合与查找键、共同资格与观察窗口。此次未发现旧限制与新结论之间的实质冲突；无需为制造审计结果而提出修辞改写。结论不延伸为完整源码正确性、一般因果推断保证或全仓库清查。
