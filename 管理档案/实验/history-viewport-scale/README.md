# TAA 历史有效矩形采样复现

[返回正文](../../../GameLibrary/图形渲染/画面呈现/时域抗锯齿/动态分辨率切换时，TAA%20怎样找准上一帧的有效像素.md)

Linux，Python 3 标准库、桌面 OpenGL 和 Mesa EGL surfaceless。实验使用 Mesa 25.0.7 软件 llvmpipe、OpenGL 4.5 core；只执行纹理采样，不运行完整的 TAA，也不测试时间稳定性或真实性能。

```sh
LIBGL_ALWAYS_SOFTWARE=1 MESA_SHADER_CACHE_DISABLE=true python3 gl_history.py
```

- [gl_history.py](gl_history.py)：使用 scissor 模拟写入历史有效矩形。先标记无效区，再填有效区及其内的蓝标记；在每种对照中保留同一张纹理分配和双线性配置。每行输出为 RGBA；`rejected outside` 的零 alpha 用来识别拒绝，黑色不是边缘历史的读数。
- [gl_observed.txt](gl_observed.txt)：完整实际读回。RGBA8 的中间值按实际实现保留，约 0.251 不是对所有实现的精度要求。
- [来源记录](../../来源笔记/history-viewport-scale-20261126.md)：核对 Unity 的接口范围、OpenGL 过滤规则及实验边界。

三组上一帧矩形、当前宽度：`(0,64)→128`、`(0,128)→64`、`(12,64)→100`。横向预置视口内坐标，纵向固定在纹理中间；非零原点只验证 X 轴。程序比较准确矩形、误用当前宽度、边缘内侧未限制、边缘内侧限制及视口外拒绝。
