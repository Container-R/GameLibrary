---
id: SOL-ANIM-001
title: 大角度原地转身脚滑：先划分根运动与控制器职责，再处理足底接触
type: solution
status: source-backed
primary_discipline: ANIM
related_disciplines: [PROG, TA, QA]
related_roles: [technical-animator, gameplay-programmer, character-technical-artist]
related_topics: [root-motion, turn-in-place, foot-planting, animation-retargeting, rig-evaluation-order, pose-dependencies]
engines: [Unity, Unreal Engine]
versions: ["Unity 6000.0", "Unreal Engine 5.6", "Unity Animation Rigging 1.2.1 documentation only"]
platforms: [engine-agnostic-diagnostic-workflow]
updated_at: 2026-10-31
verification_method: 官方版本文档与日本原始项目职责材料核对；既有4项Python二维接触模型测试；Rig依赖交接与六行接收表未执行，未运行引擎或真实角色资产
sources:
  - https://www.jp.square-enix.com/tech/library/pdf/CEDEC2015_Luminous_FFXV_Animation.pdf
  - https://docs.unity3d.com/Packages/com.unity.animation.rigging@1.2/manual/RiggingWorkflow.html
  - https://hrmos.co/pages/capcom/jobs/01_03_040
  - https://docs.unity3d.com/6000.0/Documentation/Manual/RootMotion.html
  - https://docs.unity3d.com/6000.0/Documentation/ScriptReference/MonoBehaviour.OnAnimatorMove.html
  - https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Animator-applyRootMotion.html
  - https://dev.epicgames.com/documentation/en-us/unreal-engine/root-motion-in-unreal-engine?application_version=5.6
  - https://dev.epicgames.com/documentation/en-us/unreal-engine/pose-warping-in-unreal-engine?application_version=5.6
  - https://dev.epicgames.com/documentation/en-us/unreal-engine/fix-foot-sliding-with-ik-retargeter-in-unreal-engine?application_version=5.6
---

# 大角度原地转身脚滑：先划分根运动与控制器职责，再处理足底接触

## 问题与适用范围

角色播放 90°/180° 原地转身时，支撑脚在地面画弧、身体结束后回弹，或胶囊朝向正确但脚仍滑动。不要把这些现象统称为“缺少 IK”：它们可能分别来自运动写入冲突、根运动导入、过渡混合、重定向或接触时序。

本文针对有可检查骨架、转身片段与角色控制器的工程诊断。Unity 例子以 Humanoid 为主，Generic 的 Root Node 需单独核对；UE 例子以 Character/Movement Component 为主。自研运动系统、网络回滚和 Motion Matching 的具体实现不在已验证范围内。以下公式、日志与流程为原创诊断设计，未宣称官方提供此完整方案。

## 官方来源究竟支持什么

- **Unity 6000.0 [S1]**：Root Transform Rotation 的 Bake Into Pose 会使根旋转增量为单位旋转；Loop Pose 是在根变换参照系内处理首尾姿态差。Generic 从指定 Root Node 取根变换。因此“角色在片段预览中转身”不能证明运行时提取了相同的对象旋转。
- **Unity 6000.0 [S2][S3]**：OnAnimatorMove 在动画评估之后、OnAnimatorIK 之前调用；实现该回调后，applyRootMotion 属性不再决定自动应用行为；运行时改变该属性会重新初始化 Animator。不要把每帧切开关当成无副作用的运动仲裁。
- **UE 5.6 [S4]**：Ignore Root Motion 会提取并移除根运动，但不应用到角色；Root Motion from Everything 会按参与姿态的资产权重混合根运动。提取和应用是两件事，混合期间不能只看单个源片段总转角。
- **UE 5.6 [S5][S6]**：Pose Warping 调整姿态以匹配运动；Stride Warping 关注步幅与速度关系。Speed Planting 示例则针对重定向足滑，使用源脚速度曲线及目标 IK。两者都不构成“所有转身脚滑开一个节点就解决”的证据。

## 一、先建立可观测的运动账本

选一个合法可用的单片段，平地、固定出生姿态、固定目标角；先关过渡混合和足部修正，录制以下**同一评估序列**数据：

- 帧/模拟 tick、动画评估 ID、片段时间和权重；
- 意图朝向、提取的根位移与根旋转、控制器请求与实际批准的位移/旋转；
- 胶囊/角色根、Mesh 相对角色的变换、左右脚世界位置；
- 接触权重与接触对象 ID，碰撞或网络修正量。

不能把“请求的位移”当成“实际走过的位移”。墙体阻挡后，动画仍按原速度走腿就可能滑脚。对有父节点的 Mesh，足世界位置可写作 `p_world = T_actor * T_mesh * p_bone`；先确定哪个变换出了错，再改骨骼。此等式是坐标组合，不是某引擎的内部求解顺序。

为地面静止接触段设置测量窗口，计算脚相对接触面的位置变化；例如 `slip = |p_contact(t)-p_contact(t0)|`。移动平台上应在平台局部坐标测量，否则正常随平台移动会被误判为滑动。容差必须依据角色比例、镜头和玩法确定，不把某个厘米值写成通用合格线。

## 二、每个运动通道只设一个最终执行者

先分别决定**平移、偏航、垂直运动**由谁提交，不能仅写一句“使用 Root Motion”。

| 策略 | 运行契约 | 适合与代价 |
|---|---|---|
| 动画驱动转身 | 片段产生根偏航；运动层接收并处理约束后应用一次；输入只选片段/目标 | 保留原动作重心与支撑节奏；可用角度、时长受资产覆盖影响 |
| 控制器驱动转身 | 控制器决定对象偏航；片段不能再对同一对象添加同一偏航 | 易满足瞄准/玩法朝向；必须校准脚部姿态与转速，不能随意旋转根后指望原脚轨迹仍贴地 |
| 显式混合/扭曲 | 指定谁产生候选运动、谁作一次补偿、谁提交最终运动 | 可适配目标角，但需要残差、角度极限、接触释放和失败回退 |

**双写反例**：输入代码把对象转 90°，同一动作根曲线又累计 90°。若两者直接相加，姿态、碰撞与目标角可能分离。这里的 180° 只是同轴理想化反例；真实四元数混合不能简单按任意欧拉角相加。解决办法是删除重复责任，而非乘一个经验系数遮住问题。

Unity 自定义 OnAnimatorMove 路径应把增量交给明确的运动适配器；若已由适配器应用，不再让另一 Update/FixedUpdate 重复消费。需要跨评估频率缓存时，标注评估 ID、组合顺序和已消费边界，不能每次固定更新重复使用“最新一份 delta”。UE 检查资产 Enable Root Motion、Anim Blueprint 模式和 Movement Component 接收路径，不把 Root Lock 当作角色运动执行器。

## 三、按最小增量恢复复杂性

1. **单片段无脚部修正**：确认提取的累计偏航与资产意图一致。Unity 检查 Rotation Bake Into Pose 和 Based Upon；UE 检查根骨是否确实有曲线及提取模式。预览与运行需分别观察胶囊、Mesh、骨架。
2. **恢复控制器约束**：加入碰撞、斜坡、重力后比较请求与批准运动。偏差出现时先处理运动规则，不在动画中盲目补偿穿墙或碰撞裁剪。
3. **恢复过渡与中断**：逐项启用 Idle→Turn→Idle、半途反向、移动打断，记录混合权重。若单片段正常、过渡才滑，检查接触相位、转角被混合衰减、Mesh 偏移恢复和根运动来源切换，勿直接重做所有资产。
4. **再接触锁定**：只在确证支撑期锁脚；脚离地需释放，另一只脚落地需重新建立接触。目标超过腿长可达范围时应释放/换步/改动作，而非无限拉伸膝盖。不能从“速度低”唯一推断可靠接触，悬空停顿也可能低速。
5. **最后扩展角度和体型**：测试左右转、90°/180°、不同身高与腿长。原地转身平移速度接近零，不宜直接套用 `LocomotionSpeed/RootMotionSpeed` 步幅比；转角/支撑相位才是此场景的主要约束。

## 四、区分三类足部修正

- **重定向滑脚**：原资产在源角色正常、目标角色异常。依据 [S6] 检查腿链、IK Goals、脚速度曲线和阈值。文档里的示例阈值不是所有角色的默认答案。
- **运动轨迹不匹配**：目标角色单片段也正常，进入控制器才滑。先对齐实际运动与动画轨迹，IK 只是处理剩余误差。
- **接触/混合接缝**：只在片段交接或中断时爆发。需要接触权重与状态切换契约；更长 blend time 可能减小突变，也可能延长错误支撑，必须量测。

成本主要是制作可覆盖的角度资产、接触标记、运动诊断日志及测试组合。增加 IK/warping 后需要测量目标硬件上的 CPU 时间和 LOD 行为；本轮没有性能数据，不给出固定预算或收益数字。

## 几何反例与验证边界

独立集成实验以二维刚体变换建立反例：根旋转 90°且脚局部位置补偿时可保持接触点；重复应用根旋转会破坏接触；即使两端姿态分别固定同一世界接触点，直接线性混合局部脚位置与插值根角度也可能使中间姿态滑动。此结论来自简化几何，不是对某引擎混合算法的实测断言。

2026-10-31 在 Python 3.12.14 实际执行了 4 项几何模型测试，全部通过。[脚本](../../research/experiments/root-motion/test_contact_transform.py)、[测试输出](../../research/experiments/root-motion/test-output.txt)和[运行范围](../../research/experiments/root-motion/README.md)已归档。通过结果不能外推为骨架约束、真实 IK 求解器或角色动画已验证。

## 待执行引擎验证矩阵

以下均为**建议引擎实验，未执行**。

| 用例 | 采集与验收 |
|---|---|
| 单独90°、180°左/右转 | 提取与批准运动、最终朝向、支撑段滑移曲线；阈值由项目定义 |
| 禁用一个运动写入者 | 故障是否消失；验证责任归属而不是保持偶然视觉结果 |
| Idle/Turn交接、50%时中断 | 根/胶囊/Mesh变换连续性、事件唯一消费、接触释放正确 |
| 墙边/斜坡/移动平台 | 请求与批准运动差值；平台局部脚滑而非世界位移 |
| 30/60/144渲染帧率及卡顿 | 同一逻辑输入与片段策略下无重复根增量消费；不宣称网络确定性 |
| 源角色与比例不同的目标角色 | 区分资产问题与重定向问题；检查腿可达范围与接触阈值 |

关联：[固定 Tick 与引擎表现边界](../programming/fixed-step-simulation-boundary.md)。后续若加入真正引擎复现，应保存版本、骨架/资产许可、控制器配置、日志与失败对照，再把相应**具体测试结论**标为 verified。

## 补充：Rig 的组织层级也可能是姿态执行顺序

根运动只有一个最终执行者，仍不足以保证局部姿态正确。瞄准、手脚 IK、辅助骨或物理修正可能读取或改写同一条骨链；调整 Rig 的组织方式，可能改变后续约束读到的姿态。这是**内容作者与运行集成的交接问题**，不能仅由“单个约束预览正常”验收。

### 先区分三份来源的责任与机制

- **Square Enix，CEDEC2015，FFXV Episode Duscae**：原始日文幻灯片讨论动画工具的使用者及处理顺序负担，并介绍 TA 为模型骨结构建立 Tuning Set、动画师选择预设的工作方式。这是当时项目的生产经验，不是所有工作室必须采用的编制。
- **Unity Animation Rigging 1.2.1**：`Rig Component` 文档明确，约束通过 `GetComponentsInChildren` 收集，层级深度优先顺序决定所生成 jobs 的求值顺序；这些 jobs 作用于 Animator 正常求值后的姿态。因此在这个版本，重排层级不一定只是整理文件。此处没有运行 Unity，也不声称 FFXV 使用这个实现。
- **Capcom 的日文“テクニカルアニメーター/リガー”职责页**：列出控制 Rig、IK 和脚本辅助等工作，只支持该雇主的职责示例，不能把技术动画、绑定与动画程序统一成同一个全球职称。

来源定位与访问限制见[姿态求值交接来源笔记](../../research/source-notes/rig-evaluation-handoff.md)。本节为来源支持的原创交接设计；原文已归档的是 4 项 Python 二维刚体接触几何模型测试，没有骨骼、真实 IK 或引擎回调；本节不改变其范围，也不把它当作 Unity Rigging 验证。

### 交付的是依赖关系，不只是一份骨骼名单

以下是建议的最小表，不是引擎标准 schema，也不要求所有项目使用同一求值顺序。

| 字段 | 提供者与接收者 | 最小可观察内容 |
|---|---|---|
| 动作意图与窗口 | 动画作者 → 技术动画/集成人 | 指定片段、时间段、混合权重；手要保持哪个握点、何时允许释放；接触误差与艺术判断分别记录 |
| Rig 与骨架修订 | 绑定/技术动画 → 动画程序/管线 | 具体 Rig、骨架和预设修订，受影响的骨链；不能只写“人形骨架兼容” |
| 阶段与坐标空间 | 动画程序/管线 ↔ 技术动画 | 基础姿态、各修正阶段和后续物理写入；目标及读写骨骼处于哪个空间；不要把不同阶段的世界坐标混作同一输入 |
| 约束读集/写集 | 技术动画 ↔ 动画程序 | 每个约束读取的骨骼/目标、改写的骨骼；哪些读必须消费前一约束的结果，哪些依赖仍待确认 |
| 实际顺序来源 | 管线/集成人 → 内容作者 | 引擎和包版本、Rig 层顺序、约束层级路径与实际收集顺序；内容层级变更是否改变此顺序 |
| 变更接收 | 动画/技术动画/QA | 同一输入下的变更前后阶段姿态、末端接触误差及视觉检查；失败时恢复哪份 Rig/预设，而不是盲调权重掩盖来源 |

小团队可以由同一人承担多个职责，但表中“谁产生意图、谁定义约束、谁确认运行消费”仍应分别明确。哈希或修订号只定位输入，不证明依赖关系正确。

### 未执行的反事实：躯干瞄准与握点手 IK

**这是待验证的原创情境，不是已发现的引擎缺陷。** 假设某动作要求右手保持指定武器握点，同时躯干朝目标瞄准；躯干修正会移动手臂链的父节点。手 IK 计算手的位置，而后续父节点变化可能改变最终手的世界位置。

- 候选 A：躯干瞄准之后再求解手 IK，使手 IK 消费修正后的父链。
- 候选 B：手 IK 之后再瞄准，检查后者是否破坏先前建立的接触。

不能预先规定 A 必然正确：握点也可能随武器或身体移动，后续还有约束、IK 可能不可达，项目也可能更重视瞄准姿态而允许手松开。必须先冻结目标空间、父子关系、动作意图及约束权重，再比较。**“读写依赖不同”是问题；“某顺序普遍更好”不是本节结论。**

### 有限接收工作表：先冻结判据，再观察

下列六行是未来接收计划，不是六个已通过测试。只用项目自有或许可明确的代表角色；若没有对应引擎环境，保持未执行状态，不以矩阵玩具或其他引擎替代。

| 条件 | 固定什么 / 改什么 | 应记录与决策 |
|---|---|---|
| 基础对照 | 固定片段时间、目标、出生姿态；两修正权重均0 | 确认基线姿态和握点定义；不是声称基础动作必然零误差 |
| 单约束对照 | 仅瞄准启用；仅手 IK 启用，分别记录 | 各自读取/写入阶段及单独局限；不能据两次单独通过推断组合通过 |
| 组合 A/B | 相同目标、片段、权重，两种顺序 | 比较实际阶段输出及最终接触误差；若没有差异，记录该输入无区分力，不捏造反例 |
| 层级变更 | 移动约束分组；保留并核对目标/控制对象世界姿态、骨骼与目标引用，不只看参数未变 | 同时记录约束收集顺序与空间输入；若重挂父节点改变了世界姿态，不把结果差异单独归因于顺序。顺序变更须重新接收 |
| 权重与中断 | 预先指定中间权重及中断点 | 接触释放是否符合动作意图；避免以“权重为0时正常”掩盖启用后的故障 |
| Rig 修订 | 固定同一片段/目标，更换明确的骨架或预设修订 | 重新核对读写骨链与目标空间；不要继承旧修订的合格结论 |

作为本库的实验控制建议，A/B还应核对实际收集到的约束成员/ID、Rig层归属、启用状态、权重和目标/骨骼引用，并保存实际有序列表。重挂层级若改变成员范围或设置，必须另列变化，不能得出“仅顺序导致”的因果结论；这不是未经运行确认的Unity内部行为断言。

至少记录角色/Rig/包版本、输入、真实顺序、阶段输出、最终误差、项目容差及审核决定。容差由动作比例、镜头和玩法共同决定，不给通用厘米阈值。数值接触通过也不等于动作自然；美术评审与必要的实际玩法观察仍是另一项证据。

## 原始来源、定位与版权

全部访问于 2026-10-31；只核对文本，不声称观看了嵌入动画全部帧，不转载官方示例代码、图片或角色资产。版本固定的入口可能仍被厂商更新，复现时应再次确认页面和安装版本。

- **S1** Unity Technologies，[How Root Motion works](https://docs.unity3d.com/6000.0/Documentation/Manual/RootMotion.html)，Unity 6000.0；Root Transform Rotation / Loop Pose / Generic Root Motion and Loop Pose。
- **S2** Unity Technologies，[OnAnimatorMove](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/MonoBehaviour.OnAnimatorMove.html)，6000.0，Remarks。
- **S3** Unity Technologies，[Animator.applyRootMotion](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Animator-applyRootMotion.html)，6000.0，Remarks。
- **S4** Epic Games，[Root Motion](https://dev.epicgames.com/documentation/en-us/unreal-engine/root-motion-in-unreal-engine?application_version=5.6)，UE 5.6，Enabling Root Motion / Animation Blueprint / Results / Debugging Root Motion。
- **S5** Epic Games，[Pose Warping](https://dev.epicgames.com/documentation/en-us/unreal-engine/pose-warping-in-unreal-engine?application_version=5.6)，UE 5.6，Stride Warping / Stride Scale / Min Locomotion Speed Threshold。文中不把 Slope Warping 作为已生产验证方案。
- **S6** Epic Games，[Fix Foot Sliding with IK Retargeter](https://dev.epicgames.com/documentation/en-us/unreal-engine/fix-foot-sliding-with-ik-retargeter-in-unreal-engine?application_version=5.6)，UE 5.6，Source Animation Setup / Generate Speed Curve / IK Rig Setup / Speed Planting in IK Retargeter。
- 多语言检索使用“原地转身 脚滑”“turn in place foot sliding”“ルートモーション ポーズ焼き込み”；已打开 [Unity 6000.0 日文版](https://docs.unity3d.com/ja/6000.0/Manual/RootMotion.html)，只作术语核对，不计作独立来源。
