# 半分辨率软粒子：来源与证据

- NVIDIA，*GPU Gems 3*，[第 23 章 High-Speed, Off-Screen Particles](https://developer.nvidia.com/gpugems/gpugems3/part-iv-image-effects/chapter-23-high-speed-screen-particles)，§23.3.1–23.3.2 与图 23-2–23-4：点采样或选近表面会使前景轮廓膨胀、出现背景空缝，取远处代表值会缩小遮挡轮廓并侵入前景。§23.4 给出 shader 深度比较及软交界淡出，不能把历史示例约定外推到任意设备深度。
- Unity，[Unity 6.0 URP 粒子无光照材质说明](https://docs.unity3d.com/cn/6000.0/Manual/urp/particles-unlit-shader.html)，Soft Particles、Surface Fade Near/Far 条目：靠近写入深度的表面淡出，要求开启 Depth Texture，使用 CameraDepthTexture；并非本试件的离屏实现。
- [本地双通道浮点目标与不透明度读回](../实验/低分辨率软粒子的深度边缘/README.md)直接验证邻点缺失时，深度选择不能恢复丢掉的粒子样本。只是合成几何标量，不测成本或真实粒子。
