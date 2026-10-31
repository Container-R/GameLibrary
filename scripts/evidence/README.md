# 当前 Godot 证据档案一致性校验器

标准库、只读工具；不运行夹具/引擎，不安装或联网，也不修改档案。只处理 `registry.json` 显式登记的当前证据，禁止自动扫描所有 summary 后把历史来源当成当前来源。

## 运行

```sh
python3 verify.py /path/to/GameLibrary
python3 test_verify.py
```

以仓库根为参数，输出 JSON 至 stdout；一致性失败退出1，全通过退出0。无效注册表属于配置错误，抛错且非零退出。不得对不可信方正在并发修改的目录声称安全：路径 resolve 和实际读取之间未实现无竞态文件句柄绑定。目录应为静止的审查快照。

## 当前显式范围

五个夹具 fixed-step、pause-input、focus-boundary、import-boundary、navigation-sync，共65项检查（每个 manifest 项内部还检查各文件）：

- 当前 summary `source_sha256` 的完整键集合及每个实际文件 SHA256；review summary 也对应同一当前归档源文件，而不是不存在的复跑临时目录。
- 四个含 reviewer summary 的夹具：作者/审查者 source map、二进制 SHA256 元数据及 version 字段一致性。**不读取或验证 `/usr/local/bin/godot`**，不声称证实真正使用该二进制。fixed-step 当前 summary 无 binary_sha256、无另存 current reviewer summary，未伪造该覆盖。
- 明确选定的作者/审查者 RESULT_JSON 日志，恰好一条记录，与独立解析结果 JSON 比对；JSON 拒绝重复键、NaN/Infinity 及溢出为非有限浮点数的指数值（如1e999）；比较保留布尔/数值类型差异。并不校验每个摘要中的衍生统计或退出码。
- import 的 seed、configured-inputs 文件 manifest 及 kept initial manifest 一致性。未将临时路径当可重现文件读取。
- navigation 的诊断源 variant 快照、当前 base main、诊断 runner 哈希及 binary metadata、诊断 stdout/parsed JSON。

显式排除 fixed-step `results/author-run-summary.json`（历史作者结果）与 navigation `initial-map-only-predicate`（保留失败初稿）。这些仍是合法历史证据，不应和当前源混比。没有自动更新注册表；新增/移除当前文件需审查注册表变更。

## 实际结果与测试

2026-10-31：针对 `gamelibrary-work` 静态档案执行65项检查，65通过、0失败；没有发现本范围内真正不一致。原始报告 `archive-report.json`。9项隔离单元测试全部通过，覆盖文件损坏、缺失、路径逃逸、外部符号链接、坏JSON/重复键/非有限数值、manifest漏项、日志缺失/重复/类型差异与空/重复注册项。只向 TemporaryDirectory 写单元测试数据，自动清理。

一致性既不证明执行真实发生，也不证明语义正确、测试完整、来源可信或防恶意篡改：攻击者同时改源与声明仍可一致。哈希不等于签名。没有下载执行任何归档代码；只执行本原创 verifier 与隔离测试。代码使用显式错误检查，不依赖 assert，不受 `-O` 影响。运行日志和工具文件哈希列于 `SHA256SUMS`。

独立审查发现并修复：最初 parse_constant 只拦截NaN字面量，1e999仍可由默认parse_float溢出为inf；现对parse_float显式检查math.isfinite，并在坏JSON测试加入正负溢出值。此缺陷来自隔离构造证据，不是实际档案发现。
