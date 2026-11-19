# Native float shader readback

运行 `python probe.py`。仅用 Python 标准库 ctypes 与系统已有 EGL/OpenGL 动态库；不安装包，不需要窗口系统。强制软件渲染、surfaceless EGL，禁用 Mesa shader 磁盘缓存。上下文退出时释放。`observed.json` 是两次实跑均得到的同一份结果。

实际设备是 Mesa 25.0.7 llvmpipe (LLVM 19.1.7)，OpenGL 4.5 core。请求至少 3.3 core，shader 使用 GLSL 330。将四组 float32 顶点输入交给真正的 GL vertex shader，捕获 transform feedback，再用 glGetBufferSubData 读回。不是仅在 Python 模拟 shader，也没有声称运行于硬件 GPU 或任何游戏引擎。

每行输入为 world、origin、host-relative、origin phase，后两项在主机 double 中先减/取模，再转换成 float32。period=0.75。输出四分量依次为 shader 中 world-origin、直接输入的 relative、mod(relative,period)、mod(relative+origin_phase,period)。所有值均断言为精确期望值，并检查 GL error=0。

两点相隔 0.25，但大世界 float32 上传后二者都成为 10000000，shader 相减都为 0。先用主机 double 相减再上传保留该间距。两次原点下，固定世界点的仅相对相位分别 0.125/0；加入主机计算的原点模周期相位后均为 0.375。第二个点的锚定相位均为 0.625。

边界：这里测的是驱动实际浮点着色器输入、运算和读回；没有渲染像素、真实网格、抗锯齿、纹理过滤、导数、法线或阴影。0.75 及这些偏移可二进制精确表示，不能据此宣称任意周期、任意距离或所有原点变化都精确。主机原始坐标必须尚未丢失低位；把已经量化的世界 float 转为 double 再减无法恢复。原点模周期计算在本例主机 double 范围可靠，不是任意大坐标解决方案。需要在各目标驱动与具体材质链再验证。
