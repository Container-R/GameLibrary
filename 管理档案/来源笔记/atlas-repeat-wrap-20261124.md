# 重复图集的采样梯度与周期护边：来源记录

- Khronos，[GLSL 4.60 规范](https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.pdf)，§3.8.2、§8.3、§8.9 和 §8.14.1。核对一致控制流、fract、textureGrad 和导数限制。组件中的 1 对 31 纹素是本文计算；实际级别来自测试。
- Li-Yi Wei，[GPU Gems 2 第 12 章](https://developer.nvidia.com/gpugems/gpugems2/part-ii-shading-lighting-and-shadows/chapter-12-tile-based-texture-mapping)，§12.4 示例 12-2 分开地址与梯度，§12.3–12.5 的 Wang tile 组合并非本试件的单子图周期条件。
- Khronos，[OpenGL 4.6 Core](https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf)，§8.14.1–8.14.3 的纹素尺度、整纹理寻址、级内及级间过滤。不由规范推断所有设备的精确级别。
- Mikola Lysenko，[Texture atlases, wrapping and mip mapping](https://0fps.net/2013/07/09/texture-atlases-wrapping-and-mip-mapping/)，2013。作者报告中以周期条件生成每块的缩小内容，分开处理误选级别。本文不借用其历史平台性能或四重采样方案的保证。
- [OpenGL 帧缓冲试件](../实验/重复图集的梯度与周期护边/README.md)提供实际日志。内容重构自既有支持笔记，删除重复解释、新增可轮换的单级控制和原生帧缓冲；保留旧支持笔记以便回溯。
