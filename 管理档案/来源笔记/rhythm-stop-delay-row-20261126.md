# 谱面停顿与同行音符的原始依据

- [StepMania 的 Timing Segments](https://github.com/stepmania/stepmania/wiki/Timing-Segments)：区分 Stop 同行音符在停顿前处理与 Delay 同行在停顿后处理。这里不引用它为其他谱面引擎定义通用顺序。
- StepMania 固定提交 `7cbaff8ce2dcbede32dd3d6f3f2d8fafeafd674e` 的 [FindEvent](https://github.com/stepmania/stepmania/blob/7cbaff8ce2dcbede32dd3d6f3f2d8fafeafd674e/src/TimingData.cpp#L774-L810)：从不同段取下一个事件，同行的候选比较使用严格小于，从而在本文的无 Warp 子集形成 BPM、Delay、查询标记、Stop 的顺序。[拍到时间](https://github.com/stepmania/stepmania/blob/7cbaff8ce2dcbede32dd3d6f3f2d8fafeafd674e/src/TimingData.cpp#L929-L993) 与 [时间到拍](https://github.com/stepmania/stepmania/blob/7cbaff8ce2dcbede32dd3d6f3f2d8fafeafd674e/src/TimingData.cpp#L812-L914) 的核心函数可用独立 C++ 夹具直接执行。夹具替代调用环境，不经过项目解析、查找缓存或游戏循环。
- [NoteTypes.h](https://github.com/stepmania/stepmania/blob/7cbaff8ce2dcbede32dd3d6f3f2d8fafeafd674e/src/NoteTypes.h) 定义每拍 48 行；夹具只查整数拍，无边界逼近与浮点行号舍入争议。默认段扫描、整数样本换算与有理数对照结果见 [复现材料](../实验/rhythm-stop-delay-row/README.md)。48 kHz 是对照坐标，不是引擎设备实测。
