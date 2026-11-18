# 裁剪贴图缩小：来源与验证

- Ignacio Castaño，[Computing Alpha Mipmaps](https://www.ludicon.com/castano/blog/articles/computing-alpha-mipmaps/)，[2010 年原首次发布](https://www.the-witness.net/news/2010/09/computing-alpha-mipmaps/)。记录树叶缩小后覆盖率下降，定义通过裁剪的比例、临时参考阈值及其与约定阈值的比例。公式是严格大于；正文自有试件约定大于等于。
- [Microsoft DirectXTex](https://github.com/microsoft/DirectXTex/wiki/ScaleMipMapsAlphaForCoverage) 说明基于明确参考阈值的 Mip 后处理；[Unity 6000.0](https://docs.unity3d.com/6000.0/Documentation/Manual/texture-type-default.html) 说明纹理导入的覆盖率选项与 Alpha Cutoff。未运行对应工具。
- [原始 Python 试件](../实验/裁剪透明贴图的Mip/README.md) 可复算通过率与并列误差，范围仅为离散 texel；不能推导 GPU 画质、压缩、层间采样或原项目素材结果。
