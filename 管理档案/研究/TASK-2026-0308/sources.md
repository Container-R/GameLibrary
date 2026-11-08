# 设置页序列测试：本轮来源与推理记录

核读日期：2026-11-08。仓库只读起点：`3f459949d8e580326ba77e18add259598458cbe5`。本文是方法文章，产品、控制器与测试计划为原创设计，未运行 Unity。原研究见同目录 `research.md`，其中后续步骤由本轮工作继续，不把历史未成稿状态当作当前状态。

## 原始材料及支持范围

| 编号与材料 | 本次实际核读位置及内容 | 支持主张与条件 | 正文位置 |
|---|---|---|---|
| 1 Unity Localization 1.5.14，OnSelectedLocaleChanged | Summary：初始化结束后调用，预加载结束 | 不足以声明项目文本赋值、布局或渲染完成；后半句是对接口承诺范围的判断 | 点击阶段 |
| 2 Unity Localization 1.5.14，StringChanged | Summary列首次订阅、SelectedLocale、变量、RefreshString、表/条目变化；已加载时新增订阅者收到现有值 | 字符串通知与用户点击不是一一对应关系；不声称框架本身把旧语言覆盖新语言 | 点击阶段、身份传播 |
| 3 Unity Localization 1.5.14，RefreshString | Returns与Remarks：活动加载时不能刷新，返回false；例子说明可能立即更新或等待表 | 受理状态需单独观测，仅限该方法，非全部语言选择API | 点击阶段 |
| 4 NIST作者预印本，2012 | 物理1–2页：Definition每行是符号排列，t子序列可不相邻；Example 2正反两行覆盖所有二元次序 | 正反L/S/P覆盖先后不覆盖所有相邻；重复/异步事件必须重新建模属于本文推导 | 三种覆盖 |
| 5 Unity Localization 1.5.14，GetLocalizedStringAsync | 含TableReference、TableEntryReference、Locale、FallbackBehavior、arguments重载；返回AsyncOperationHandle<string>，Locale可覆盖默认SelectedLocale | 可用显式输入和具体句柄承载捕获的请求记录；token机制是本文建议，不是框架自带 | 身份传播 |
| 6 Unity UI 1.0.0，Auto Layout | Layout Calculations：水平计算/设置然后垂直计算/设置；Triggering Layout Rebuild：延迟到渲染前 | 文本赋值和布局读取不是同一检查点；不把文档时机当实际游戏测量 | 布局检查点 |
| 7 Unity uGUI固定源码7ca0363…，包7.0.0 | CanvasUpdateRegistry.cs，CleanInvalidItems 152–193行；PerformUpdate 196–267行；注销/禁用418–450行 | LayoutComplete也用于清理，异常被捕获记录；布局后还有裁剪和图形更新。按实际函数分析，没有把示例调用注释当作API可编译范本 | 布局检查点 |
| 8 同一uGUI固定源码 | LayoutRebuilder.cs 70–104行及布局遍历实现：ForceRebuildLayoutImmediate直接调用Layout阶段；普通延迟重建说明 | 测试主动强制重建可能掩盖被测失效通知缺陷，是本文工程推论 | 布局检查点 |
| 9 Unity Test Framework 1.3.9 | Using the UnityTest Attribute：跨帧IEnumerator与yield return null跳一帧示例 | 时间推进不是指定请求语义完成的判据，此区分为本文推论 | 检查与等待 |

完整原始URL与版本见正文参考资料1–9。可变文档只按本次读取页面标识陈述，不宣称链接永久冻结版本。NIST作者按预印本首页为四人，项目页会议版列五人，正文已区分。

对应文档URL：
1. https://docs.unity3d.com/Packages/com.unity.localization@1.5/api/UnityEngine.Localization.Settings.LocalizationSettings.OnSelectedLocaleChanged.html
2. https://docs.unity3d.com/Packages/com.unity.localization@1.5/api/UnityEngine.Localization.LocalizedString.StringChanged.html
3. https://docs.unity3d.com/Packages/com.unity.localization@1.5/api/UnityEngine.Localization.LocalizedString.RefreshString.html
4. https://www.nist.gov/customcf/get_pdf.cfm?pub_id=906770 与 https://csrc.nist.gov/Projects/automated-combinatorial-testing-for-software/combinatorial-methods-in-testing/event-sequence-testing
5. https://docs.unity3d.com/Packages/com.unity.localization@1.5/api/UnityEngine.Localization.Settings.LocalizedStringDatabase.GetLocalizedStringAsync.html
6. https://docs.unity3d.com/Packages/com.unity.ugui@1.0/manual/UIAutoLayout.html
9. https://docs.unity3d.com/Packages/com.unity.test-framework@1.3/manual/course/unitytest-attribute.html

固定源码URL：
- https://github.com/Unity-Technologies/uGUI/blob/7ca0363fd41d8de5f3cbc6121fe9a5acf95c88c6/com.unity.ugui/Runtime/UGUI/UI/Core/CanvasUpdateRegistry.cs
- https://github.com/Unity-Technologies/uGUI/blob/7ca0363fd41d8de5f3cbc6121fe9a5acf95c88c6/com.unity.ugui/Runtime/UGUI/UI/Core/Layout/LayoutRebuilder.cs
- https://github.com/Unity-Technologies/uGUI/blob/7ca0363fd41d8de5f3cbc6121fe9a5acf95c88c6/com.unity.ugui/package.json

仓库提交注明Unity 7000.0.0a17的镜像，package.json声明7.0.0。另核读了官方仓库历史提交5ab4c0fee7cd5b3267672d877ec4051da525913c的两份对应源码，清理与注销调用LayoutComplete、布局后继续图形重建的机制同样存在；正文只引用当前固定快照，不将两版本共同核读扩张成全部版本保证。Localization 1.5.14、UI 1.0文档与uGUI 7.0源码用于分别说明接口与实现，不是已验证的统一安装组合。

## 原创推理和工程方案

内容提交必须捕获工作发起时的不可变输入与请求身份；完成时读取全局current重新标记结果会破坏归属。日志应来自实际赋值入口，并回读控件，而非仅复制测试替身计划结果。单线程并不自动消除setter重入，正文伪代码限定串行且无重入的提交过程。

布局签名E由实际依赖的单调版本组成。提出以Prelayout捕获、真实布局根阶段记录、PostLayout读几何的被动观察方案，前提是标准布局组、没有更晚尺寸改写，所有相关根均经过阶段且无异常。该方案没有Unity实现、编译或运行证据。正文没有把收到回调本身等同于布局成功，也没有在测试中替产品标脏或强制重建。

“最终正确”“提交历史无过期结果”“像素没有闪帧”三种主张分别需要最终快照、每次真实提交记录和对应渲染观察。本文模型只支持前两者的有限状态区别。

## 实际执行观察

`model/settings_model.py`、`model/results.json`和`model/README.md`为本轮原创Python有限模型及真实输出，独立执行者编写并运行，作者复核。无Unity、Playwright、原生布局、字体、图形或时钟实验。每项输出保留supports与not_tested，案例数不代表覆盖率或缺陷检出率。原研究的两请求小模型仍留存，不替代本轮模型。

本轮执行15个固定案例，作者再次执行所得JSON与保存结果一致。模型的request是已打开预览上的内容请求，不建模闭预览L/S保存目标与P读取目标的完整设置控制器；这些由正文作为待项目接入的契约说明。

## 相邻正文核对

已从固定仓库起点读取并通读：
- 测试设计/《游戏UI配置回归的约束建模与组合覆盖》：只承诺稳定配置，本题独立交付路径与异步测试，不向其塞入新主体。
- 异步资源/《关闭装备预览后，未完成的资源加载怎样收尾》：已有请求失效和资源责任说明，本题引用而不重复释放教程。
- 自动化测试/《自动测试角色到达终点后，还要检查什么》：已有过程与最终结果区分，本题必须进一步给出请求/布局观测接口和具体判据。

没有对全库正文进行语义穷举，不把目录检索当作全文精读。
