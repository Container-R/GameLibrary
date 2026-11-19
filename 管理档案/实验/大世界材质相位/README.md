# 大世界材质相位：坐标换算、周期与着色器读回

[正文](../../../GameLibrary/图形渲染/着色器开发/世界坐标与精度/大世界材质改用相机相对坐标，怎样让花纹仍固定在世界上.md)

Python 3 标准库：

```sh
python3 check_relative_phase.py | cmp - observed.json
python3 check_wrap_interpolation.py | cmp - wrap-observed.json
```

第一项用实际 binary32 序列化和相邻位表示检查主机侧数值，第二项用有理数比较跨周期边界时的插值顺序。[原生对照](native/README.md)另调用系统现有 EGL/OpenGL 软件驱动，以真实顶点着色器的 transform feedback 读回。三者都不是在真实场景里验证过滤、引擎或硬件性能。
