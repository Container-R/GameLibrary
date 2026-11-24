# 单面模型镜像绕序：离屏帧缓冲对照

[返回正文](../../../GameLibrary/图形渲染/渲染开发/光栅化/单面模型镜像后的绕序与实例剔除.md)

在有 Mesa libEGL、libGL、llvmpipe 和 Python 3 + Pillow 的 Linux 上，从本目录执行：

```sh
python3 native_probe.py | tee native-observed.txt
```

实测 OpenGL 4.5 Core Profile，Mesa 25.0.7-2+deb13u1，llvmpipe LLVM 19.1.7；96×64 的 surfaceless EGL pbuffer，24 位深度、无多重采样。程序用 OpenGL 原生绘制并读回颜色与中心深度；PNG 是对原始颜色读回的近邻放大拼接，带标签，不是模拟或重画。

卡片共享顶点序列与绘制状态；三张实例分别为常规、X 反射、X/Y 反射。前三个对照各为同一次 `glDrawArraysInstanced`；拆分对照按奇偶性提交两次。有背面剔除时，原 CCW 只留左/右，整体 CW 只留中间，按奇偶性发两次后三张均为正面。

两墙 XY 四角为 (±0.5, ±0.5)，A/B 的世界 Z 分别为 +0.5/−0.5，各向外绕序。顶点着色器计算 `clip=(x,y,-z,1)`，即沿正交视线从 +Z 观察且较小窗口深度更近。墙模式的深度比较是 GL_LESS；不剔除对照特意先发近墙 B，再发远墙 A，验证不是后绘覆盖制造的结果。A/B 用橙/蓝，绿色通道值区分片元 `gl_FrontFacing`；所有墙对照逐像素比较轮廓掩码。图中像素数以原 96×64 读回为准。

- [原生最小程序](native_probe.py)
- [完整读回日志](native-observed.txt)
- [帧缓冲对照图](native-comparison.png)

图中未使用光照、法线贴图或阴影，不作为引擎、导入器、着色质量、设备性能或玩家体验的验证。
