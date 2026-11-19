# 图集 Mip 串色：来源和证据

- Khronos [OpenGL 4.6 Core Profile Specification](https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf)，§§8.14.2–8.14.4：线性取样位置和加权，离散/层间 Mip 过滤，GenerateMipmap 的重复滤波缩减不会规定某一核，二维数组每层独立生成；§8.10 的 MAX_LEVEL 与 MAX_LOD 是独立参数，§8.17 另定纹理完整性。正文的数值来自指定实现与另外的精确数学试件，不当成规范要求。
- NVIDIA [Batching Via Texture Atlases](https://download.nvidia.com/developer/NVTextureSuite/Atlas_Tools/Texture_Atlas_Whitepaper.pdf)，WP-01387-001，2004，*Using Mip-Maps with Atlases*，印刷页 3–7，图 2–4：独立滤波后按级打包，2 的幂对齐的无串色特例，低分辨率导致不同尺寸的素材到达各自最后有效级别。不要沿用关于这些级通常难以访问的早期管线判断作为当下工程保证。
- Unity [Sprite Atlas 属性参考](https://docs.unity3d.com/ja/2023.2/Manual/class-SpriteAtlas.html)，2023.2，Padding 指图块间像素数，过滤和生成 Mip 分开。未验证 Unity 导入器的具体核、打包填充或 TextureArray 驱动。 
- [复现](../实验/图集Mip串色/README.md)区分精确箱式模型和软件 GL 4.5 渲染，基础图与图集中的物体均为原创常色试件。各测试纵向颜色恒定且 Alpha=1，不能拿来外推 Alpha 覆盖率、色彩管理、压缩、各向异性或硬件性能。原始 PPM 直接取 framebuffer；PNG 保留 RGB，逐像素 5 倍最近邻放大。
