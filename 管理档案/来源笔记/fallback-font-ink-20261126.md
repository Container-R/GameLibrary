# 文字回退与字形裁剪：来源核对

核查轮次：北京时间 2026-11-26 02:50。[复现](../实验/文字回退与字形裁剪/README.md)。

- [FreeType Glyph metrics](https://freetype.org/freetype2/docs/glyphs/glyphs-3.html)，baseline、bounding box、typographic metrics；区分墨迹边界、字体度量和行距离。
- [OpenType OS/2 table](https://learn.microsoft.com/en-us/typography/opentype/spec/os2)：`sTypo*` 用于排版行度量，`usWin*` 用于裁剪边界等历史用途。资料也提醒应用使用不同做法；本文不拿 Windows GDI 的实现当项目默认。
- [Godot TextServer 4.7](https://docs.godotengine.org/en/4.7/classes/class_textserver.html) 的塑形、字形取回、行上升及下降量接口。按两个明确字体进行实际无窗口读取；像素层用另一套栅格实现手工选择两段字体，没有跨实现混同。
