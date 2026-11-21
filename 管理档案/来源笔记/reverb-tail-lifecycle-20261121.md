# 混响尾音与返回生命周期：来源与证据

- W3C，[Web Audio API：ConvolverNode](https://www.w3.org/TR/webaudio/#ConvolverNode)，线性卷积按脉冲响应处理，零输入时仍可有输出尾段。正文试件在 Python 中做同一线性机制的有限卷积，没有运行浏览器节点。
- FMOD，[Studio API 2.04 EventInstance／FMOD_STUDIO_STOP_MODE](https://www.fmod.com/docs/2.04/api/studio-api-eventinstance.html#fmod_studio_stop_mode)，ALLOWFADEOUT 明确允许事件 AHDSR 和 DSP 尾音，IMMEDIATE 立即停止事件实例。不由此推断共享返回、输出门控和总线卸载语义。
- [合成复现](../实验/混响尾音与返回生命周期/README.md)比较同一敲击、固定 IR、同输出比例下的七段声音；状态清零是本输入的等价对照。案例中的电平非推荐回收阈值；主观听感和引擎测量未做。
