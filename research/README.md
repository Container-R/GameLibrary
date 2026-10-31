# 研究记录与可复核证据

任务以 [队列](../.agent/queue.json) 和 [恢复状态](../.agent/state.json) 为准；草稿、来源审计、模型测试和实际运行证据不混称为完整生产验证。成熟知识见 [CATALOG](../CATALOG.md)。

## 原创 Python 模型

```sh
python3 scripts/run_model_tests.py
```

运行前审阅代码。标准库模型无依赖安装或网络请求；每个 `research/experiments/*/test_*.py` 独立进程执行，任一失败或未找到测试均返回非零。日志文件是记录时的输出，不会被该入口自动更新。通过不证明引擎、设备、声音、网络或平台集成；其中存档在途写反例断言的是限制，而非保护成功。

[有种子的深度对抗实验](experiments/deep-model-qa/README.md)单独执行，保留独立判据、模型哈希与故障变异结果；增加种子数不等于增加真实平台覆盖。

## 实际 Godot 引擎证据

以下夹具需要本机已有 Godot，不由纯 Python 模型入口自动触发。各自记录二进制、源哈希和执行边界；其运行器可能替换自己的 results，应先保留需要的历史输出。

- [固定规则与表现回调](experiments/godot-fixed-step/README.md)：6 组实际进程；人工 `fixed-fps` 与实时 `max-fps` 分开，不证明设备输入、GPU 或物理确定性。
- [暂停与合成输入队列](experiments/godot-pause-input/README.md)：实际输入 API 分发与常驻应用队列反例；固定心跳排除空洞暂停观察，不是物理设备测试。
- [焦点恢复的实例身份](experiments/godot-focus-boundary/README.md)：实际 Viewport owner、信号和延迟调用；不是 Unity、视觉或完整模态输入墙验收。
- [干净检出后的资产导入](experiments/godot-import-boundary/README.md)：遗漏 sidecar 时仍可加载、UID 相同但纹理尺寸不同；[工程契约](../solutions/engine/asset-import-intent-contract.md)区分源文件、导入意图与生成缓存。

- [导航就绪与部分路径](experiments/godot-navigation-sync/README.md)：实际地图/region同步阶段、空路径与非空部分路径；不证明持续异步事务或角色运动。

## 实际文件系统反例

[Linux/tmpfs 路径替换](experiments/filesystem-save-publication/README.md)：完整旧版本仍可覆盖已发布的新版本；安排好的预调用重检查仅是有限对照，不是 CAS、持久性或 Steam 验证。

## 固定版本来源审计：没有运行时执行

- [ink v1.2.1 宿主边界](source-notes/ink-v1.2.1-host-boundary.md)：General 与便捷重载默认纯度不同；状态格式不等于项目内容或宿主检查点身份。没有 C# 运行证据，不作为成熟叙事文章计入索引。
- [多语言导入策略线索](source-notes/asset-import-policy-availability.md)：日本语历史Unity文档与可访问6000.0英文正文对照；不是独立工作室案例，也不形成当前DLL建议。
- [音频来源深度审查](audits/audio-source-depth-review.md)：固定 Wwise 历史提交与 FMOD 启动失败回调边界。

## 审查与分类历史

[14篇时的覆盖/优先级快照](audits/2026-10-31-coverage-priority.md)将下一项转向关键非语音声音的可访问性验收；这是带日期的选择依据，不是不断增长的实时完成率。

[初始七篇覆盖快照](audits/initial-coverage-and-taxonomy.md)不是实时完成率；其后 ACCESS 兼容拆分见 [分类说明](../taxonomy/README.md)。[存档草稿对抗审查](audits/cloud-save-adversarial-review.md)保留发布前失败和修复回归。各实际夹具的独立复核记录在其 README 中定位，同一机器的重复验证不冒称跨平台复现。

## 只读证据一致性检查

从仓库根运行：

```sh
python3 scripts/evidence/verify.py .
python3 scripts/evidence/test_verify.py
```

[工具说明与显式注册表](../scripts/evidence/README.md)覆盖九个运行夹具（六个 Godot、一个 ICU、两个 SQLite）阶段的103项一致性检查；[独立工具审查](audits/evidence-integrity/AUDIT.md)保留数值溢出解析缺陷及修正。它不启动归档夹具或引擎，不检查当前安装的Godot二进制，不以一致性证明执行真实性、来源可信或语义正确。历史作者摘要和失败初稿不会误当当前源码校验；新增当前证据需审查注册表。

9项工具单元测试与游戏模型的86项测试是不同范围，103项文件/记录检查也不是103项运行行为测试。运行前仍应审阅工具代码；应针对静止快照，不能在恶意并发改写目录上宣称无竞态安全。

精确字节哈希也会发现换行变化。仓库`.gitattributes`使用`* -text`禁止Git自动换行转换，而不禁止普通文本diff；这是[Git官方属性语义](https://git-scm.com/docs/gitattributes)，不是字符编码或运行时兼容保证。保留原始字节比替换换行后继续沿用旧哈希更重要。[本地策略检查](audits/evidence-integrity/check_git_byte_policy.py)在临时Git仓库设`core.autocrlf=true`后验证检出字节与文本diff；它是Linux/Git2.52.0的有限测试，不是Windows执行测试，也不修改用户全局Git配置。该检查需Git，和只需Python标准库的校验器分开。

[Godot 运行来源边界](source-notes/godot-runtime-provenance.md)区分公开源码、程序自报版本与文件身份；[调用新鲜度](source-notes/runner-invocation-freshness.md)说明历史 PASS 不等于最近调用成功。

[动画方法轨 seek 与 advance](experiments/godot-animation-events/README.md)保留初始错误假设与六例实际回调、独立复跑和明确构建身份限制。

## 内容与职责证据

- [关键声音信息合同](../solutions/accessibility/critical-sound-information-contract.md)及[原创假设遭遇表](case-notes/critical-sound-encounter.md)：不是实际玩家研究。
- [试玩干预证据](../solutions/production/playtest-intervention-evidence.md)：不将提示后完成当作独立发现。
- [Steam 胶囊素材交付](source-notes/steam-capsule-handoff.md)：规则核对不是平台审核或销量证据。
- [游戏 QA 职责](../roles/qa/game-quality-assurance.md)与[关卡策划职责](../roles/design/level-designer.md)：多家雇主和制作资料分层，原创交付矩阵不是内部规程。
- [精选阅读路线](../DISCOVERY.md)连接五个已归档岗位与一个跨学科问题，完整清单仍见 CATALOG。

[ICU MessageFormat 有限实测](experiments/icu-message-boundary/README.md)保留四种输入、独立复跑及运行器拒绝路径，不是 Unity、布局或 LQA 验证。

[SQLite 提交与应答](experiments/sqlite-ledger-boundary/README.md)保存直接退出、重新读取和同键重试；[双写者握手](experiments/sqlite-writer-contention/README.md)仅补一个 BEGIN BUSY 序列。不是断电持久性、生产重试策略或远程授权保证。

[BC纹理逐mip预算](experiments/texture-block-budget/README.md)增加有限CPU布局与逐级包装解码；十夹具阶段109项档案一致性检查，不是109项运行测试。

[交错网格属性](experiments/mesh-attribute-contract/README.md)区分合法字节的错误解释、非法view跨度与独立几何意图。十一夹具阶段115项档案一致性检查；不替代DCC/引擎/GPU验收。

[合成尝试分母](experiments/telemetry-attempt-contract/README.md)保留两份as-of与身份/冲突/未知状态，不能当真实玩家研究。当前十二夹具120项档案检查，不是120次行为测试。

[ink内容恢复深审](source-notes/ink-save-content-compatibility.md)是固定源码调用链，不是新运行时实验或新增已验证文章。[19:00离线回归](audits/release-regression-1900/README.md)重跑86个原有模型方法及隔离工具测试；120档案检查正常/-O一致，无引擎/数据库/解码器重跑。

[Destiny配置准入与数据恢复案例](../case-studies/liveops/destiny-config-admission-rollback.md)分析历史第一方复盘，分开当时已部署措施、后续承诺和原创未执行验收协议；[独立来源审查](audits/liveops-destiny-2020/REVIEW.md)。没有事故复现或新增运行测试。

[音乐主体 PCM 帧区间](../solutions/music/pcm-loop-frame-contract.md)通过原创 marker WAV 的实际离线 FFmpeg 提取，分离半开区间与 inclusive 循环端点；[实验与无损归档](experiments/music-loop-frame-contract/README.md)、[独立复验](experiments/music-loop-frame-contract/review/REVIEW.md)、[集成归档检查](audits/music-frame-integration/README.md)。不包含设备播放或 FMOD 运行。

[日本 Cygames 叙事制作交接案例](../case-studies/narrative/cygames-scenario-voice-handoff.md)使用实际可读的日语第一方博客，区分历史工具采用过程和原创未执行验收矩阵；[独立来源审查](audits/cygames-scenario-handoff/REVIEW.md)。未假称读完幻灯片或测得制作效率。

[精灵 alpha 表示交接](../solutions/art2d/alpha-association-contract.md)通过实际 CPU 数值 buffer 转换与合成，检验 associated 字节被当成 straight 后的重复衰减；[原始证据](experiments/art2d-alpha-contract/README.md)、[独立复验](experiments/art2d-alpha-contract/review/REVIEW.md)。未做图片作品、PNG、引擎、颜色管理或可见暗边验证。
