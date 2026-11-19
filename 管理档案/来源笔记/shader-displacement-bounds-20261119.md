# 着色器位移与可见性剔除：来源和证据

- Godot 4.6 [ArrayMesh](https://docs.godotengine.org/en/4.6/classes/class_arraymesh.html) 指出 custom_aabb 对 shader 顶点偏移的用途；[GeometryInstance3D](https://docs.godotengine.org/en/4.6/classes/class_geometryinstance3d.html) 支持每实例 custom_aabb 和额外 margin，明确区分 ignore_occlusion_culling 与 frustum。未运行 Godot 渲染。
- Unity 6000.0 [Renderer.localBounds](https://docs.unity3d.com/kr/6000.0/ScriptReference/Renderer-localBounds.html) 说明局部空间、自定义顶点变形和运行时指定，并不可假设保存自定义值到 scene/prefab。未运行 Unity。
- Epic UE5.8 [Material Inputs](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-material-inputs-in-unreal-engine?application_version=5.8) WPO 与原始包围盒的失配、阴影以及放大代价；[UE5.9 Material Properties](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-material-properties) WPO 限制、0 含义，Nanite 单独簇边界。未运行 Unreal 或验证 GPU 集群剔除。
- [实际图像与精确模型](../实验/顶点位移剔除/README.md)：二维精确边界是数学消融；软件 OpenGL 4.5 由 Python 模拟提交门，实际 shader 与 framebuffer，配合可见像素计数。非性能、阴影或正式引擎渲染验收。PPM 原始读回字节和 PNG 像素已对照。
