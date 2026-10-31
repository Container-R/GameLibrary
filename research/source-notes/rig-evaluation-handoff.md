# Rig 求值顺序与跨岗位交接：来源边界

访问日期：2026-10-31。本文支持既有动画方案的交接补充，不是运行报告或新增岗位标准。

## S1：日本原始项目材料

Square Enix，今村紀之（Noriyuki Imamura）、川地克明（Katsuaki Kawachi），《FINAL FANTASY XV –EPISODE DUSCAE– のアニメーション ～接地感向上のためのとりくみ～》，CEDEC2015，2015-08-26 17:50–18:50。

原始PDF：https://www.jp.square-enix.com/tech/library/pdf/CEDEC2015_Luminous_FFXV_Animation.pdf

74页，以下为**PDF物理页码，从1开始**：
- 第1页：标题、作者、会议时间。
- 第23页：AnimGraph 的使用者为动画师。
- 第27–29页：不同姿态修正/物理/辅助骨计算次序问题。
- 第32页：模型骨结构对应的 Tuning Set；TA 制作预设，动画师选择。
- 第40–43页：动画工作职责扩大，技术动画方向、数据驱动的代价与职责重定义。
- 第45页：FK、后处理、Simulation 的阶段概览。

实际读取的是可访问PDF文字层；针对部分页的截图请求返回cache miss，没有据未能检查的图形颜色/区域推断职业分界。没有观看会议视频。不转载整套幻灯片、图或参数表。材料是2015年该项目经验，不保证后来版本或其他团队沿用。

## S2：英文版本化引擎文档

Unity Technologies，Animation Rigging **1.2.1**，Rigging Workflow：
https://docs.unity3d.com/Packages/com.unity.animation.rigging@1.2/manual/RiggingWorkflow.html

已读取HTML正文。页面metadata/title为1.2.1；generator显示2025-06-27，仅是文档生成日期，不据此推断发行时间。

定位Core Components → Rig Builder Component / Rig Component：Rig Builder将Playable Graph接到Animator状态机；Rig收集约束生成有序jobs，作用于正常动画评估后的姿态。`GetComponentsInChildren`的深度优先层级遍历决定约束job顺序，因此组织层级会参与执行语义。

这不是全部脚本、物理与动画系统的统一生命周期规范；更没有证明所有约束交换顺序都会产生不同结果。未安装或运行Unity1.2.1，不把其他引擎或纯数学演示当成它的执行证据。

## S3：日本雇主职责材料

Capcom，テクニカルアニメーター/リガー：
https://hrmos.co/pages/capcom/jobs/01_03_040

读取仕事内容与相关能力说明；涉及动画控制Rig、spline/fullbody IK、脚本辅助、面部控制设置。正文没有已确认的首次发布日期。仅作为该雇主角色范围例子，不断言持续招聘、不记录薪资/个人资料，不推广为全行业同义岗位。

## 原创推导与未执行边界

阶段/读写依赖表、六行接收工作表、躯干瞄准和握点手IK的A/B情境均是本库原创建议；不是上述厂商提供的统一规章，也不是FFXV架构在Unity中的复现。作用是把内容层级变更的潜在语义影响交给明确接收者，而非增加泛化职业文章。

与原根运动方案互补：原方案处理对象运动提取/消费及接触诊断，这里处理局部姿态修正之间的依赖。已重新核对原文“4项几何模型测试”段与 research/experiments/root-motion/README.md：原根运动证据是Python二维刚体模型，不是Godot运行；没有骨骼、求解器或引擎回调。其他Godot动画事件实验也不建立根运动或Unity Rig约束顺序结论。若后续无法取得对应运行环境，保持source-backed方法，不声称测试通过。

一次Autodesk2025资料链接读取失败；没有采用其支持结论，没有规避访问限制或重复穷举。
