# 协议独立 oracle v2：活跃句柄的保留位条件

2026-11-02。接受这项执行前语义澄清；它不是新场景，也不授权原生执行。

## 固定输入与保留历史

协议仍为 `faa507b4a1cb3c3efd274c174a6a8e32377983db4aa9685871d0c65b5b47aa2d`，作者 schema 仍为 `b89e746367b99ece69066a4a279b32d678a7bf2cb6fc615a8a04be53becd812c`。此前独立 oracle `3bb0f324154852cf070c0e92778f8481bc7c2aed6a4d27a25858c6c970558d03` 和协议审查 `ebcd9b1c1655723bacac9b035a9ef497817c4e1f0ea449057971d55fe0e7b381` 原字节保存在 `history/independent-before-reserved-handle-clarification/`。不覆盖原审查结论，也不将它冒称已经包含此次发现。

## 本次实际源读与独立推导

直接重开官方 EnTT 固定提交 `78213075654a688e9da6bc49f7f873d25c26d12c` 的 [entity.hpp](https://github.com/skypjack/entt/blob/78213075654a688e9da6bc49f7f873d25c26d12c/src/entt/entity/entity.hpp) 95–145、220–275，以及 [storage.hpp](https://github.com/skypjack/entt/blob/78213075654a688e9da6bc49f7f873d25c26d12c/src/entt/entity/storage.hpp) 950–970。文件 blob 分别为 `f5cd054185d2a7d86114ee1627be72dab31d82e4`、`4d01e70ac20614a86d409f243fb1f15c1007caa3`。

null_t 与实体比较取实体索引部分，不要求完整整数等于全一值。因此 index=0xfffff、version=0 的完整值虽不是 0xffffffff，仍与 entt::null 相等。只用完整值排除全一值会误收这种伪造活跃记录。普通实体创建的 entity_at 限制索引小于保留索引，初始版本来自零值；next 跳过保留版本 0xfff。本协议又排除了 hint、自定义分配和销毁等扩展，故报告为活跃身份的 R/H/S/B/L 均须排除保留索引和保留版本。

这不是要求未来输出固定版本0或某个分配整数。仅增加必要的活跃值语义约束，仍按完整句柄检查相等性、跨阶段一致性和最终三活跃集合成员关系。prepared 的未知映射继续要求真实转换得到的具体全一 null 表示；JSON null 继续表示未观察字段。不能将二者混为一类，也不能把所有 uint32 都全局禁止保留值。

已静态阅读当前 checker 的 full!=0xffffffff 检查，确认它与上述 null_t 语义不同。本审者本轮未执行伪造输入或测试；反例实际被接受的记录由主编及作者另行保留。之前接受漏掉这项必要条件，应由本次澄清与后续代码复核补正，而不是删去初审。

## 最终 oracle 与后续门槛

新版 independent-oracle.json SHA256：`92f2fe2c5dbfe5e3fa3a8a281b171e2bbde033bdcea0257ea86658f9d32eeb15`。

建议最小 checker 修复仅对五个活跃身份应用 index<entity_mask、version<version_mask，并保留相应的合成负例；原 token、阶段、关系、次数和 native 预算均不变。等待作者冻结 checker/test/输入清单后再核对实现，不在本报告预先认定修复或运行通过。此次缺陷属于合成不可能记录的误接受，不据此宣布任何历史实际输出无效，也不新增分配或绕回实验。

本次仅原源读取、静态源码检查、JSON 文本修订与文件摘要；没有编译、fixture、原生调用或新运行结果。
