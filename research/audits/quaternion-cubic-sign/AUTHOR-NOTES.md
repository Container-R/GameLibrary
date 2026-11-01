# 作者说明：四元数符号与立方动画

日期：2026-11-01。拟发布正文：`research/source-notes/quaternion-sign-and-cubic-animation.md`。本次仅提供新来源笔记，不修改既有岗位或文章。

## 来源身份与定点阅读

Khronos glTF 2.0 官方 `specification/2.0/Specification.adoc`，固定提交 `59ecbdba704206bb656965ab4e202881806066f1`，源文件 blob `e5088cdc9a4e344e836568f57e2db6726f5a6740`。原文链接：

- https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#L879-L895
- https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#L3979-L4077

读取范围为 TRS 和 Appendix C；4067–4075 的归一化与零值提醒不被提升为任意切线的完整非零判据。提交日期 2026-10-30 是所选快照的提交日期，不是 glTF 2.0 发布日期或该条款首次引入时间。正文只简述相关规范，未复制实现、图示或示例资产。

## 原创数学与边界

最终选用 120° 终点，而非候选门中的 180° 例子；只保留一个反例，避开把差异归因于最短方向平局。q₀·q₁=1/2，所有切线为零，Δt=1。两个值权重 a、b 非负且和为1，ab≤1/4；两条曲线平方范数分别至少3/4与1/4。中点四元数及矩阵第一列均在正文展开，便于独立手算复核。

没有计算 LINEAR 的任何数值输出。全局取负保持旋转的结论以所有值及相关切线统一取负、原曲线非零为前提；独立逐键取负的反例不等于所有局部取负都失败。没有有限采样充分性、自动修复或完整曲线分类结论。

交接表是原创建议，非 Khronos 工具流程要求。没有执行数学程序、生成资产、运行导出器、播放动画或进行视觉评价。现有平移重定时与标量惯性化只用于区分问题，不继承其测试或验证等级。

正文相对链接按拟发布路径编写：动画师岗位为 `../../roles/animation/game-animator.md`，同目录标量来源笔记为 `scalar-inertialization-continuity.md`。没有新增索引 ID。
