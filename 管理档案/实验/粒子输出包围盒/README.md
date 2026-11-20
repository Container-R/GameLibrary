# 粒子输出包围盒复现

- [图形试件与实际像素读回](native/README.md)：在同一四边形上改脚本的绘制准入范围，记录提交次数和 OpenGL 实际输出。
- [区间判断脚本](interval_probe.py)和[区间记录](interval_observed.json)：额外保存旧盒、输出范围和补边量。在本目录运行 `python3 -B interval_probe.py | cmp - interval_observed.json`。

两者没有使用商用引擎或项目素材。图形试件没有模拟粒子生命周期，不能验证特定引擎的离屏暂停或测得帧率损益。
