# FMOD 2.04 多监听者的距离、声像和掩码

核读时间：2026-11-19 北京时间。当前《Steam Audio遮挡与反射声的路由诊断》针对外部插件的直达/反射链，本篇是普通 Studio Spatializer 的多监听者共同输出，不替代它。

1. [Studio API 3D Events 2.04](https://www.fmod.com/docs/2.04/api/studio-api-3d-events.html)：14.2 说明所有属性先于 update，以免同帧混入旧位置；14.6.1 的默认示例距离增益以最近者为依据，两个方向仍一起贡献；14.6.2 的显式权重示例增益也变化；14.7 掩码排除与无活动监听者错误；14.9 自动参数默认最近，有权重时按距离累积至 100%。不复刻内置实现，不推广到对象声或其他空间处理。
2. [Studio::EventInstance 2.04](https://www.fmod.com/docs/2.04/api/studio-api-eventinstance.html#setlistenermask)：按监听者索引构造位掩码，应用于三维声像和相对监听者的自动参数；不是音频输出选择。
3. 原创几何对照见 [试件](../实验/FMOD分屏的监听者几何/README.md)。距离输入简单，未运行 FMOD 或音频引擎；未声称听音、声压或矩阵结果。
