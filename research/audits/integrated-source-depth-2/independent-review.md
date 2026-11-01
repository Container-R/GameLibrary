# 三项来源增量的独立正文复核

2026-11-01 UTC。**结论：本次限定的三个增量中，未发现缺失前提或来源误读造成的实质性阻断问题。** 不认证旧全文、实际执行、完整资源管理器或全仓库安全。

## 独立性、快照与限制

先读了本目录 `review.md`，因此本次不是盲审。本人未参与这三项新增来源门或新增段落的选题、起草；但早前参与过音乐生命周期旧模型/正文及构建岗位旧稿的审查，不能称对整篇文章毫无既往接触。此次决定性版本化来源均重新打开，不把前一审查者的结论当作来源证据。

通过 GitHub 插件直接读取公开提交 **`c9120627e9b3070066f5c9c857d2b64e18391d62`**，对返回全文 UTF-8 独立计算 SHA-256：

| 文件 | 全文件 SHA-256 | 实际裁决范围 |
|---|---|---|
| `research/source-notes/box2d-sensor-step-and-sweep.md` | `23e50a2eb011aea2f602466d5fdfcaf2161b3d6fb623d759fe2f306f94e5e0a7` | 全文 |
| `roles/engine/build-engineer.md` | `e6973e93f1a37e63272f154646c70471b81aee524d0b73bd15da62ff06570c2c` | “生成工具也是输入”小节及必要前后衔接 |
| `solutions/audio/music-state-transition-contract.md` | `0fb9f95ae8070e74c803275dec6b54ca46ab4f0efd297cf680439f54ce4294cb` | “场景退出时，事件释放与 bank 持有是两项责任”及生命周期衔接 |

全文返回/哈希不代表审查范围扩大。未读取关联运行档案或执行环境资料；没有安装、配置、运行构建/引擎/音频或测试，没有 GitHub 写入。本地仅保存此文字审查。

## 1. Box2D：版本差异与扫掠前提

重新取读两份固定源码，而非只读文档结论：

- v3.1.1 `8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3`：[world.c 730–793](https://github.com/erincatto/box2d/blob/8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3/src/world.c#L730-L793)、[sensor.c 47–106](https://github.com/erincatto/box2d/blob/8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3/src/sensor.c#L47-L106)、[solver.c 212–245、425–450](https://github.com/erincatto/box2d/blob/8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3/src/solver.c#L212-L450)、[simulation.md Sensors](https://github.com/erincatto/box2d/blob/8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3/docs/simulation.md#L922-L956)。
- main `dd8bd3fb525f0f33f1079f8ca3c5770783c44a53`：[solver.c 138–215、287–312、358–425、542–550](https://github.com/erincatto/box2d/blob/dd8bd3fb525f0f33f1079f8ca3c5770783c44a53/src/solver.c#L138-L550)、[simulation.md 1071–1103](https://github.com/erincatto/box2d/blob/dd8bd3fb525f0f33f1079f8ca3c5770783c44a53/docs/simulation.md#L1071-L1103)。

对抗检查：旧版步末占用检查是否被误写为每子步扫掠；新版暂存候选是否被误写为最终事件；运动 sensor 或任意数量是否被偷渡进保证。正文均保留正确边界。特别是候选处 `<=` 与最终转交 `<` 的差别、八项暂存容量、两个形状的事件开关和 fast shape 自身 sensor 排除，均不推翻正文的有限结论。

源码对普通 fast body 查询静态树，bullet 才额外查询其他树。因此“非移动 sensor”应继续按正文中的**文档支持情形及待验证方案**解释，不能扩成任意 body 类型、任意 transform 操作均可靠；当前正文没有作这种保证，也没有给 begin/end 全链路或交付帧承诺。无需为此强行新增算法。

## 2. CMake：有序不等于失效传播

重新取读 `6acf7153156bb45038be62e79a32ed5a6ea2d00e` 的 [add_custom_command.rst 35–44、138–175](https://github.com/Kitware/CMake/blob/6acf7153156bb45038be62e79a32ed5a6ea2d00e/Help/command/add_custom_command.rst#L35-L175)和 [CMP0112.rst 全文](https://github.com/Kitware/CMake/blob/6acf7153156bb45038be62e79a32ed5a6ea2d00e/Help/policy/CMP0112.rst)。

正文已提供同目录消费 target，使单输出规则进入构建图；不是只有一个不会被消费的命令声明。完整 `TARGET_FILE` 的顺序依赖与 executable target 在 `DEPENDS` 中增加文件级依赖的差别吻合原文。CMP0112 的名称/目录组件不能替代完整表达式，这个限制也已保留。

“缺少重跑保证”而非“所有生成器绝不重跑”是恰当措辞。额外工具输入、时间戳保留及交叉编译并未被一个 target 名自动解决。原创建议明确未运行，也未归因于 Cygames 的真实故障。本次没有核验旧招聘内容或 SLSA 合规性。

## 3. FMOD：结束通知不等于 bank 所有权或声学完成

重新打开 FMOD 2.04 [EventInstance](https://www.fmod.com/docs/2.04/api/studio-api-eventinstance.html) 的 release、callback types、STOP_MODE；[Bank](https://www.fmod.com/docs/2.04/api/studio-api-bank.html) 的 unload/unloadSampleData；[Studio Guide](https://www.fmod.com/docs/2.04/api/studio-guide.html) §13.4、13.7–13.8、13.11。页面标记2.04.00，未把可变文档地址当作源码构建认证。

正文没有把 release 当成 stop，也没有因样本加载计数尚在就声称整体卸载安全。共享使用者收束、继续 update、按初始化模式处理回调，以及已复制的项目记录与迟到句柄查询的区分，支持其有限退出政策。START_FAILED 分支仍明确独立，未被要求等待 STOPPED。

检查了最危险的简化：“任一 STOPPED 到达即可卸载”。正文并未给这种算法，且明确结束记录是项目政策、持有资源并不保证完整可听输出。没有承诺所有总线尾部、用户内存、跨 bank 或流式依赖已安全处理。这些未实现部分是声明的范围，不是可据现文误判为已完成的证据。

## 裁决

接受此快照下三项有限来源增量，无需为本次审查修改正文。保持 source-only / 原创未执行分类；不得把本审查计作新运行、独立实验复跑或全篇认证。后续实际实施仍须另定版本、输入和观测合同，本轮没有取得这些证据。
