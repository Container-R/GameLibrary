# 动态分辨率与帧时间

对应正文：[已经降分辨率，帧时间为什么还是超预算](../../../GameLibrary/图形渲染/渲染开发/帧性能诊断/已经降分辨率，帧时间为什么还是超预算.md)。

**实际覆盖量。** 在 Mesa 25.0.7 llvmpipe（LLVM 19.1.7，OpenGL 4.5 Compatibility）上通过 surfaceless EGL 创建离屏上下文，向颜色附件画一个满视口图形，无深度或模板测试，单采样。脚本读取通过样本数。分别运行两个尺寸步骤，固定输出尺寸不变；第二次复跑逐字一致。命令：`MESA_SHADER_CACHE_DISABLE=1 LIBGL_ALWAYS_SOFTWARE=1 python3 pass-coverage.py`。原始标准输出见 [pass-output.jsonl](pass-output.jsonl)。该对照不报告现实管线成本；实际项目也可能保持满尺寸分配，仅改变有效范围。

**合成帧号归属。** `node delayed-timing.mjs`，原先运行环境为 Node.js 24.22.3，[实际输出](delayed-output.json)。产生帧 4 执行 70%，到达帧 4 却读到帧 0、100% 的 22 ms；帧 4 真实低档的模型结果 14.35 ms 在帧 8 到达。脚本还验证两段跨队列区间直接加为 14，覆盖并集为 10；没有模拟信号量、显示或真实设备延迟。

三组吞吐表用像素比 1 与 .49。CPU 分别为 8、18、8 ms，GPU 固定项 7、7、16.9 ms，满比例像素项 15、15、5.1 ms。只按无同步/限速的理想稳定流水线理解，不从两档拟合生产 GPU 时间。
