# EnTT Link 字段保留：有限原生观察协议草案

2026-11-02。仅协议与预期 schema，**未授权实现、编译或执行**。一个条件：组件所属 holder 已映射，未经显式转换的 Link.target 是否仍保存来源箱子的完整值。不是新书；不继承已有无组件观察的结果或执行预算。

## 来源及一个待独立闭合的纠正

固定 EnTT v3.13.2 commit `78213075654a688e9da6bc49f7f873d25c26d12c`。已读来源门槛与 GATE-REVIEW（原 SHA `be97a7c2146deda833b8dd71c24be55449a8b3f3e083981bd95d2e2f906e28bc`）。

- [snapshot.hpp L78–110](https://github.com/skypjack/entt/blob/78213075654a688e9da6bc49f7f873d25c26d12c/src/entt/entity/snapshot.hpp#L78-L110)：官方 writer。
- [同文件 L366–415](https://github.com/skypjack/entt/blob/78213075654a688e9da6bc49f7f873d25c26d12c/src/entt/entity/snapshot.hpp#L366-L415)：实体先恢复、普通组件 archive(elem) 后存到映射 owner。
- [官方测试 L757–807](https://github.com/skypjack/entt/blob/78213075654a688e9da6bc49f7f873d25c26d12c/test/entt/entity/snapshot.cpp#L757-L807)：在自定义 archive 内主动 map target 的正向源例；此次不执行该转换。

**执行前来源纠正（主编与独立修订记录均已确认）**：原 gate review 写 writer 一次 archive 接收 owner+component，不能作为本固定实现前提。L102 的 fold expression 对 tuple 各项分别调用单参数 archive；官方 writer 测试 L102 的 lambda 也只有一个参数。固定单头同式在 L39284。此协议以真实代码为准：本普通非空 Link 条件有 entity 归档4个逻辑 token、Link 归档3个逻辑 token；按该路径也是分别4/3次单参数 archive 调用。不把 std::apply 的 tuple 展开本身误称 archive 的双参数调用。主编 MAIN-CORRECTION.md 已明确接受此纠正（SHA256 5f0d7af12d8e9996487341be8aa23f83697ec3cebb42731e63f66db8bb032415）；纠正版 GATE-REVIEW-v2.md（SHA256 3a87f6d6a87fffa1c309c2e20ee6e61de570ae8edc05189c6c883fdd063bf910）也确认单参数折叠；原错误报告保留。仍须独立协议审查及 oracle 冻结后才可实现。

## 唯一条件

默认 entt::entity/registry，单线程，无自定义 traits、allocator、hint、销毁、signals 或 hooks。Link 是仅含 `entt::entity target` 的简单值聚合，不定义有副作用构造/复制/移动。来源普通创建 remote_box，再创建 remote_holder，仅 remote_holder 持有 Link{remote_box}。目标只预置一个 local_seed；loader 绑定目标且只解释此来源。

使用官方 snapshot writer 按 entity、Link 次序生成两个分开的有类型内存流。输出 archive 的明确单参重载分别处理 uint32/entity/Link，按值保存；不允许隐式万能转换掩盖类型。Link token 的值只保存真实 target。输入 archive 每次只接受单参数引用，先检查游标/类型再复制；读取 Link 时另外记录所读 target，不调用 map 改字段。归档不是磁盘存档、网络序列化或跨版本格式。

观察 full/index/version，不预设具体分配整数。完整句柄等值比较必须保留所属 registry 语义；对 remote_box 的目标 valid 只作技术观察，不对其执行组件 get 或业务动作。

## 阶段与首错停止

1. 来源与目标建立后，检查来源两实体有效且不同、source holder 的 Link 存在，才读取源字段；源字段必须等于 remote_box。官方 writer 保存两个流，核 entity4/Link3的类型/边界及真实字段。输出 declaration、七 token 与 prepared 阶段。
2. 仅消费 entity 流，loader.get<entity> 后输出 entities_loaded 阶段。核两个 map 非空、目标有效、彼此不同且都不等 seed；**mapped_box != remote_box** 必须成立，否则停止为无区分力，不能继续组件读取或临时增加 seed。检查 seed/来源仍有效、目标活跃数3、目标 Link 数0、消费数 entity4/Link0。
3. 用新单参输入 archive 消费 Link 流。确认 mapped_holder 仍有效且有 Link 后才 get 该组件，捕获最终字段，再输出 component_loaded。核 source target、归档 target、输入读取 target、最终 target 全等于 remote_box，最终 target != mapped_box。映射、来源/seed保持不变，目标活跃数3、Link数1，entity4/Link3完全消费。

每阶段输出的是实际捕获值，随后立即显式验证；偏离不进入下一阶段。若安全 get 的前置条件失败，仅保留已有输出及安全失败状态，不调用 get 以凑完整行。独立 checker 必须拒绝不完整输出，不能依赖 fixture 自报 PASS。无 assert 作为唯一成功门槛。

## 记录与字面预期

完整成功输出固定11行 JSONL：1声明、7token、3stage，具体字段和关系见 EXPECTED-SCHEMA.md。输出UTF-8/LF，无多余行、重复key、NaN、bool伪整数。独立 reviewer 应在实现前另写字面 oracle；本文件和 schema 是作者提案，不是独立 oracle。reader/fixture不得从运行输出倒写预期。

只有最终 loaded_target_in_local_valid 和 loaded_target_equals_seed 是描述性布尔值，不指定其真假；不将它们当“正确对象”的证明。完整数值与既有跨记录等值关系仍须自洽；最终目标仅有 seed、mapped_box、mapped_holder 三个活跃实体，因此 loaded_target_in_local_valid 必须等于 loaded_target 完整句柄是否属于这三个值的集合，不预设分配整数。不同条件或显式字段转换不偷偷加入本次。

## 拟定执行边界（尚未授权）

固定单头和许可证可用现有公开来源字节；约3.1MB header 的 SHA256 `31be51708c7325ecb7877182fa9ee68a20fb2121ce6bcd6c1687506f0fb1c8b5`、Git blob `b3a763a203cb7c2acc467de1dc97920562721989`。不安装，不引入 GoogleTest，不联网运行。后续代码阶段才复用已审 v3 五键 helper/生命周期逻辑并创建新的输入身份，不能沿用旧清单或结果。

预注册最多两个新副本，各一次构建、一次 native；相同源码、命令、条件，首错停止，无自动重试。拟定构建 `c++ -std=c++17 -O0 -g0 -Wall -Wextra -Wpedantic -Werror -I source fixture.cpp -o out/fixture`，120秒；执行 `./out/fixture`，10秒。编译返回0且stdout/stderr空才允许native；native非零、超时、诊断、schema/关系错误均停止，保留真实首错。编译器内部子进程不计成“只有四个系统进程”。

build/native各自拥有新的phase根，prepare五个真实目录 HOME/XDG_CACHE_HOME/XDG_CONFIG_HOME/XDG_DATA_HOME/TMPDIR，紧邻Popen前再次validate；不记录实际映射。根准备及部分失败清理、进程组有限收尾、总输出根证据保留分别处理。已存在根拒绝，不删除非拥有目录；清理异常不覆盖首错，进程清理不确定时保留phase根。五键检查非sandbox，不认证所有写入、所有后代或网络隔离。

源、fixture、协议、schema、独立oracle、checker、runner/helper和测试均须预冻结，新manifest前后核对；各副本源和产物前后本地绑定。总体PASS仅两次完整内容检查和全部后置绑定后发布；pending回执正常关闭后同目录原子命名，非断电持久性证明。公开资料不输出安装/构建产物指纹、实际路径、进程身份或原私有回执整体身份。

v2旧两次和v3旧两次均不是组件结果。即使此次未来观察符合预期，也只证明这个普通 Link、这个按值 archive 与固定版本的一条路径；不能证明全部引用图、转换 callback、网络或存档迁移正确，不能宣称实际打开了错误箱子。
