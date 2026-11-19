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
