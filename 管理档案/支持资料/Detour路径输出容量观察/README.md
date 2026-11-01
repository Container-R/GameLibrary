# Detour：搜索终点与输出数组的容量

一个调用成功，不一定表示调用者拿到了整条路径。这里记录固定 Detour v1.6.0 的小规模原生观察：三个相邻矩形 A、B、C 构成唯一通路，起点在 A 内、目标在 C 内，只改变 `findPath` 声明允许写入的路径项数。

| 声明上限 | 实际输出 | 原始状态 | 解释 |
|---|---|---|---|
| 2 | A、B | `0x40000010` | 成功位与 BUFFER_TOO_SMALL 共存，没有 PARTIAL_RESULT |
| 3 | A、B、C | `0x40000000` | 成功，输出包含目标 |

每次实际分配三个槽，上限2时第三个零哨兵保持不变。这只观察一个位置未被改写，不是完整内存安全证明。输入没有分叉、节点池容量16足够；没有测试节点耗尽、动态地图、真实烘焙、权重路线、几何最短路或角色移动。

## 观察从哪里来

[主编原始观察](observations/main.json)与[独立副本观察](observations/independent.json)逐字节一致，SHA256为 `0edf850d701be23d45c1fdca270b578081b7cc62371a2165d267dca198404674`。两个副本的真实引用均为4、5、6；它们是库生成的polygon标识，不是主机地址。JSON记录实际顶点、邻接、链接、默认filter、节点池、调用数和全部返回槽，不只有PASS文字。

[主编回执](receipts/main.json)及[独立回执](receipts/independent.json)均完成构建、原生调用和24项输入身份后检。另建副本是同一环境重复，不是跨机器或跨平台验证。普通与优化模式的Python只重复消费已捕获输出，没有增加原生查询。详见[独立原生复核](NATIVE-REVIEW.md)。

## 先停过一次，警告并没有消失

[第一次回执](receipts/first-build-gate.json)保持失败：编译器退出0，但一条上游 `-Wclass-memaccess` 诊断未预先接受，门槛因此阻止了原生启动；该次查询为0。随后核对固定类型与初始化代码，重新审查协议，只允许空诊断或[这份精确诊断](reviewed-build-stderr.txt)，没有改上游、压制警告或换编译旗标。

两次成功构建都仍带着这份已审警告。这允许对未改固定实现作有限经验观察，不证明所有C++实现的对象生命周期、全零指针表示或ABI安全。具体理由与拒绝条件见[诊断审查](BUILD-DIAGNOSTIC-REVIEW.md)。

实际合计3次构建、2次fixture启动、4次findPath；只是同一输入的两种容量重复两遍。不是4种场景，首次停止也不计作两条查询失败。

## 复现所需文件与执行边界

[源码清单](SOURCE-MANIFEST.json)固定 `recastnavigation/recastnavigation` 提交 `6dc1667f580357e8a2154c28b7867bea7e8ad3a7` 的7个cpp和9个头文件；上游保持原样及其许可，本包不重新分发整份上游代码。需从该固定提交取得清单文件，放到本目录的 `upstream/Detour/...` 对应位置，按清单核Git blob与SHA256。

[协议](PROTOCOL.md)、[fixture](fixture.cpp)、[字面期望](expected.json)、[消费器](validate.py)和[运行器](run.py)由[代码清单](CODE-MANIFEST.json)绑定。协议中的“未执行”是各次冻结时的记录；实际执行结果以本页两份观察及三份回执为准，不把后来的成功倒写进早期协议。完整编译argv在运行器中明确列出；本轮使用自报GCC14.2.0的C++工具，不据此认证其二进制发行身份。没有运行CMake、安装SDK或调用网络。

在完整、独立的新副本中，可先检查纯测试，再按协议执行：

```sh
python3 -B -m unittest -v test_validate
python3 -B -O -m unittest -v test_validate
python3 -B independent/challenge.py
python3 -B -O independent/challenge.py
python3 -B run.py
```

运行器要求全新 `execution/attempt-002`，已有目录直接拒绝，不覆盖旧结果。构建限60秒，成功并通过精确诊断门槛后才启动一次限10秒的fixture；最多两查询，首错停止。不同编译器即使只改变诊断措辞，也会被当前门槛拒绝，应先审查，不能随意放宽。

消费器文件中的 `consumer_only/pass` 只表示该JSON符合字面期望；还必须查看完整receipt的身份后检和最终状态。合成JSON能通过消费器并不证明真实调用发生。输入身份与已审运行器、原始输出及回执须一起使用。

执行前作者13方法与独立11方法在普通及优化模式各通过；同一集合重复不算双倍覆盖。它们包括精确诊断/新增诊断、重复键、状态位、引用、哨兵、缺输出、旧目录拒绝和身份后检等有限反例。没有用这些纯测试冒充Detour查询。[实现审查](INDEPENDENT-IMPLEMENTATION-REVIEW.md)保留初版setup记录问题、消费者PASS语义风险及其修订；[协议审查](PRE-REVIEW.md)保留初始化失败退出边界。

`history/attempt-001-inputs`只保存首门槛与当前版本不同的历史输入及清单，非独立可运行目录；其fixture、expected、validate与SOURCE-MANIFEST字节与本目录相同。第一回执和固定源身份对应该历史版本，不把它升级为当前版本的成功证据。审查文件中旧执行路径是发生时的相对定位；本归档中的原始观察和回执以本页链接为准，没有附带编译程序或私有执行信息。

## 原始来源与返回正文

- 固定版本[状态定义](https://github.com/recastnavigation/recastnavigation/blob/6dc1667f580357e8a2154c28b7867bea7e8ad3a7/Detour/Include/DetourStatus.h)。
- 固定版本[findPath结果与getPathToNode回写](https://github.com/recastnavigation/recastnavigation/blob/6dc1667f580357e8a2154c28b7867bea7e8ad3a7/Detour/Source/DetourNavMeshQuery.cpp#L1156-L1204)。
- [原有源分析与调用者政策](../../研究记录/source-notes/detour-findpath-status-and-capacity.md)仍有未在本单元运行的范围。

[返回导航正文](../../../GameLibrary/游戏人工智能/移动导航/路径查询/如何判断导航路径是否真正可用.md)。
