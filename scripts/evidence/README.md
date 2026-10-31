# 显式登记证据档案一致性校验器

标准库、只读工具；不运行夹具/引擎，不安装或联网，也不修改档案。只处理 `registry.json` 显式登记并绑定对应源码快照的证据，包括明确登记的历史阶段；禁止自动扫描所有 summary，或把历史结果误配到最新源码。

## 运行

```sh
python3 verify.py /path/to/GameLibrary
python3 test_verify.py
```

以仓库根为参数，输出 JSON 至 stdout；一致性失败退出1，全通过退出0。无效注册表属于配置错误，抛错且非零退出。不得对不可信方正在并发修改的目录声称安全：路径 resolve 和实际读取之间未实现无竞态文件句柄绑定。目录应为静止的审查快照。

## 历史 103 项阶段的范围说明

当时九个夹具：六个 Godot 夹具（fixed-step、pause-input、focus-boundary、import-boundary、navigation-sync、animation-events）、ICU MessageFormat、SQLite ledger 与 SQLite writer-contention，共 103 项检查（每个 manifest 项内部还检查各文件）：

- 当前 summary `source_sha256` 的完整键集合及每个实际文件 SHA256；review summary 也对应同一当前归档源文件，而不是不存在的复跑临时目录。
- 五个含 reviewer summary 的 Godot 夹具：作者/审查者 source map、二进制 SHA256 元数据及 version 字段一致性。**不读取或验证 `/usr/local/bin/godot`**，不声称证实真正使用该二进制。fixed-step 当前 summary 无 binary_sha256、无另存 current reviewer summary，未伪造该覆盖。
- 明确选定的作者/审查者 RESULT_JSON 日志，恰好一条记录，与独立解析结果 JSON 比对；JSON 拒绝重复键、NaN/Infinity 及溢出为非有限浮点数的指数值（如1e999）；比较保留布尔/数值类型差异。并不校验每个摘要中的衍生统计或退出码。
- import 的 seed、configured-inputs 文件 manifest 及 kept initial manifest 一致性。未将临时路径当可重现文件读取。
- navigation 的诊断源 variant 快照、当前 base main、诊断 runner 哈希及 binary metadata、诊断 stdout/parsed JSON。

显式排除 fixed-step `results/author-run-summary.json`（历史作者结果）与 navigation `initial-map-only-predicate`（保留失败初稿）。另排除 animation-events 的 `historical-initial` 与 `historical-corrected-four`，避免将失败假设或旧四例源与当前六例混比。这些仍是合法历史证据，不应和最新源混比。历史证据并非一概排除：例如 isolation 的初始/最终阶段已分别绑定自己的源码快照。注册表不会自动更新；新增、移除或调整绑定均需审查。

## 当前注册范围与历史结果

本次快照的 `registry.json` 显式登记 340 项一致性检查，涵盖后续追加的证据及 isolation 初始/最终阶段的来源与日志绑定。340 是登记项数，不是夹具数、子进程数或运行测试数；每项只检查其声明字段，完整语义与制品验收仍见对应独立 checker。以下 65/82/95/99/103 等数值是各历史阶段记录，不描述当前全部范围。

2026-10-31：初次五夹具65项报告保留于 `archive-report-initial65.json`。新增动画夹具的17项显式检查后，当时六夹具82项全部通过，报告保留为 `archive-report-82.json`。新增 ICU 的13项显式检查后，当时七夹具95项全部通过，报告保留为 `archive-report-95.json`。新增 SQLite 两个 source manifest 与两组 metadata/source 比较后，当时八夹具99项报告保留为 `archive-report-99.json`。写者竞争新增两组 source manifest 与两组 source/metadata 比较后，当时九夹具103项全部通过，历史报告为 `archive-report-103.json`。上述增量均为扩展档案检查范围，不是对应数量的新增引擎或数据库行为测试。9项隔离单元测试全部通过，覆盖文件损坏、缺失、路径逃逸、外部符号链接、坏JSON/重复键/非有限数值、manifest漏项、日志缺失/重复/类型差异与空/重复注册项。只向 TemporaryDirectory 写单元测试数据，自动清理。

一致性既不证明执行真实发生，也不证明语义正确、测试完整、来源可信或防恶意篡改：攻击者同时改源与声明仍可一致。哈希不等于签名。没有下载执行任何归档代码；只执行本原创 verifier 与隔离测试。代码使用显式错误检查，不依赖 assert，不受 `-O` 影响。运行日志和工具文件哈希列于 `SHA256SUMS`。

独立审查发现并修复：最初 parse_constant 只拦截NaN字面量，1e999仍可由默认parse_float溢出为inf；现对parse_float显式检查math.isfinite，并在坏JSON测试加入正负溢出值。此缺陷来自隔离构造证据，不是实际档案发现。

已安装程序自报版本与公开标签提交存在[未解决身份对应](../../research/source-notes/godot-runtime-provenance.md)。即使作者与复核者二进制摘要相同，也不能由本工具认证官方发行来源。

ICU 的两份 source manifest、八个原始日志/解析结果与三组元数据比较只检查归档一致性；不读取本机 ICU 库、不认证其实际加载依赖或官方来源。四个作者与四个审查者子进程的行为解释见该夹具，不把新增13项归档检查当成13个格式化测试。

ICU 当前 registry 对应加固后的 runner；historical-runner-v1 与 runner-negative 的注入输入/旧结果不参与当前来源比对。独立负例证明拒绝路径，不是额外 ICU 功能样例。

SQLite 的终止进程有意没有 RESULT_JSON，不纳入现有单载荷 log 类型；其 CONFIG/CHECKPOINT/RESULT_JSON、退出码、持久结果由独立 raw checker 验收。四个 base64 数据库的解码字节摘要另核对，不在该历史103项范围内；不能声称本注册表覆盖了全部 SQLite 原始证据。

写者竞争的 EVENT/CONFIG 与父协议先后由独立 raw checker 验证，base64 由其另行解码核对；这里只登记 source/metadata 四项，不冒充协议行为检查。

纹理夹具新增两组 source manifest 与四组版本/来源字段比较，当时十夹具109项检查（历史报告archive-report-109.json）；103项历史报告保留于 `archive-report-103.json`。这6项不验证解码器身份、像素、DDS语义或GPU行为；独立原始制品checker另存于纹理review目录。

纹理stdout使用 `RESULT_JSON `（空格），而当前log规则只接受 `RESULT_JSON=`；未把它注册为兼容日志。集成时另行精确解析一条空格前缀记录并与summary比较，不修改既有verifier或计入109项。

网格夹具新增两份source manifest及四组source/Python/制品哈希字段比较，当时十一夹具115项（历史archive-report-115.json）。不是115次运行测试，也不验证几何语义、官方validator或GPU；原始空格前缀stdout另行比较，字面几何oracle见该夹具review。

合成遥测报表新增两份source manifest和三组source/Python/输入哈希字段比较，当时十二夹具120项。不是120次玩家、服务或运行试验；actual输入SHA、空格前缀stdout、两份as-of输出另行核对，独立字面人口oracle见该夹具review。

## Additive environment helper for future callers

[isolation.py](isolation.py) provides `prepare_environment(base_env, owned_root)` and `validate_environment(env, owned_root)`. From the repository root, import with `from scripts.evidence.isolation import prepare_environment, validate_environment`. The caller supplies a fresh, exclusively owned absolute temporary root and retains it through all child activity; validation must occur immediately before spawning. Only HOME, XDG_CACHE_HOME, XDG_CONFIG_HOME, XDG_DATA_HOME and TMPDIR are selected. Preserve the returned five-key manifest, not the complete environment. Partial creation cleanup remains caller-owned. This is not a sandbox, complete XDG implementation, race defense or crash-prevention guarantee.

[Protocol, original tests and independent evidence](../../research/audits/runner-isolation/README.md) distinguish initial and final source stages and eight synthetic children from zero engine runs. [Source contract](../../research/source-notes/runner-environment-contract.md) documents limits. Existing runners and fresh-harness registry/adapters are unchanged; callers are **not automatically migrated**.
