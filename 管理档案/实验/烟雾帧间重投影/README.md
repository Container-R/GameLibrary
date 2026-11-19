# 烟雾帧间重投影

[返回正文](../../../GameLibrary/%E8%A7%86%E8%A7%89%E7%89%B9%E6%95%88/%E7%89%B9%E6%95%88%E5%88%B6%E4%BD%9C/%E5%BA%8F%E5%88%97%E7%BA%B9%E7%90%86/%E4%BD%8E%E5%B8%A7%E7%8E%87%E7%83%9F%E9%9B%BE%20Flipbook%20%E7%9A%84%E5%8F%8C%E5%BD%B1%EF%BC%9A%E8%BF%90%E5%8A%A8%E7%9F%A2%E9%87%8F%E7%83%98%E7%84%99%E4%B8%8E%E9%87%87%E6%A0%B7%E9%AA%8C%E6%94%B6.md)

在本目录运行：

```bash
python3 -B check_translation.py | diff -u observed.json -
python3 -B check_atlas_boundary.py | diff -u atlas-observed.json -
python3 -B make_two_dimensional.py
```

最后一项在运行目录写出 `two-dimensional-observed.json` 与 `two-dimensional.svg`。若不希望更改检出的文件，可把该脚本复制到临时目录后运行，再与存档比较。两组一维对照分别固定匀速平移及两格边界；二维图以 18×15 像素的有理数透明度说明平移和新生。没有执行 Unity、Houdini、真实烟雾、GPU 采样或材质压缩。
