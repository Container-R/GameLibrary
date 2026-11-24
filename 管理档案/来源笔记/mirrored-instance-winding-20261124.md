# 单面模型镜像后的绕序与实例剔除：来源记录

| 主张 | 原始来源与位置 | 支持与边界 |
| --- | --- | --- |
| 图元分类依赖投影后窗口绕序与绘制的正面约定，顶点法线不参与 | Khronos Group，2022，[OpenGL 4.6 Core Profile](https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf#page=499)，§14.6.1，印刷页 478–479 | 窗口有符号面积受 clip origin 约定影响；FrontFace 定义前侧，CullFace 和 enable 是不同状态。正文使用左下原点。 |
| 非奇异节点全局变换的符号决定实例三角面绕序约定 | Khronos Group，[glTF 2.0 §3.7.4 Instantiation](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#instantiation)，查阅 2026-11-24 | 可逆仿射线性部分负行列式反转定向。叉积恒等式为本文推导：两边分别与任意一条 M 变换后的向量做内积，由有符号体积的缩放可得结果。它不是“每个三角形的投影符号都会翻”。 |
| glTF 双面着色不能替代正面定义 | Khronos Group，[glTF 2.0 §3.9.5 Double Sided](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#double-sided) | 双面禁用背面剔除，背面法线在着色前反转。实验用无光照的方向调试色，不验证任何 BRDF 或导入材质。 |
| 常规实例化用相同几何序列，有实例 ID，不自动切换光栅状态 | Khronos Group，[glDrawElementsInstanced reference](https://registry.khronos.org/OpenGL-Refpages/gl4/html/glDrawElementsInstanced.xhtml)及上列 §14.6.1 | 参考页说明逐实例的元素重放和索引；FrontFace 是绘制状态，实验实际用 glDrawArraysInstanced 和顶点着色器中的固定序列。 |
| 可用上游样例另验导入器 | Ed Mackey，[Negative Scale Test](https://github.com/KhronosGroup/glTF-Sample-Assets/tree/main/Models/NegativeScaleTest)，Khronos glTF Sample Assets | 查看了预期和常见问题说明；没有运行或转载样例。 |
| 相同轮廓掩码可能显示错误的面；关闭剔除时可见面仍可能分类为背面 | [离屏实验与原始读回](../实验/单面模型镜像绕序/README.md) | 正交、两平行墙、无 MSAA、开 GL_LESS；A/B 调试色通道编码 gl_FrontFacing。仅代表实测 Mesa 软件光栅配置。 |
