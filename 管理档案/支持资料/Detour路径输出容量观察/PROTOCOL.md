# 固定 Detour 三矩形：搜索成功与输出容量协议草案

状态：执行前草案，待独立审查；没有fixture、编译或运行。本轮只允许一个固定输入、两次同步查询。权重双走廊不属于本协议。

## 1. 问题与成功条件

要实际区分：搜索内部到达终点，与调用者数组包含终点。默认过滤器、三个相邻平面矩形A/B/C、足够的节点池。两次查询只改变maxPath，预先期望2槽前缀含BUFFER_TOO_SMALL却不含PARTIAL，3槽取得全链。不是节点耗尽、性能、最短几何轨迹、角色到达或通用内存安全测试。

源码固定recastnavigation/recastnavigation v1.6.0，commit `6dc1667f580357e8a2154c28b7867bea7e8ad3a7`。建图、查询及状态推导原源定位见GATE.md。未修改上游源码、未引入替代搜索逻辑。

## 2. 唯一输入

所有整数字面如下；除写明参数外dtNavMeshCreateParams先零初始化。

- verts的8个三元组依次(0,0,0),(1,0,0),(2,0,0),(3,0,0),(0,0,1),(1,0,1),(2,0,1),(3,0,1)，类型unsigned short。
- nvp=4，polyCount=3，vertCount=8。每行先4个顶点索引、再4个邻接输入：
  - A：0,4,5,1；0xffff,0xffff,1,0xffff。
  - B：1,5,6,2；0,0xffff,2,0xffff。
  - C：2,6,7,3；1,0xffff,0xffff,0xffff。
- flags=[1,1,1]，areas=[0,0,0]；cs=ch=1；bmin=(0,0,0)，bmax=(3,1,1)；walkableHeight=2、walkableRadius=walkableClimb=0；buildBvTree=false。所有detail/offmesh指针空，数量0，无自定义allocator/filter。
- start=(.5,0,.5)，end=(2.5,0,.5)。A/C为其所属poly；不调用findNearestPoly或straightPath。
- dtQueryFilter默认构造，记录实际include/exclude和area0系数并核对0xffff/0/1。
- 一个dtNavMesh、一个dtNavMeshQuery。query只init一次，maxNodes=16；不在第二查询前重新init。正常全部成功时query必须先于navmesh销毁；部分初始化失败遵循下述隔离进程停止策略，不自动析构可疑对象。

输入邻接是0起始polygon索引，不是内部neis的1起始编码。0xffff表示边界。预期实际neis：A=[0,0,2,0]，B=[1,0,3,0]，C=[2,0,0,0]；实际内部链接只应为A↔B↔C。所有链接side=0xff，无外部tile/offmesh。

## 3. 调用次序与先决校验

1. 调用dtCreateNavMeshData一次，记录布尔结果和正数据大小；失败立即停。
2. 用公开单tile init(data,size,DT_TILE_FREE_DATA)一次；必须DT_SUCCESS。成功后不再手工释放tile data，由navmesh拥有；正常成功释放查询和navmesh时不再访问其内容。builder或任一init失败、对象状态或所有权不确定时，记录并flush已完成阶段与首错，然后以非零状态立即结束隔离进程，不走可疑部分对象的析构或清理。不能继续查询。
3. 读取实际tile，校验3个ground polygon、8顶点、各顶点顺序/坐标、flags/areas、邻接和链接全部对应上述字面输入；遍历实际links必须先核索引范围并限定不超过本tile maxLinkCount次，检测循环而不是无界追链。保留观察后才校验，不只写“setup=true”。以本次getPolyRefBase(tile)和索引取得A/B/C引用，校验非零/互异/有效及引用映射。公共结果只记录这些库内引用，非主机执行标识。
4. query.init(nav,16)一次成功；记录实际节点池容量16作为设置观察，不新增池耗尽情形。
5. 第一遍把真实3槽dtPolyRef数组全部置0、pathCount置-1，调用findPath(A,C,start,end,filter,path,&count,2)。保存原始status、count、全部3槽及各槽到A/B/C的映射。先核对第一遍字面oracle；任何不符立即停止，不执行第二遍或调参。
6. 同一个query，独立3槽数组重新全置0，count=-1，第二遍调用相同参数，maxPath=3。findPath自己的clear是该次查询行为，不依赖外部重置。保存同样观察并校验。

只允许2次findPath，禁止sliced、raycast、moveAlongSurface、debug redraw或额外探测查询。无网络、GPU、引擎或用户资产；不要求或尝试绕开任何tracing限制。

## 4. 独立字面oracle

两个门户是(1,0,.5)、(2,0,.5)，仅有A-B-C通路，节点16足够。默认区域费用都是1，但不以成本数值作为原生观察结论。

| case | maxPath | count | 全部3槽符号 | 原始status |
|---|---:|---:|---|---|
| prefix | 2 | 2 | [A,B,0] | 0x40000010 |
| full | 3 | 3 | [A,B,C] | 0x40000000 |

两者均SUCCESS且不含FAILURE/IN_PROGRESS/PARTIAL_RESULT/OUT_OF_NODES；只有prefix含BUFFER_TOO_SMALL。全部状态位精确匹配，不仅检查success。prefix第三槽不变是本输入对maxPath边界的一次有限观察，不概括成所有缓冲写入安全。

独立consumer应固定case数量2、名称/顺序/容量、精确状态/count、引用映射与全部槽值，并核setup；不得从结果生成期望或导入作者选择分支。不使用浮点容差：该输入顶点、起终点、系数均二进制精确，观察不包含近似费用或归一化向量。坐标和输入浮点拒绝非有限值。

## 5. 输出与失败保留

fixture输出一份有限JSON观察：协议标识、固定源码commit、完整输入字面、setup的实际顶点/poly/neis/links/filter/node容量、A/B/C实际引用、按调用顺序的case记录。引用编码为十进制字符串，0哨兵明确；status为非负整数另附十六进制显示。consumer严格JSON，拒绝重复键、非有限数字、bool冒充数字、缺行/多行/错序及任何未知引用。观察不是性能数据。

失败中尚未调用的case明确未执行，不能填成零结果。失败应先输出已完成的setup/case和具体阶段、保留首错并flush。不重试、不运行后续case、不覆盖原失败档案。builder/init失败或所有权、对象完整性不确定时，立即非零结束隔离进程，绕过可疑部分对象的析构；fixture不可把这些对象放在会因返回而自动析构的栈路径上。只有正常全部成功时，才按query→nav顺序释放。不能用断言作为唯一校验，也不做故意畸形C指针或OOM故障注入。该策略只是有限harness避免掩盖首错的停止方式，借进程终止回收资源，不是生产OOM修复、泄漏安全或库故障清理保证。

## 6. 构建、身份与执行边界

实现后、执行前冻结原始fixture/consumer/字面oracle/此协议及固定上游7cpp+9头文件清单（主编已物化且本轮只读确认共16文件，使用既有SOURCE-MANIFEST.json，不重复下载）；每个上游文件同时核Git blob身份和原字节SHA256。保留原许可，公众支持包不必重分发上游bulk。源/输入身份是复现条件，不公开安装二进制指纹或主机路径。

直接C++构建，不运行CMake/Ninja，不安装依赖。建议单一 `c++ -std=c++11 -O0 -Wall -Wextra -Iupstream/Detour/Include fixture.cpp` 加七个固定Detour cpp、输出相对位置；不用NDEBUG/fast-math或特殊Detour宏。最终完整argv必须在实现审查时列明。

一次构建上限60秒，一次fixture上限10秒。构建非零或有未事先审查诊断时，不启动fixture；运行非零/超时/结果不符，保留首错并停止。工具原始日志可本地保留，公众摘要只给源与输入身份、实际命令的相对形式、状态和有限结果，不暴露私有执行标识。独立重复如有需要另授权，不在当前两查询外自动增加。

## 7. 尚未满足的接受门槛

本协议当前未执行。下一步先独立核数组绕序、邻接、builder生命周期、输出前缀oracle；通过后才写fixture/consumer。实现再作源审与纯合成consumer负例，随后主编单独批准构建和运行。任何观察都不得追溯修改旧“未执行”历史说明；若将来通过，只补明确日期、输入和两次实际查询范围，不新建重复正文。

## 执行前失败策略修订记录

独立审者从固定nav init的分配路径发现部分对象析构风险；本轮没有执行OOM。原协议a653bdbc已保存history/PROTOCOL-before-failure-policy.md。仅修订失败退出/正常清理策略，输入、两查询及字面oracle未变，仍未实现或运行。

## v2：首次构建已停止后的精确诊断例外

首次attempt-001构建真实退出0，但出现一条上游-Wclass-memaccess诊断，依原门槛整体失败；未启动fixture，确认findPath调用0。旧协议与runner及原始attempt保留，不改旧失败结果。独立BUILD-DIAGNOSTIC-REVIEW已核固定源码实际可达清零路径；不是未调用代码，也不认证C++跨ABI/对象生命周期安全。

本版下一次只可使用全新attempt-002。完整编译argv、fixture、两行oracle和16上游文件不变。构建仍须退出0、stdout严格空；stderr仅可空或与reviewed-build-stderr.txt整份字节相同。该受信任文件同时进入源清单，并固定SHA256 d887b09f1c4f304b009fbfbcf61834c5d71dd80a44d8cc1cdb7f9978952f0bd5。任何新增/缺失/改变的诊断、fixture警告、非零退出均拒绝；不按类别/文件/子串放行，不抑制警告或换旗标。receipt记录empty或reviewed_warning。

这只允许准备新门槛，须经独立代码审查和主编单独执行授权后才可再构建；没有自动重试。若进入fixture仍只同一输入两findPath，消费者和身份后检门槛不变。
