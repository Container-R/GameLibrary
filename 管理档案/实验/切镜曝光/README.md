# 切镜曝光：适应、测光和缓冲比例对照

从此目录运行（Python 3.12.14）：

```bash
set -o pipefail
python3 -B probe.py | cmp - observed.json
python3 -B native/probe.py | cmp - native/observed.json
```

第一组用固定单灰块和人为设定的两帧测光延迟、0.1 秒离散步、每秒最多 4 档变化，独立对照是否继承上一镜头增益、是否允许旧镜头测光。数值是进入色调映射前的线性量。运行 `python3 -B draw_trace.py` 可从归档 JSON 重新生成 trace.png，需要 Pillow 和 DejaVu Sans。轨迹横轴是切后的帧序号，纵轴是亮度与线性目标 0.18 的比值以 2 为底对数。

第二组要求 EGL 和 Mesa。以同一静态两像素线性亮度 2.88 / 28.8 分别乘预曝光比例 8 / 1/16 后写入 RGBA16F，再在另一着色器从该缓冲读回，写入 RGBA32F。正确使用 E/P 或故意只乘 E，两种情况独立渲染并读回实际值；不做 sRGB 和色调映射。参考实现实报 Mesa 25.0.7 OpenGL 4.5 Core / llvmpipe，得到的数值包含半浮点量化。模型没有显示设备、真实自动测光、曝光时间、相机或真实引擎运行，不用于比较性能、平台、项目画质或光敏风险。

归档 SHA256：模型 JSON `0f084afafb1f645e85fc139080e791c1e51d02687287d6650e99c1910cfc209f`；轨迹 PNG `e3748eed4e24b23dedd6f82eb58757f2b35edd8c33429ec4da503781d56c2c65`；原生读回 JSON `7a6710acffa03b39501b54a19bfd2f1e99ee9594f8d656785374ab13a4db7a35`。
