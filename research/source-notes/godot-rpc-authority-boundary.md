# Godot RPC 入口与应用授权：来源和证据定位

访问/复核日期：2026-11-01。对应[客户端预测与权威边界](https://github.com/Container-R/GameLibrary/blob/1a7bf18b24ba56395892c4c0cdb3b2acecc16985/solutions/programming/client-prediction-authority-boundary.md)的新增 RPC 小节；[实验档案](../experiments/godot-rpc-authority-boundary/README.md)。不是对预测算法的实际引擎验证。

## 本次实际阅读的原始来源

| 来源与版本 | 定位与有限用途 |
|---|---|
| [Godot 4.6 High-level multiplayer](https://docs.godotengine.org/en/4.6/tutorials/networking/high_level_multiplayer.html) | Initializing / Managing connections / Remote procedure calls：连接信号、同名 NodePath 和显式 RPC 配置。 |
| [MultiplayerAPI 4.6](https://docs.godotengine.org/en/4.6/classes/class_multiplayerapi.html) | RPCMode、get_remote_sender_id、poll：开放调用模式不等于角色所有权；sender 的当前调用上下文。 |
| [ENetMultiplayerPeer 4.6](https://docs.godotengine.org/en/4.6/classes/class_enetmultiplayerpeer.html) | create_server、create_client、set_bind_ip：请求绑定地址/端口；不是 OS 接口审计。 |
| [ENetConnection 4.6](https://docs.godotengine.org/en/4.6/classes/class_enetconnection.html) | get_local_port：记录实际端口。 |
| [SceneMultiplayer 4.6](https://docs.godotengine.org/en/4.6/classes/class_scenemultiplayer.html) | allow_object_decoding / auth_callback：记录禁用对象解码及空认证回调，不推导账号认证。 |
| [Object 4.6](https://docs.godotengine.org/en/4.6/classes/class_object.html#class-object-method-call-deferred) | call_deferred：空闲阶段执行；不等同固定等待完整一帧。 |
| [Callable 4.6](https://docs.godotengine.org/en/4.6/classes/class_callable.html#class-callable-method-rpc-id) 与 [Node 4.6](https://docs.godotengine.org/en/4.6/classes/class_node.html#class-node-method-rpc-id) | 两种 rpc_id 的返回合同不同；用于解释并修正首次解析失败，不扩大实际网络范围。 |

仅作源码机制比较的官方提交：`35e80b3a8822a9df9be390814b62f44c0a9c69e8`。

- [scene_rpc_interface.cpp 240–295](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/multiplayer/scene_rpc_interface.cpp#L240-L295)：RPC mode 分支、反序列化参数与节点方法调用；不是角色授权实现。
- [scene_multiplayer.cpp 130–135](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/multiplayer/scene_multiplayer.cpp#L130-L135)：处理 packet 前设置 sender、调用后清零，支持区分入口上下文与后续处理。实际 fixture 另外观察 getter。
- [enet_multiplayer_peer.cpp 60–98](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/enet/enet_multiplayer_peer.cpp#L60-L98)：服务器绑定及客户端非零 local_port 的绑定路径。实际代码请求固定 loopback，并读回端口；没有独立抓包或 OS 套接字审计。

## 证据不互相代替

- 原有 Python 模型的 16 项测试仍只覆盖其整数协议；跨实体时间归属小节仍为未执行推演。
- 新 fixture 在真实两个 Godot 进程中传递三条有限请求，观察入口 sender、deferred getter、双方收到的 outcome，以及原创应用规则的前后累计值。
- 静态 consumer 比对原始事件/终态、源码及输出哈希、命令、环境、状态和关联 ID。它不是运行真实性认证，不需访问当前二进制或原始绝对路径。
- 初次解析失败、修正后的接受记录、纯测试与优化启动拒绝分开保存。没有用失败的 parse attempt 充当 ENet 能力或 RPC 行为证据。
- 所有权映射、整数规则、stop-and-wait、STOP 屏障和验收表是原创有限设计；不是 Godot 对账号、攻击、速率或重连的保证。

安装字节指纹已从本公开衍生说明省略；历史自报 `4.6.3.stable.official.7d41c59c4`；自报 “official” 不构成独立来源认证，比较提交未证明就是这些字节的构建来源。只保留原创实现、分析和定位链接，不批量转载引擎源码或文档。

公开记录维护说明：本次仅省略安装指纹并固定旧文章引用；技术观察与失败范围保留，没有重新运行或认证安装来源。
