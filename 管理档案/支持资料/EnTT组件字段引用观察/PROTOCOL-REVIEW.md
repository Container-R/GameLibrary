# EnTT Link 字段协议与独立字面关系审查

2026-11-02。**接受进入实现前代码设计；不授权编译或原生执行。** 绑定 PROTOCOL.md `d7d6efc355774ea1489c075865e116fbc147938e23c9b6411d2651344a4aceee`、EXPECTED-SCHEMA.md `1c4e220295a133ed9247f8f033688eff7d28a96fba067fc90c147b31b9a49dcc`。

已完整读取纠正后的 `entt-component-reference-source-gate/GATE-REVIEW-v2.md`（指定 3a87f6d6…），不采用被撤回的双参数调用判断。该文件不在 native 目录；首次本地定位失败后已按实际路径读取。

## 独立推导依据

亲自重开官方固定提交 `78213075654a688e9da6bc49f7f873d25c26d12c` 的 snapshot.hpp 50–115、270–290、366–455，官方 snapshot.cpp 测试 757–807，以及 entity.hpp 25–90。读取源码及测试文本，没有执行官方测试。

writer 先输出存储计数。实体分支另输出活跃数和每个实体，两个无销毁实体因此为2、2、两个句柄，共4次。普通非空 Link 的 reach 元组被 std::apply 展开后，lambda 内逗号折叠逐个调用 archive；单个组件为计数、所属实体、Link 值，共3次单参数调用，不是一次 owner+Link 双参数调用。

连续加载实体的 restore 建立两个本地对应。组件分支读取 owner 并 restore，再 archive(elem)，随后 emplace(map(owner), elem)。本条件的 archive 只复制值，所以 owner 已转成本地，Link.target 仍为来源值。官方扩展测试是在自定义 archive 内主动改 target，不是默认 get 自动调用私有 update。此次不执行那个转换正例。

## 独立 oracle

另写 `independent-oracle.json`，从上述路径推导四加三个 typed token 和三阶段关系，使用 R/H/S/B/L 符号，不固定未来分配整数。允许两实体 token 的实际存储次序，但不能排序后比较两次输出；两次相同条件须保持完整实际记录一致。

除了 schema 的基本类型、计数和一致性条件，明确了一项容易漏检的推导：最终 target 的本地 valid 不固定真假，但目标活跃集合在这个封闭条件下恰为 seed、mapped_box、mapped_holder，因此实际布尔值应与完整 target 是否在该集合相符。这不预言它必为 seed，也不证明业务对象正确。字段等于 seed 的布尔值同样必须和完整值比较一致。请在后续 checker 中落实这类关系，不能把“描述性”误解为允许自相矛盾。

协议具备足够区分力：先确认 mapped_box != remote_box，才读组件；不满足即止，不临时增加 seed。prepared map 是真实空实体哨兵，而未发生的字段读取是 JSON null；无效 holder 不得为了输出完整行而执行组件 get。任何截断仅能作为失败保留。

## 后续源审必须落实的门槛

同意新 build/native phase 根分别准备五位置，紧邻 Popen 再验证；源和输入冻结、真实输出先记录后判定、安全前置检查、首错停止、部分目录失败与进程收尾分别处理。两副本最多两构建两原生只是未来预算，不是现在已执行次数。helper 不能被表述为沙箱或全写入追踪。

本次仅协议及原源审阅和独立 JSON 预期写作；没有实现、导入夹具、运行测试、编译或原生调用。旧 v2/v3 无组件结果不参与新组件预期的证明。

## 最终修订绑定闭合

作者随后提供协议 `faa507b4a1cb3c3efd274c174a6a8e32377983db4aa9685871d0c65b5b47aa2d`、schema `b89e746367b99ece69066a4a279b32d678a7bf2cb6fc615a8a04be53becd812c`。实际差分只增加上述最终 valid 与三活跃句柄集合的关系，并将通用进程标识缩写换为中文。该关系已由本审者在收到修订前独立写入 oracle，不依赖作者字段自报。

接受这两个最终文件进入代码审查阶段。独立 oracle 只更新绑定的协议/schema 摘要，其预期关系未改变。初次 oracle 与本报告初版保存在 `history/independent-proposal-v1/`，不把旧绑定假装成最终文件。仍未授权或执行代码及原生测试。
