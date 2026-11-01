# 序列号回绕：教学模型与有限检查

[返回读者正文](../../../GameLibrary/网络与在线服务/实时同步/消息顺序/序列号回到零时怎样判断消息的新旧.md)。

`sequence_wrap.py` 只实现有限位宽比较与固定 ENet 入站窗口条件的简化片段，不是传输协议或实际年代检测器。只用 Python 标准库，不发送数据包、不调用原生 ENet。源代码与本文同步，不包含私人执行环境记录。

## 运行

从仓库根目录运行：

```sh
python3 -B -m unittest discover -s 管理档案/支持资料/序列号回绕 -p test_sequence_wrap.py
python3 -B -O -m unittest discover -s 管理档案/支持资料/序列号回绕 -p test_sequence_wrap.py
```

比较器限制教学位宽2至16，拒绝bool、整数子类、浮点、越域值等。它用模距离；测试判据另外按 RFC1982 §3.2 普通整数条件分支表达。穷举4位256对及8位65536对，共65792个有序对，检查结果与交换方向的关系。普通/优化模式重复同一集合，不是两倍独立案例。16位只检查选定边界。

12个测试方法在作者、主编及独立审阅者的有限执行中通过。独立审阅还用沿圆周逐步前进的4位判据和字面边界检查，而非只重跑作者测试。这些是数学合成检查，不是原生库、丢包、重连或真实网络验证。

`reliable_window_not_rejected` 的True只表示模型中这道窗口条件没有拒绝。它不检查peer状态、重复、分配、分片、队列或实际交付；相等值可以通过本guard，但固定源码后续可靠命令分支仍会拒绝。不要把True解释为完整接收许可。

## 来源与身份

- [RFC1982](https://www.rfc-editor.org/rfc/rfc1982.html)，§2–6；DNS语境下的序列运算，可由其他用途明确采用，不是游戏通用强制规则。
- ENet v1.3.18，固定提交 `2662c0de09e36f2a2030ccc2c528a3e4c9e8138a`，[窗口常量](https://github.com/lsalzman/enet/blob/2662c0de09e36f2a2030ccc2c528a3e4c9e8138a/include/enet/enet.h)和[入站排队函数](https://github.com/lsalzman/enet/blob/2662c0de09e36f2a2030ccc2c528a3e4c9e8138a/peer.c)。只模拟选定普通可靠命令的初始窗口guard，未移植完整实现。

详见[有限检查摘要](verification.json)。它只绑定这份代码与上述执行范围，不是库或引擎的性能、安全与互通证明。
