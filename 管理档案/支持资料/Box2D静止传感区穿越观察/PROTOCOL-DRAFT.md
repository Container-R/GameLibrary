# Box2D 3.2.0 静止 sensor 穿越：执行前协议草案

2026-11-01。**仅协议和实现计划，本协议作者未取得源码bulk、未实现fixture、未构建或调用引擎；主编另行进行的源码取得进度不冒充这里的执行结果。** 独立事件oracle源审须完成并与本协议共同冻结后，才可另行授权实现；构建和行为执行还须各自授权。

绑定已有gate SHA256 `146600e1fb559f805bb7df604eb1a75bb1bfb40c35a730cd110425ecd3405a2f`。固定仓库erincatto/box2d，提交 `178495ba35695aefe9c321e569d2277f06db3b90`，源码项目3.2.0。不测试3.1.1，不借任何既有原生档案扩大本次范围。

## 1. 一个问题、两个新世界

目的：在一个静止传感区及单一高速实心圆形visitor的固定输入中，观察步后begin/end、visitor事件开关，以及缓存overlap与末端几何位置的不同含义。

一个原生进程，按顺序创建、完成、销毁两个彼此独立的新世界：`events_on`，然后`visitor_events_off`。两者各恰好3次世界步；第一世界/任一步不满足预设门槛立即停止，不能继续收集另一组以掩盖失败。正常共2世界、6步，不预热、不追加探测步、不改变速度或geometry寻求通过。

同一进程仅调用一次b2GetVersion记录自报3.2.0，不另开版本/能力探针。自报不是源码构建真实性认证，后者另由源码/构建身份绑定。

## 2. 固定输入：必须用官方默认定义，再显式改字段

禁止用全零手造WorldDef/BodyDef/ShapeDef。分别调用b2DefaultWorldDef、b2DefaultBodyDef、b2DefaultShapeDef取得完整合法定义，保持内部标记；以下字段显式赋值：

- 世界gravity=(0,0)，enableContinuous=true，enableSleep=false，maximumLinearSpeed=512，workerCount=1；enqueueTask/finishTask/userTaskContext=NULL。不设置custom filter/preSolve，不安装第三方调度器。全新进程保留默认长度尺度1，不调用b2SetLengthUnitsPerMeter或改变allocator/assert等全局配置；只在版本记录及两个world setup读取b2GetLengthUnitsPerMeter并要求精确1。
- sensor body：static，position=(0,0)，rotation=(c=1,s=0)。唯一polygon由b2MakeBox(0.125,1)构造，radius=0。shape.isSensor=true，enableSensorEvents=true，filter.categoryBits=1、maskBits=1、groupIndex=0；density=1、updateBodyMass=true。创建后不得再变换或修改形状。
- visitor body：dynamic，position=(-2,0)，rotation=(1,0)，linearVelocity=(256,0)，angularVelocity=0，linearDamping=angularDamping=0，gravityScale=1，enableSleep=false、isAwake=true、isEnabled=true、isBullet=false、safetyFactor=0.5；motionLocks的linearX/linearY/angularZ均false。
- visitor唯一circle局部center=(0,0)，radius=0.25；isSensor=false，density=1，updateBodyMass=true；相同filter(1,1,0)。enableSensorEvents在第一世界true、第二世界false。双方enableCustomFiltering/contactEvents/hitEvents/preSolveEvents均false；其余无关默认字段不凭空另改。
- shape.updateBodyMass必须明确为true。创建形状之后，实际body minExtent必须0.25、safetyFactor必须0.5、质量必须有限且正；否则在Step之前拒绝。不允许dirty/default extent破坏fast判据，再用“端点对了”代替前提。
- 每一步只有 `b2World_Step(world, 0.015625f, 1)`；dt=1/64，subStepCount=1。三步之后正常销毁整个世界，不读取销毁产生的额外事件，也不将其计入第二世界。

构造成功后才读getter；先核ID有效，再传入进一步接口。没有用户资产、实体障碍、关节、附加body/shape或窗口。两个世界的请求配置仅visitor事件标志不同；ID或分配代次的不同不算另一个配置。

## 3. 请求记录与真实读回分层

本轮独立打开固定 `include/box2d/box2d.h`、types.h、id.h、math_types.h、base.h及src/CMakeLists全文/相关声明，以下API确实存在。实现不得把request JSON复制到observed分支：

| 对象 | 实际getter及接收条件 |
|---|---|
| world | IsValid；GetGravity=(0,0)、IsContinuousEnabled=true、IsSleepingEnabled=false、GetMaxLinearSpeed=512、GetWorkerCount=1 |
| sensor body | IsValid、GetType=static、GetTransform位置(0,0)/单位旋转、GetShapeCount=1、GetShapes返回实际sensor ID |
| visitor body | IsValid、GetType=dynamic、GetTransform、GetLinearVelocity、GetAngularVelocity、GetLinearDamping=0、GetAngularDamping=0、GetGravityScale=1、IsSleepingEnabled=false、IsAwake=true、IsEnabled=true、IsBullet=false、GetSafetyFactor=.5、GetMotionLocks全false、GetMinExtent=.25、GetMass有限正、GetLocalCenter=(0,0)、GetWorldCenter与实际body位置对应、GetShapeCount=1/GetShapes实际visitor ID |
| 两shape | IsValid、GetType（polygon/circle）、GetBody/GetWorld归属、IsSensor真/假、AreSensorEventsEnabled对应两配置、GetFilter=(1,1,0)、GetDensity=1；AreContactEventsEnabled/AreHitEventsEnabled/ArePreSolveEventsEnabled=false |
| geometry | GetPolygon实际count=4、全部vertices/normals/centroid/radius；GetCircle实际center/radius。polygon顶点集合须精确为(±.125,±1)、无重复，radius0；不从请求box尺寸冒充getter |

没有公开getter可确认的task函数指针、shape.updateBodyMass、custom callback未安装等，只在`requested`记录并由冻结fixture代码审查支持，标为request-only；不输出实际指针值。用GetMinExtent/GetMass观察质量更新相关后果，但不把这些结果称为一般质量计算验证。

创建后、每次Step后都记录两个body的实际transform及visitor速度/角速度；每步读回visitor minExtent、safetyFactor、bullet和shape事件标志，sensor姿态必须仍固定。静态参数的完整初始读回只需一次，不以每步重复所有setter制造覆盖。

## 4. 与sensor缓存独立的端点分离

每世界初始及步后，用**getter读回**的polygon局部vertices、sensor world transform，以及circle局部center/radius、visitor world transform独立算几何。

将实际polygon全部顶点变到世界坐标，取xmin/xmax；将实际circle中心变到世界坐标，其x投影为[cx−r,cx+r]。初始要求circle右界小于polygon xmin；三个末端要求circle左界大于polygon xmax；实际间隔均须>1世界单位。分离投影是本例充分条件，不需要调用sensor overlap cache，也不是一般多形状碰撞算法。名义初始与第一末端间隔为1.625。

把原始geometry/transform保留给独立consumer重新计算，不能仅消费fixture输出的`separated=true`。姿态门槛单位旋转、y≈0已另行检查；即使不用axis-aligned假设，旋转后的多边形顶点投影分离仍足以证明这两形状端点分离。

初始x=-2，步后x=2/6/10；各步y=0，rotation=(1,0)，velocity=(256,0)，angularVelocity=0。对这些**运动读回值**冻结绝对误差≤1e−5、无相对误差。该数只属本有限验收，不是引擎精度承诺。所有值先拒绝NaN/Inf。setup中的dyadic几何/标志/配置值精确比较；不靠容差把错误配置放行。

每步实际dx还须>当前minExtent×safetyFactor=.125，以实际速度、步长与位移支持fast输入前提；不把这一检查当作内部fast标志的getter。几何端点分离也不证明中间真实轨迹或精确TOI；源码对本配置的连续路径解释与实际事件观察分开表述。

## 5. 步后事件、缓存与字面oracle

每次Step返回后立刻调用GetSensorEvents，先记录beginCount/endCount，范围必须各为0或1。正数对应指针必须有效；不满足时保留实际count并停止，不截断成“只有一个”。在下一Step或Destroy之前复制全部许可范围内pair，记录真实sensorShapeId和visitorShapeId并核IsValid，必须匹配本世界创建的两个shape。

ID记录结构字段index1/world0/generation，整数精确类型/范围，比较三字段而非只index。ID是库对象句柄，不是地址、私有执行标识或持久业务ID。不要求销毁后新世界使用完全不同数字，不跨世界比较已销毁句柄。

同时调用sensor的GetSensorCapacity，必须0或1；以容量1的实际数组调用GetSensorData，记录返回数量和实际填入的ID，未填槽不假装有效。此调用读取刚完成世界步留下的 sensor 集合，不进行独立末端几何求交。若capacity或returned count超限，停止而非静默截断。初始不读取事件/cache作额外行为探针，只以几何与对象读回确认起点。

| world | step | begin/end | pair身份 | sensor cache capacity/data count |
|---|---:|---|---|---|
| events_on | 1 | 1/0 | begin为本sensor/visitor | 1/1，visitor |
| events_on | 2 | 0/1 | end为同pair | 0/0 |
| events_on | 3 | 0/0 | 空 | 0/0 |
| visitor_events_off | 1/2/3 | 每步0/0 | 空 | 每步0/0 |

以上是执行前源推导，已由独立SOURCE-REVIEW（SHA d7c87d213e482cd53ccd10e39dc2ba5a1a57651b795823ed383c9dba3bbf8f02）确认，包括可选cache数量；不是观察结果。穿越hit先进入本步sensor集合，下一步集合差分才有end；本协议不要求同一步一对begin/end，不读取内部TOI fraction，不推断即时回调顺序。不在运行后更改表来匹配结果。

## 6. 原源码精确取得规范（84文件已取得，过程与复现要求保留）

使用主编已冻结 `box2d-sensor-native-gate/SOURCE-EXPECTED.json`，SHA256 `80d1c1bc0f578b9039c3747e1a2eb0c573b67415c9929db398367cdd216ce986`：84路径、43 C、总1,466,283原字节、固定Git blob。

本轮独立从src/CMakeLists抽读得到BOX2D_SOURCE_FILES=72项（43.c、27.h、2.inl），BOX2D_API_FILES=9个公开头，合计81构建文件；另外根CMakeLists、src/CMakeLists和LICENSE为3项出处/许可文件，总84。只按此显式集合取得原文本，不glob不增例程、测试、benchmark、Tracy或依赖。CMake文件只读取不运行，禁用PROFILE和SIMD，不触发FetchContent。

取得过程及未来复现须对每条固定path/ref保留原字节，核路径唯一/根内/无符号链接和预定byte length，并对 `ASCII("blob " + 十进制原始字节长度) || 单个0x00字节 || 原始文件字节` 求 SHA-1，结果必须等于已知 Git blob SHA；同时生成SHA256清单。取得不完整、编码/换行变化、版本不符均停，不自动切分支或下载整个包。许可原样保留，本协议不授权向公众重分发源码bulk。

取得后的SOURCE-MANIFEST保留84条真实SHA/blob/length，构建只显式使用原43 C及原header/inl。独立复查清单后才冻结fixture/consumer/oracle身份；不得从原生输出生成golden。81构建输入与3出处文件角色分开，不谎称LICENSE被编译。

## 7. 分离构建与执行，不沿用旧项目路径

计划采用本单元自己的两个显式命令模式，不自动build后执行：

1. `build`：创建全新只允许一次使用的构建尝试目录，先核84源及原始fixture/consumer/oracle/protocol/runner清单；复制后再核同一身份。单次编译上限120秒。没有任何Box2D行为调用。
2. `execute`：必须获得主编单独授权，输入一个已接受构建的receipt，创建独立全新执行目录。验证该receipt的接受状态、源/输入和生成可执行文件身份；再单次运行上限20秒。版本自报在这一个行为进程内，最多两世界六Step。

拟定编译参数：`cc -std=gnu17 -O0 -ffp-contract=off -DBOX2D_DISABLE_SIMD -DBOX2D_VALIDATE -Wall -Wextra -Iupstream/include -Iupstream/src fixture.c` 加官方显式43 C列表，末尾 `-lm -pthread -o sensor_fixture`。顺序按CMake表，不自行筛掉未直接调用单元；最终完整argv在实现前列明。无NDEBUG、fast-math、PROFILE、DOUBLE_PRECISION、SIMD扩展或第三方runtime。本协议不再请求compiler --version/help探针。主编已单独取得一次自报cc (Debian 14.2.0-19) 14.2.0，可作为技术版本记录，不是二进制来源认证；安装二进制身份不属于公众衍生资料。

v1构建门槛为退出0且stdout/stderr均空；首次构建因诊断按此门槛停止。v2仅增加文末独立审查的完整stderr字节例外，stdout仍须空；其他任何诊断保留并停止，不改旗标、不复用旧项目allowlist。行为必须正常退出0、stderr空、完整结构/全部oracle/源输入后检通过。超时及启动后错误清理拥有的整个进程组，保留首错、已输出记录和实际退出；不因leader已退出就忽略后代。此为有限runner责任，不声称全系统进程审计或网络隔离。

构建产物hash只在本地receipt做artifact绑定，执行前后比对；不发布安装编译器/库二进制指纹、机器绝对路径或原始私有执行日志。公众后续候选仅相对命令、公开源/原创fixture输入身份、有限结果和范围；本协议阶段不发布任何东西。

## 8. 观察、consumer与失败保留实现计划

建议fixture输出逐条JSONL并flush：一次version；每世界requested、setup observed、initial pose/geometry；每Step开始标记、返回后完整step观察；正常world destroy后标记；最终完成。这样断言/异常/超时仍有已完成阶段，不靠最后一次大JSON才保留。记录器不调用引擎setter来修复状态。

counts、ID字段为整数；开关为JSON bool；物理量输出明确浮点格式；拒绝非有限数。原始event pair、缓存ID与geometry不可仅写预期名。缺失末条/半行、未知字段、重复JSON键、重复/缺失/额外world/step、错序、bool冒充整数、越界ID、事件错pair、浮点越容差均不接受。失配时先保存原观察、阶段和首错，再停止；未执行步骤标未执行，不填零事件假记录。

独立consumer用冻结的两配置/六步字面表和自己从原geometry/transform计算的投影间隔，验证所有getter与请求区别。不存在的getter用request-only明确，不给“全部实际设置均读回”结论。consumer结果必须标consumer_only；只有最终receipt status=pass且所有源/输入/产物前后身份一致才是整次接受。后检失败不能因先写的consumer-only通过文件而伪装PASS。

纯合成测试拟覆盖：合法观察控制、开关getter与请求相反、质量/extent/safetyFactor不符、错begin/end步、错pair、缓存被误当端点位置、运动未完成/容差越界、外加/缺失行、重复键/非有限/类型替换、oracle文件修改、源清单遗漏、旧目录残留、失败后不执行及首错保留。纯测试只能mock进程，不能借“测试”启动编译器或原生程序。

不增加运行中改开关、销毁触发end、移动sensor、双高速物体、旋转、ray/shape cast、外部线程、压力/性能、音画或碰撞响应实验。若本固定输入失败，保留它并停，不能为证明3.2.0文案正确而改变世界。

## 9. 当前门槛与下一步

本协议是草案，已读独立SOURCE-REVIEW并纳入默认定义、质量/extent、awake/enabled/damping/locks、质心、长度尺度和临时事件数据等要求；仍须主编和独立协议审者冻结调用列表、完整观察schema和字面oracle。源码取得已完成；修正版协议接受后才可授权实现；源码/纯测试审查通过后再分别授权构建和行为。不是从门槛直接跳到native，也不把尚未发生的观察写入读者正文。

### 本次补读记录

独立源审完成后，本协议作者只读主编正在取得的固定 `src/core.c` 36–46及 `include/box2d/math_functions.h` 755–758，确认默认长度尺度1及公开getter/ setter声明；只用getter，不修改尺度。没有触发新的源码取得、编译或运行。早先草案4dc2版本已保存history，改变的是证据状态/默认尺度与质心前提，不增加行为配置或世界步。

### 主编源码取得状态更新

主编随后报告84文件取得完成并逐字节重核，SOURCE-MANIFEST SHA256 `7b4b4756e22e0ad9bc72110034c5e8b1be3c1fb74090a3a3874f1694795e9396`。本协议的取得步骤现在作为已完成取得过程的要求与后续复现规范保留，不要求重复下载。本作者没有把主编静态include解析报告当成预处理/构建成功，也未自行运行编译器。实现阶段应使用这份既有清单并重新核身份，不扩展文件集合。

### v2：首构建失败保留与完整诊断字节例外

v1代码清单996a1133及本协议b36c4cb9原字节保存在history/v1-before-reviewed-build-diagnostics；build-001也原样保留为fail。实际编译返回0、stdout空，stderr 32,263字节、73条warning；尚无原生行为、世界或Step。这是门槛失败，不是六步事件oracle失败。独立BUILD-DIAGNOSTIC-REVIEW（16db2dca4f44e625a86efd031b07603efa26914e3718922cd104be6759985284）审读全部诊断及固定源用点后，由主编批准以下有限政策；不是上游完整语言安全认证。

新build-002仍须另外授权，仍用原43 C argv、fixture、oracle、84源文件。退出必须0、stdout必须空；stderr只允许空，或与reviewed-build-stderr.txt完整原字节相等。该文件SHA256固定为c55f639fa5da94fed9737ff07f07048c47386213d14fe39dbefaf75e281ff4b5，纳入代码清单及复制/前后身份检查；即使stderr为空也先核已审文件身份。不得按warning类别、前缀、正则或清洗后的内容放行，不抑制警告，不改变旗标或源。非零退出、改字节、截断、追加fixture或其他诊断均停止。

构建收据的process.diagnostic_policy明确empty或reviewed_exact_warning，同时保留实际stderr摘要。原生执行stderr仍必须空，不继承构建例外；行为仍单独授权。此修订只授权代码与纯mock测试准备，没有启动第二次构建或行为。
