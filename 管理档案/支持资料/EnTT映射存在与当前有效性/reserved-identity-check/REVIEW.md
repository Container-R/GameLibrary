# 保留标识补充消费者的独立审查

2026-11-02。**接受本候选的有限事后内容检查用途。** 不将它归入旧执行输入，不重新签署旧执行结果。本审者此前参与旧文章、流程限制和新组件协议审查；此次实际重新读本候选全部代码、说明、测试及获准的四份旧输出，不声称从未接触这一主题。

## 精确绑定

| 文件 | SHA256 |
|---|---|
| check_supplement.py | 9792d5af94340891dd55b172a5b5c471ddf78be1dee970135df2ba9089ebec21 |
| test_supplement.py | 5e6a7e77278064c00e2de746a4f688a5936e9c6d9dcb0adf404bc6138de1a4a7 |
| frozen_checker.py | 788f72e5e978b90a14047822cd28d023e49c7495d75119cc856525a8cc78d732 |
| frozen_oracle.json | 90169423b365a0a3a553462caff0be05ebb6672de6f58758959b9a5c139497cf |
| README.md | a7c030bf355c91b70d9f0c7b54699b93a640e3df55fad1cb01ddab38d2cddc89 |
| CANDIDATE-HASHES.json | 304acf18b9e3951e20c069fb0191c24f18dcd44e49501de6f12d3e734e6b2883 |

已核冻结 checker/oracle 与旧 v2、v3 对应文件摘要相同。四份获准的原始八行输出逐份实际读取，内容摘要均为 `504bdd9c35c4bd06a9c589e14c662206ce87768c316495559b299172aa2b3843`。这些是输出内容身份，不是执行环境身份或执行真实性证明。

## 语义与边界

直接读取固定 EnTT 提交 `78213075654a688e9da6bc49f7f873d25c26d12c` 的 [entity.hpp](https://github.com/skypjack/entt/blob/78213075654a688e9da6bc49f7f873d25c26d12c/src/entt/entity/entity.hpp) 95–145、220–275、280–350，以及 [storage.hpp](https://github.com/skypjack/entt/blob/78213075654a688e9da6bc49f7f873d25c26d12c/src/entt/entity/storage.hpp) 950–970，支持保留索引、保留版本与本条件普通创建身份的区分。

补充在旧严格消费者之后检查 source、seed，以及加载后 mapped_now/mapped_initial 的保留位；这些值曾来自普通创建，即使随后失效也不能变成保留身份。它没有要求 externally_destroyed 的旧句柄重新有效。加载前 mapped_now 的具体全一 null 哨兵仍保留，mapped_initial 的 JSON null 仍表示尚未观察。跨阶段值、计数、类型、token 及旧句柄失效等原检查仍由逐字冻结消费者执行，不被补充替换。

两依赖先验字节摘要检查发生在导入旧消费者之前；修改或缺失均拒绝。本结论不是恶意并发修改、动态导入缓存或任意环境下的安全证明，也不是通用 EnTT 合法实体判定。未知输入仍可能包含本补充未覆盖的问题。

## 本审者实际重复与额外挑战

只运行纯 Python 消费者和测试，未调用编译器、runner、原生夹具或网络运行条件。

- `python -B test_supplement.py` 与 `python -B -O test_supplement.py`：每模式同一 5 个方法通过。实际执行其中 8 个一致修改的旧误接受反例、28 个字段位置反例、5 个旧严格条件反例、2 个依赖字节修改反例及合法/stale 对照。两模式不相加为不同原生场景。
- `check_supplement.py` 在普通及 `-O` 下分别只读消费旧 v2 两份、v3 两份 stdout：均接受。原输出确实没有保留索引或保留版本身份；空映射及失效旧句柄未被误拒绝。
- 独立 `review-results/dependency-probes.py` 在普通及 `-O` 下各执行 4 个纯反例：分别修改/移除冻结 checker、oracle。每个消费者 main 返回 1、输出 REJECTED，不回显临时位置；缺文件为 FileNotFoundError，改字节为 SupplementError。只操作独立临时副本，不改旧依赖。

本轮各命令正常结束；原始标准输出/错误保存在 `review-results/` 的 tests、archives、dependencies 对应普通/optimized 文件。独立探针没有创建原生子进程。候选原文件复核摘要未变。作者先前结果在初读目录中只有 README 摘要，本结论依据上述本次实际重复，而不将文字摘要冒称另读到作者原始日志。

## 公开范围

候选和本报告不含实际宿主目录、二进制指纹或私有回执总摘要。旧输出、代码、协议不修改；旧审查绑定继续作为历史保留。README 正确保留旧 v2 环境准备不合规的限制：消费者补充既不修复该流程，也不据此推断越界写入或宣布现有数据无效。未发现需要阻止本有限补充发表的剩余问题。
