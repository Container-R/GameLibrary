# ENet 发送队列边界：待批准的有限原生实验协议

日期：2026-11-01。状态：**仅方案；没有编译、调用编译器版本命令或执行实验。** 实现须先获主编批准，随后代码和独立字面预期审查通过，才能另行批准原生运行。

## 1. 问题与可行性

检验固定上游 `enet_peer_send` 在临界长度、四种单独 flags 和 unreliable 序号边界下，实际生成哪些队列命令、序号、分片字段与 packet 引用。不是重新写一个分支模拟器；被测函数、setup、链表、packet 和 reset 均链接原样上游代码。

**源码层面可行，编译兼容性尚未执行确认。** 建立一个只支持本次 queue/reset 调用的人工 host/peer，不声称它经历了真实连接协商。不得调用 host_create、host_connect、host_service、host_flush、socket API、DNS 或协议收发函数。没有外部地址、端口、报文、传输、重组或接收测试。链接库中存在网络函数不意味着调用它们；代码审查必须检查 fixture 的完整调用路径，不以“链接成功”证明没有网络行为。

现有分片正文的固定上游与本协议相同；新增价值仅是直接检查原生队列实现和释放责任，不能升级原文为网络、延迟或实际游戏验证。

## 2. 固定原源、依赖与编译设计

唯一上游：ENet v1.3.18 提交 `2662c0de09e36f2a2030ccc2c528a3e4c9e8138a`，不是当前主分支或 Godot fork。

本次通过只读 GitHub 接口读取下列固定原文件。实现前将精确原文件保存于独立 scratch 的 `upstream/`，记录逐文件 Git blob 与 SHA-256；不得修改上游内容，不把上游源文件批量归档到公共知识库。

- [peer.c 92–222](https://github.com/lsalzman/enet/blob/2662c0de09e36f2a2030ccc2c528a3e4c9e8138a/peer.c#L92-L222)：所有权、输入拒绝和发送选择；同文件约 254–423 的 reset/队列清理，以及 [637–721](https://github.com/lsalzman/enet/blob/2662c0de09e36f2a2030ccc2c528a3e4c9e8138a/peer.c#L637-L721) setup/queue 实际序号与入队。
- [host.c](https://github.com/lsalzman/enet/blob/2662c0de09e36f2a2030ccc2c528a3e4c9e8138a/host.c)：host_create 初始化、host_connect 的 channel 初始化（完整读取至 270 行）。**不执行这两个函数。**
- [packet.c 19–68](https://github.com/lsalzman/enet/blob/2662c0de09e36f2a2030ccc2c528a3e4c9e8138a/packet.c#L19-L68)：create 初值及 destroy 回调。
- [protocol.c 12–33](https://github.com/lsalzman/enet/blob/2662c0de09e36f2a2030ccc2c528a3e4c9e8138a/protocol.c#L12-L33)：setup 调用的真实 command size 查询。
- `list.c`、`callbacks.c`：真实链表及默认 malloc/free/abort；`unix.c` 和 `include/enet/unix.h`：Unix 实现和字节序定义。
- `include/enet/{enet,protocol,types,list,callbacks,time,utility}.h`：结构、常量及内部声明；`compress.c` 与 `Makefile.am`：Unix 完整链接依赖集合，压缩函数仅链接不调用。

避免为了只编译 peer.c 而伪造 `enet_protocol_command_size` 或 `enet_host_flush` 等符号。使用完整 Unix 库源集合：

```text
cc -std=gnu99 -O0 -Wall -Wextra -Iupstream/include fixture.c \
  upstream/callbacks.c upstream/compress.c upstream/host.c upstream/list.c \
  upstream/packet.c upstream/peer.c upstream/protocol.c upstream/unix.c \
  -o queue_fixture
```

原源文字哈希清单见 `UPSTREAM-SOURCE-MANIFEST.json`，包括八个 Unix C 文件、八个必需头文件及 Makefile.am；实现时必须逐项匹配，再编译。

无 CMake、make、configure、下载依赖、安装或自定义平台功能宏。`-std=gnu99` 使用本机 Unix 标准头默认接口；编译失败停止，不临时换宏/删除函数/加 stub 以求通过。编译警告完整保存并审阅，不以静默忽略作通过。默认分配回调保留；不注入 OOM，不改分配分支。此集合的 `host.c`/`compress.c` 等只是满足链接依赖，不能声称其未调用功能被验证。

## 3. 每行独立的人工对象及初始化不变量

每一行重新创建清零的 `ENetHost` 和 `ENetPeer`，两者在该行全程存活；没有跨行排队状态。

1. host.socket 设 `ENET_SOCKET_NULL`，host.mtu=1392、maximumPacketSize=上游默认 32 MiB、maximumWaitingData=默认值、checksum=NULL、totalQueued=0；host.peers=&peer、peerCount=1、channelLimit=1、dispatchQueue 清空。host 其他成员保持清零。
2. peer.host=&host；incomingPeerID=0；两 sessionID=0xFF；清空 acknowledgements、sentReliableCommands、outgoingCommands、outgoingSendReliableCommands、dispatchedCommands 五个链表。初始 state=DISCONNECTED、channels=NULL、channelCount=0。
3. 调用真实 `enet_peer_reset` 设置内部默认值。此时所有 reset 会访问的链表已具备 sentinel；尚未分配 channel，不会误 free 栈内存。
4. 用 `enet_malloc` 分配一个 channel 并清零（不能使用栈 channel，因为 reset 会释放）；如 host_connect，清空其两个 incoming 链表、归零 incoming 序号和 reliable windows。设置 outgoingReliableSequenceNumber=42，outgoingUnreliableSequenceNumber 为该行 65534 或 65535；peer.outgoingUnsequencedGroup=7。
5. channelCount=1。调用真实 `enet_peer_on_connect`（当前仍 disconnected）后设 peer.state=CONNECTED，因此 host.connectedPeers=1，incomingBandwidth=0，bandwidthLimitedPeers=0。这只满足被测调用的内部计数，不构造握手记录。
6. 在调用 send 前验证上述重要前提、空队列、版本宏和 linked_version=1.3.18，以及 sizeof uint16=2、uint32=4、协议头=4、分片命令=24、可靠命令=6、不可靠/无序命令=8。不合即停止，不据本机布局重算预期。

因此 F 固定为 1392−4−24=1364，长度只取 1364/1365。checksum 路径不测。最大包长、MTU 合法区间和分片数都远离异常配置。输入数据为原创确定字节模式 `i mod 251`，通过 `enet_packet_create` 复制；无 NO_ALLOCATE。设置 packet.freeCallback 指向原创只记录释放次数、释放时 referenceCount/flags/dataLength 的观察函数，不修改库状态。回调观察存于行外仍存活的上下文，不保存或输出裸指针。

## 4. 冻结 16 个成功行与 1 个拒绝行

每行仅调用一次 `enet_peer_send(peer,0,packet)`。flags 只为 0、8（UNRELIABLE_FRAGMENT）、1（RELIABLE）、2（UNSEQUENCED），不测试组合位。初始可靠序号 R=42，无序组 G=7。

表中命令是实际 header.command 字节；`R/U` 为每个 outgoing command 的主机序可靠/不可靠序号；末列为 channel 最终 R/U 和 peer G。`ordinary` 指 outgoingCommands，`reliable` 指 outgoingSendReliableCommands。

| 长度 | flags | 初始 U | 命令序列 | R/U 序列 | 队列 | 最终 R/U/G |
|---:|---:|---:|---|---|---|---|
|1364|0|65534|7|42/65535|ordinary|42/65535/7|
|1364|0|65535|134|43/0|reliable|43/0/7|
|1364|8|65534|7|42/65535|ordinary|42/65535/7|
|1364|8|65535|134|43/0|reliable|43/0/7|
|1364|1|65534|134|43/0|reliable|43/0/7|
|1364|1|65535|134|43/0|reliable|43/0/7|
|1364|2|65534|73|0/0|ordinary|42/65534/8|
|1364|2|65535|73|0/0|ordinary|42/65535/8|
|1365|0|65534|136,136|43/0,44/0|reliable|44/0/7|
|1365|0|65535|136,136|43/0,44/0|reliable|44/0/7|
|1365|8|65534|12,12|42/65535,42/65535|ordinary|42/65535/7|
|1365|8|65535|136,136|43/0,44/0|reliable|44/0/7|
|1365|1|65534|136,136|43/0,44/0|reliable|44/0/7|
|1365|1|65535|136,136|43/0,44/0|reliable|44/0/7|
|1365|2|65534|136,136|43/0,44/0|reliable|44/0/7|
|1365|2|65535|136,136|43/0,44/0|reliable|44/0/7|

所有成功行 return=0，packet.flags 保持输入值，数据/长度不变。一个命令时引用数 1、totalQueued=1、queueTime=1；两个命令时引用数 2、totalQueued=2、queueTime=[1,2]。其他发送/接收/确认队列为空。命令的 packet 与当前 packet 是同一活对象；只记录身份比较布尔值，不输出地址。command.header.channelID=0；header reliableSequenceNumber 转回主机序必须等于表中 R。

- 单命令：offset=0、fragmentLength=1364，命令 dataLength=1364；7 的 unreliableSequenceNumber=65535；73 的 unsequencedGroup=8。只读取当前命令实际初始化的 union 成员，不 dump 未初始化 union/padding。outgoingDataTotal：7/73 为1372；134为1370。
- 双命令：offset=[0,1364]、fragmentLength/dataLength=[1364,1]、fragmentCount=[2,2]、fragmentNumber=[0,1]、totalLength=[1365,1365]。可靠 startSequenceNumber 均43；不可靠均65535。两个分片同属一个 packet。outgoingDataTotal=1413。其余 setup 的 sendAttempts、sentTime、roundTripTimeout 均0。

第17行：长度1365、flags1、初始 R42/U65535/G7，但 channelID=1（channelCount=1）。预期 return=-1、全部队列空、引用0、packet内容/flags不变、R/U/G不变、totalQueued=0、outgoingDataTotal=0、释放观察次数仍0。此行不代表所有失败路径；断连、过长包、分配失败都未测。

独立审者应在看结果前根据固定源另冻结字面 oracle，不导入作者选择函数或从运行结果学习期望。枚举17行而不是实现另一套 flags 决策来制造循环验证。

## 5. 所有权与清理

成功行：观察完毕调用真实 `enet_peer_reset(&peer)`，不得手动销毁仍被队列持有的 packet。预期 freeCallback 仅1次且回调时引用数0；flags/长度仍匹配。之后不得再解引用 packet，不能用已释放对象验证“销毁”。检查 peer.channels=NULL、channelCount=0、state=DISCONNECTED、host.connectedPeers=0、五队列和 host.dispatchQueue 为空。host.totalQueued 仍为原命令数，peer.outgoingDataTotal 经 reset 变0。

拒绝行：send 后立即记录 packet 仍活且回调0；由调用者执行一次真实 `enet_packet_destroy`，回调1次且ref0，再 reset peer。不能把 reset 销毁 packet 与调用者销毁混在一起。回调次数只证明这次 packet 生命周期观察，不是全进程无泄漏或通用内存安全证明。

如果检查失败，先保留失败行证据，在仍可判定对象所有权时尽力按上述路径清理；保留第一错误，不因清理失败替换它。禁止为了得到成功日志而继续下一个案例。

## 6. 记录、运行上限与验收

拟实现：原创 fixture.c、Python runner、独立只读 consumer、字面 oracle、纯合成反篡改测试、README。先源码清单冻结及独立审查，**本协议本身不授权构建或运行**。

批准后单轮至多：1次 `cc --version`（5秒）、1次上述编译（60秒）、1次 `strace -f -e trace=network -o network.trace ./queue_fixture`（整个跟踪进程组20秒，fixture仅执行一次、17行）；任一步失败或超时即停止，无自动重试、备用编译器、宏切换、追加案例或网络探测。独立重复需要另批，只重复相同17行，不算34种独立配置。

跟踪仅用于 fixture，不跟踪编译。原始 `network.trace` 留本地、不公开；验收要求 strace 成功、完整正常退出标记、没有任何 network 类系统调用记录，不能把空/缺失文件当作0调用。退出状态与 fixture 结果必须同时成功。若 ptrace 权限/工具能力不足，停止报告阻碍，不绕过跟踪或再次无跟踪运行。此处 strace 不是替换 ENet 分支的 stub；“未观察到网络系统调用”只覆盖这一个进程组的有限跟踪，不扩成全系统或端到端安全保证。超时终止并回收整个自有进程组，保留部分 trace 与原始错误。

runner 使用 fresh scratch 及固定最小环境，不继承编译注入变量；清理旧 PASS 必须早于动态导入和启动保护。记录真实命令/退出/原始输出与错误、原源及 fixture/consumer/oracle 哈希；所选编译工具和产物的本机身份只留本地审查，不能直接加入公共文件。源输入运行前后字节一致；每轮唯一关联标记绑定行记录、结束记录与外层结果。固定 schema 和记录顺序，17行恰好一次、不允许重复键/非有限数/额外行；整数和布尔类型严格分开。按已初始化字段逐项比对，而非只看 native passed=true。

输出至少包含：协议版本、linked_version和所验尺寸；每行输入、初始状态、send返回、两队列的顺序命令字段、packet引用/flags/内容匹配、最终序号、计数、释放前后观测；最后完成行数。所有 multibyte wire 成员先用真实 ENet 宏转主机序再记录。consumer 独立核对字面表、数据范围/键集及 raw 与派生记录严格类型相等；不同 queue 用显式名字标注，不从合并列表猜测。

纯合成回归须能拒绝缺行/重复行、错误队列/命令/序号/引用、bool替代integer、原始记录与派生记录不一致、陈旧PASS、构建失败却出现结果、源输入修改。测试不得偷偷执行 cc 或 fixture。任一失败保留首份输出再请求修订；禁止修改预期追随原生结果。

公共支持仅考虑原创代码、固定上游来源标识、去除私有执行信息的可读结果与范围；不复制完整上游库，不发布本机编译器/二进制指纹或 scratch 路径。此实验不评估实际网络连接、MTU协商、发送/确认、重传、压缩、接收窗口、重组、吞吐、卡顿、交付顺序或应用状态；将人工 CONNECTED 写入当成真实在线连接是明确禁止的结论。
