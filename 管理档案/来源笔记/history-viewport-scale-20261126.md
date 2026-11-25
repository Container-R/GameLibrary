# TAA 历史矩形与过滤来源记录

- Unity Core RP Library 16.0.6，[Using the RTHandle system](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@16.0/manual/rthandle-system-using.html)。查 Using RTHandles 与 Camera specific RTHandles，尤其是 `SwapAndSetReferenceSize` 后对 buffered RTHandle 之前一帧 `.zw` 的说明。官方文档支持常规现帧 `.xy`、相机缓冲历史 `.zw` 和前帧视口与分配相关属性；不是对任意 Unity 管线 TAA 的行为归因。通用的任意矩形起点是本文的工程推导。
- Khronos，[OpenGL 4.6 Core Profile Specification](https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf)，2022-05-05，§8.14.2 Coordinate Wrapping and Texel Selection、§8.15 Texture Magnification。线性取样按纹素中心求相邻索引和权重；CLAMP_TO_EDGE 作用于被采样纹理图像的边界。将坐标先限制在应用定义的子矩形纹素中心范围是本文的接入方法，不是 GL 自动识别历史有效区。
- [离屏对照与实际输出](../实验/history-viewport-scale/README.md)：Mesa EGL + llvmpipe，单级 RGBA8→RGBA32F；升、降、偏移、固定 X 坐标及越界拒绝。同一分配尺寸，scissor 模拟有效区写入；并未实现运动/抖动重投影和时域混合。
- 以上一手资料于 2026-11-26 北京时间核对。原始资料仅链接，不复制其大段内容。
