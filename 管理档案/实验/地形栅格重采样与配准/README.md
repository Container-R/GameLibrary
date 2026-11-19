# 地形栅格重采样与配准：复现实验

[正文](../../../GameLibrary/技术美术/环境管线/地形数据/地形重采样后山脊变平：检查高程、网格和影像.md)

使用 Python 3 及 GDAL 3.10.3 命令行程序 `gdalwarp`、`gdal_translate`、`gdaladdo`。高程试件写入临时 ASCII 栅格，生成 GeoTIFF，转 XYZ 后抄取同一行；只比较相同版本的输出。非整数原点的两组对照用于避开源像元边界。实测命令输出：

```sh
python3 check_grid_phase.py | cmp - expanded-observed.json
python3 check_registration_and_imagery.py | cmp - registration-observed.json
python3 check_overview.py | cmp - overview-observed.json
```

第二份试件用三个已知坡度的平面精确计算一轴取样偏移与高程偏置，并用合成灰度序列比较同一几何上的影像平移和对称模糊。第三份写同一 GeoTIFF 的 2 倍平均概览，保持输出网格及近邻算法，切换概览 AUTO 和 NONE。没有对真实测绘数据拟合，也没有运行 Unity 或 Unreal。第三方 CTX 动图仅在正文链接，不随试件再分发。
