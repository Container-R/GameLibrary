# 原始来源与主张边界

本轮访问日期：2026-11-08 UTC。下列定位已经实际读取，不是仅依赖搜索摘要。未下载、转载原章全文、图表或示例代码。

## S1：效用尺度、行动选择和惯性

David “Rez” Graham，An Introduction to Utility Theory，Game AI Pro，2013，第 9 章，印刷页 113–126。

原始公开章节：https://www.gameaipro.com/GameAIPro/GameAIPro_Chapter09_An_Introduction_to_Utility_Theory.pdf

实际核读：§9.2.1，印刷页 114（PDF 第 2 页）；§9.6，印刷页 120–122（PDF 第 8–10 页）；§9.7，印刷页 122（PDF 第 10 页）；为分辨章节示例的目的，也读了 §9.8 的开头。

来源支持：评分需要共同尺度；最大分与加权随机是不同选择方式；惯性可以通过当前行动加权或延迟下一次决策实现。§9.7 提到 The Sims Medieval 在互动队列为空后决策，行动完成或失败后再选。

不能据此归给作者：本包的加法常数、严格比较、候选键、类型奖励反例、每帧资格检查与时延值；这些是原创模型。章节 demo 采用加权随机，不能当作本包确定性迟滞的执行证据。

## S2：保留上下文不是禁止改主意

Kevin Dill，Structural Architecture: Tricks of the Trade，Game AI Pro，2013，第 5 章官方网页预览。

原始链接：https://www.gameaipro.com/papers/structural-architecture-tricks-of-the-trade.html

实际核读：§5.2 对 reasoner 和 option 的定义；§5.4 层次化判断；§5.5 Option Stacks 全节。网页标题元信息与正文题名不同，这里采用正文题名。

来源支持：一个角色可以有多个选择器；临时反应可以保留原行动上下文；失去能力后仍应改选。本文只借这些区别限定问题，不复刻选项栈，也不从中推出同步停止、最低持续时间或原生接口。

## S3：选择对象与条件状态必须对应

Jeff Orkin，Three States and a Plan: The A.I. of F.E.A.R.，GDC 2006。

作者署名论文公开镜像：https://www.gamedevs.org/uploads/three-states-plan-ai-of-fear.pdf

实际核读：印刷页 12（PDF 第 12 页），Difference #2: No Add/Delete Lists，以及相邻 Difference #3 的说明。此轮读取的是论文镜像；没有重新验证原作者站点字节或观看演讲。

来源支持：该历史实现一次规划关注一把选定武器和一个目标，对象由规划器外系统选择。它说明对象选择可以位于另一层，不证明该项目使用本包的效用惯性设计。

## 本轮证据类型

- S1–S3：来源中的历史说明和概念，不是当前引擎保证。
- `findings.md`：从明确规则作出的原创推导，限定确定性最大分选择器。
- `selector_model.py` / `results.json`：实际运行的 Python 原创同步回放，仅观察输入与选择；没有游戏、运动、感知、动画、寻路或玩家测试。
- `input-manifest.json`：冻结提交中旧文与相邻材料的公开 GitHub 定位及 blob 标识，支持去重与范围选择，不当作外部独立证据。
