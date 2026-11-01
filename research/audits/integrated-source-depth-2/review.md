# 三项已发布来源增量：有范围限制的对抗式复核

日期：2026-11-01。结论：**在下列固定正文与增量范围内，未发现需要阻断的实质性错误。** 这不是运行通过、全文章逐项认证或全仓库安全判断。

## 独立性与快照

复核者曾参与这三题的来源发现与选择门，故存在明确研究重叠；本次是对后来整合正文重新作出的对抗式判断，**不是完全独立的第二来源发现，也不增加一份独立实验背书**。直接读取远程提交 `c9120627e9b3070066f5c9c857d2b64e18391d62` 的文件；未读取链接中的运行档案。

| 文件与本次裁决范围 | Git blob SHA | 正文 UTF-8 SHA-256 |
|---|---|---|
| `research/source-notes/box2d-sensor-step-and-sweep.md`，全文 | `bd2341770b7849b9f70b9ccf56b428e09f4bc1cb` | `23e50a2eb011aea2f602466d5fdfcaf2161b3d6fb623d759fe2f306f94e5e0a7` |
| `roles/engine/build-engineer.md`，新增“生成工具也是输入”及其衔接 | `9b36d15f44ad4c2789fffca64c0a6134b505c6ca` | `e6973e93f1a37e63272f154646c70471b81aee524d0b73bd15da62ff06570c2c` |
| `solutions/audio/music-state-transition-contract.md`，新增“事件释放与 bank 持有”及生命周期衔接 | `cc2722b1911203cf7b7cacd789202576e61ae7a5` | `0fb9f95ae8070e74c803275dec6b54ca46ab4f0efd297cf680439f54ce4294cb` |

哈希标识完整文件，不表示裁决扩张到旧雇主、历史音乐案例或旧实验。

## 1. Box2D：检查新版路径是否推翻旧版反例

复读固定 v3.1.1 `8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3` 的 [world.c 730–793](https://github.com/erincatto/box2d/blob/8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3/src/world.c#L730-L793)、[sensor.c 47–106](https://github.com/erincatto/box2d/blob/8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3/src/sensor.c#L47-L106)和 solver 的候选 sensor 排除；对照已读固定新版 `dd8bd3fb525f0f33f1079f8ca3c5770783c44a53` 的 [solver.c 138–215、287–312、358–425、542–550](https://github.com/erincatto/box2d/blob/dd8bd3fb525f0f33f1079f8ca3c5770783c44a53/src/solver.c#L138-L550)与 [Sensors 文档 1071–1103](https://github.com/erincatto/box2d/blob/dd8bd3fb525f0f33f1079f8ca3c5770783c44a53/docs/simulation.md#L1071-L1103)。本轮部分固定源码通过此前读取保留的全文重新检查，而非声称全部重新下载。

- 旧例限定实际直线路径、过滤和端点分离，没有把改变运动轨迹的 substeps 说成绝对无效果。
- 新版记录候选的 `<=` 与最终转交的严格 `<` 不同；正文正确采用最终“早于”条件，没有把宽相候选或暂存项当成最终事件。
- 容量限制、fast shape 自身为 sensor 的排除及移动 sensor 限制均保留；没有把静止 sensor 支持扩张到任意运动或数量。

因此，历史反例与新版解释没有被混为同一版本。现有来源足以支持检测路径选择，不能支持开始／结束事件全链路、交付帧或任意相对运动保证；正文没有声称这些。

## 2. CMake：检查例子是否根本未进入构建图

重新读取固定 CMake `6acf7153156bb45038be62e79a32ed5a6ea2d00e` 的 [add_custom_command.rst 1–45、102–175](https://github.com/Kitware/CMake/blob/6acf7153156bb45038be62e79a32ed5a6ea2d00e/Help/command/add_custom_command.rst#L1-L175)及 [CMP0112 全文](https://github.com/Kitware/CMake/blob/6acf7153156bb45038be62e79a32ed5a6ea2d00e/Help/policy/CMP0112.rst)。

正文已补同目录消费 target 和单个 OUTPUT，故不是只有孤立命令声明的伪反例。完整 TARGET_FILE 的目标顺序边与 DEPENDS executable target 的文件级失效边匹配文档。表不变、工具重编的检查保留“缺少保证”而非武断宣称任何生成器绝不重跑；时间戳保留、隐式输入及交叉编译排除也避免过度承诺。没有把 executable 的文件产物语义套到 custom target，亦未将独立假设归给 Cygames。

未发现缺失前提会推翻这一有限例子；没有配置或运行构建来认证实际生成器行为。

## 3. FMOD：检查事件完成通知能否合法决定 bank 卸载

重新读取 FMOD 2.04 [EventInstance](https://www.fmod.com/docs/2.04/api/studio-api-eventinstance.html) 的 release（1039–1064）、callback types（1951–1994）及 STOP_MODE（2206–2209）；[Bank](https://www.fmod.com/docs/2.04/api/studio-api-bank.html) 的 unload / unloadSampleData（716–768）；[Studio Guide](https://www.fmod.com/docs/2.04/api/studio-guide.html) §13.4、13.7–13.8、13.11。页脚标记 2.04.00，不作为实现提交认证。

重点反驳尝试是：“收一个 STOPPED 后立即卸载 bank”会不会伤及其他使用者，或迟到通知会不会查询失效句柄。正文没有给出这种快捷算法：它要求继续持有所需资源、收束其他使用者，区分项目结束政策和可听结果，并要求复制通知记录而非延迟查询旧句柄。START_FAILED 不等待 STOPPED 的旧分支仍保留。

整体卸载不受样本加载计数保护，支持事件 release 与 bank 所有权分层。继续 update 与回调线程条件也有直接文档支撑。项目结束记录、错误与超时处理仍待实现，但正文明确是有限政策选择，不冒充完整资源管理器；这里的留白不推翻“不应以三个请求已提交证明尾音完整”的结论。

## 总结

三项均提供实际机制而非仅靠免责声明：观察阶段与连续路径、构建图依赖边、事件及 bank 两层寿命。原创情景没有被提升为已观测结果。本次没有修改文章、运行引擎／构建／音频、读取原始运行资料或远程写入；不据此认证任何完整项目。
