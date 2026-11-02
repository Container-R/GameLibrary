# EnTT 组件字段引用观察

导入实体时，组件附着到了新对象，不等于组件内部保存的实体编号也已经转换。本例只检查这个区别：来源有箱子和持有 `Link{箱子}` 的实体，目标预先有一个 seed；归档只按值复制 Link，不替字段调用映射，也没有构造监听器。

固定 EnTT v3.13.2 的同一条件，由同一操作者在同一环境的一次 runner 调用中，用两个新副本各构建、执行一次。两份11行输出相同；它不是独立操作者或跨机器复现，也不是前一个无组件实验的结果。本页只整理既有记录，没有重新运行。

## 实际方法与结果

官方 snapshot writer 产生两个有类型内存流：实体流4项，Link流3项。先加载两个实体，确认箱子和 holder 都有有效本地映射，并且箱子的本地值不同于来源值，才加载组件。从目标注册表读取已载入的 Link 前，另检查 holder 的本地映射当前有效且确有 Link，不访问无效组件。

这里的具体整数来自此次夹具，不是今后分配的保证：

| 对象或字段 | 实际完整值 | 所属或含义 |
|---|---:|---|
| 来源箱子 | 0 | 来源注册表 |
| 来源 holder | 1 | 来源注册表，持有 Link |
| 目标 seed | 0 | 目标注册表的既有实体 |
| 箱子映射 | 1 | 目标注册表 |
| holder 映射 | 2 | 目标注册表，最后持有 Link |
| 载入后 Link.target | 0 | 字段仍保存来源箱子的值，不是箱子本地映射1 |

源组件字段、归档字段、输入 archive 读到的字段与最终存储字段均为0；所属 holder 则确实转换成目标中的2。最终 Link.target 在目标中碰巧有效，因为0恰好也是 seed 的完整值。这没有证明它仍是原箱子，正好说明“在这个注册表中有效”与“对应来源对象”不是同一判断。没有执行开箱、删除 target 或其他业务动作；错误业务后果只能条件推演。

[第一份原始输出](observations/repeat-1/native.stdout)和[第二份](observations/repeat-2/native.stdout)逐字相同。每份是声明、7个typed token、3阶段；两份构建stdout和四份stderr均为空。声明中的C++ 201703、GCC 14.2.0、EnTT 3.13.2是技术宏，不是完整工具链来源认证。

[独立结果审查](NATIVE-REVIEW.md)核对了两份实际输出和输入绑定，并仅重新运行消费者，没有追加编译或原生执行。同操作者、同环境的归属来自主编执行记录，不由回执自身认证身份。

## 它没有证明什么

这是一个普通 Link 和只复制值的 archive。没有容器、嵌套引用、显式转换 callback、组件图修复、版本绕回、网络或产品存档格式。官方测试里有在 archive 内主动调用 map 转换成员的正向例子，但本次没有执行该路径；不能说 EnTT 不支持字段转换，也不能声称该 callback 已实测。

四个构建/执行阶段记录均为启动前五键验证完成、环境根清理完成。HOME、三个XDG位置和TMPDIR的实际路径不公开；有限目录验证不是沙箱，不证明所有写入、网络调用或所有后代均受控。组信号与leader回收也不是所有后代状态的认证。

[安全回执投影](receipt-projection.json)保留状态、输入前后关系和内容检查，省略四个构建产物摘要。保留的产物前后相等仅是原记录判断，不重新认证省略身份；原私有回执整体身份仅本地保存。原记录没有改写，公开整理不是新执行。

## 执行前纠错也保留

本轮在编译前纠正了两件事，不能藏在最后的成功结果后面：

- 最初审查把 writer 的 tuple 展开误认为一次双参数 archive 调用。固定代码实际逐项单参数调用，本条件实体4次、组件3次；错误没有进入执行实现。
- 最初 checker 只排除完整值全1，误接受保留索引或保留版本的“活跃句柄”。独立合成检查发现10个这种错误接受，修复后逐个拒绝，保留正常非零版本。它是消费者执行前缺陷，不是 EnTT 原生失败。

[执行前问题与旧消费者复查](pre-execution/README.md)保留最小 source-free 失败重现材料。[修正代码审查](CODE-REVIEW-v2.md)和[独立消费者闭合](CONSUMER-REVIEW-v2.md)说明接受范围。旧消费者的失败不表示本次真实输出包含那些不可能的活跃值。

## 输入与复查

[协议](PROTOCOL.md)、[typed schema](EXPECTED-SCHEMA.md)、[独立预期](independent-oracle.json)、[协议审查](PROTOCOL-REVIEW.md)及[保留位澄清](PROTOCOL-REVIEW-v2.md)均保持执行绑定的原字节；其中“尚未执行”属于各自冻结时点。新 [INPUT-MANIFEST.json](INPUT-MANIFEST.json) 的14项不因公开整理删减。

本包不包含约3.1MB官方单头及许可证文件本体，按 [UPSTREAM-SOURCE.json](UPSTREAM-SOURCE.json) 的固定官方地址准备 `source/entt.hpp`、`source/LICENSE` 并核对字节。上游许可仍适用；没有自动安装或下载器。包内清单只是公开材料绑定，不能替代执行输入清单。源码缺少时应停止，不删除输入项以通过。

从本目录可复查不调用原生程序的合成测试：

```text
python3 -B -m unittest test_checker test_runner_cleanup test_environment
python3 -B -O -m unittest test_checker test_runner_cleanup test_environment
python3 -B independent-consumer-check-v2.py
python3 -B -O independent-consumer-check-v2.py
```

作者套件每模式23方法，包括3个合成正例、45个反例及18个生命周期方法；独立脚本每模式5正例、91反例。两模式重复同组输入，不增加原生场景；Popen与信号由mock替代。公开整理未重跑这些命令。独立脚本是审查工具副本，不加入原14项执行清单。

若另行复现原生流程，需准备完整上游输入、Python 3、C++17编译器与标准库，并满足runner的POSIX进程组条件；不承诺其他平台直接可用。核对输入后从本目录运行 `python3 -B runner.py fresh-observation`，输出目录必须不存在且父目录已存在，首错停止；最多2次构建与2次fixture入口，不含编译器内部子进程数量保证。新原始回执含本次产物身份，不自动成为安全公开内容。

[返回实体句柄正文](../../../GameLibrary/引擎与工具/运行时系统/缓存与存档/实体句柄什么时候能保存，什么时候需要映射.md)
