---
id: SOL-UX-001
title: 模态菜单关闭后的焦点恢复：有效目标、嵌套作用域与失效回退
type: solution
status: source-backed
primary_discipline: UX
related_disciplines: [A11Y, QA, PROG]
related_roles: [ui-programmer,ux-designer,accessibility-specialist,qa-tester]
related_topics: [modal-dialog,keyboard-navigation,gamepad-navigation,focus-restoration]
engines: [Unity]
versions: ["Unity 6000.0 UI Toolkit 文档", "XAG 113：2026-03-04 更新页面"]
platforms: [PC,console]
updated_at: 2026-10-31
verification_method: 官方文档溯源；Python 3.12.14 原创纯状态模型11项测试通过；未执行Unity或平台认证测试
sources:
  - https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/113
  - https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/112
  - https://docs.unity3d.com/6000.0/Documentation/Manual/UIE-focus-order.html
  - https://docs.unity3d.com/6000.0/Documentation/Manual/UIE-Focus-Events.html
  - https://docs.unity3d.com/6000.0/Documentation/Manual/UIE-Panel-Events.html
  - https://docs.unity3d.com/6000.0/Documentation/ScriptReference/UIElements.VisualElement.html
  - https://docs.unity3d.com/6000.0/Documentation/Manual/UIE-Runtime-Event-System.html
---

# 模态菜单关闭后的焦点恢复：有效目标、嵌套作用域与失效回退

## 问题与适用边界

玩家从设置页打开确认框，关闭后方向键不再移动；或者仍能移动，但下一次确认落到了已隐藏的底层按钮。更隐蔽的变体是：确认框等待网络返回期间，原列表刷新、启动按钮被销毁，而关闭逻辑仍向旧引用调用 `Focus()`。把“上次焦点”存下来只能解决最简单路径，不能保证它仍能接收输入或被玩家看见。

本文面向键盘、手柄数字导航的单用户模态 UI，给出可移植的**应用层策略**，并说明 Unity 6000.0 UI Toolkit 接入检查点。它不是 Unity 内部实现说明、可直接粘贴的 C# 插件、读屏完整方案或任何平台认证证明。分屏多用户需要按玩家分别维护焦点域；系统级登录/购买覆盖层的生命周期必须由平台集成处理，不能由本地菜单假装拥有。

## 1. 已核实的来源事实

- **[S1] XAG 113** 要求焦点指示清晰可见、不落在不可见或屏幕外元素；其对话框示例把焦点移到框内交互控件，并限制打开期间的焦点范围。该要求给出了目标，不提供恢复栈算法。
- **[S2] XAG 112** 强调可预测的导航和返回路径，并讨论通过相同输入方式离开控件；特殊模式需给出清楚的退出提示。它不意味着模态对话框应允许方向导航穿到背景。
- **[S3] Unity Focus order** 区分 `focusable` 和 `tabIndex`，每个 panel 有焦点顺序。负 `tabIndex` 不参与 Tab 导航；不能由此推导“禁止所有程序化聚焦”。
- **[S4] Focus events** 中 `FocusInEvent`/`FocusOutEvent` 在焦点变化之前，`FocusEvent`/`BlurEvent` 在变化之后。请求焦点与观察最终变化是不同阶段。
- **[S5] Panel events** 说明元素必须附着到 panel 才能渲染或接收事件；移出前发 detach 事件。父元素不会因为后代单独附着/脱离而自动收到该后代的 panel 事件，不能只监听最外层就假定捕获所有失效。
- **[S6] VisualElement API** 提供 `panel`、`enabledInHierarchy`、`visible`、`resolvedStyle` 等信息；这些单个属性都不是本文完整“适合恢复”的谓词。
- **[S7] Runtime event system** 描述 UI Toolkit 与 uGUI 混用时的输入模块和焦点桥接：某一方取得焦点会影响另一方。只在 UI Toolkit 内部保存一个目标，不足以证明整个混合 UI 只有一个输入所有者。

以下状态机、回退顺序、输入抑制和测试矩阵均为本研究的工程建议，不声称来自微软或 Unity 的指定算法。

## 2. 先定义不变量，而不是到处补 Focus()

对每个本地 UI 用户建立一个 FocusCoordinator，统一拥有以下状态：

```text
ScopeFrame = {scopeId, frameToken, viewGeneration, root, returnTarget, defaultTarget, lastValidTarget}
TargetRef  = {stableId, instanceGeneration, ownerViewGeneration}
Coordinator = {scopeStack, revision, actualFocus, pendingRequest, inputOwner}
```

- `scopeStack` 底部是当前页面，顶部是唯一允许交互的模态作用域。确认框内再开帮助框属于新栈帧。
- `TargetRef` 不仅保存对象或名字。虚拟列表复用控件后，同名节点可能代表另一个商品；应同时保存实例代次和业务上下文。若业务明确允许恢复到“同一条记录的新控件”，由列表适配器按记录 ID 重新解析并验证，不能无条件接受旧对象。
- `frameToken` 每次打开时分配新值，即使 scopeId 相同也不复用；关闭请求必须携带该 token，只有匹配当前栈顶才可弹出。它与下面的 revision 独立：关闭子框后，父框 token 仍有效。
- `revision` 在打开/关闭/页面替换/用户归属改变，以及新的用户导航或其他取代旧请求的聚焦意图时递增。实际实现也可分开保存树事务版本与聚焦请求版本；只更新前者不能阻止同一框内旧请求覆盖较新的用户选择。不要对所有观测到的焦点事件无条件自增/重新请求，需识别本协调器提交与外部新意图，避免反馈循环。延迟请求携带当时版本，防止过期回调抢走新对话框焦点。
- `actualFocus` 来自引擎最终状态或提交后的事件观测，不把“发出了请求”当作成功。

必须维持：

1. 可交互模态存在时，导航、确认和指针点击都不能激活其背后内容。只拦截 Tab，不拦手柄导航或鼠标点击，不构成模态隔离。
2. 焦点落点必须位于当前作用域的**当前活树**，并能呈现可见指示；旧节点即使还被引用，也不是活树成员。
3. 一次用户动作只归一个输入所有者消费。用来关闭框的确认键不得同帧继续激活恢复后的按钮。
4. 无有效候选时显式进入恢复/加载状态，不偷偷跳到被遮挡页面。正常交互态不能无限期没有有效焦点。

## 3. 目标资格：附着、可用、可见、属于当前范围

建议由 UI 适配器实现 `eligible(target, activeScope)`，返回布尔值和拒绝原因。不要仅判 `target != null`。

| 检查 | 不通过例子 | 处理 |
|---|---|---|
| 身份和代次匹配 | 列表重新绑定；旧视图回调完成 | 重新按业务 ID 解析或放弃旧目标 |
| 活树和当前 panel 匹配 | 已移出树、场景卸载、旧 UIDocument | 不发请求；清理记忆 |
| 当前作用域成员 | 背景按钮、已关闭父页 | 拒绝，不跨模态域“寻找最近按钮” |
| 层级启用且允许交互 | 自身启用但父容器禁用；业务锁定 | 选明确回退项 |
| 允许焦点 | 装饰元素、禁用的容器代理 | 选交互控件或专门设计的可访问入口 |
| 当前可呈现 | 隐藏祖先、未完成布局、零面积、透明退出动画 | 等可展示的生命周期点再验证 |
| 指示可被看到 | 滚动裁剪、被其他模态覆盖、屏幕外 | 先滚入可视区域并完成布局，重新检查 |

“可见”是应用层合成判断：一个节点的 `visible` 为真，不等于祖先没有 `display:none`、没有裁剪、没有透明度动画、没有遮挡。不要宣称 `worldBound` 相交就证明指示清晰，也不要要求通用像素级遮挡检测才能开始实现；给模态布局制定可检验的可视区域和遮挡契约，再在目标屏幕比例、缩放与背景中验收。

如果候选需要滚动进入视野，把它标记为 `pending-reveal`，先完成滚动/布局，再发焦点请求。滚动过程中允许保持原有效焦点或短暂加载状态，但不能让不可见目标长期接收确认。

## 4. 打开与关闭必须是事务

### 打开模态

1. 记录当前作用域中已验证的焦点为 `returnTarget`。鼠标打开时优先记录实际触发控件，而不是恰好残留的键盘焦点；记录方式需项目明确。
2. 立即把输入所有权交给新模态范围，屏蔽背景的导航、确认和点击；在画面打开动画期间也不能穿透。
3. 建立新栈帧，递增 revision。等待实际挂树、数据和可见布局就绪，不假定固定延迟一帧足以覆盖异步资源。
4. 选择该框明确的初始交互项。把安全/取消项安排在符合内容逻辑的初始位置；不要因自动聚焦就提交删除、付费等动作。
5. 检查资格后请求焦点，并核对最终目标。若请求期间树变化，重新解析一次当前状态；若持续失败，给出带返回路径的故障 UI，而非每帧无限重试。

### 关闭最上层模态

1. 只有栈顶的有效关闭 token 能执行关闭；重复关闭回调幂等丢弃。子框仍在时，不允许父框异步返回直接 `pop()` 栈顶。
2. 消费关闭输入，取消该框旧的待执行焦点请求；递增 revision。
3. 移除/隐藏该层并完成所有权切换。在退出动画仍阻挡画面的期间，由显式过渡态持有输入，不把背景按钮提前开放。
4. 在恢复后的当前范围依次尝试：**原 opener → 该范围最近仍有效的焦点 → 明确默认入口 → 明确安全返回入口**。每项都重新执行资格检查，去重后尝试。
5. 如果父框仍开着，恢复目标必须在父框内；只有最后一个模态关闭才回页面。原页面已被路由替换时，旧 returnTarget 全部作废，新页面走自己的初始聚焦协议。
6. 确认提交后的焦点有效，再解除过渡态。没有候选时创建可操作的错误/返回状态；对于不可取消的短暂加载，明确标识加载并在完成/失败事件中恢复，不以“永久无按钮”作为容错。

概念伪码（不是 Unity API 实现）：

```text
onReady(request):
    if request.revision != coordinator.revision: discard
    if request.scope != activeScope: discard
    for ref in deduplicated(request.preferred, lastValid, default, safeExit):
        target = resolveInCurrentTree(ref)
        if eligible(target, activeScope):
            requestFocus(target)
            scheduleCommitCheck(revision, scope, target)
            return
    enterExplicitRecoveryState(activeScope)
```

后置检查也必须携带 revision。若“请求 A”触发回调打开 B，A 的后置失败处理不得强制把焦点抢回 A。不要在每个 `BlurEvent` 中立刻无条件恢复自己，那会使多个控件相互争抢。

## 5. Unity 6000.0 接入边界

将策略与引擎适配层分开。适配层至少负责：解析当前 UIDocument 树、检查 panel/层级启用/可聚焦性与应用可见性、实施范围隔离、接收最终焦点变化、取消卸载节点相关请求。

`FocusInEvent` 是变化前事件，不宜拿它单独做“恢复成功”证据。观察变化后事件并核对当前焦点；具体读取接口和时序必须在使用的补丁版中验证。[S4] 挂树事件可驱动就绪，detach 可失效引用，但需覆盖实际被移除的节点及视图生命周期，不依赖父级捕获所有后代事件。[S5]

不要把 `tabIndex=-1` 当模态输入墙：它描述 Tab 顺序，不解决程序化请求、方向导航、鼠标或另一套 UI 的选择。[S3] 混合 uGUI 时先记录实际 EventSystem、输入模块和 Active Input Handling，确认没有两套自定义输入转发同时执行；围绕桥接后的真实焦点测试，而不是只看一个视觉高亮。[S7]

本稿不声称 `StopPropagation()` 一行就能防止全部默认行为；导航事件、默认行为、点击和游戏动作路由要分别验证。下层视觉 UI 可以保留显示，但必须由作用域策略保证它不可接受相关交互。

## 6. 输入设备改变不等于焦点消失

维护不同概念：`logicalFocus`（接受导航/确认的对象）、`pointerHover`、`lastInputModality`（提示图标/导航方式）、`inputOwner`（哪个玩家/设备获准操作）。鼠标掠过控件不必篡改恢复栈；手柄接入也不应把焦点重置到页面第一个按钮。

即使 UI 在指针模式采用不同样式，也不要仅因最近检测到鼠标位移就让仍接收键盘确认的焦点变得不可辨认。用轮廓、形状或其他不只依赖颜色的方式提供清楚状态，并测试动态背景和放大 UI；本文不定义替代可访问性标准的数值阈值。[S1]

**控制器断开边界（原创策略）**：

- 断开事件使该设备输入归属失效，不自动提交/取消当前操作；保留可重新验证的逻辑焦点上下文。
- 如果出现“重新连接”本地模态，作为更高一层作用域管理；若是平台覆盖层，暂停本地焦点请求，等待真实返回事件。
- 重连先确认用户/设备归属，再恢复当前栈顶有效目标；不把新设备输入直接映射给旧用户，也不补播断线期间缓存的确认。
- 允许的替代键盘操作须符合平台与游戏的用户策略；需要原设备时清楚解释限制。设备中立/重新按下门槛应在输入层定义，防止保持按键产生一次意外确认，不能用清空全游戏输入的粗暴方式破坏其他玩家。

## 7. 原创纯状态模型：已运行的窄范围验证

配套[模型与运行记录](../../research/experiments/ui-focus/README.md)已归档于 `research/experiments/ui-focus/`。执行环境 Python 3.12.14；仓库根目录命令 `python3 research/experiments/ui-focus/test_focus_model.py`，2026-10-31 执行，11 项测试通过。集成审查发现初版仅按作用域名字关闭会误关同名重开框，现已使用每次打开唯一 token 并补入回归测试。模型禁止同名scope同时位于栈中；真实产品如允许同一模板多实例嵌套，必须给节点绑定唯一活动帧/视图身份，而非只比较模板名。模型采用布尔值模拟资格，不模拟 Unity 布局、祖先样式、真实设备或读屏。

| 已运行模型测试 | 证明的局部策略 |
|---|---|
| 同名scope同时重入 | 明确拒绝且不修改栈/焦点/版本；实际多实例须按帧身份归属 |
| 两层模态依次关闭 | 先回父框，再回原页面 opener |
| opener 被删除 | 采用页面安全默认项 |
| live/enabled/visible/focusable 各为假 | 旧 opener 不被选中 |
| 相同 ID 换 generation | 不误认新实例为旧 opener |
| 模态尝试聚焦背景 | 当前 scope 检查拒绝 |
| 旧 revision 延迟回调 | 不能抢走新模态焦点 |
| 同一框内用户已导航到新目标 | 旧延迟请求不能覆盖较新的用户选择 |
| 父框先关闭 | 不错误弹出子框 |
| 同名框关闭后重新打开，旧关闭回调晚到 | 每次打开的唯一 token 拒绝关闭新实例 |
| 模态没有有效候选 | 保持模态域并返回 None，不逃到背景 |

最后一个测试只证明“没有跨域”，**不是可用性通过**：实际产品必须实现前述恢复状态与可操作退出路径。模型省略完整的 lastValid/safeExit 链、过渡动画和最终事件确认，因此不能用 11/11 宣称文章所有算法已通过集成验证。

## 8. 引擎与人工验收矩阵（尚未执行）

每次记录：引擎完整版本、输入包/模块、设备与用户、当前页面/栈、视图及请求代次、输入事件 ID、请求目标、实际目标、拒绝原因、截图或视频时间点。不记录玩家文本框内容、账户令牌等无关数据。

| 场景 | 必须观察的结果 |
|---|---|
| 键盘 Tab/Shift-Tab、手柄 D-pad 四方向 | 模态内逻辑顺序合理；不能移动到背景；仍有明确关闭路径 |
| 关闭后立刻确认；按住确认；重复关闭回调 | 关闭动作只执行一次；恢复后的目标没有被同一动作误触发 |
| 嵌套框关闭；父请求晚返回 | 顺序正确；旧回调不改新栈 |
| opener 销毁、禁用、隐藏祖先、重新绑定 | 资格拒绝正确；可预期回退而非无焦点 |
| opener 在滚动区外、最大 UI 缩放、小屏比例 | 滚入并显示焦点指示后才允许操作；没有被裁剪的落点 |
| 页面加载中收到旧回调、卸载重建同名控件 | 视图代次隔离；旧对象不再接收请求 |
| 鼠标/键盘/手柄交替；UI Toolkit 与 uGUI 混用 | 一致的实际输入目标；没有两个高亮却只有一个能操作 |
| 控制器断开重连、用户切换、平台覆盖层返回 | 不误操作，不串用户；返回时重新验证当前状态 |
| 模态数据为空或所有按钮暂禁用 | 有明确恢复/返回策略，不能无限留在无输入出口的状态 |
| 读屏和辅助输入 | 名称、角色、状态与上下文可理解；视觉通过不代替语义验收 |

建议把资格拒绝原因做成开发 HUD，复现时显示 `detached / wrong-scope / disabled / hidden / stale-generation / stale-request`，比只有“Focus 失败”日志更能定位跨生命周期的问题。测试队列随机交错打开、关闭、重建和数据刷新，可进一步发现事务重入问题；本稿没有执行该随机测试。

## 来源定位与使用范围

访问日期均为 2026-10-31。Unity 旧 URL 当前跳转到官方 `docs.unity.com/en-us/engine/6000.0/` 对应页，按 URL 与正文 Unity 6.0 导航核对版本；网页侧栏同时列出其他版本，不把它们当作本稿目标版本。所有代码和策略为原创，没有复制来源示例代码或游戏截图。

- **S1** Microsoft，XAG 113，Implementation guidelines，尤其可见焦点与对话框示例；页面更新日期 2026-03-04。[正文](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/113)。这是可访问性设计依据，不等同认证条款覆盖清单。
- **S2** Microsoft，XAG 112，Implementation guidelines 的返回路径、离开控件与特殊模式提示。[正文](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/112)。只读取网页文本，未声称观看其嵌入视频。
- **S3** Unity 6000.0，Focus order of elements，focus ring、focusable、tabIndex。[正文](https://docs.unity3d.com/6000.0/Documentation/Manual/UIE-focus-order.html)。未依赖正 tabIndex 的排序细节，方向导航仍需项目验证。
- **S4** Unity 6000.0，Focus events，变化前后事件说明。[正文](https://docs.unity3d.com/6000.0/Documentation/Manual/UIE-Focus-Events.html)。
- **S5** Unity 6000.0，Panel events，附着前提、事件受影响范围、Attach/Detach 时序。[正文](https://docs.unity3d.com/6000.0/Documentation/Manual/UIE-Panel-Events.html)。
- **S6** Unity 6000.0，VisualElement API，Properties。[正文](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/UIElements.VisualElement.html)。
- **S7** Unity 6000.0，Runtime UI event system and input handling，混合 UI、输入模块与 Pointer routing, panel order, and focus。[正文](https://docs.unity3d.com/6000.0/Documentation/Manual/UIE-Runtime-Event-System.html)。

检索词：modal focus restoration / UI focus handling / UI Toolkit panel lifecycle / 模态焦点恢复 / 手柄菜单焦点。后续最有价值的补证是实际 Unity 项目中的挂树、布局、输入消费与焦点事件轨迹，而非再添加更多概述链接。

## 关联知识

[伪本地化契约](../localization/pseudo-localization-contract.md)补充文本变化后的布局验收；[音乐状态交接](../audio/music-state-transition-contract.md)使用类似的异步请求失效原则，但不能替代UI自身生命周期。
