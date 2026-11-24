# 单帧姿势与动画轨迹：OpenGL 对照

[返回正文](../../../GameLibrary/图形渲染/渲染开发/帧调试/用%20RenderDoc%20定位角色变形：一帧能证明什么.md)

使用桌面 OpenGL 3.3 或更高、Mesa 的 surfaceless EGL，以及 Python 3 标准库。不包含 RenderDoc 捕获，也不需要游戏或资产。

```sh
MESA_SHADER_CACHE_DISABLE=true LIBGL_ALWAYS_SOFTWARE=1 python3 gl_probe.py
```

[脚本](gl_probe.py)固定 128×128 RGBA8 绘制环境和顶点输入 `(0,0),(2,0)`。对每组时刻只改关节旋转矩阵，变换反馈读出顶点着色器的 `posed`，`glReadPixels` 取同一次 draw 的输出；正交缩放由着色器内固定系数完成。逐点核对旋转结果，并断言缓冲中有白线，避免把两个空画面当作通过。白线和背景在红通道就可区分，差异计数因此按该通道计算；完整 RGBA 数据另作逐字节比较与 SHA-256 记录。

[原始输出](gl-observed.txt)：Mesa 25.0.7 的 llvmpipe（LLVM 19.1.7），中心帧 30°，顶点与全缓冲精确相同；两侧帧角度相差 9°，各有 82 像素不同。同一环境两次运行输出逐字节一致。不同驱动的线段覆盖和末位浮点可能不同，中心/两侧是否一致才是本对照检验的关系。
