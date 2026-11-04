# 固定 L 形 Detour 网格：直连检查与完整 corridor

2026-11-04。**新实验的执行前协议，待独立协议审查。未实现、未编译、未运行。** 本文件、expected.json、SCHEMA.md 和源清单均不构成执行批准。原容量协议的批准不适用；新协议通过后才准备实现，实现仍须独立审查及主编明确批准构建/运行。

## 1. 唯一问题与范围

测试同一个人为指定平面网格上，L→C、C→F 两次直连通过，L→F 直连受阻，但 L→F 存在完整 polygon corridor。全部结果必须来自未修改的固定 Detour，而不是本地数学模型重新贴标签。三个 raycast 不是角色依次走完的移动指令。

这是支持既有同伴跟随文章的独立有限机制实验，不是 Naughty Dog 源码/地图/原图/参数复原，也不是现有纸面矩形示意的原样实现。旧直条网格为凸矩形且只观察输出容量，不适合本题。原作者材料、原纸面例与本新网格分别保留范围。

## 2. 固定源与实际物化

上游 recastnavigation/recastnavigation v1.6.0，commit `6dc1667f580357e8a2154c28b7867bea7e8ad3a7`。SOURCE-MANIFEST.json 与既有容量档案清单字节一致；16项本次均读取现存源字节并验证 SHA-256 与 Git blob，结果见 SOURCE-CHECK.json。未下载。未来执行时仍须各自执行前后双核，不以此静态检查替代。

源输入来自既有容量实验的16个已核文件；准备实现时仅本地复制到本包 `upstream/Detour`，再次核对双重身份。执行时从本包复制到各隔离执行副本的 `upstream/Detour`；保留上游许可，不改源，不运行旧 binary。公众支持包可不重分发上游代码，读者须将固定源清单对应文件取得后放入本包同一相对位置。清单只包含7个cpp和9个头文件，无其他依赖或资产。

以下定位使用同身份源文件的实际行号：

- `Detour/Include/DetourNavMeshQuery.h` 125–147：dtRaycastHit；392–423：两个 raycast 重载及声明。使用410–423的带 options、dtRaycastHit 重载。
- `Detour/Source/DetourNavMeshQuery.cpp` 2430–2691：raycast 说明与实现，2466开始目标重载；2547–2555终点位于polygon时 FLT_MAX；2657–2674无邻接墙命中仍返回累计状态；973–1165 findPath；1167–1204 getPathToNode。
- `Detour/Source/DetourCommon.cpp` 110–175：dtIntersectSegmentPoly2D 的边裁剪与 segMax。
- `Detour/Source/DetourNavMeshBuilder.cpp` 363–385：边数及 maxLinkCount；410–423：无detail时三角形数；492–550：实际坐标、polygon与邻接编码。
- `Detour/Source/DetourNavMesh.cpp` 267–287：单tile初始化；524–558：内部邻接到链接。

全部源链接以 `https://github.com/recastnavigation/recastnavigation/blob/6dc1667f580357e8a2154c28b7867bea7e8ad3a7/` 加以上路径定位。expected.json 是源码与手工几何推导的 oracle，不是观察转存。

## 3. 唯一几何与设置

所有坐标为(x,y,z)，y=0。P0覆盖x,z∈[0,1]；P1覆盖x∈[1,2],z∈[0,1]；P2覆盖x∈[1,2],z∈[1,2]。左上缺失区域是真实无polygon区域。

8个 unsigned short 顶点按索引：0=(0,0,0)、1=(1,0,0)、2=(2,0,0)、3=(0,0,1)、4=(1,0,1)、5=(2,0,1)、6=(1,0,2)、7=(2,0,2)。nvp=4，polyCount=3，vertCount=8。

每行先4顶点，后4输入邻接：

- P0：0,3,4,1；65535,65535,1,65535。
- P1：1,4,5,2；0,2,65535,65535。
- P2：4,6,7,5；65535,65535,65535,1。

邻接输入是0起始polygon索引，65535为边界，实际 neis 应为 P0=[0,0,2,0]、P1=[1,3,0,0]、P2=[0,0,0,2]。实际链接顺边索引递增：P0 edge2→P1；P1 edge0→P0、edge1→P2；P2 edge3→P1。每个side=255、bmin=bmax=0，其他边无链接。P0/P2只接触角点，不得建立链接。

dtNavMeshCreateParams 先零初始化。flags=[1,1,1]，areas=[0,0,0]；cs=ch=1；bmin=(0,0,0)，bmax=(2,1,2)；walkableHeight=2、walkableRadius=walkableClimb=0；buildBvTree=false。detail/offmesh指针空且计数零，无外部tile、自定义allocator/filter。固定默认filter为include=65535、exclude=0、area0 cost=1。

builder生成的实际header必须记录并核对：polyCount3、vertCount8、detailMeshCount3、detailVertCount0、detailTriCount6、offMeshConCount0、bvNodeCount0、maxLinkCount12。实际顶点、polygon顺序/type=GROUND=0/flags/area/neis/links必须与expected一致。每条链接在读取前校验范围，最多遍历maxLinkCount条并检测重复/循环，不无界追链。引用由本tile getPolyRefBase与索引取得，三者非零、互异、isValidPolyRef通过；后续输出必须使用真实引用。

L=(0.25,0,0.5)严格在P0内，C=(1.25,0,0.5)严格在P1内，F=(1.25,0,1.5)严格在P2内。没有边界起终点，不需nearestPoly。向前取+z，不宣称原作者方向或长度。

## 4. 调用顺序、数量与输出

单执行副本只允许一个builder、一个nav init、一个query init，然后3个raycast及1个findPath。raycast的hit先值初始化，path每次独立3槽置0，maxPath=3；options=0、prevRef=0，调用dtRaycastHit重载。不请求费用，不以pathCost作断言。query只init一次，maxNodes=16，观察实际node pool容量。

每步先保存原始结果再验证；首错立即停止，不启动后续查询：

1. dtCreateNavMeshData一次：必须true、非空data及正dataSize。
2. nav.init(data,dataSize,DT_TILE_FREE_DATA)一次，DT_SUCCESS。成功后data归nav拥有；成功正常清理不可双重释放。
3. 实际mesh检查及引用绑定全部通过。
4. query.init(nav,16)一次DT_SUCCESS、节点池16；核浮点格式FLT_RADIX=2、FLT_MANT_DIG=24、FLT_MAX_EXP=128及float最大值。不同格式停止，不换oracle。
5. raycast(P0,L,C,filter,0,hit,0)：status=0x40000000，pathCount2，槽[P0,P1,0]，t=FLT_MAX。
6. raycast(P1,C,F,filter,0,hit,0)：status=0x40000000，pathCount2，槽[P1,P2,0]，t=FLT_MAX。
7. raycast(P0,L,F,filter,0,hit,0)：status=0x40000000，pathCount1，槽[P0,0,0]，t=0.5，hitEdgeIndex1、hitNormal=(0,0,-1)。
8. findPath(P0,P2,L,F,filter,path,&count,3)：独立3槽置0、count=-1；status=0x40000000，count3，槽[P0,P1,P2]，末引用严格为F所在P2。
9. 正常成功先销毁query，再销毁nav，记录released并输出成功观察。

禁止其他路径/射线/最近点/移动/Crowd查询，不新增容量不足、节点耗尽、性能、动态障碍、碰撞或图形界面实验。所有成功状态必须精确匹配，额外任何位都拒绝。

前两射线没有墙命中，其法向量不是API承诺，**不读取作接受判断**；输出hit_normal=null、hit_edge=null作为“不适用”，并非声称原始数值为null。受阻射线命中(0.75,0,1)，远离角点，法线来自P0 edge1，其数值正负零等价。raycast成功位仅指查询成功，不代表直连无墙；必须独立核t。

FLT_MAX必须输出为有限原始数值，C++以double提升float后用17位有效数字序列化：`3.4028234663852886e38`。不要只打印9位float再让JSON double精确比较失真；不输出Infinity，不用FLT_MAX计算命中点。0.5及坐标二进制精确，无容差。其他float同样按double提升后17位输出。

几何手推：LC在x=1穿P0/P1门户；CF在z=1穿P1/P2门户；LF的x=.25+t、z=.5+t，t=.5时在x=.75离开P0顶边，那里无链接。P0→P1→P2是唯一图通路，16节点足够，3槽可容完整路径。findPath结果不说明真实角色运动或几何最短线。

## 5. 失败与观察完整性

成功输出精确遵循expected.json和SCHEMA.md。不得由观察生成或修订期望。失败保留已完成的setup/cases、准确calls、completed前缀、首错stage与简短failure_detail，并标记status=fail；未执行结果不可填零冒充调用。部分setup可为null，并另存有限partial_setup_text。每步校验不能仅依赖assert或NDEBUG状态。

builder/init/所有权/对象完整性不确定时，记录并flush首错，以非零状态立即结束隔离进程，绕过可疑部分对象析构；对象不得放在会因返回而自动析构的栈生命周期中。正常成功才按query→nav清理。此方案不是生产内存安全或OOM处理保证，不注入故障。

消费者只判断捕获JSON的内容，必须输出consumer_only而非声称原生已验证；真实运行证明另需源/代码身份、构建记录、调用输出、身份后检和整体receipt。纯合成反例不计作Detour调用。

## 6. 两次拟议执行与暂停条件

**仅规划同一操作者的两次隔离新副本执行**：主执行 main 与重复执行 repeat，使用相同冻结输入、源码、编译argv及schema，不同空执行目录；其后另作独立结果审查。不是现在授权，不是独立操作者原生复现，也不是跨平台验证。每次最多一次构建与一次fixture启动，各3 raycast+1 findPath；若全部成功，总计2次构建、2次启动、6 raycast和2 findPath，不是8种案例。

第一份出现未预审编译诊断、构建/运行失败、超时、身份不符、环境验证失败或结果不符时，停止当前并停止尚未开始的第二份。若第二份失败保留首份成功与第二份失败，不抹去或平均。任何重试或修改另立审查和主编批准；不得自动调整网格/期望来获取成功。

建议固定编译argv（实现审查前不可执行）：

`c++ -std=c++11 -O0 -Wall -Wextra -Iupstream/Detour/Include fixture.cpp upstream/Detour/Source/DetourAlloc.cpp upstream/Detour/Source/DetourAssert.cpp upstream/Detour/Source/DetourCommon.cpp upstream/Detour/Source/DetourNavMesh.cpp upstream/Detour/Source/DetourNavMeshBuilder.cpp upstream/Detour/Source/DetourNavMeshQuery.cpp upstream/Detour/Source/DetourNode.cpp -o fixture`

构建最多60秒，fixture最多10秒。编译退出0、stdout空及stderr为空或已在实现批准前独立审查并冻结的**整份字节**诊断才可启动。旧容量警告本次不自动放行；如尚无本新argv对应精确诊断获批，非空stderr必须停止，无论旧分类是否相同。不能抑制警告、改旗标、修改上游或放宽为子串匹配。

在每次构建/fixture调用前，创建并验证工作副本中互不相同的HOME、TMPDIR、XDG_CONFIG_HOME、XDG_CACHE_HOME、XDG_DATA_HOME、XDG_STATE_HOME、XDG_RUNTIME_DIR七个目录：实际目录、无符号链接、解析后在本副本内、可写；runtime按XDG要求私有0700。环境白名单至少仅包含受控PATH、LC_ALL=C、LANG=C及七项路径，不继承用户配置或凭据。环境准备/验证失败不得启动。使用独立进程组，超时终止所有自有后代并保存首错与清理异常，不把leader退出视为全部后代已结束。

本任务不安装、下载或调用网络/外部服务；阅读代码不证明操作系统已实现网络隔离，不能如此声称。路径与执行元数据仅留私有工作证据。

执行前后必须核冻结代码、oracle、schema、协议、source manifest及16源文件身份；重复副本不得从主观察推导期望。输出摘要可比较语义与字节（若引用同环境相同），但不预设数值引用4/5/6；实际引用绑定才是接受条件。

## 7. 下一道门槛与公开边界

独立审者先核本协议、expected与schema、所有源定位、浮点序列化、邻接、生命周期及失败停止策略。通过后才实现最小fixture/consumer/runner与纯合成消费者负例，再独立实现审查，然后由主编明确批准上述两份有限执行。

公开材料只含源/输入/输出身份、必要相对命令、有限观察与范围；私有环境路径、PID、程序二进制指纹或凭据绝不进入公开派生。保持上游许可，勿重发整份源码。现有支持“未运行导航网格”只能在真正获得新观察并明确限定后更新，不追溯改旧历史。
