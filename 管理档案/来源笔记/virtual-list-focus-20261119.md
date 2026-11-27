# 列表复用焦点：来源和证据

正文范围：已在单人键盘或手柄菜单中的行复用、临时不可见的目标、过期滚动和按下到松开的身份；不展开现有弹窗栈恢复、IME 候选提交、多人输入或指针拖放。

| 原始材料 | 核到的内容 | 用法限制 |
|---|---|---|
| [Unity 6000.0 UI Toolkit ListView](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/UIElements.ListView.html)，Remarks | 滚动时复用实际可见的 VisualElement；复杂项可用 makeItem、bindItem、unbindItem、destroyItem。示例 bindItem 接收数组索引。 | 用于区分行实例、当时索引和游戏数据 ID；未测试 Unity 自己的 FocusController、滚动时序或设备。 |
| [Unreal 5.8 UListView](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/UMG/UListView?application_version=5.8)、[RegenerateAllEntries](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/UMG/UListViewBase/RegenerateAllEntries?application_version=5.8) | Item 和 Entry Widget 的区别；完整重建 Entry 时可以是释放/重新绑定同一 UWidget，接收 OnEntryReleased 与 OnListItemObjectSet，并不必发生 Destruct/Construct。 | 不把完整重建的说明泛化为所有焦点、每个滚动实例的精确通知顺序。 |
| [Xbox Accessibility Guideline 113](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/113)，Overview、Implementation guidelines | 清楚显示操作焦点；焦点若移到不可见／屏外位置，可阻碍玩家导航。 | 不是稳定 ID 或过渡决策的规定；本文的方法是工程推导，未进行真实设备和平台认证。 |
| Godot 4.6：[Control.grab_focus](https://docs.godotengine.org/en/4.6/classes/class_control.html#class-control-method-grab-focus)、[Viewport.gui_get_focus_owner](https://docs.godotengine.org/en/4.6/classes/class_viewport.html#class-viewport-method-gui-get-focus-owner)、[BaseButton ActionMode](https://docs.godotengine.org/en/4.6/classes/class_basebutton.html#enum-basebutton-actionmode) | 控件实体取得焦点，视口查询实际持有者；ACTION_MODE_BUTTON_RELEASE 需要按下并释放，pressed 对应 action_mode。 | 原生例固定合成 ui_accept、两行、简单窗口与应用自行绑定，没有测真实滚动、视觉反馈或焦点恢复的跨引擎相同性。 |

项目策略：稳定业务 ID、一次聚焦意图、行绑定代次各有独立生命周期；同一个 ID／控件仍存在不能替代两项版本核对。转交焦点、筛选回退和不提前排队确认是例子所选的行为，不是上述框架强制策略。

[试件](../实验/列表复用焦点/README.md)固定 Godot 4.6.3，实际产生 Button 信号。无守卫改绑、当前目标正确但按下开始于旧对象、旧滚动与新目标争用、同 ID 重绑代次变化提供反例。记录的业务操作只是内存中的道具 ID 无实际物品转移。日期：2026-11-19 UTC。

## 2026-11-28 补读 Unity 6000.0.22f1：延迟滚动的载荷

固定 GitHub 标签 6000.0.22f1 对应提交 2021617d502418406603ffd8e5cee0f4df3c472e。逐个读取 UIElements C# 文件，不是拿 master 猜这个版本。

- `Controls/ListView.cs` 的 CreateViewController 创建 ListViewController；它与基类 BaseListViewController 未覆写两向 ID 映射，`Collections/Controllers/CollectionViewController.cs` 125–139 默认返回参数本身。只据此讨论普通未换控制器的 ListView，不套用树、自定义控制器或其他版本。
- `Controls/BaseVerticalCollectionView.cs` 1196–1212 的查找从活动行返回根元素，未检查它在裁剪后的可视区。1404–1432 是索引入口和 ID 入口，后者先转成索引。文档另明示 -1 的末项语义。
- `Collections/Virtualization/FixedHeightVirtualizationController.cs` 49–87 的分支可以先设置偏移，也可以安排布局不干净时的延迟重试。共享 `VerticalVirtualizationController.cs` 244–279 保存并重放索引；282–330 保存焦点所在索引与行内路径。这里是条件性推断，未测到 Unity 实际发生错滚，不声称动态高度、重建或所有分支顺序相同。
- Godot 4.7.2 stable 下用远端原脚本重跑，JSON 与 4.6.3 存档逐字一致；仍是普通 Button，不能用来验证 Unity。新添 Python 应用模型直接验证重排后索引错位、无目标拒绝、行代次和可见性检查。没有运行 Unity。
