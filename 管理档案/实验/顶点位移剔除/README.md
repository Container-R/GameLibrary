# 顶点位移剔除：复现实验

[返回正文](../../../GameLibrary/图形渲染/空间查询/可见性剔除/顶点着色器把网格移进镜头，为什么还没被画出来.md)

- `check_bounds.py`：精确二维矩形与位移集合。源盒宽 0.5，例子包含只向左偏移、非等比缩放与旋转的逆线性向量转换；不是引擎执行。
- [原生试件](native/README.md)：程序自行判断是否执行 draw；软件 OpenGL 实际运行顶点偏移、裁剪和光栅。用宽 1 的网格分别验证源盒、保守盒与关闭剔除，量测最终像素。没有比较硬件、引擎内部实现或深度／阴影阶段。
- [Framebuffer PNG](native/readback.png)为原始 PPM 的无改色格式转换。

```sh
set -e
python3 -B check_bounds.py >/tmp/gl-bounds.json
cmp /tmp/gl-bounds.json geometry-observed.json
```
