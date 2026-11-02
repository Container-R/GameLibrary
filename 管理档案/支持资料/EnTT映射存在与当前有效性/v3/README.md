# EnTT 映射观察 v3：补齐五个运行位置后的独立记录

本目录保留同一四阶段观察的 **v3 新执行**：同一操作者在同一环境的一次 runner 调用中，用两个新副本各构建、执行一次。没有组件或网络行为。v3 的两个原始输出相同，且技术数据与旧 v2 相同；这不是不同操作者或跨机器复现。

## 为什么另存 v3

v2 当时只设置 TMPDIR、干净 PATH 和 locale，没有显式准备规范要求的 HOME、XDG_CACHE_HOME、XDG_CONFIG_HOME、XDG_DATA_HOME，属于当时流程不符合。它的两次真实构建、两次真实原生执行和旧文件保留，不追改为五键合规。

v3 用新的协议、runner 和输入清单补齐五键准备与启动前检查，再新增两次构建、两次原生执行。两版本合计四次构建、四次原生调用，仍是同一个实体映射条件，不是四种场景。v3 没有重写 v2 回执，也不能凭相同输出消除旧流程问题。

## 看到了什么

来源注册表创建一个实体，目标先创建 seed。连续加载器读取来源实体后，外部逻辑删除映射得到的本地实体，再从头读取相同内存归档。

| 阶段 | 映射非空 | 映射句柄在目标中有效 | 目标活跃数 |
|---|---|---|---:|
| 加载前 | 否 | 否 | 1 |
| 加载后 | 是 | 是 | 2 |
| 外部删除后 | 是 | 否 | 1 |
| 相同归档再加载后 | 是 | 是 | 2 |

删除后的映射仍是最初的完整句柄；重新加载才得到新的有效完整句柄，旧句柄仍无效。来源实体和 seed 始终有效。这只观察映射保存与当前有效性的区别，不是组件引用迁移、业务权限、版本绕回或整个 ECS 正确性验证。

[第一次原始八行输出](observations/repeat-1/native.stdout)与[第二次](observations/repeat-2/native.stdout)均保留原字节。两份声明行是 C++ 201703、GCC 14.2.0、EnTT 3.13.2；这是技术宏声明，不认证完整工具链来源。两份构建 stdout、四份 stderr 均为空，文件仍保留于各 observations 子目录。

[独立结果审查](NATIVE-REVIEW.md)重新检查原始输出、输入绑定与过程记录，并只重新运行消费者，没有追加原生执行。公开审查副本只转换包内原始输出路径并显式标注。

## 五键检查意味着什么

每次 build/native 分别新建拥有的 phase 根，在其下创建 HOME、XDG_CACHE_HOME、XDG_CONFIG_HOME、XDG_DATA_HOME、TMPDIR 五个目录；紧邻 Popen 前再次验证。四个进程记录均为 VALIDATED_BEFORE_LAUNCH，环境根收尾均为 REMOVED。[回执投影](receipt-projection.json)不输出实际映射路径。

这只检查当时五个指定位置，不是文件系统或网络沙箱，不消除检查与启动之间的竞态。根准备、部分创建清理、进程组收尾分别负责；组信号与 leader 回收不能认证所有后代终止，也不能认证所有写入都发生在五个目录内。清理失败不能覆盖已有首错。

公开投影保留返回码、无超时、空诊断、输入前后关系及内容检查，省略四个编译产物摘要字段；所留产物前后相等只是原记录的历史判断，不是对省略身份的重新认证。原私有回执整体身份只在本地保存。本页和投影是既有记录的整理，没有追加运行。

## 复查与复现材料

[协议](PROTOCOL-v3.md)、[输入清单](INPUT-MANIFEST.json)、[fixture](fixture.cpp)、[runner](runner.py)、[checker](checker.py)、[字面预期](independent-oracle.json)、[原协议审查](PROTOCOL-REVIEW.md)和[执行前代码审查](CODE-REVIEW.md)保留冻结字节。旧审查中的“尚未执行”是其历史时点，不否认本目录后来的 v3 记录；本页也不把代码审查当作独立原生复跑。

本包不分发约3.1MB官方单头或构建产物。按 [UPSTREAM-SOURCE.json](UPSTREAM-SOURCE.json) 的固定 EnTT v3.13.2 提交地址取得单头与许可证，放到 `source/entt.hpp`、`source/LICENSE`，核对大小和摘要；保留上游许可证要求。缺源时清单检查应失败，不能删掉这两项来通过。

公开包清单只绑定包内材料，不能代替原执行 INPUT-MANIFEST；后者仍含全部11项输入。准备 source 后，从本目录可复查纯测试：

```text
python3 -B -m unittest test_runner_cleanup test_environment
python3 -B -O -m unittest test_runner_cleanup test_environment
python3 -B independent_environment_tests.py
python3 -B -O independent_environment_tests.py
```

前两条各18方法，独立脚本各5方法，其中一个含40子例；这些历史合成检查通过，Popen/信号使用 mock，不是额外原生条件。独立脚本只是审查工具，不加入冻结输入清单。本次公开整理没有重跑这些命令。

若另行决定复现原生流程，还需 Python 3、C++17 编译器与标准库，以及支持该 runner 的 POSIX 进程组操作；不能承诺其他平台直接可用。核对输入后从本目录运行 `python3 -B runner.py fresh-observation`，输出目录必须不存在、父目录已存在。最多两个编译器入口和两个 fixture 入口，首错停止，不自动重试；编译器可能创建内部子进程。自行产生的原回执含本次产物身份，不自动成为安全公开材料。

[返回映射存在与当前有效性的支持说明](../README.md)
