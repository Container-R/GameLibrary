# 文字回退与字形裁剪：复现

[正文](../../../GameLibrary/本地化与无障碍/本地化制作/文字排版/字体已经能显示文字，为什么附标还是被裁掉.md) · [来源](../../来源笔记/fallback-font-ink-20261126.md)

脚本需要独立取得 DejaVu Sans 与 Noto Sans Thai Regular 字体，不附二进制；实际使用字体文件的 SHA-256 记录在 [Pillow 输出](ink-observed.txt)。本机动态加载，以命令参数传入所用字体文件：

```sh
godot --headless --path native --script probe.gd -- "$LATIN_FONT" "$THAI_FONT"
python3 ink.py "$LATIN_FONT" "$THAI_FONT"
```

- [Godot 输出](native/observed.txt)：4.7.2.stable.official.ed1daf0bf，内建 ICU / HarfBuzz / Graphite。单行文字按给定的两字体顺序塑形，关闭系统字体回退；逐字形检查 font RID、glyph index 以及行的 ascent/descent。只读排版结果，未绘制图像。
- [像素比较](clip-comparison.png)：Pillow 13.0.0、FreeType 2.14.3、RAQM 0.11.0，显式指定字体画两个文本段，基线相同。满幅缓冲高度 104；裁剪范围外清零，计数非零像素。图为同一份实际像素掩码放大并标注，不是 Godot 截图。较宽裁剪与无裁剪逐字节比较。

数值依赖字体和版本；对照不声称指定不同现代字体也会得到 44 像素，更不是对泰语译文正确性的测试。
