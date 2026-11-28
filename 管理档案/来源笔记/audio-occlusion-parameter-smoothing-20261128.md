# 来源笔记：运行时遮挡增益的样本变化

对应正文：[音源经过门框时，遮挡音量为什么会啪一声](../../GameLibrary/声音与音乐/游戏音效/空间音频/音源经过门框时，遮挡音量为什么会啪一声.md)。

| 主张 | 一手来源与位置 | 使用界限 |
| --- | --- | --- |
| 逐样本乘增益、指数时间常数、取消时保留当前自动化值 | W3C [Web Audio API 1.0 2021 Recommendation](https://www.w3.org/TR/2021/REC-webaudio-20210617/)，[GainNode](https://www.w3.org/TR/2021/REC-webaudio-20210617/#GainNode)、[setTargetAtTime](https://www.w3.org/TR/2021/REC-webaudio-20210617/#dom-audioparam-settargetattime)、[cancelAndHoldAtTime](https://www.w3.org/TR/2021/REC-webaudio-20210617/#dom-audioparam-cancelandholdattime) | 说明一种固定规范和数学关系；不把某浏览器或游戏中间件的实现当成实测 |
| 五组增益控制下的浮点样本差与实际增益 | FFmpeg [Filters：aevalsrc](https://ffmpeg.org/ffmpeg-filters.html#aevalsrc)，音频表达式、样本序号、采样率；[试件](../实验/遮挡增益的样本过渡/README.md)在 FFmpeg 7.1.5 执行 | 按原始样本号捕获；没有体现真实音色、听觉阈值、硬件缓冲与 API 同步 |
| 通过连续遮挡量的两阈值使示例切换从 6 次降到 2 次 | 同试件中的十个人工输入与比较 | 不是最佳阈值，不用于直接解决二值射线交替 |
