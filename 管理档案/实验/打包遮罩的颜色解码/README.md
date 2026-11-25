# 打包遮罩的颜色解码：复现

[正文](../../../GameLibrary/技术美术/环境管线/纹理与材质/贴图通道接对了，粗糙度为什么还是变了.md) · [来源核对](../../来源笔记/packed-mask-srgb-20261125.md)

在安装了桌面 OpenGL、EGL 和 Mesa 软件驱动的 Linux 下，从本目录运行：

```sh
LIBGL_ALWAYS_SOFTWARE=1 MESA_SHADER_CACHE_DISABLE=true python3 gl_mask.py
python3 probe.py
```

[实测原始读数](gl-observed.txt)：Mesa 25.0.7 llvmpipe，GL 4.5 Core。两次把完全相同的 8×1 RGBA 8 位数据直接上传至不同内部格式，七个灰度样本另加 (32,128,224,64) 排列探针。片元着色器用 `texelFetch` 取第 0 级的单个整数坐标；线性 RGBA32F 目标禁用帧缓冲 sRGB 和混合，通过 `glReadPixels` 读回浮点值。位于 128 的 G 输入比较 0.4 阈值，在脚本中用实测值判断，不是假定运行了植被材质。0/255 两端分别相等，Alpha 对全部样本均未转换。

[公式参考](observed.txt) 独立按 sRGB 传递函数以及 8 位归一化计算，用于识别曲线和对照实现近似。本试件没有 PNG/ICC、导入器、压缩、过滤或显示变换，不能拿它推断某个现有资产具体在哪一关改值，也不能当作全平台误差界限。
