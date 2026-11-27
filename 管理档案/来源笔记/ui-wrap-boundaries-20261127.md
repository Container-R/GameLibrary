# 窄文本框换行：来源

- [正式正文](../../GameLibrary/本地化与无障碍/本地化制作/文字排版/窄文本框换行，为什么不能按字符数硬切.md)；[断点和宽度的实测](../实验/窄文本框的换行边界/README.md)。
- Unicode 16.0 [UAX #14 修订 53](https://www.unicode.org/reports/tr14/tr14-53.html)：区分强制断点、允许断点和禁止位置。第 6 节 LB5 等规则处理 CR/LF，第 6 节可裁剪的规则处理标点及不换行字符；具体表中位置应以已运行的 ICU 配置为准。
- Unicode 16.0 [UAX #29 修订 45](https://www.unicode.org/reports/tr29/tr29-45.html)，第 3 节：GB9、GB11 的组合和表情范围。字素分段不承诺字形数量和宽度，也不是默认的整词或行边界。
- ICU [Boundary Analysis](https://unicode-org.github.io/icu/userguide/boundaryanalysis/) 与 [Break Rules](https://unicode-org.github.io/icu/userguide/boundaryanalysis/break-rules.html)：实际探针走 ICU4C 的 UTF-16 缓冲和行规则状态；其他输入 API 可能返回不同索引单位。
- Pango [WrapMode](https://docs.gtk.org/Pango/enum.WrapMode.html) 及 [Layout.get_size](https://docs.gtk.org/Pango/method.Layout.get_size.html)：区分词、字素兜底和逻辑宽度。HarfBuzz [Getting started](https://harfbuzz.github.io/getting-started.html) 的 UNSAFE_TO_BREAK 是复用塑形边界提示。
- 两份实验分别测 ICU 76/Unicode 16 的边界与 Pango 1.56.3/DejaVu Sans 的布局。没有用 Pango 确认中文表情的生产字体链、没有把两个引擎视作同一个排版运行时。
