# 缩放实例的纹素密度：实际 OpenGL 读回

需要 Python 3、Mesa 的 EGL 与 OpenGL；生成拼图另需 Pillow。在该目录：

```sh
python3 -B probe.py | cmp - observed.json
python3 -B probe.py --png-base64 | base64 -d | cmp - contact.png
```

Mesa llvmpipe 25.0.7（OpenGL 4.5 Compatibility）。无窗口 64×32 RGBA8，最近邻重复同一 8×8 黑白纹理，四边形 4×2 m。三个策略仅改变提交给 OpenGL 的 UV 角点：原 UV 的 U 重复一次、实例锚定和世界锚定的 U 重复两次，V 均一次。保持固有四边形和相机相对构图不变，仅世界策略加入 0.25 m 对应的 U 相位，等价于固定世界网格上墙和相机一起移动。记录实际第一个像素、横纵测试行列颜色跳变和完整 RGBA SHA-256。拼图是读回放大，不重画格子。

独立复跑 JSON 一致。没有运行 Unreal 或 Unity，未模拟较高分辨率纹理、动态 Mip、LOD、压缩或性能。1024×1024 是正文算例，棋盘只有 8×8。
