# 两条耦合距离约束：原生 XPBD 有限复现

本附录回答一个很小的问题：一条孤立约束修正后不再移动，为什么加入另一条共享质点的约束后，仍需要继续迭代？这里实际调用固定版本的 C++ 距离约束函数，不重写 XPBD 求解公式，也不运行完整布料、绳索或引擎场景。

本说明及 `observations.json` 是方法与观察结果的公开整理版，省略执行主机身份信息；它们不是原始冻结文档的逐字副本。`driver.cpp` 和两份 JSONL 轨迹则保持原始字节不变。附件没有包含原生库、Eigen 源码包、执行程序或主机诊断。

## 源码与参数

- 原生实现：[InteractiveComputerGraphics/PositionBasedDynamics](https://github.com/InteractiveComputerGraphics/PositionBasedDynamics)，固定提交 [`10a70bc146a97873dc3c8fef372f5217e010542e`](https://github.com/InteractiveComputerGraphics/PositionBasedDynamics/tree/10a70bc146a97873dc3c8fef372f5217e010542e)，版本文本为 2.2.2。
- 调用 [`XPBD::solve_DistanceConstraint`](https://github.com/InteractiveComputerGraphics/PositionBasedDynamics/blob/10a70bc146a97873dc3c8fef372f5217e010542e/PositionBasedDynamics/XPBD.cpp#L14-L60)。编译完整、未修改的 `XPBD.cpp`、`PositionBasedDynamics.cpp`、`MathFunctions.cpp` 及原始头文件。后两者满足完整翻译单元的链接依赖，不表示本例测试了那些功能。
- Eigen 3.4.0，使用上述提交自带的 `extern/eigen`。其树身份及原生输入文件的 Git blob 身份列在 `source-identities.json`。原生执行前，所用 337 个非 CMake Eigen 文件均与固定源码的字节身份相符。
- GCC 14.2.0；`Real` 为默认 float，4 字节、24 位有效二进制数。未定义 `USE_DOUBLE`，未启用 fast-math。
- 编译选项：`-std=c++17 -O0 -fno-fast-math -ffp-contract=off -DEIGEN_MPL2_ONLY -Wall -Wextra`。

三个预测位置为 `(0,0,0)`、`(1.2,0,0)`、`(2.6,0,0)`，逆质量分别为 0、1、1。约束 01 和 12 的静止长度均为 1。接口接收的是 **stiffness=100**，不是柔度 .01；dt=.1。原生缩放项为 `1/(stiffness*dt*dt)`。每条约束有各自的 λ，只在开始时置零。

每轮先访问 01 并立即应用修正，再访问 12 并立即应用修正。共 8 轮、16 次原生函数调用，在第 1、2、8 轮保存检查点。没有速度更新、时间积分、外力、碰撞或跨步热启动。

## 原始调用记录说明了什么

第一次修正 01 后，x1 约为 1.100000024。接着修正 12 时，它又被推到约 1.266666651。因此，01 的柔性残差重新出现；这不需要丢弃或清零它已积累的 λ。

这里应检查 `r=C+α̃λ`，不能把几何伸长 `C` 本身当作必须归零的误差。固定正序共线分支的解析极限为 x1=1.2、x2=2.4，两条 λ 均为 −.2，几何伸长各为 .2。

下表来自保存的原生轨迹。残差由记录中的实际 float 参数和状态重新计算，表中只做显示舍入：

| 完成轮数 | x1 | x2 | r01 | r12 |
|---|---:|---:|---:|---:|
| 1 | 1.266666651 | 2.433333397 | .1666666299 | 1.2418e−7 |
| 2 | 1.211111188 | 2.405555725 | .02777785609 | 1.2500e−7 |
| 8 | 1.200000286 | 2.400000334 | 5.8711e−7 | 1.1027e−7 |

验收前固定的绝对容差为 **2e−6**，位置、乘子和残差均使用这一容差。第 8 轮的解析残差小于该容差，因此这里只能说观察与解析预期在容差内相符，不能宣称精确分辨了第 8 轮残差或残差已经等于零。

实际完成两次新目录中的构建与运行，每次仍是同一条 16 次调用的轨迹，共 32 次原生调用。两份 21 行 JSONL 轨迹字节一致，SHA-256 均为 `c6ca6a9abdd55ed9421a823acfacd8084fe8edbbd8ad5c25cd6abde62ba318e8`。这是同一操作者、同一工具链的重复运行，不是独立复现。两次构建各有 6 条未使用参数警告，位于本例未调用的四面体相关函数；构建与运行均正常退出，运行标准错误输出为空。

## 解析检查与适用边界

只在本例始终满足 x0<x1<x2 的共线分支上，二次目标的极小点满足：

`3*x1-x2=6/5`，`-x1+2*x2=18/5`。

在这个分支上，累计位移可写成 `x1=6/5+lambda01-lambda12`、`x2=13/5+lambda12`。中点受两条约束影响，末点只受后一条影响。代入残差定义后，得到 `r01=1/5+2*lambda01-lambda12`、`r12=2/5-lambda01+3*lambda12`。

完成 n 轮后（n≥1），令 `q=6^(-n)`，解析预期为：

- `x1=6/5+2*q/5`，`x2=12/5+q/5`。
- `lambda01=-1/5+3*q/5`，`lambda12=-1/5+q/5`。
- `r01=q`，`r12=0`，此处是理想实数运算。

这些式子在运行前已推导。原生记录则包含 float 舍入：记录的 dt 为 0.10000000149011612；原生 float 表达式得到缩放项 1，检查器用较宽浮点重新计算该项约为 0.9999999701976783。差异不能隐藏成精确实数计算。

驱动和检查器同时检查有限数、正距离与正分母、锚点与共线性、乘子连续保留，以及返回修正是否立即应用。原生函数在某些退化分支也返回 true，因此只看返回值并不足够。

本结果支持的是固定源码、输入、调用顺序和精度下的有限原生核测试。原始 `DistanceConstraint_XPBD`、TimeStepController 和分组调度只做过源码核对，没有在本驱动中执行。本例没有测碰撞、长绳、布料、耗时、完整时间推进或跨平台一致性，也不能把解析分支的收敛率推广到任意约束网络。

## 可直接打开的材料

- [驱动源码](driver.cpp)与[轨迹检查器](check_traces.py)
- [第一次原始合成输出](trace-repeat-1.jsonl)与[第二次原始合成输出](trace-repeat-2.jsonl)
- [整理后的观察结果](observations.json)、[固定来源身份](source-identities.json)及[文件清单](artifact-manifest.json)

## 只核查已有轨迹

已有 Python 3 即可运行：

```sh
python3 check_traces.py trace-repeat-1.jsonl trace-repeat-2.jsonl
```

这个命令只读两份已有输出，检查 21 条记录、16 次调用、调用连续性、三个解析检查点和重复轨迹一致性。`STORED_TRACE_CHECK_PASS` 表示保存的输出通过检查，**不会编译或重新执行原生求解器**。检查器是原验收逻辑的公开衍生版，只保留数值与轨迹检查，移除了构建、主机身份及执行目录管理。

## 用自己准备的源码重新运行

下面是 Unix shell 下的简化复现命令，需要已有 g++、Python 3、git、tar 和 GNU timeout。先把 PBD 改为你已准备好的上游仓库位置。命令从本地 Git 对象提取指定源码，不联网、不安装依赖，不使用根 CMake；`pbd-source`、`run-1`、`run-2` 必须不存在。

```sh
set -eu
PBD=../PositionBasedDynamics
PIN=10a70bc146a97873dc3c8fef372f5217e010542e
mkdir pbd-source
git -C "$PBD" archive "$PIN" \
  Common/Common.h \
  PositionBasedDynamics/XPBD.cpp PositionBasedDynamics/XPBD.h \
  PositionBasedDynamics/PositionBasedDynamics.cpp PositionBasedDynamics/PositionBasedDynamics.h \
  PositionBasedDynamics/MathFunctions.cpp PositionBasedDynamics/MathFunctions.h \
  extern/eigen LICENSE | tar -xf - -C pbd-source
for n in 1 2; do
  mkdir "run-$n"
  timeout 300s g++ -std=c++17 -O0 -fno-fast-math -ffp-contract=off \
    -DEIGEN_MPL2_ONLY -Wall -Wextra -I pbd-source -I pbd-source/extern/eigen \
    driver.cpp pbd-source/PositionBasedDynamics/XPBD.cpp \
    pbd-source/PositionBasedDynamics/PositionBasedDynamics.cpp \
    pbd-source/PositionBasedDynamics/MathFunctions.cpp -o "run-$n/fixture"
  timeout 10s "./run-$n/fixture" > "run-$n/trace.jsonl"
done
python3 check_traces.py run-1/trace.jsonl run-2/trace.jsonl
```

这是核心编译、运行和数值检查的简化说明，不是原始隔离包装的逐字副本。原始执行另有全输入身份核对、新 HOME/TMP/XDG 目录、清理继承环境、资源上限及失败日志保留。若在其他工具链得到不同字节，先检查参数、精度和实际误差，不能因此自动宣布数学或实现错误，也不能为通过检查临时放宽容差。

## 署名与许可

PositionBasedDynamics 项目 README 署名 Jan Bender；项目贡献者保留其 [MIT 许可与版权声明](https://github.com/InteractiveComputerGraphics/PositionBasedDynamics/blob/10a70bc146a97873dc3c8fef372f5217e010542e/LICENSE)。Eigen 有独立的 [许可说明](https://github.com/InteractiveComputerGraphics/PositionBasedDynamics/blob/10a70bc146a97873dc3c8fef372f5217e010542e/extern/eigen/COPYING.README) 和 [MPL 2.0 文本](https://github.com/InteractiveComputerGraphics/PositionBasedDynamics/blob/10a70bc146a97873dc3c8fef372f5217e010542e/extern/eigen/COPYING.MPL2)，不能将其一并视为 MIT。上面的提取命令保留原始源码及随附许可文件。

此处的驱动、解析例子与说明为本库编写；它们不是上游作者的实验案例。原生项目实现的来源身份也不等于声称它是 2016 年 XPBD 论文作者的官方参考实现。

---

[返回主文：多做几次约束修正，为什么物体反而更硬](../../../GameLibrary/玩法程序/玩法系统/时间与模拟/多做几次约束修正，为什么物体反而更硬.md)
