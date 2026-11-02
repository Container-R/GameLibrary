# EnTT 映射生命周期：独立执行前审查

2026-11-02。审查协议 SHA256 `a3fefc5e87d617dc6db834cc7021537402d545a47bb205e7d1b0b77903f71e2c`。**四阶段机制与两次相同输入的范围可接受；下述 initial 字段语义须澄清，完整 schema/失败收尾须在实现冻结时落实，再审代码，不能据此执行。** 本报告不导入夹具逻辑，没有夹具运行结果。

## 实际来源阅读

完整阅读现有《实体句柄什么时候能保存，什么时候需要映射》（SHA256 `914dd362e1b5c545cc9e67a6d0fd6ccd9a5ad30b0953ab91ee38ee1024455305`）。现书已经说明映射与有效性不同，本实验仅为该有限机制增加可观察证据，不应增加书目或借此认证业务权限、整个恢复系统。

独立从官方 skypjack/entt 读取固定 `78213075654a688e9da6bc49f7f873d25c26d12c`：

- [snapshot.hpp](https://github.com/skypjack/entt/blob/78213075654a688e9da6bc49f7f873d25c26d12c/src/entt/entity/snapshot.hpp) 50–115、260–460：写归档、restore、实体 get、contains/map。
- [registry.hpp](https://github.com/skypjack/entt/blob/78213075654a688e9da6bc49f7f873d25c26d12c/src/entt/entity/registry.hpp#L460-L545) 460–545：有效性、普通创建/销毁及不同的指定版本入口。
- [storage.hpp](https://github.com/skypjack/entt/blob/78213075654a688e9da6bc49f7f873d25c26d12c/src/entt/entity/storage.hpp#L1000-L1120) 1000–1120：swap_only 实体存储及普通 emplace 回收路径。
- [sparse_set.hpp](https://github.com/skypjack/entt/blob/78213075654a688e9da6bc49f7f873d25c26d12c/src/entt/entity/sparse_set.hpp#L239-L247) 230–255 与503–509：销毁推进版本、减少活跃头及 free_list 返回；620–650另读的是迭代器段，不把它当活跃数证据。
- [entity.hpp](https://github.com/skypjack/entt/blob/78213075654a688e9da6bc49f7f873d25c26d12c/src/entt/entity/entity.hpp#L25-L155) 25–155：默认 uint32 traits 与完整标识分解/后继。

未运行编译器、预处理器、C++ 或检查器；未 independently 复核本地单头全部原字节，后续须依源清单核 Git blob/大小/SHA256。没有网络隔离或系统调用观察。

## 独立字面预期（在任何原生结果前固定）

下面值为直接源推导的预期，不由实现运行产生。字段顺序建议固定；句柄本身保留真实 uint32，不要求碰巧取某个预设索引。

| stage | contains | mapped_nonnull | mapped_valid | active_count | initial_valid | source_valid | seed_valid | input_consumed |
|---|---|---|---|---|---|---|---|---|
| before_load | false | false | false | 1 | null | true | true | null |
| loaded | true | true | true | 2 | true | true | true | 3 |
| externally_destroyed | true | true | false | 1 | false | true | true | null |
| reloaded | true | true | true | 2 | false | true | true | 3 |

这里 input_consumed 仅在刚执行 get 的阶段代表本次新游标消费数；其余 null，不能含糊充作累计数。也可另放两条固定读取记录，但实现前要选定一种，不能允许任意记录数。

归档的独立字面类型/计数：`[(uint32,1),(uint32,1),(entity,remote_entity)]`。前两个1分别是 storage.size 与 free_list；仅因为来源只创建一个且未销毁，此输入两者相等。实体 token 的值必须等于已记录的来源完整句柄，不能只比较索引。读写 archive 重载必须真区分 uint32 与 entt::entity，不能经泛型隐式转换后伪称类型检查。

跨行关系：source 和 seed 完整句柄均不变；loaded 的 mapped_now == mapped_initial，且不同于 seed；destroyed 的 mapped_now == loaded.mapped_now；reloaded 的 mapped_now != mapped_initial 且不同于 seed；从 loaded 起 mapped_initial 数值始终不变，销毁/重载后仍 invalid。两次 get 从同一不可变归档的新游标开始，均消费恰好3项。map 查询不能触发恢复，restore 发生于第二次 get。

必要精度修正：协议“前两阶段没有可比较的旧句柄”易使 loaded 的 initial 被错误写为 null。实际第四步已保存 mapped_initial；应改成“仅 before_load 尚无 mapped_initial；loaded 开始记录其真实完整值及当前有效性”。若另有“与先前映射相等”字段可以在无先前映射时为 null，但不能混淆对象本身不存在。

这里没有假设无穷版本不重合：只使用这一轮普通销毁/再创建，无指定版本、hint、自定义 traits 或绕回。实体 storage 的 free_list 在本 swap_only 路径是活跃前缀边界；不把名称推广到任意类型 storage 的活跃数量定义。

## 最小 schema 与收尾门槛

建议一个技术声明、3个 typed token、4个 stage，固定共8条记录；每类固定字段与顺序，拒绝缺项、额外项、重复 stage、重复 JSON key、非有限数和 bool 伪整数。句柄 full/index/version 分别限制 uint32、20位索引、12位版本，消费者独立核 full 的位分解；null 哨兵与“没有记录 initial”应明确区分，不能把 full=0 当不存在。无 map 时也可记录实际 entt::null 的 full/index/version 及 mapped_nonnull=false，不强行把它伪装成未调用。

所有检查必须从原始记录重算关系，而非只信 fixture 的 `passed` 标记。消费者 PASS 仅是内容检查；整次接受还需编译/运行返回码、空诊断、无超时以及后置源码/fixture/oracle/checker 身份一致。若后置身份失败，即使已写内容检查结果也不能留整体 PASS。

运行目录必须新建且拒绝复用；共享的最终 summary/PASS 在任何动态导入/编译前清除或明确不存在。首错保留首错、已读 token/已完成阶段、原始流，不进入第二次副本；写日志等次生异常不得遮盖首错。已启动进程的超时/异常要有限收尾拥有的进程组，不只等待编译器父进程；不要求为此增加实际故障配置。普通协议仅两次同配置，不是两个不同场景，也不是跨平台验证。

建议声明加编译宏技术版本，例如 `__cplusplus` 与存在时 `__GNUC__`/`__GNUC_MINOR__`/`__GNUC_PATCHLEVEL__`，并记录 EnTT 版本宏和预期 traits；这不需要额外版本子进程，也不是安装二进制身份。不要写主机路径、指针或编译器安装指纹。宏仅描述本次构建，不证明工具链来源完整可信。

固定 argv 的 Werror/无诊断门槛合理；若首次构建出现警告，应停下来重新审查，不能预先放宽。协议的“无网络需求/无网络调用设计”与“观察到零网络系统调用”必须保持不同，当前完全没有后者证据。

结论：内容预期可冻结，必要 initial 语义修正与 schema 冻结后可进入实现审查；本报告不授权编译/执行，也不认证尚未写出的 runner。
