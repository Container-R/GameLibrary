# 图集 Mip 串色：复现实验

[返回正文](../../../GameLibrary/技术美术/环境管线/纹理与材质/图集缩小时为什么串色：区分%20Mip%20生成与边界采样.md)

- [原生 OpenGL](native/README.md) 真实生成全图各级并读取纹理和 framebuffer；[放大后的结果](native/readback.png)是四组实际色样。红无蓝时 RGB=(255,0,0)；第 1、3 组含蓝但成因不同。
- `check_atlas_mip.py` 是不透明、线性颜色、所有行相同的精确箱式模型。在不同对齐位置验证生成与采样，再以同 UV 比较一像素、两像素扩边与跨级，输出 `atlas-observed.json`。该模型不是特定引擎或 GPU 的过滤器。

用 Python 3 运行：

```sh
python3 -B check_atlas_mip.py >/tmp/gl-atlas-box.json
cmp /tmp/gl-atlas-box.json atlas-observed.json
```

实际软件 GL 的运行环境和步骤见子目录。原生与数学的图集宽度、坐标和设置不同，不直接比较两个表的数字。原生 RGBA8 量化，数学使用有理数权重。
