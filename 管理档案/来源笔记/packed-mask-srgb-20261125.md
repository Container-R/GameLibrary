# 打包遮罩：颜色解码来源核对

核查日期 2026-11-25。[复现实验](../实验/打包遮罩的颜色解码/README.md)。

- [OpenGL 4.6 Core，§8.24](https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf#page=310)：表 8.24 列出 sRGB 内部格式；RGB 转线性，Alpha 不变；式 8.17 为参考曲线。规范讨论过滤前后转换，本实验刻意不混合纹素，不以它验证多纹素过滤或 mip。
- [glTF 2.0，§3.9.2](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#metallic-roughness-material)：底色 RGB 带 sRGB 编码；metallicRoughnessTexture 的 G/B 是粗糙度与金属度，纹理使用线性编码。乘数在线性数值上应用，不将 glTF 通道命名泛化到其他打包器。
- [Unity 6000.0 TextureImporter.sRGBTexture](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityeditor/textureimporter/srgbtexture)：Linear 项目中按该标记控制采样转换；不作为所有项目、包格式和平台导入结果的证明。
- [Microsoft DXGI 色彩转换文档](https://learn.microsoft.com/en-us/windows/win32/direct3ddxgi/converting-data-color-space)：绑定带 sRGB 修饰格式的 SRV 在读入着色器时转换，RTV 的转换发生在输出。未验证具体资源创建标志或可互换的视图族。
