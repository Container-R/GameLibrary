# Box2D传感区：独立实现及纯负例审查

2026-11-01。**接受最终冻结实现进入单独授权的构建阶段；没有剩余阻塞项。** 本次没有启动编译器、预处理器、Box2D、窗口或原生进程；没有执行run.py命令入口。全部进程相关测试使用mock，不能当作六步事件已被观察。

## 精确最终绑定

- CODE-MANIFEST.json：`996a1133f24d2826770719db605eb4f2f255c155ada6dc49aa9f7479746760d4`
- fixture.c：`3ed5674db919dcb12df6ecb3e25aa408367965612ea09401823f1e55cf7271e5`
- expected.json：`42db20a5ed693dff27b96789976d3db53661b28bb5fc8b4de2a67fc817f1e7c5`
- validate.py：`15a48c7c61c765906123260036aa5bb6b5ada69feff1fb483ca0df26a38c8e13`
- run.py：`4458c9380e378c1a0afe2653321415244c62aefea8c3a3427c1c6ad7b9a30acb`
- test_validate.py：`1f3106f0d4952b3b3709a0a53c4caa567ae2ed378784cdba6a79a955c327be33`
- 已接受协议：`b36c4cb9ecd5585dbd13a70eae1e432463b354a0d35e464f18316ea02f4f78ff`

完整读fixture、consumer、runner、作者纯测试、字面表生成器、完整编译argv和实现说明；检查314槽冻结表的结构与两配置六步事件/缓存/位置字面值。实际核对最终清单9项内容身份。另只读验证84项固定上游文件的SHA256、长度及Git blob，并核43个C文件的顺序与上游CMake一致；这是文件校验，不是预处理或构建。

## 真实getter、事件及几何

fixture使用官方Default定义后设置固定参数；ID先IsValid再调用进一步接口，visitor形状质量更新开启。minExtent、safetyFactor、质量、质心、awake/enabled、锁约束等实际读回，不用请求数据填充observed。仅无getter的字段明确为requested；步开始/返回、销毁返回和完成计数是控制流记录，不假称引擎getter。

geometry来自GetPolygon/GetCircle，固定四顶点、法线、半径与中心逐项记录并检查；transform/速度实际读取。投影、间隔由这些数据计算，consumer再次计算，不用缓存替代末端几何。默认单精度下b2WorldTransform为b2Transform别名，当前fixture声明与冻结的无DOUBLE_PRECISION构建一致；不据此支持双精度构建。

每步begin/end两个实际计数均先输出再判断，超出预期会在解引用数组前停止；正数指针检查非空后只复制许可范围内的一个事件。实际pair完整身份和有效性验证，cache capacity/data返回数另检。未填缓存槽不输出为有效ID。首错逐行flush并_Exit，不对不确定世界做清理；正常路径才销毁世界。数值非有限值记录为null后拒绝，先前完整观察仍保留；不将其冒充可继续计算的数字。

此行为范围仍只有两个世界、各三步，一次版本自报；第一配置首错不会进入第二配置。预期第一步begin、下一步end来自已审源码解释，不是本次运行事实。

## 字面consumer及身份链

expected.json被consumer内固定SHA约束；不能修改表后仅重生成代码清单使任意结果通过。严格键集、顺序、记录数、重复键、bool/int区别、非有限值、对象关联、真实几何重算均有拒绝路径。表由作者编写，正控制也是从作者冻结表展开；本审查不把这种生成方式伪称独立oracle作者。独立核对的六步字面结果及另设负例见下。

build只编译，execute另验已接受build receipt再执行；新目录排他创建，旧PASS不能替代新尝试。复制代码/源及复制产物在执行前核身份，consumer在动态导入前再核代码；结束后核原构建receipt/代码/源、原与复制产物及当前代码。只有最终receipt pass和所有后检完成才表示整次接受，validation保留consumer_only身份。没有自动从build跳到execute。

超时、通信错误、非零退出、诊断和构建stdout拒绝均进入拥有进程组的清理分支，包含leader已返回的情形。测试证明的是mock调用顺序和拒绝结果，不是操作系统中任意后代或逃逸进程都已被观察清除。普通接受进程的fixture源码不产生子进程；本单元不宣称通用恶意进程沙箱或无竞态身份防护。

## 发布前发现与修正过程

初次实读中间清单9dd3时，execute在复制产物后只核代码/源，直到运行后才核复制二进制。这不满足执行前产物绑定，本审查向主编提出修正。作者同时完成最终996a修订：运行前检查复制产物，导入consumer前检查代码，运行后补原构建receipt及源/代码检查。本审查实际读回最终行，并构造复制时改坏产物的纯反例，确认command未调用，问题闭合。此过程是执行前源码发现，不是构建或原生失败。

主编先前发现的“子进程已返回但因诊断拒绝时未清理组”也已进入统一首错分支，并有第13个作者mock方法；旧版/结果保存在history。作者最初-O失败属于mock设置与真实优化保护相冲突，记录仍保留；最终生产runner仍拒绝-O，不借修测试放宽保护。

## 本次实际纯测试

在该单元目录运行作者套件：

- `python -B -m unittest -v test_validate`：13方法通过。
- `python -B -O -m unittest -v test_validate`：同13方法通过。

独立追加 `independent/challenge.py`，SHA256 `c01d180a20c8862381146e89459de307b469e4e06e0e477af0fd91e0409cab6b`：

- `python -B independent/challenge.py`：7方法通过。
- `python -B -O independent/challenge.py`：同7方法通过。

独立方法覆盖：314槽及六步字面表/错误end与cache/错误事件标志和法线/越界ID；缺失、半截、重复输出；复制产物篡改在command前拒绝；更改consumer代码在导入前拒绝；消费成功后build receipt变动仍整次fail；真实84文件静态绑定、缺源拒绝与43文件argv顺序；失败build/旧尝试不得启动行为。独立脚本全局将真实Popen替换为失败保护，运行路径中的command也仅mock；没有真实子进程探针。

-O使用实际优化解释器，但runner工作流的sys.flags.optimize由纯mock代理模拟正常模式，专门优化拒绝方法仍验证生产保护；不能把这些工作流测试称为runner获准在-O下执行。

本次日志保留在 `independent/author-normal.txt`、`author-optimized.txt`、`challenge-normal.txt`、`challenge-optimized.txt`。模式重复不增加原生配置覆盖，也不是40个不同引擎案例。审查结束时单元没有attempts目录：真实构建0、原生进程0、世界步0。下一步仍需单独构建授权，构建结果接受后才能另行授权行为；原始本地收据/日志不自动获准公开。

## v2完整诊断例外：有限独立闭合

2026-11-01，接受最终v2代码清单 `bd4b97e9b3676378ccc00ebfa1927c75cbaf25f950ff8a33860c08ba33e03a8f`，协议 `c12f4e9b26747d8cf18d36b1e844cd3ea3a0ed4aeac9317ee6056c3f6fcff890`。本次只读差异并运行纯合成测试，没有第二次构建或行为。

与 `history/v1-before-reviewed-build-diagnostics` 逐字节比较，fixture、expected、consumer、完整编译argv、来源清单及字面表生成器均未变。run.py新增已审文件的固定hash约束、完整字节比较和构建诊断标记，不改变native分支的stderr必须为空要求。代码输入精确集增为10项，加原84来源为94项；实际核对10项身份。reviewed-build-stderr.txt与build-001原stderr逐字节一致，32,263字节，SHA256 `c55f639fa5da94fed9737ff07f07048c47386213d14fe39dbefaf75e281ff4b5`。

独立实际确认：可信文件在stderr为空时仍被读入并核硬编码hash；删除文件、变更文件或连同外层清单重新绑定错误文件仍不能通过。放行依据完整字节，不是warning类别或正则。退出非零、stdout非空、在native阶段出现同一份已审诊断仍拒绝；清理分支保持TERM/KILL。现有后检和consumer_only语义未放宽。

本次实际执行：作者15方法在normal/-O各通过；独立challenge扩充为9方法，在normal/-O各通过。新增独立反例覆盖缺可信文件、改变/截断/追加诊断、改“warning”为“error”、可信文件改后重绑清单仍拒绝，以及native错用例外、非零退出、非空stdout的拒绝和组清理调用。全部是mock；没有运行编译器或本机信号操作。

独立脚本最终SHA256 `14d27f497fb6476959d47e10d1b6c9471e0ce90e27db845c0e922d1fc3a3ed1b`，原7方法版本保留 `independent/challenge-v1.py`。新结果为 `independent/author-v2-normal.txt`、`author-v2-optimized.txt`、`challenge-v2-normal.txt`、`challenge-v2-optimized.txt`。模式重复不增加引擎案例覆盖。

实际读回build-001仍为fail，attempts中仅此旧目录。当前累计1次构建、0原生行为、0世界步；允许主编另行决定新的build-002授权，不自动启动，也不将构建例外当作行为授权。首构建诊断审查与原初实现审查事实均保留。
