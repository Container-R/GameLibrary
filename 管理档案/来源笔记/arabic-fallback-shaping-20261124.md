# 阿拉伯文的字体回退与连写塑形：来源记录

- Unicode Consortium，[UAX #29](https://www.unicode.org/reports/tr29/)，§3 字素簇边界。扩展字素簇用于分割输入，不能推出所有塑形可独立断开。访问日期：2026-11-24。
- HarfBuzz，[Working with HarfBuzz clusters](https://harfbuzz.github.io/working-with-harfbuzz-clusters.html)：字形到输入索引、合并，以及簇级别差异；[hb-buffer](https://harfbuzz.github.io/harfbuzz-hb-buffer.html#hb-glyph-flags-t)：UNSAFE_TO_BREAK 用于当前塑形结果的簇起点，不据此推断另一字体。
- Microsoft，[IDWriteFontFallback::MapCharacters](https://learn.microsoft.com/en-us/windows/win32/api/dwrite_2/nf-dwrite_2-idwritefontfallback-mapcharacters)：头部匹配长度、字体、缩放；不是本文使用的回退器。
- [Noto Arabic 项目](https://github.com/notofonts/arabic)与[复现记录](../实验/阿拉伯文回退切段/README.md)。临时改动 cmap 的原字体文件不分发。独立 HarfBuzz 字形记录和 RAQM 渲染分开，不外推操作系统、引擎、更换字体风格或跨文字系统。
