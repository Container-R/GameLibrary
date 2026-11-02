# EnTT continuous_loader：映射存在与当前有效性的原生观察协议 v3

2026-11-02。**仅供源码、夹具与独立字面预期审查，不授权编译或执行。** 不是 reader 正文；尚无原生结果。后续须先冻结夹具、检查器、独立预期与最终协议，再由主编明确授权执行。

## 问题与已读来源

完整读当前《实体句柄什么时候能保存，什么时候需要映射》及既有 ecs-entity-identity-source-gate 的 GATE、SOURCE-REVIEW、MAIN-SOURCE-CHECK。正文已明确：map 返回已保存的本地句柄不再次调用 registry.valid；restore 在重新加载时才可能重建已失效的本地对应。因此不新增理论，只观察固定实现的一条有限生命周期。

重新直接读固定 EnTT v3.13.2 commit `78213075654a688e9da6bc49f7f873d25c26d12c` 的 [snapshot.hpp 全文](https://github.com/skypjack/entt/blob/78213075654a688e9da6bc49f7f873d25c26d12c/src/entt/entity/snapshot.hpp)：writer 78–109，continuous restore 277–285、entity get 366–395、contains/map 434–455。已有 registry/entity/storage 源链定位保留于前述来源门槛。本协议不靠组件 get 注释声称引用重映射。

## 依赖与源码可用性

在本工作区及共享工作区定向寻找 entt.hpp / entt/entity/snapshot.hpp 未找到已有副本；不是全机器软件盘点。通过官方仓库只读接口取得该提交的 `single_include/entt/entt.hpp` 和 LICENSE，保存在本草案的 source 子目录。

- 官方单头大小：3,085,766 bytes。
- 官方 tree API Git blob：`b3a763a203cb7c2acc467de1dc97920562721989`。
- 本地源文件 SHA256：`31be51708c7325ecb7877182fa9ee68a20fb2121ce6bcd6c1687506f0fb1c8b5`。
- 文本保存初次多加一个末尾换行，已在运行前去掉，随后按 Git blob 计算精确匹配上游大小与对象值；不是修改实现。
- 固定 CMakeLists.txt 第110行声明 cxx_std_17。此次无需运行CMake、项目测试、下载第三方依赖或安装包。单头在普通非Android目标只需C++标准库；条件Android系统头不适用本拟定环境。
- 只检查了现有 C++ 编译器命令可解析，没有执行编译器或查询其版本。是否真正可构建仍未知，不能以源码取得成功替代构建结果。

依赖规模为一个约3.1MB官方单头、一份许可证、待审原创小夹具及标准库。源码不属于字体/游戏资产，不取得任何项目存档、账号或网络数据。候选公开材料不得带安装路径、安装二进制指纹或执行尝试身份。

## 唯一条件与变量含义

单线程、默认 entt::entity / entt::registry，无自定义traits/allocator、hint创建、显式版本销毁、并发、组件、网络或文件存档。

- `remote_registry`：来源注册表。普通create一次得到 `remote_entity`。全流程不销毁来源实体。
- `local_registry`：独立目标注册表。先普通create一个 `local_seed`，保证目标非空；全流程不销毁该seed。
- `loader`：始终是绑定该目标、解释同一来源的一个 continuous_loader。
- `mapped_initial`：第一次加载后保存的完整本地句柄；**它不是远端句柄，也不是裸索引**。
- `mapped_now`：每阶段重新调用 loader.map(remote_entity) 的返回值。

不预设真实实体整数恰好是7或任何业务身份。输出完整标识的无符号整数、to_entity、to_version仅用于核对同次记录关系；这些都是夹具创建的技术数值，不是对象永久ID或权限。

## 固定步骤与纸面预期

1. 创建上述两个registry、来源实体和目标seed；构造loader。
2. 用官方 `entt::snapshot{remote_registry}.get<entt::entity>(output_archive)` 得到内存归档。输出归档只接受明确类型 uint32 与 entt::entity，分别记录标签和值；不把枚举与计数混成一个无类型数组。按源码预计归档恰为计数1、活跃计数1、来源实体三个token。归档类型/次数任何偏差停止，不从结果修改预期。
3. 输出阶段 `before_load`；map尚未知。
4. 用只读游标从头消费该归档，执行 `loader.get<entt::entity>(input_archive)`。类型与长度精确检查、必须无未消费项。保存 mapped_initial，输出 `loaded`。
5. 前置检查 mapped_initial 有效且不是seed，再由普通 `local_registry.destroy(mapped_initial)` 模拟外部逻辑删除。**不通知loader、不重建loader、不先get再map**。输出 `externally_destroyed`。
6. 用新游标从头读取完全相同归档，再get一次，输出 `reloaded`。不创建任何其他实体、不调用orphans。

| 阶段 | loader.contains(remote_entity) | map非null | local_registry.valid(mapped_now) | 目标活跃数 | 来源实体/seed仍有效 |
|---|---|---|---|---|---|
| before_load | false | false | false | 1 | true / true |
| loaded | true | true | true | 2 | true / true |
| externally_destroyed | true | true | false | 1 | true / true |
| reloaded | true | true | true | 2 | true / true |

额外字面关系：destroyed阶段的mapped_now等于mapped_initial；reload阶段mapped_now不等于mapped_initial，旧mapped_initial仍invalid。仅 before_load 尚无 mapped_initial，使用明确null；从 loaded 起记录已保存的完整 mapped_initial 及其当前有效性，不能用0伪装不存在。loader.contains表示保存来源映射，不是当前本地有效性。

活跃数以实体storage.free_list()记录，不把storage.size()（可能包含非活跃槽）当活跃数。每次map返回值的当前有效性由目标registry查，不误查来源registry。独立预期应冻结以上行和关系，不导入夹具的判定代码；不得从运行输出倒写oracle。

## 拟定命令与两次重复

执行工作副本均只有固定source/entt.hpp、LICENSE、待审fixture.cpp、空out目录；两副本输入字节相同。以下是未来授权后的预注册argv，不在本阶段运行：

```text
c++ -std=c++17 -O0 -g0 -Wall -Wextra -Wpedantic -Werror -I source fixture.cpp -o out/fixture
./out/fixture
```

每副本一次编译（上限120秒）、仅编译门通过后一次fixture（上限10秒）。重复为另建副本按同一argv、相同配置再做一次，不改优化级别、不加新场景。不执行编译器版本子命令、CMake、原项目测试、探测型试编译、性能测试或网络程序。两次重复最多两个编译器入口及两个fixture入口；编译器可能调用内部工具，不谎称操作系统总进程只有四个。

本 v3 runner 的五键准备、临启动验证和生命周期责任以末节为准。环境从 PATH 与固定 locale 的最小字典开始，不继承 CXXFLAGS/CPATH 等变量。执行阶段无网络需求，runner不调用网络；若不能实际隔离网络，不声称拥有网络沙箱，只说明夹具和流程不进行网络操作。私有工作路径仅执行者本地使用，不进入公开支持说明。

## 观察、检查和停止门槛

- 编译返回0、没有警告/诊断且无超时才准运行；首次警告也停止，保留完整失败，不能悄悄去掉Werror重试。若需调整，应先独立审源码/诊断并开新版协议。
- fixture不依赖assert判定观察结果；显式检查归档类型、界限、必要前提和输出错误，任何失败非零退出。不得因为release禁用assert就被误判通过；本固定命令不定义NDEBUG。
- 正常输出只允许一个声明行、精确三个归档token和上述四阶段记录；schema、整数域、bool类型、字段集合和顺序固定。实际完整字段名见下方固定schema，不留下任意额外字段。
- 检查器验证每个阶段字面预期及跨阶段句柄关系、归档完全消费、退出码、stderr、超时。两个成功副本比较相同技术观测字段；不将构建差异或命令身份当行为证据。
- source、fixture、协议、oracle、checker输入在前后核字节；产物摘要仅关联本次产物，不推官方二进制认证。保留原stdout/stderr及停止记录；公开投影保留技术失败/次数但不复制安装路径、PID或尝试标识。
- 首个前提、构建、运行或检查失败即停，不继续第二副本、不加场景补结果。没有“尽量跑到成功”的重试预算。

## 能说明与不能说明

若按预期观察，可给现有源码解释增加同环境有限原生依据：已有map非空和contains为真，可以与当前目标invalid并存；重新加载相同来源实体的restore会建立有效对应。不是EnTT故障，不证明所有调用者都安全，也不是所有版本/编译器结果。

这不是snapshot_loader恢复测试、组件字段引用迁移、版本绕回、跨机器复现、事务异常保证或网络同步测试。归档是夹具内存typed stream，不是自描述或可跨版本的产品存档。保存map之后业务是否允许打开箱子仍未测试。正文保留原源码范围，不能把本项运行升级为整篇ECS结论验证。

当前停止：v0保留；已根据独立PROTOCOL-REVIEW修正initial语义并实现待审fixture/runner/checker。只做Python语法静态检查，未编译或运行C++，未生成模拟原生结果。须代码独立接受及主编明确授权，才可执行。

## v1 固定输出 schema 与原语义修正

v0原始SHA256为 a3fefc5e87d617dc6db834cc7021537402d545a47bb205e7d1b0b77903f71e2c，原稿保留为PROTOCOL-v0.md。独立PROTOCOL-REVIEW.md的四阶段字面表是independent-oracle.json的来源，未用程序输出生成预期。此次纠正loaded阶段initial应存在，不遮盖原草案歧义。

输出为UTF-8 JSON Lines，恰好8行，每行一个对象，LF结尾，无额外空行。字段按以下顺序；拒绝重复key、非有限值、额外字段和bool伪整数。

1. declaration：kind、schema、cplusplus、gcc、clang、entt、entity_mask、version_mask。kind固定declaration；schema整数1；cplusplus为编译宏值且至少201703；gcc/clang分别为存在时三个非负整数宏或null，作为技术描述不锁死本机版本；entt固定[3,13,2]，掩码1048575/4095。不得输出__FILE__、自由字符串版本、安装位置或指纹。
2. 三条token：kind、index、type、value。kind固定token；index依次0/1/2；type依次uint32/uint32/entity；前两value为1，第三为source.full。
3. 四条stage：kind、stage、source、seed、mapped_now、mapped_initial、contains、mapped_nonnull、mapped_valid、active_count、initial_valid、source_valid、seed_valid、input_consumed。阶段及字面结果逐项采用独立表。source/seed/mapped_now均为含full、index、version的对象；完整值限uint32，index=full低20位、version=full右移20位。实际entt::null仍输出其完整值4294967295及拆分；仅未赋值的mapped_initial用JSON null。input_consumed仅loaded/reloaded为3，其余null。

两次原始8行数据按严格JSON类型逐项一致比较，包括描述性编译宏；这不说明另一台机器也应同编译器版本。消费者从原始记录核关系，不接受fixture自报passed。

本次输入manifest冻结v3协议、fixture、runner、checker、独立oracle、原独立协议审查、官方单头及LICENSE、原清理测试、新环境测试和未改字节的isolation helper，逐文件SHA256。manifest自身在执行前后另行绑定，避免自哈希循环。原生输出文件不属于输入manifest。

runner拒绝任何已有输出路径；每次只有repeat-1/repeat-2新工作副本，各自固定编译和fixture调用。编译器入口PATH使用系统标准命令搜索路径，环境保留PATH、C locale及每阶段新拥有目录下的五键；不沿用用户编译标志。所有记录中只存相对argv和副本标签，技术宏并非官方工具链来源认证。

发生首错后，保留已生成原始流，记录首错类别并尽力收集输入后置摘要；后置收集错误不覆盖首错。超时终止拥有的进程组并有限等待。receipt只在流程结束写入，且整体PASS必须两次构建/运行/内容与复制输入、原输入、产物的后置检查均通过。失败时不能存在整体PASS；局部content_check不代表整体接受。无自动重试。

公开支持包不复制约3MB官方单头全文；提供固定上游地址、大小、Git blob与SHA256、许可证定位，加原创代码/预期/安全输出和有限结果即可。公开材料整理需另审，不自动发布任意原始诊断。

## v2 执行前停止与清理修正

独立CODE-REVIEW发现v1两处不足：leader已退出时跳过进程组清理，以及fixture仅输出部分阶段而未即时拒绝偏离。完整v1输入与manifest保留history/v1，未运行该版本，原发现不删除。v2不改成功8行schema、官方源、场景、字面oracle或2次同条件限制。

runner将等待、退出码/诊断/长度及文件读取拒绝统一置于清理边界内。已创建进程组无论leader是否退出，都尝试SIGKILL并有限等待leader；组不存在是正常结束，清理异常单独记录，不覆盖已存在首错。成功返回前也收尾拥有的组，使后续内容检查失败时不遗留尚未处理的拥有组；若该成功路径清理失败则整体拒绝。此处没有用leader.poll推断组存活，也不声称已观察到所有后代终止或全部网络系统调用。

fixture每阶段先捕获实际观察、输出并flush，再显式核字面条件和已知关系；任何偏离抛出受控错误并停止，不能进入下一get。loaded的initial依然是真实map结果，失败也可看到该前缀；观察值不以预期常量替代。独立checker保持字节不变，仍从完整原始结果单独检查。

纯Python test_runner_cleanup.py有7个进程控制mock方法，普通/优化模式均通过；Popen与killpg全部替换，未创建子进程或发真实信号。覆盖leader先退出而返回非零、非空诊断、清理信号失败、清理等待失败、超时且组已不存在、成功时组已不存在、成功路径清理失败。它们不是EnTT原生结果，不增加原生场景。test文件纳入v2输入manifest；纯测试文本输出单独保留，不充当native.stdout。

本阶段仍未调用编译器或fixture。仅待另一审查者核差分、mock与新输入绑定后，主编才可决定是否执行既定两次流程。

执行前主编另发现v1正式receipt直接写入可留下可解析PASS前缀。v2改为同目录receipt.pending.json写入并正常关闭后，最后原子改名为receipt.json；pending明确非权威结果，写/close失败不会产生正式receipt。失败stderr保留首错及写入失败信息。此为正常操作发布顺序，不是断电持久性保证。新增3个纯Python发布测试：写入可解析前缀后失败、close失败、正常close后发布；连同7个清理mock共10方法，两模式通过。原生场景仍不变。

## v3：新的环境流程修复候选（尚未执行）

v2 的真实两次构建、两次原生观察及其全部冻结文件保留原样。它当时仅设置 TMPDIR 和干净 PATH/locale，没有按当时现行规范显式准备 HOME、XDG_CACHE_HOME、XDG_CONFIG_HOME、XDG_DATA_HOME，属于流程不符合，不能用其既有 PASS 取消这项事实。v3 不是重标旧记录，也没有新原生结果；若将来获准执行，须单独计最多两个新构建和两个新原生入口，首错停止，场景及成功八行完全不变。

实际读当前《研究与发表规范》五键段、工具 evidence/isolation.py 全文与 runner-environment-contract 来源笔记全文。isolation.py 原字节复制进本目录并纳入新输入绑定，不修改其接口或扩大承诺。

每个 repeat 下，build 和 native 分别创建新 environment-build / environment-native 目录。该调用成功 mkdir 后才标记自己拥有根；已有路径拒绝且绝不删除。prepare_environment 从最小环境准备五个实际子目录；返回的映射仅在内存使用，不写入回执。打开输出流后、Popen 之前再次 validate_environment，重定向值、缺目录或符号链接导致拒绝，不启动本阶段进程。

根目录管理、部分创建清理、进程组生命周期是三件事。准备中途失败由本 runner 删除自己新建的 phase 根；删除失败单独标记，不覆盖准备首错。进程已创建后，沿用已审有限组信号/leader wait；清理失败保留 phase 根，不能在已知清理不确定时删除。记录只保存 PREPARED/VALIDATED_BEFORE_LAUNCH 和清理状态标签，不保存实际五键路径。没有进程或组清理返回成功时再删除 phase 根；删除失败在无既有首错时拒绝本阶段，有首错时保留首错。调用总根保留原流、回执及副本，直到执行者另外完成记录归档；不是自动删除证据。

helper 检查的是当下选定位置，不认证目录所有权，不消除 validate 与 launch 间竞态，不是文件系统/网络沙箱，不证明所有后代终止。沿用组信号成功加 leader 回收的有限清理门槛，不冒称对任意脱离进程组的子孙具有完整控制。其他写入位置及进程权限仍不在此五键检查内。

纯 Python 检查由原10方法加新8方法构成，普通和优化模式各18通过；所有 Popen、killpg 都被 mock，没有创建子进程或发真实信号。新方法核五目录在 launch 时实际存在、改值/缺目录/symlink 拒绝、部分创建失败清理、清理失败保首错、已有根不删除、进程清理失败保留根。真实临时目录只用于这些合成文件系统检查。它们不是 C++ 构建或 EnTT 结果。下一步必须独立审查协议/完整差分/测试与输入身份，再由主编另行授权；现在不得执行 runner。
