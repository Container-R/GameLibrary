# Blender 4.3.2 原生烘焙：把物体分开是否必然产生接缝

```sh
blender -b --factory-startup -noaudio --python-exit-code 1 --python probe.py | sed -n 's/^RESULT //p' | python3 -m json.tool | diff -u observed.json -
```

在 Blender 4.3.2、Cycles CPU、2 线程、16 样本和固定 seed=4 下连跑两次，RESULT 逐字相同。两个共面四边形分别在世界 X=[−1,0]、[0,1]，Y=[−0.5,0.5]，Z=0；不改变几何位置、法线或纯白 Diffuse BSDF。在黑色世界中用斜上方零半径点灯提供非平坦的直接照明，没有放置遮挡物。Bake 选 DIFFUSE / DIRECT，未把 INDIRECT 或 COLOR 混入；关闭去噪和自适应采样。读的是 float non-color atlas 的红通道（灰度照明）。

三档：单网格连续 UV、两个物体且 UV 分开、单网格且 UV 分开。后两档使用完全相同的 UV 包装，将同一张图集上的两个不焊接四边形放进一个或两个物体，保持顶点连接方式相同，区分对象组织。连续 UV 档焊接共边，且采用连续图表，是连通与排布共同变化的参考组。各档 128×128 图集，每模块 UV 核心均 32×32 像素；各块从整像素边界开始，确保每世界单位的 texel 数和中心相位匹配。EXTEND margin=8；读回只比较映射到模块内部的 texel，不测 padding/mip。每块 1024 个核心 texel 均超过 0.05 且存在非零梯度，远离岛的底边仍全零。

分开物体和单一物体在相同分岛布局下的全部 2048 个核心样本相等。换用连续 UV 布局后，匹配核心平均绝对差约 0.0000873，最大差约 0.001091；32 行的边界相邻色差相对于连续对照的最坏增量绝对值约 0.000427，而连续对照的平均自然邻点差约 0.00663。不能据此断言严格无数值差，也不能推断差值来自哪一种采样细节。

只证明在本简单直接光和设置下，没有观察到由拆物体本身制造的不连续。未测真实遮挡、反弹间接光、探针、UV 扩边残留、运行时滤波、mips、压缩或引擎烘焙器，也不能把这些数值当视觉阈值或 Unity/Godot 测量。

## 独立间接光对照

```sh
PROBE_SEED=4 blender -b --factory-startup -noaudio --python-exit-code 1 --python probe_indirect.py | sed -n 's/^RESULT //p' | python3 -m json.tool | diff -u indirect-seed4.json -
PROBE_SEED=91 blender -b --factory-startup -noaudio --python-exit-code 1 --python probe_indirect.py | sed -n 's/^RESULT //p' | python3 -m json.tool | diff -u indirect-seed91.json -
```

同样的三种接收物体/打包。上方 Z=1.6 加一块 4×4、朝下的漫反射面，灰度反照率 0.8，点灯移到下方 Z=0.8，灯光可照到反弹面。用 DIFFUSE / INDIRECT 读间接分量，黑世界、512 样本、2 次 diffuse bounce 上限、4 次总 bounce 上限，不去噪。seed=4 重跑逐字一致，另跑 seed=91。两种 seed、三种布局的每块核心均 1024 个样本超过 0.001。同样 UV 打包的拆物体和合并物体仍全部相等；不同打包的匹配平均绝对差约 0.029，连续与分岛的平均邻边差比较甚至随 seed 反向。这不是普遍的间接光无缝结论，也不能把一个 seed 的最大像素差当成系统性接缝。试件不定义接缝的视觉可见阈值；灯、bounce card 和接收几何只构成一组实跑条件。
