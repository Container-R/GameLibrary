---
id: NOTE-MODEL-BAKE-001
title: 模型烘焙交接：piece 名称对应，不等于追踪集合未变
type: research
status: source-backed
primary_discipline: MODEL
related_disciplines: [TA, ANIM]
related_topics: [texture-baking, piece-matching, component-visibility]
versions: ["SideFX Houdini 22.0 文档；Bake Geometry Textures 2.0 节点；页面标注 Since 21.0；发布日期未确认"]
updated_at: 2026-11-01
review_after: 2027-02-01
verification_method: 官方节点文档正文核对；分组反例与接收程序为原创未执行分析；未生成资产、运行烘焙或观察纹理及引擎画面
sources:
  - https://www.sidefx.com/docs/houdini/nodes/cop/bakegeometrytextures-2.0
---

# 模型烘焙交接：piece 名称对应，不等于追踪集合未变

更新：2026-11-01。主学科：MODEL；关联：TA、ANIM。证据类型：官方节点文档与原创未执行分析。没有制作模型、运行烘焙或观察纹理、角色和引擎画面。

## 模型作者交付的还有组件间关系

烘焙接收不能只问“高低模名字能否对上”。如果这些名字参与追踪过滤，合并分组就可能改变允许参与烘焙的表面，即使几何、UV 和法线都没改。

本文只讨论 SideFX Bake Geometry Textures 2.0 的按名称匹配机制。重点不是一般的资产命名规范，而是模型作者与烘焙接收者是否批准了**哪些组件可以相互参与追踪**。组件是可动、可拆，还是只用于固定组装姿态，会影响这个决定；没有一个适用于所有资产的“全部隔离”答案。

## 文档支持的有限机制

所读[官方文档](https://www.sidefx.com/docs/houdini/nodes/cop/bakegeometrytextures-2.0)页头为 Houdini 22.0，节点为 Bake Geometry Textures 2.0，标注 Since 21.0；访问2026-11-01，发布日期未确认。这不是固定源码，也不证明所有条款自21.0起相同。

`Baking best practices` 建议可动/可拆组件独立烘焙，在 low、high、cage 为同一组件赋相同 piece 值。`Match Pieces by Name` 说明：不属当前匹配 piece 的射线命中被忽略；Piece Attribute 指定跨输入的 primitive 属性。Include/Exclude 决定纳入烘焙的集合，排除在包含之后生效，不能把它们当成任意逐对可见性配置。`Cage mesh` 的拓扑对应条件另行成立，名字匹配不会修复 cage 对应错误。

这些是节点文档的机制，不是已经执行的像素比较。下面的资产、变更和接收步骤都是原创假设。

## 有限反例：两个对应正确的集合被合成一个

假设一个箱体带有可开合锁扣。low、high、cage 都已有对应的 primitive 分组；按名称匹配开启，Include 为 `*`，Exclude 为空。固定几何、UV、三角化、法线、cage 与其他烘焙设置，仅改 piece 值：

| 输入版本 | 箱体 primitive | 锁扣 primitive | 跨 low/high/cage 对应 |
|---|---|---|---|
| A：分开 | `body` | `latch` | 同组件使用同名 |
| B：合并 | `prop` | `prop` | 同组件仍使用同名 |

两版本都能通过“每种输入的名字对应”检查，但分组关系不同。考虑一条属于箱体、可能与锁扣几何相交的候选射线：A 中锁扣属于另一个 piece；B 中二者属于同一 piece。**B 取消了这里的跨 piece 排除条件。** 其他距离、剔除、射线方向等条件仍可能排除该候选，因此不能预填“B 一定命中锁扣”，更不能预填某个像素变暗或 AO 增加多少。

若接收要求是锁扣独立移动时仍可复用自己的贴图，那么是否允许把特定组装态的跨件影响纳入烘焙，应先明确。若贴图本来就只服务一个固定组装态，也不能自动断言这种影响有错。这里改变的是追踪输入政策，不是已经诊断出画面缺陷。

### 一致改名与合并不是同一件事

将所有输入中的 `body→shell`、`latch→catch` 做一一对应改名，并保持 Include/Exclude 的**实际选中集合**不变，保持的是本例的分组关系。它不同于把两个名字都改成 `prop`。

所以，字符串变化本身不证明集合语义改变；名字在三种输入都存在，也不证明语义未变。模式筛选也必须复核：例如仍按旧名排除的规则，可能在改名后选中不同集合。本节不证明任何改名后的烘焙逐像素相同。

## 原创有限接收程序（未执行）

以下只接收这一处分组变更，不替代完整烘焙验收。

1. **固定用途及输入对应。** 保存当前组件到各输入 primitive 的映射，声明锁扣需要独立运动/拆卸，还是贴图只覆盖指定组装态。不要求 high 与 low 具有相同 primitive 数量；要说明它们哪些表面属于同一意图组件。cage 的独立有效性条件另查。
2. **比较分组，而不只比较名称。** 对照变更前后哪些组件被合并或拆分、同组件是否仍在 low/high/cage 对应。若无法可靠对应当前 primitive，就不能仅凭名字一致批准“只改标签”。
3. **核对有效筛选。** 记录匹配开关、Piece Attribute、Include/Exclude，以及其实际纳入的集合。配置文本不变不保证改名后的选择不变。
4. **按变化处置。** 合并/拆分作为追踪输入变更交给模型作者与烘焙接收者确认用途，再决定重烘焙；一一对应改名且有效选择不变，只能关闭“该分组关系未改”这一项，不能自动宣布全部输出通过。
5. **留下真实接收缺口。** 在实际验证阶段，固定其余相关输入比较实际 maps，并按声明用途检查组装态及要求支持的开合/拆卸状态。本文尚未做这些检查，不规定通用像素阈值，也不把一个状态的通过扩大到所有动作。

无需改动几何就能改变烘焙的追踪集合，是本例要求重审的理由；不是要求每次重命名都无条件重做全部纹理。若模型用途发生变化，即使分组没改，也要重新决定原来的烘焙政策是否仍适用。

## 与已有研究的边界

[切线 handedness 与法线变换](../../来源笔记/tangent-handedness-normal-transform.md)讨论方向与空间合同；[网格简化请求与返回](mesh-simplification-request-result.md)讨论数量和误差接收。本条不重复这些推导，也不继承它们或关联实验的测试结果。

缺失属性、未匹配名字的具体行为、不同 AOV 的所有影响、cage 错配后的输出、渲染器结果及性能都未验证。本文不是完整烘焙教程、自动修复器或 Houdini 缺陷报告。来源定位为官方页的 `Baking best practices`、`Match Pieces by Name`、`Cage mesh`；没有复制图片、软件画面或节点实现。
