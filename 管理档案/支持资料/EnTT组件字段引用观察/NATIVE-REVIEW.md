# EnTT 组件引用：独立原生结果审查

## 结论与实际审查范围

接受这一次预注册运行留下的有限结果。这里是**独立结果审查，不是审查者独立原生重跑**。提供的 `observations/` 中只有 `receipt.json`、`repeat-1/`、`repeat-2/`；根据主编的执行记录，本单元由主编在同一次 runner 调用中执行两个新副本；回执列出两次构建和两次原生执行。这里属于同操作者、同环境重复，不是独立原生复跑；操作者与环境归属不是回执自身的身份证明。四个进程均返回 0、没有超时，构建标准输出及全部标准错误为空。本次审查没有调用编译器、fixture 或 runner，也没有真实进程组信号操作。

完整读取两份各 11 行 `native.stdout`、回执与 fixture，并检查其余六份空原始流；重新读取固定源码的 snapshot 单参数展开和 continuous_loader 组件读取分支、runner 的环境准备与收尾。对两份实际原始输出各用普通 Python 和 `-O` 调用冻结 checker，均接受。两种 Python 模式消费的是同两份输出，不增加原生覆盖。

## 冻结身份与实际绑定

- `INPUT-MANIFEST.json`：`7af256d00360edbed9722d80196503548afada426016060312f42f96ef1faf38`。
- `fixture.cpp`：`a0ef9f35226c791bfb8917541737faabfcedd35a578bb07462739995e8eb7e57`。
- `checker.py`：`21dffbb35f6ae3365c8d8c14b581f6e36e566da449464446ff484a3cc05a2a2e`。
- `runner.py`：`1d7a61cb4f0e2a89350b5939c0ab4da23171f7cd5e461cf43a90466e97f3bd69`。
- `independent-oracle.json`：`92f2fe2c5dbfe5e3fa3a8a281b171e2bbde033bdcea0257ea86658f9d32eeb15`。
- 两份实际原生标准输出逐字节相同，SHA-256 均为 `c10b06e4ec7c2ab71b003c529f1c6a0cae7921728de71f0f1ee3deb79764c8d6`。

独立计算并核对了全部 14 个当前输入与清单、回执输入前后集合，以及清单前后身份。两副本各自的 fixture、源头单头文件、LICENSE 均与原输入及回执前后记录相同。八份输出流均与回执绑定一致。编译产物的当前内容、构建后记录与执行后记录在本地核对相等；本报告不公开产物指纹、私有回执整体摘要或机器身份。

## 不依赖 PASS 标签的结果解释

实际源端 box 为 0、holder 为 1；目标注册表预先存在 seed 0。二者数值相同不意味着跨注册表是同一对象。

1. `prepared`：映射尚不存在，两个映射值是规范 null；目标活动实体数 1、Link 数 0。组件字段尚未读入，相关观察用 JSON null，而不是虚构结果。
2. `entities_loaded`：源 box 0 映射到目标 1，源 holder 1 映射到目标 2。两映射当前有效且与 seed 区分；目标活动数 3、Link 数仍为 0。读取实体流 4 项，尚未读取组件流。
3. `component_loaded`：holder 的映射仍为 2，已持有 Link；目标活动数仍为 3，Link 数为 1。源字段、归档字段、输入回调所见字段和实际存入字段都为 0，而映射后的 box 是 1。实际 `local.valid(loaded_target)` 为 true，且字段等于 seed。因此本例不是“无效引用被检测出来”，而是**原样复制的字段恰好指向目标注册表里另一个有效实体**。

这与固定 EnTT v3.13.2（提交 `78213075654a688e9da6bc49f7f873d25c26d12c`）的该调用路径相符：组件所有者经 `restore`/`map` 处理；非空组件通过 `archive(elem)` 读入，再 `storage.emplace(map(entt), std::move(elem))`。本 fixture 的 InputArchive 只做类型受检的值复制，没有显式字段转换；不能把所有者映射推成 Link 内部成员自动映射。

snapshot 的 `std::apply` 内使用 comma fold 对每一个参数分别调用 archive。此简单条件下实际记录为实体流 4 项、组件流 3 项，共 **7 次单参数调用**；不是一次双参数 owner/component 调用。11 行由 1 声明、7 token、3 阶段组成，不是 11 个独立实验。

## 环境与计数边界

冻结 runner 在各 build/native 阶段创建独立根，由 helper 准备 HOME、XDG_CACHE_HOME、XDG_CONFIG_HOME、XDG_DATA_HOME、TMPDIR，随后在 Popen 前验证。回执最终环境状态为 `VALIDATED_BEFORE_LAUNCH`；代码中此前为 `PREPARED`，这是顺序覆盖的状态字段，不是两份独立现场快照。四阶段均记载 `REMOVED`、进程组 `NO_GROUP`、leader `REAPED`。审查时四个阶段根均已不存在。

这支持有限生命周期记录，不是五键以外全部写入的审计，不是 sandbox，也不能事后重新观察已经删除的目录当时全部状态。本次仅在所提供目录与回执范围内没有发现额外尝试记录，不能证明别处从未执行。

本组件单元记录的实际总量为 **2 次构建、2 次原生执行**。执行前的源码调用形态误读、初版 checker 保留位漏拒绝、初次接受后撤回均仍是执行前审查问题，不能改记为原生失败或抹去。原审查和 rejected-v1 输入继续保留；本次实测也不能倒推原 checker 已充分严格。此前无组件加载单元的 v2/v3 运行是另一条件，不计入本组件单元。

## 可得与不可得结论

此结果支持这个固定版本、普通 Link 聚合、明确源/目标创建顺序及纯复制 archive 下的具体反例：目标注册表 valid 为 true 仍不足以说明字段引用语义正确。没有执行带显式转换的对照分支；不得声称已原生验证转换方案、任意组件图、循环引用、版本回绕、所有实体分配顺序、持久文件格式、真实游戏或跨机器可移植性。没有因结果通过而扩大场景。
