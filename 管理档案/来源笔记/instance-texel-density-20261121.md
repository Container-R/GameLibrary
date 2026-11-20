# 缩放实例的纹素密度：来源与证据

- Epic Games，[Texturing Material Functions](https://dev.epicgames.com/documentation/en-us/unreal-engine/texturing-material-functions-in-unreal-engine)，2026-11-21 核对页面为 Unreal Engine 5.9，WorldAlignedTexture 段的 TextureSize 单位与移动时纹理滑动。未运行该材质节点。
- 纹素方向密度为由世界单位长度到纹素坐标差的直接计算。三角形局部映射的主伸长率通过同一对边在相互对应的坐标中求得；不是某一资产工具的统计规则。
- [原创软件 OpenGL 试件](../实验/缩放实例的纹素密度/README.md)比的是同几何下三种 UV 与一个相位变换，实际读取 RGBA，不把屏幕跳变换算成帧率或比较产品引擎性能。
