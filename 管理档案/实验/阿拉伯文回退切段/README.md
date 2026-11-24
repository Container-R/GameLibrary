# 阿拉伯文字体回退：真实塑形与渲染对照

在 Linux 上安装 Python 3、fontTools、带 RAQM 支持的 Pillow、系统 `libharfbuzz.so.0` 和 Noto Sans Arabic Regular。运行 `python3 reproduce.py --font /path/to/NotoSansArabic-Regular.ttf`。默认读取 Debian 的 Noto 字体位置；原机字体 SHA-256 见 [测量输出](fallback-observed.txt)。产物 [comparison.png](comparison.png) 只包含渲染图；字体本身不随材料分发。Noto Sans Arabic 发布源及许可证见 [Noto Arabic 项目](https://github.com/notofonts/arabic)。脚本只在自动清理的临时目录制作修改版，不要把这个人为删字的版本打包进项目或再分发。

源字符串依逻辑顺序是 U+0628 U+062A。主字体由同一份 Noto Sans Arabic 原件复制，仅移除所有 Unicode cmap 子表中的 U+062A 映射；去掉的是从字符到字形的入口，不删除任何轮廓，也不改变字号或字体风格。未修改的字体作为唯一回退。三个策略为：

1. 主字体整段塑形，用于确认覆盖缺口。
2. 两个字符分别使用有覆盖的字体，但发起两次相互独立、各自 RTL 的塑形，再按原 RTL 位置拼起来。
3. 将整个同脚本、同方向的词交给未修改字体，一次塑形。此例的回退由脚本显式分派，不使用任何操作系统或游戏引擎的回退器。

系统 HarfBuzz 10.2.0 的 OpenType 字体函数给出字形号及输入码点索引；字形号只在这个字体及其保留字形次序的副本内有意义。整段的输出依视觉顺序，独立小段却以各自索引 0 起算并按逻辑段顺序报告。Pillow 13.0.0 通过 RAQM 0.11.0 / HarfBuzz 14.5.0 做真实栅格绘制并返回 advance；这个栈和取得字形号的系统库版本不相同，不能把日志字形号说成从 Pillow 读出。

图在 96 px、同一基线与右对齐下对照。主字体单用出现空框；逐字符都有非零字形却不连写，约 190.66 px；整词回退形成连写，约 130.75 px。该对照没有覆盖附标定位、换行、跨多个脚本、连接控制字符或不同字体轮廓的视觉兼容性。

[返回正文](../../../GameLibrary/本地化与无障碍/本地化制作/文字排版/阿拉伯文的字体回退与连写塑形.md)
