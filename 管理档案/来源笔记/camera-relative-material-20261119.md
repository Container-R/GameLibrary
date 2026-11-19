# 大世界材质相位：来源和证据

- Oracle [IEEE Formats，Single Format](https://docs.oracle.com/cd/E60778_01/html/E60763/z4000ac019878.html)：23 位存储小数和正常数隐含首位，解释 10,000,000 附近的步长；不采用十进制位数粗略估计。
- Epic Games [UE 5.9 Large World Coordinates Rendering](https://dev.epicgames.com/documentation/en-us/unreal-engine/large-world-coordinates-rendering-in-unreal-engine-5)：材质 World Position Origin Type、translated world 与 view space 区分、DoubleFloat 和 tile-offset 不混用。没有运行 UE 或比较其实现性能。
- Godot [4.6 Large world coordinates](https://docs.godotengine.org/en/4.6/tutorials/physics/large_world_coordinates.html)：并非所有三维着色器路径都享受相同精度；文档列三平面、某些世界顶点等限制，此实验证据不涉及 Godot。
- Khronos [GLSL 4.60.8](https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.html)：mod 的数学定义采用 floor，但规格亦提到近似实现可能在断点附近产生与理论不同的结果。[WebGL EXT_shader_texture_lod](https://registry.khronos.org/webgl/extensions/EXT_shader_texture_lod/) 的示例将取模的采样坐标与连续坐标梯度分开；本文没有测纹理过滤或目标 GPU 的导数。
- [附录](../实验/大世界材质相位/README.md)：CPU binary32 序列化、精确有理数插值与 Mesa EGL 原生读回。后者是 4.5 core 软件驱动的 GLSL 330 顶点计算和 transform feedback；两次复跑逐字一致。截取的数据不是光栅图像，不支持滤波、阴影、导数或引擎渲染结论。
