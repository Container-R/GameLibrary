# Detour 容量单元：独立实现审查

2026-11-01。**接受以下最终冻结候选提交主编决定是否单独授权一次构建/运行。** 本审查自身不授权执行，没有调用编译器、fixture 或 Detour。实际执行仅 Python 纯合成检查；没有真实子进程/信号、网络或引擎测试。当前 native 执行目录不存在。

## 最终身份与阅读范围

完整阅读 fixture.cpp、expected.json、validate.py、test_validate.py、run.py、IMPLEMENTATION.md、CODE-MANIFEST.json；复用此前独立 PRE-REVIEW 的固定上游实际源阅读，不假称这次重新认证所有 Detour 实现。另实际核对 pre-setup-review 的 fixture 差异，以及本次 consumer 标签修正差异。

| 文件 | SHA256 |
|---|---|
| CODE-MANIFEST.json | 84a9b515ec726d1c0d9fbd68c4fd869fe772c36ecf1ac98c6320f5b0d01ac913 |
| fixture.cpp | dce68bd7eeb9508f72e1c207c0de67e36cca578934ff49f5d70747326728c085 |
| expected.json | c30414c81af4d665d787312aba22f0f259556bde645013dac4bba43efc609140 |
| validate.py | c8382e08a6f9b4a9c8fcf536027164c1d28c13d394521de8b85d105ed9abfc6d |
| test_validate.py | d23e455abb06e2b5f6dccae57d16830840bc8f471a40c3a9f39edf56abf77639 |
| run.py | 1e4b9c5391af386c682b13f9bddb19a78f13720dc2bc97112e2385b74a4c88b9 |
| PROTOCOL.md | a9a385b58b3adc60ccc8f460e937083ee34348c142c6f7f5c9d4409f157c1406 |
| SOURCE-MANIFEST.json | 0cfadaf8b16ebfc537259734b752f75a3baeac2186245d30191c6fe35d76c9ea |

独立检查最终 identity 函数实际返回 7 项候选及 16 项上游身份，全部匹配。上游逐项同时核 SHA256/Git blob；完整七 cpp 明列于 BUILD，不使用 glob 加入未知编译单元。

## 代码判断

- 几何、邻接、flags/area、两查询容量与预审一致。实际 tile 顶点、poly 属性、neis、links、refs、header 和池容量均读取对象记录；refs 必须非零互异有效，链接的 target/ref/edge/side 与预期链同时约束。0 哨兵及每次全部三槽保留。
- query.init 在 mesh 校验后，计数变量在真实调用前递增；两次 findPath 使用同一 query。第一行原始状态/count/path 写入后立即校验，失败以 `_Exit(1)` 终止，不进入第二行。精确状态预期仍是 0x40000010 与 0x40000000；不是只看 success。
- 初始化/不确定失败通过 require→emit→flush→`std::_Exit`，nav/query 为堆对象，不因退出 require 而走部分对象栈析构；正常全部通过才 delete query、delete nav。没有故意制造 OOM 或损坏内存。异常、资源耗尽或库内崩溃未必能生成完整失败 JSON；runner 对非零/缺输出仍拒绝，不能把这条停止策略叫通用故障清理保证。
- 主编先前指出的三个源审问题已实改：mesh 先于 query.init；输入属性由 params、header 值由实际 header 读出；未拼完 setup 的内容以明确 `partial_setup_text` 字符串保留，不能伪装成成功 JSON 对象。这是执行前修订，不是原生失败后调整输入。
- consumer 固定 expected 原字节 SHA，不从观察反推 oracle。只让本次三个非零 32 位 ref 和合理正 data_size 取实际值，余下递归逐类型精确比对；拒绝重复键、非有限数、bool 冒充数字、缺/多/错序行及未知 ref。合成记录能够通过只说明消费器合同，无法鉴别任意伪造 JSON 的真实性；真实调用归因仍需要已审 fixture 和 runner 身份链。
- runner 排他创建一次 attempt 目录，旧目录存在不覆写。构建非零/任何未审诊断不进入 native；native 非零、stderr、空/坏 JSON 不通过。源码与复制品前后核验，后检失败不返回整体 PASS；异常/超时清理即使 leader 已退出仍尝试进程组终止。所有这些在本轮是代码和 mock 结果，没有实际编译或进程清理实证。

## 本轮发现与闭合

独立 mock 有效消费之后改变临时源副本：runner 返回 1、receipt=fail，但此前写出的 validation.json 留有 pass。**原 runner 并未错误返回整次 PASS**；风险是只拿消费器文件误称整个执行通过。

已采用最小语义修正：consumer 结果明确 `result_kind=consumer_only`，以及 `overall_acceptance_requires=receipt.json status=pass after identity checks`；说明文同步解释。最终差异仅返回标签、对应控制断言与文档/清单绑定，fixture、runner、oracle 不变。历史清单 1a5e9e… 和文件保存在 `history/pre-consumer-label-review`。不得脱离最终 receipt 把 validation.json 当整体接受记录。

更早首版 475a… 的 setup 问题保存在 `history/pre-setup-review`。没有隐去失败发现，也没有从原生观察反向改期望。

## 实际纯检查

在候选目录分别实际执行：

```
python -B -m unittest -v test_validate
python -B -O -m unittest -v test_validate
python -B independent/challenge.py
python -B -O independent/challenge.py
```

最终作者集合普通/-O 各 **10 方法**通过；独立集合普通/-O 各 **9 方法**通过。两模式是相同用例，不计成双倍覆盖。独立九项包括：两行字面状态；额外 FAILURE/IN_PROGRESS/PARTIAL/OUT_OF_NODES 位；真实调用计数、池容量/header 错值；link ref 与 target 不一致；缺输出/null/重复键/多对象；源身份；有效合成控制；构建诊断/非零阻止 native；native 非零和身份后检失败；mock 超时/非零保留部分 stdout 并调用 cleanup。

独立 runner-main 测试全部替换 command 并禁止真实 Popen；-O 下仅为这些 mock 场景模拟 runner 要求的 normal-mode flag，其余解释器仍是真正 -O。没有以此称 runner 支持直接 -O 运行。command 单元也使用假 child 和假 cleanup，不发送信号。

独立测试初次对 sys.flags 使用过宽 Mock，破坏 importlib 的其他 flags 读取，使正控制失败；已保留 `independent/history/flag-mock-error`，改为保留其他真实 flag 的代理后复跑。该失败是审者测试装置问题，不是候选 native 或消费器失败；未改变两行 oracle。

独立挑战脚本 SHA256：`07fef5133015b688f4504844e286280a06c2eacda0173d7b534589293d6d5345`。
最终普通输出：`91e858e8ab0cbbdd95f5c555d26c0027f27cb2c67b8c30ecf2a105f7acb0173c`。
最终 -O 输出：`85ff5f1d9eab3063eb35a0d7d44a7ea39c7da1238eb1dd0b21b8e2379e6e3a21`。

## 仍未证明

零原生查询、零构建。本审查没有证明编译成功、两行 native 实际成立、任意坏指针防护、所有内存访问安全、进程组实际清理、性能、节点耗尽、权重路线或真实移动。任何下一次构建警告/失败均须保留停止，由主编另行决策；不自动抑制警告或更换输入。

## v2 精确诊断门槛：有限差异闭合

2026-11-01，首构建停止后另作只读 diff 与纯合成复核；不是自动批准第二次执行。新绑定：

- CODE-MANIFEST.json：`5cb938c46fecce826907b4f1555b283f3a2b742be2cf9ab1a73b65a758210877`。
- run.py：`8f01a64defe594fd2ac97d0790274163548b93859908b8489fea6986a6a672c2`。
- PROTOCOL.md：`5277d072502002256de47bb560789302bfbf3fab495ab6f7f4d781043ab2cc7f`。
- test_validate.py：`e71d47d37fc8b05ecb16a867faf4a5ca26619e753f152d5f6df4c53cb7c1d101`。
- reviewed-build-stderr.txt：`d887b09f1c4f304b009fbfbcf61834c5d71dd80a44d8cc1cdb7f9978952f0bd5`，实际逐字节等于首次 build.stderr。

fixture、expected、validate、SOURCE-MANIFEST 与 attempt-001 副本实际逐字节相同，完整 BUILD 列表/旗标未变。新代码只增加固定 attempt-002、受信任诊断文件和 validate_build 门槛，并在 receipt 标记 empty/reviewed_warning；协议/纯测试同步。8 项候选+16 项上游＝24 项，独立测试明确将原固定计数23改24，而非从结果猜计数。

validate_build 每次先核受信任文件原字节 SHA，即使 stderr 为空也不跳过。严格整数 returncode=0、stdout 空，stderr 只允许空或整份精确相等。真实 command 函数还会先拒绝非零退出。任何字节变化/新增诊断/其他文件警告均未得到放行。初次 attempt-001 仍为 fail/build、只有一项 build 记录；审查结束时 attempt-002 不存在。

独立实际复跑同样四条纯命令：作者集合普通/-O 各 **13 方法**通过，独立集合普通/-O 各 **11 方法**通过。独立新增精确 warning 正控制（包括 mock 完整 runner 流程）、改为 note/截尾/追加字节、非零/错误类型返回码，以及受信任诊断文件缺失或篡改时即使空 stderr 也拒绝。原有缺输出、首阶段诊断停止、身份后检失败等仍通过。mock command 现在显式补模拟 process record 的 returncode；不是实际构建进程。

独立脚本新 SHA：`165be1ae1b45451980b5846b9a87c4a25102a4946642efe2f43bb4c8e64bca76`。旧脚本保留 `independent/history/pre-v2`；本轮输出为 `independent/AUTHOR-v2-normal.txt`、`AUTHOR-v2-optimized.txt`、`PURE-v2-normal.txt`、`PURE-v2-optimized.txt`。

**接受该最小 v2 候选供主编另行决定一次新尝试。** 已审诊断保留不等于跨平台内存安全证明；本独立复核没有第二次构建或原生查询。首次失败及诊断边界详见 BUILD-DIAGNOSTIC-REVIEW.md，历史判断不被本附录倒改。


公开归档说明：已将早期研究副本的目录前缀归一化；这些历史定位不表示本归档附带原执行目录。可复现输入与实际观察以README映射为准，技术结果未改，本文件不是原审查原字节副本。
