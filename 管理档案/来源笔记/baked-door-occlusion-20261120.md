# 门洞的遮挡剔除：来源记录

2026-11-20 阅读 Unity 6.0（6000.0）官方文档：
- [Occlusion culling](https://docs.unity.com/en-us/engine/6000.0/manual/cameras/occlusion-culling/occlusion-culling)：区分视锥和遮挡；烘焙空间单元及相邻可见性；常规动态物体不能担当遮挡体。
- [Control occlusion in areas with Occlusion Portals](https://docs.unity.com/en-us/engine/6000.0/manual/cameras/occlusion-culling/class-occlusion-portal)：设置、烘焙、编辑器开关对照；可独立于门，释放遮挡开关后再启动开门动画。晚关和读档首帧对照是本文的保守推导，不是声称手册定义全部运行时顺序。
- [Cull moving GameObjects](https://docs.unity.com/en-us/engine/6000.0/manual/cameras/occlusion-culling/dynamic-gameobjects)：动态 Renderer 的 Dynamic Occlusion 指被静态物遮挡后的剔除资格；页面另有 GPU Resident Drawer 备注，本文不推广到其他实时剔除机制。
- [原创整数射线试件](../实验/门洞的遮挡剔除/README.md)：验证指定假设下的错误准入与保守准入差异。未运行 Unity 或渲染器。
