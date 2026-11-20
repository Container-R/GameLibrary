# 顶点色遮罩与三角剖分：来源和证据

- Hugues Hoppe，[New Quadric Metric for Simplifying Meshes with Appearance Attributes](https://www.hhoppe.com/newqem.pdf#page=3)，§4、图 2。使用 3D 几何对应点，在三角面内插值后比较属性。文中平面手工翻对角线自己的对照不使用论文算法。
- Epic Games，[Mesh Paint Mode Tools and Settings](https://dev.epicgames.com/documentation/unreal-engine/mesh-paint-tool-reference-in-unreal-engine)，To LODs：把 LOD0 顶点色应用到各 LOD。资料不承诺迁移后的遮罩逐点保真，文章的对比检查属工程建议。
- meshoptimizer，[Attribute-aware simplification](https://github.com/zeux/meshoptimizer/blob/f0a684f11ead064e176775c9b796f82a55910e92/README.md#attribute-aware-simplification)，钉定提交。索引隐含的属性不连续与传入数值及权重是不同信息；权重有单位/量程和位置误差取舍。实际返回索引数与边界误差须另外验收，未执行该简化器。
- [实际软件 OpenGL 与 CPU 格点试件](../实验/顶点色遮罩与三角剖分/README.md) 是文章的独立证据。对应位置硬阈值分类数和图用程序读回；等覆盖条带只由 CPU 计算。未测商业引擎、生产资产、硬件 GPU 或帧率。
