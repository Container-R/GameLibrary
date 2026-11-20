# 顶点色遮罩与三角剖分：读回和算例

软件 OpenGL 与精确 CPU 模型是两个独立材料。图 [compare.png](compare.png) 来自软件 OpenGL 实际读回，不是人工重画。

```sh
set -o pipefail
export EGL_PLATFORM=surfaceless LIBGL_ALWAYS_SOFTWARE=true MESA_SHADER_CACHE_DISABLE=true
python3 -B probe.py | cmp - gl-observed.json
python3 -B probe.py --png | sed -n 's/^PNG://p' | base64 -d | cmp - compare.png
node sample.js | cmp - cpu-observed.json
```

软件实验使用 Python 3.12、Mesa llvmpipe 25.0.7；生成 PNG 另需 Pillow。相同平面几何、四个顶点及 1/0/1/0 颜色、两个三角形，只切换对角线。无窗口单采样线性 RGBA32F FBO，R 读回原始插值，G 读回片元着色器的阈值分类。100×100 对齐像素通过数 7,450 与 2,450，5,000 个位置分类不同。101×101 的正中心另测，分别为 1.0 与约 5.03×10⁻⁸（浮点残差）。[源码](probe.py)｜[实际 JSON](gl-observed.json)。

CPU 用正方形格中心的精确整数重心插值交叉验证闭式，并单测两条等覆盖但位置分离的带：每条 2,000 格、4,000 处不同。[源码](sample.js)｜[实际 JSON](cpu-observed.json)。两条移动的带只做数值试件，不是 GL、产品引擎或玩家观测。两种方法都没有运行简化器、生产材质或硬件性能测试。
