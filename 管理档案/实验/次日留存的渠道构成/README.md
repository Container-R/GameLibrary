# 次日留存的渠道构成：SQLite 对照

[返回正文](../../../GameLibrary/数据分析/指标设计/玩家行为/每个渠道的次日留存都下滑，为什么总留存还涨了.md)。

用 Python 3 标准库运行，实测 SQLite 3.53.1。不用 Python 优化模式，保留断言。

```sh
python3 cohort_fixture.py > /tmp/ret-cohort-output.txt
cmp /tmp/ret-cohort-output.txt cohort-observed.txt
```

[生成及查询脚本](cohort_fixture.py) · [原始输出](cohort-observed.txt)。

安装表每账号一行，打开表允许多行。设小时 500 为已覆盖水位，按每账号 `[t0+24,t0+48)` 是否至少有一条回访计数；要求水位已到窗口末。2000 个成熟账号生成四组计数；10 个窗口未满的正例不纳入，不在正例提前成熟。第二个对照在 B 额外纳入 20 个渠道未知账号，有 17 人回访，不给 A 虚构参与者，验证 B 共同覆盖为 1000/1020。

原始源是合成数据，SQLite 核对查询，Python Fraction 按相同权重复算。未涉及任何实际玩家、归因系统、跨时区、迟到修订或版本效果。
