# 独立技术审稿

日期：2026-11-08。最终结论：**通过**。首轮结论为需修订，T1 已解决。审查性质：未参与初稿的独立模型技术审稿，不是真人试用或 Unity 运行验收。依据项目研究与审稿规范；首轮通读全文、sources.md、模型源码与说明，自主核对决定结论的原始来源并复跑模型；修订后再次通读全文。

## 首轮问题与解决记录

### T1：关闭起点与串行基线的完成语义没有接通（已解决）

位置：第二节“先固定一个可恢复的起点……预览关闭”及“每项操作完成后才进行下一项”；第三节 AcceptLanguage / Complete 伪代码；回归表“L完成→S完成→P”。

影响：正文先让读者在预览关闭时执行 L 并等待完成，但后面的内容完成路径会在界面关闭时拒绝结果，统一等待条件又要求指定 token 的内容提交和匹配布局。因此仅照正文，读者无法决定 L→S→P 中 L 的等待条件，可能等到超时，或自行发明与正文不同的后台预加载语义。P 打开时究竟沿用哪个请求、是否产生新界面请求，也没有定义。有限模型不能补上这一步：它从打开状态开始，并直接拒绝关闭时的 request。

通过条件：在正文明确区分设置状态更新与预览展示请求，并说明预览关闭时 L、S 的受理/完成依据，P 打开时如何读取当前语言与缩放、分配代次并发起展示请求；或者调整起点/操作定义，使串行例子与伪代码一致。至少给出一条从关闭起点执行 L→S→P 的完整判据链，并明确其 token 与后面乱序用例的关系。无需扩大为持久化教程或编写真实 Unity 加载器。实质修订后复核全文，避免只补一句却保留矛盾等待条件。

复核：新版第一、二节区分设置回执与内容请求，第三节将入口明确为仅在预览打开时调用的 BeginPreviewContent，并关联 originating_operation。按正文可完成：关闭预览时 L(ja) 更新目标并回读；S 更新缩放目标并回读；P 新建代次、读取这两个目标并产生内容 token；等该 token 的实际提交、对应 E 的布局采样与产品判据。异步交错则从已打开且内容就绪的预览起步，L1、L2 各自生成内容请求。此链不再要求不存在的关闭界面完成布局，T1 达到通过条件。

新增部分复核：S 修复内容被限定为开篇错误实现的额外假设，不与基本缩放方案混用；几何判据例区分节点矩形与实际字形可见范围，并要求统一坐标系；失败用例改等对应错误与终态而非成功内容。全文主线仍是序列与异步完成测试，没有扩张为完整排版或资源管理教程。正文、模型与来源之间未发现新的阻断缺口。

## 核查后的专业判断

- 价值：独立成文成立。它交付的是序列、请求归属与检查位置的联动，不是配置组合文章的重复。
- 机制：串行先后覆盖不等于相邻覆盖，两次请求三种合法次序的推导成立；参数与请求实例必须保留。请求来源捕获、失败路径归属、关闭代次隔离、布局输入版本以及持续观察旧工作互相衔接。
- 实现：对串行队列和无 setter 重入的前提写得清楚，避免把 token 比较误称通用并发保证。布局观察要求真实根到达、输入不变和几何采样，不能被观察器自己的回调替代。原有 T1 实施缺口已通过分阶段回执与打开路径解决。
- 证据：主动取样核对 NIST 原预印本 Definition/Example 2，确实允许不相邻子序列；Unity RefreshString 官方 1.5.14 页面支持活动加载时未发起刷新；Auto Layout 1.0 官方文档支持宽度先于高度、延迟重建。固定 uGUI 提交的 CanvasUpdateRegistry 正常遍历、异常捕获、清理/注销/禁用调用和后续图形阶段，与正文结论吻合。LayoutRebuilder 的强制入口直接执行 Layout，与“强制修复可能掩盖缺陷”的推论一致。没有把三套版本当成已实跑的统一环境。
- 完整性：核心知识没有藏进管理材料；模型仅作有限反例，不替代项目适配。几何正确性具体指标仍应来自产品规则，正文现在主要完成的是采样归属和时机方法，不应宣传为完整排版质量指南。

## 自主选择的反例与复现

1. 同值 ja→fr→ja 的第一项迟到：语言值相同不能替代请求身份，正文与模型均能区分。
2. 新请求 pending 时收到旧内容的有效布局回执：模型 operation_ready 同时检查 current、committed_token、status 与 layout_done，不会误判新请求就绪。
3. 正确新内容后，旧内容短暂提交又被 S 修复：最终快照仍可通过，逐次提交记录揭示错误。模型中 S 按当前目标重建是明确设定，非引擎事实。
4. 仅观察 LayoutComplete：固定源码清理与注销路径构成直接反例，正文已处理；PostLayout 几何与实际呈现也正确分开。
5. 从正文规定的关闭起点执行 L→S→P：首轮无法确定 L 的可满足完成条件，形成 T1；修订后可按设置回读、P 的新内容请求及匹配布局逐步完成。

执行：`python3 candidate/管理档案/研究/TASK-2026-0308/model/settings_model.py`，退出码 0，15 项。重新生成的 JSON 去掉 environment 后与保存输出完全一致。没有运行 Unity、实测布局或画面。

模型的 complete 对过期请求只记 ignored_completion，不将旧记录 settled 设为 true。因此它证明的是提交拒绝，不是完整旧工作清算器；正文的“观察至旧工作终态”仍需项目适配，不能把模型15项通过当成闭合观察段的运行证明。本次不据此要求扩建模型，但发表说明应保留现有边界。

## 核读来源

- https://www.nist.gov/customcf/get_pdf.cfm?pub_id=906770 ，Definition 与 Example 2。
- https://docs.unity3d.com/Packages/com.unity.localization@1.5/api/UnityEngine.Localization.LocalizedString.RefreshString.html ，Returns/Remarks。
- https://docs.unity3d.com/Packages/com.unity.ugui@1.0/manual/UIAutoLayout.html ，Layout Calculations/Triggering Layout Rebuild。
- https://raw.githubusercontent.com/Unity-Technologies/uGUI/7ca0363fd41d8de5f3cbc6121fe9a5acf95c88c6/com.unity.ugui/Runtime/UGUI/UI/Core/CanvasUpdateRegistry.cs ，PerformUpdate/CleanInvalidItems/注销和禁用实现。
- https://raw.githubusercontent.com/Unity-Technologies/uGUI/7ca0363fd41d8de5f3cbc6121fe9a5acf95c88c6/com.unity.ugui/Runtime/UGUI/UI/Core/Layout/LayoutRebuilder.cs ，ForceRebuildLayoutImmediate/Rebuild/遍历顺序。

## 最终通过绑定版本

首轮正文摘要：`31eba2b747627d92f5f7cea08902b824dcad2b7cbbaf07054c0330a122ac1c69`，当时结论需修订；以下为全文复核后的通过版本。模型三文件摘要均未变，保留首轮实际复跑结果。

正文路径：`candidate/GameLibrary/项目管理与测试/质量保证/测试设计/游戏设置页的操作序列与异步完成测试.md`

SHA-256：
- 正文：`431544e66abdc85ba2fee83b556de100e569f7e37dd783fa11d23043f155f199`
- sources.md：`8d8e01c018191d65df3d0179921bc5616f38460546848d3602edfef6bd1a108a`
- model/settings_model.py：`1bd33020d3e30a2bd9dbd8cc9f7500e15d550c3e0086e7de0cc344fa80a3f656`
- model/results.json：`db9f8951ee66af67774dc310fe2145fc57fedd60b8f48b2e9d791d1438be4ebb`
- model/README.md：`397e75729c2a29e9791d0ac9ce3441691995b137b490dd71e0057ae93f39a74c`

本报告不是导航审查，也不替代读者审读。正文或实验发生实质修改后本轮结论不能自动沿用。

## 打包时来源记录小范围复核

2026-11-08 实际重读更新后的 sources.md 全文。新增完整文档 URL 索引与模型覆盖边界，和已审正文、实际模型一致：模型 request 仅是打开预览上的内容请求，闭预览设置保存及 P 读取目标属于正文设计契约，未声称已在模型实现。此次未改变技术结论；维持通过，仅更新 sources.md 绑定摘要。正文与模型版本沿用上述已核版本。
