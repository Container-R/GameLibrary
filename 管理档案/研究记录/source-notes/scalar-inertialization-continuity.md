# 标量惯性化：来源与数学选择

对应[ SOL-ANIM-002 ](https://github.com/Container-R/GameLibrary/blob/1a7bf18b24ba56395892c4c0cdb3b2acecc16985/solutions/animation/scalar-inertialization-continuity.md)。读取2026-11-01。

核心来源为Daniel Holden的[Spring-It-On](https://theorangeduck.com/page/spring-roll-call)，页面显示04/03/2021，正文可变；作者身份由[本人介绍](https://theorangeduck.com/page/about)核对，不据当前雇主倒推文章历史归属。定位Half-life and Frequency、Critical Spring Damper、Inertialization三节。正文只短述机制；公式用本库符号重新推导，夹具为原创标量实现。没有复制演示或源仓库代码。

历史区别参考[David Bollo的GDC2018会话页](https://www.gdcvault.com/play/1025331/Inertialization-High-Performance-Animation-Transitions)。研究/复核读取原始PDF指定文字时发现部分公式抽取损坏，因此没有照抄有限时间多项式系数，也没有实现或比较该算法。本条只验收弹簧残差形式，不混用两者的完成时间与性能结论；未播放视频或分析动画图像。

作者链接的代码仓库LICENSE标为MIT、copyright2021 Daniel Holden；本库没有把这个许可扩大到网页文章或GDC幻灯片，也没有借此转载素材。后续若实际采用仓库代码，应另锁定版本并保留许可。

本库明确选择标准math.exp而不是网页快速指数近似，主要参数为λ而非半衰期标签；连续目标与导数由解析式给定。输入、容差、事件顺序在数值执行前冻结，见[实验](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/research/experiments/scalar-inertialization/README.md)。独立代数审查和分别编写的RK4只验证有限标量问题，不认证原作游戏实现、脚部接触、四元数、导数估计、渲染表现或性能。未发布PDF、图像、批量转写或整篇译文。
