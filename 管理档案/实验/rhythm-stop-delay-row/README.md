# 同一谱面行的 Stop 和 Delay · 复现

[对应正文](../../../GameLibrary/玩法程序/玩法系统/时间与模拟/音游谱面停在一拍时，这颗音符该在停前还是停后按.md)。

## 数学对照

执行 `python3 model.py`，与 [observed.txt](observed.txt) 对照。拍 0 的歌曲秒为 0，第 8 拍之前 120 BPM，之后 180 BPM；第 8 拍放 0.4 秒的单一正向停顿。选择 48 kHz，三行算例都恰落在整数样本上。

## 直接夹测固定源码的正、反转换核心

取固定 StepMania 提交 `7cbaff8ce2dcbede32dd3d6f3f2d8fafeafd674e` 上的 [TimingData.cpp](https://raw.githubusercontent.com/stepmania/stepmania/7cbaff8ce2dcbede32dd3d6f3f2d8fafeafd674e/src/TimingData.cpp)，在本目录将其保存到临时路径；抓取源文件而不是 GitHub 的网页 HTML。下面脚本校验字节摘要并仅在临时区提取三个内部函数用到的原始行：

```sh
tmp=$(mktemp -d)
# 将上方链接的源文件保存为 "$tmp/TimingData.cpp" 后：
python3 extract.py "$tmp/TimingData.cpp" "$tmp/timing-excerpt.inc"
c++ -std=c++17 -Wall -Wextra -I"$tmp" harness.cpp -o "$tmp/probe"
"$tmp/probe"
```

夹具替代了谱面分段对象、每拍 48 行的整数换算和当前 BPM 查询，填入正向 BPM、Stop 或 Delay 数据；上游自身的选择和转换函数在夹具中执行。它不构建或运行 StepMania 游戏，不覆盖解析器、查找缓存、倍速、输入评分与实际音频。样本取最近整数，且带断言核对 [native-observed.txt](native-observed.txt)；4.4 秒是两种停顿的右端点。
