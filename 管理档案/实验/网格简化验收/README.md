# 简化网格验收复现材料

- [原生索引预算探针](native_probe.cpp)与[实际输出](NATIVE-OUTPUT.txt)。
- [对角翻转反例精确复算](diagonal_counterexample.py)，独立于简化程序。
- [返回正文](../../../GameLibrary/技术美术/环境管线/模型细节级别/简化网格的验收：实际索引预算与曲面偏差.md)。

从 meshoptimizer v0.25 固定提交 `6daea4695c48338363b08022d2fb15deaef6ac09` 取 [meshoptimizer.h](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/meshoptimizer.h) 与 [simplifier.cpp](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/simplifier.cpp)，将本目录的两个探针文件放在同一工作目录，把两份上游源码放进该工作目录的 `upstream/`，再从工作目录运行：

```sh
c++ -std=c++17 -O2 -I upstream upstream/simplifier.cpp native_probe.cpp -o native_probe
./native_probe
python3 diagonal_counterexample.py
```

原生测试用 GCC 14.2.0，重复输入分别从同一原网格和普通选项开始，只报告数量与代理误差。没有运行 CGAL。
